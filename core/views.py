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
)
from django.contrib import messages
from django.contrib.auth import login
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


# ۴. داشبورد و پروفایل هوشمند (با قابلیت تبریک تولد شمسی آنلاین و پنل‌های تفکیک‌شده)
@login_required
def dashboard_view(request):
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
    if (
        user.role in ["general_supervisor", "women_supervisor"]
        or user.is_superuser
    ):
        reservations = Reservation.objects.all().order_by("-created_at")

    auditions = []
    if user.role in ["director_actor", "general_supervisor"] or user.is_superuser:
        auditions = Audition.objects.all().order_by("-created_at")
 # ساخت کانتکست عمومی برای جلوگیری از خطای ۵۰۰
    context = {
        "user": user,
        "is_birthday_today": is_birthday_today,
        "today_jalali": f"{today_jalali.year}/{today_jalali.month}/{today_jalali.day}",
        "reservations": reservations,
        "auditions": auditions,
    }

    # آپدیت آواتار با ایجکس
    if request.method == "POST" and request.FILES.get("avatar"):
        user.avatar = request.FILES["avatar"]
        user.save()
        return JsonResponse({"status": "success", "avatar_url": user.avatar.url})

    # تفکیک رندر بر اساس نقش گروه طلوع
    if user.role == "director_actor":
        context["plays"] = Play.objects.all()
        return render(request, "core/director_panel.html", context)
    elif user.role in ["general_supervisor", "women_supervisor"]:
        context["actors"] = User.objects.filter(role="actor")
        return render(request, "core/supervisor_panel.html", context)
    else:
        context["my_photos"] = GalleryPhoto.objects.filter(
            caption__icontains=user.username
        )
        return render(request, "core/actor_panel.html", context)


# 4.1 ویوی پروفایل اختصاصی (برای مچ شدن با urls.py)
@login_required
def profile_view(request):
    return render(request, "core/profile.html", {"user": request.user})


# ۵. ویوی نمایشنامه‌ها
def plays_view(request):
    plays = Play.objects.all().order_by("-created_at")
    return render(request, "core/plays.html", {"plays": plays})


# ۶. ویوی تاریخچه
def history_view(request):
    events = HistoryEvent.objects.all().order_by("-id")
    return render(request, "core/history.html", {"events": events})


# ۷. ویوی گالری و آرشیو تصاویر
def gallery_list_view(request):
    albums = GalleryAlbum.objects.all().order_by("-created_at")
    return render(request, "core/gallery_list.html", {"albums": albums})


def gallery_detail_view(request, album_id):
    album = get_object_or_404(GalleryAlbum, id=album_id)
    photos = album.photos.all()
    return render(
        request, "core/gallery_detail.html", {"album": album, "photos": photos}
    )


# ۸. ویوی صفحه هنرمندان و بیوگرافی بازیگران
def actors_view(request):
    actors = AllowedActorPhone.objects.filter(
        role__in=["actor", "director_actor"]
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
def play_create_view(request):
    if request.user.role not in ["director_actor", "general_supervisor"]:
        return redirect("dashboard")

    if request.method == "POST":
        form = PlayCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = PlayCreateForm()

    return render(request, "core/play_form.html", {"form": form})


# ۱۴. آپلود تصویر در آرشیو اختصاصی بازیگر
@login_required
def upload_actor_archive(request):
    if request.method == "POST":
        form = ActorArchiveUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            if not photo.caption:
                photo.caption = request.user.username
            photo.save()
            return redirect("dashboard")
    else:
        form = ActorArchiveUploadForm()

    return render(request, "core/upload_archive.html", {"form": form})