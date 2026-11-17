import math
from PIL import Image
import jdatetime
from .forms import ActorArchiveUploadForm, PlayCreateForm
from .models import (
    Actor,
    Audition,
    GalleryAlbum,
    GalleryPhoto,
    HistoryEvent,
    HomeBanner,
    Play,
    Reservation,
    Script,
    Show,
    User,
    AllowedActorPhone,
    TechnicalIssue,
)
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render


# ۱. ویوی ورود اختصاصی عوامل و بازیگران (با شماره همراه و رمز عبور)
def actor_login(request):
    if request.method == "POST":
        phone = request.POST.get("phone_number", "").strip()
        password = request.POST.get("password", "").strip()

        if not phone or not password:
            messages.error(
                request, "لطفاً شماره همراه و رمز عبور خود را وارد کنید."
            )
            return render(request, "core/login.html")

        allowed_actor = AllowedActorPhone.objects.filter(
            phone_number=phone
        ).first()

        if allowed_actor:
            if allowed_actor.check_user_password(password):
                actor_name = getattr(allowed_actor, "full_name", "هنرمند")
                user, created = User.objects.get_or_create(
                    username=phone,
                    defaults={
                        "phone_number": phone,
                        "first_name": actor_name,
                        "role": allowed_actor.role,
                        "role_description": allowed_actor.role_description,
                    },
                )
                user.role = allowed_actor.role
                user.role_description = allowed_actor.role_description
                user.save()

                login(request, user)
                messages.success(request, f"خوش آمدید {actor_name} عزیز ⚡️")
                return redirect("home")
            else:
                messages.error(request, "رمز عبور اشتباه است.")
        else:
            messages.error(
                request, "این شماره تلفن در لیست عوامل و بازیگران ثبت نشده است."
            )

    return render(request, "core/login.html")


# ۱.الف - خروج از حساب کاربری
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "از حساب کاربری خارج شدید.")
    return redirect("home")


# ۲. ویوی ورود کاربران عادی با اکانت گوگل
def google_login_view(request):
    return redirect("home")


# ۳. ویوی اصلی سامانه (صفحه اصلی تئاتر طلوع) + بنر و تایمر زنده
def home_view(request):
    banner = HomeBanner.objects.filter(is_active=True).order_by("-id").first()
    shows = Show.objects.all()[:3]

    context = {
        "banner": banner,
        "shows": shows,
    }
    return render(request, "core/home.html", context)


# ۴. پروفایل هوشمند و مدیریت پنل‌ها
@login_required
def profile_view(request):
    user = request.user

    # دریافت تاریخ امروز به صورت شمسی و آنلاین از سیستم
    today_jalali = jdatetime.date.today()
    current_month = today_jalali.month
    current_day = today_jalali.day

    # بررسی تبریک تولد کاربر
    is_birthday_today = False
    if hasattr(user, "birth_date") and user.birth_date:
        try:
            parts = str(user.birth_date).split("/")
            if len(parts) == 3:
                b_month = int(parts[1])
                b_day = int(parts[2])
                if b_month == current_month and b_day == current_day:
                    is_birthday_today = True
        except (ValueError, IndexError):
            pass

    # اطلاعات پایه پنل‌ها
    reservations = []
    if user.role in ["general_supervisor", "women_supervisor"] or user.is_superuser:
        reservations = Reservation.objects.all().order_by("-created_at")

    auditions = []
    if user.role in ["director_actor", "general_supervisor"] or user.is_superuser:
        auditions = Audition.objects.all().order_by("-created_at")
 # گزارش مشکلات تجهیزات برای سرپرست
    technical_issues = []
    if user.role in ["general_supervisor", "women_supervisor"] or user.is_superuser:
        technical_issues = TechnicalIssue.objects.all().order_by("-created_at")

    context = {
        "user": user,
        "is_birthday_today": is_birthday_today,
        "today_jalali": f"{today_jalali.year}/{today_jalali.month}/{today_jalali.day}",
        "reservations": reservations,
        "auditions": auditions,
        "technical_issues": technical_issues,
    }

    # آپدیت آواتار با ایجکس
    if request.method == "POST" and request.FILES.get("avatar"):
        user.avatar = request.FILES["avatar"]
        user.save()
        return JsonResponse({"status": "success", "avatar_url": user.avatar.url})

    return render(request, "core/profile.html", context)


# ۴.ب - ثبت بازیگر جدید توسط کارگردان یا سرپرست
@login_required
def add_actor_view(request):
    if request.user.role not in ["director_actor", "general_supervisor", "women_supervisor"] and not request.user.is_superuser:
        return redirect("home")

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        role = request.POST.get("role", "actor")
        role_description = request.POST.get("role_description", "")

        if phone_number and password:
            AllowedActorPhone.objects.create(
                full_name=full_name,
                phone_number=phone_number,
                plain_password=password,
                role=role,
                role_description=role_description
            )
            messages.success(request, f"بازیگر {full_name} با موفقیت ثبت شد.")
            return redirect("profile")
        else:
            messages.error(request, "شماره همراه و رمز عبور الزامی است.")

    return render(request, "core/add_actor.html")


# ۵. ویوی نمایشنامه‌ها
def plays_view(request):
    plays = Play.objects.all().order_by("-created_at")
    return render(request, "core/plays.html", {"plays": plays})


# ۶. ویوی تاریخچه
def history_view(request):
    events = HistoryEvent.objects.all().order_by("-id")
    return render(request, "core/history.html", {"events": events})


# ۷. ویوی گالری و آرشیو تصاویر (همراه با هوش مصنوعی و آپلود عکاس)
def gallery_list_view(request):
    albums = GalleryAlbum.objects.all().order_by("-created_at")
    return render(request, "core/gallery_list.html", {"albums": albums})


def calculate_image_similarity(img1_path, img2_path):
    """محاسبه شباهت بصری و هیستوگرام رنگی دو تصویر با Pillow"""
    try:
        img1 = Image.open(img1_path).convert("RGB").resize((64, 64))
        img2 = Image.open(img2_path).convert("RGB").resize((64, 64))
        
        h1 = img1.histogram()
        h2 = img2.histogram()
        
        rms = math.sqrt(sum((a - b) ** 2 for a, b in zip(h1, h2)) / len(h1))
        similarity = max(0, 100 - (rms / 15))
        return similarity
    except Exception:
        return 0


def gallery_detail_view(request, album_id):
    album = get_object_or_404(GalleryAlbum, id=album_id)
    photos = album.photos.all().order_by("-id")
    matched_photos = None
    is_ai_search = False

    if request.method == "POST":
        # ۱. آپلود عکس جدید توسط عکاسان یا عوامل مجاز
        if "upload_photo" in request.POST and request.user.is_authenticated:
            if request.user.role in ["photographer", "director_actor", "general_supervisor", "women_supervisor"] or request.user.is_superuser:
                new_img = request.FILES.get("photo_file")
                caption = request.POST.get("caption", "")
                if new_img:
                    GalleryPhoto.objects.create(
                        album=album,
                        image=new_img,
                        caption=caption
                    )
                    messages.success(request, "تصویر با موفقیت به آلبوم اضافه شد 📸")
                    return redirect("gallery_detail", album_id=album.id)
 # ۲. جستجوی هوشمند با تصویر (مخصوص بازیگران و عوامل)
        elif "ai_search" in request.POST and request.FILES.get("reference_image"):
            ref_img = request.FILES["reference_image"]
            is_ai_search = True
            scored_photos = []

            for photo in photos:
                if photo.image:
                    score = calculate_image_similarity(ref_img, photo.image.path)
                    if score >= 55:  # آستانه شباهت قابل قبول
                        scored_photos.append((score, photo))
            
            scored_photos.sort(key=lambda x: x[0], reverse=True)
            matched_photos = [item[1] for item in scored_photos]

    context = {
        "album": album,
        "photos": matched_photos if is_ai_search else photos,
        "is_ai_search": is_ai_search,
    }
    return render(request, "core/gallery_detail.html", context)


# ۸. ویوی صفحه هنرمندان و بیوگرافی بازیگران
def actors_view(request):
    actors = AllowedActorPhone.objects.filter(
        role__in=["actor", "director_actor", "photographer", "sound_light", "logistics"]
    ).order_by("id")
    return render(request, "core/actors.html", {"actors": actors})


# ۹. ویوی ثبت تست بازیگری
def audition_submit_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        gender = request.POST.get("gender")
        interest = request.POST.get("interest")
        video_file = request.FILES.get("video_file")

        Audition.objects.create(
            full_name=full_name,
            phone=phone,
            gender=gender,
            interest=interest,
            video_file=video_file,
        )
        messages.success(
            request,
            "درخواست تست بازیگری شما با موفقیت ثبت شد. در صورت تایید با شما تماس گرفته خواهد شد.",
        )
        return redirect("home")
    return render(request, "core/audition_form.html")


# ۱۰. ویوی ثبت فرم رزرو اجرا توسط کاربر
def reservation_form_view(request):
    if request.method == "POST":
        Reservation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            province=request.POST.get("province"),
            city=request.POST.get("city"),
            address=request.POST.get("address"),
            sound_capacity=request.POST.get("sound_capacity"),
            light_capacity=request.POST.get("light_capacity"),
            play_title=request.POST.get("play_title"),
            offered_price=request.POST.get("offered_price"),
        )
        messages.success(
            request,
            "درخواست رزرو اجرا با موفقیت ثبت شد. در صورت تایید با شما تماس گرفته خواهد شد ⚡️",
        )
        return redirect("home")
    return render(request, "core/reservation_form.html")


# ۱۱. ویوی صفحه کمک به گروه
def help_group_view(request):
    return render(request, "core/help_group.html")


# ۱۲. ویوی صفحه آخرین اجراها و آرشیو (Past Shows)
def past_shows_view(request):
    past_shows = HomeBanner.objects.all().order_by("-show_date")
    return render(request, "core/past_shows.html", {"past_shows": past_shows})


# ۱۳. افزودن نمایشنامه جدید توسط کارگردان
@login_required
def add_play_view(request):
    if request.user.role not in ["director_actor", "general_supervisor"] and not request.user.is_superuser:
        return redirect("home")

    if request.method == "POST":
        form = PlayCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("plays")
    else:
        form = PlayCreateForm()

    return render(request, "core/play_form.html", {"form": form})


# ۱۴. آپلود تصویر در آرشیو اختصاصی بازیگر/عکاس
@login_required
def upload_actor_archive(request):
    if request.method == "POST":
        form = ActorArchiveUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            if not photo.caption:
                photo.caption = request.user.username
            photo.save()
            return redirect("profile")
    else:
        form = ActorArchiveUploadForm()

    return render(request, "core/upload_archive.html", {"form": form})


# ۱۵. ویوی ثبت مشکلات تجهیزات (صوت، نور، تدارکات)
@login_required
def report_issue_view(request):
    if request.method == "POST":
        section = request.POST.get("section")
        title = request.POST.get("title")
        description = request.POST.get("description")
        
        allowed_reporter = AllowedActorPhone.objects.filter(phone_number=request.user.phone_number).first()
        
        if allowed_reporter:
            TechnicalIssue.objects.create(
                reporter=allowed_reporter,
                section=section,
                title=title,
                description=description
            )
            messages.success(request, "گزارش مشکل تجهیزات با موفقیت ثبت شد.")
            return redirect("profile")
        else:
            messages.error(request, "شما دسترسی لازم برای ثبت گزارش را ندارید.")
            
    return render(request, "core/report_issue.html")