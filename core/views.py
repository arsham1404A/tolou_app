from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import AllowedActorPhone, User, HomeBanner, Show, Play, HistoryEvent, GalleryAlbum, GalleryPhoto, Actor, Audition, Reservation

# ۱. ویوی ورود اختصاصی عوامل و بازیگران (با شماره همراه)
def actor_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number', '').strip()
        
        if not phone:
            messages.error(request, "لطفاً شماره همراه خود را وارد کنید.")
            return render(request, 'core/login.html')
        
        allowed_actor = AllowedActorPhone.objects.filter(phone_number=phone).first()
        
        if allowed_actor:
            actor_name = getattr(allowed_actor, 'full_name', 'هنرمند')
            user, created = User.objects.get_or_create(
                username=phone,
                defaults={
                    'phone_number': phone,
                    'first_name': actor_name,
                    'role': allowed_actor.role,
                    'role_description': allowed_actor.role_description
                }
            )
            login(request, user)
            messages.success(request, f"خوش آمدید {actor_name} عزیز ⚡️")
            return redirect('home')
        else:
            messages.error(request, "این شماره تلفن در لیست عوامل و بازیگران ثبت نشده است.")
            
    return render(request, 'core/login.html')


# ۲. ویوی ورود کاربران عادی با اکانت گوگل
def google_login_view(request):
    return redirect('home')


# ۳. ویوی اصلی سامانه (صفحه اصلی تئاتر طلوع) + بنر و تایمر زنده
def home_view(request):
    banner = HomeBanner.objects.filter(is_active=True).order_by('-id').first()
    shows = Show.objects.all()[:3]
    
    context = {
        'banner': banner,
        'shows': shows,
    }
    return render(request, 'core/home.html', context)


# ۴. ویوی پروفایل کاربر (نمایش رزروها برای سرپرست و تست‌ها برای کارگردان)
@login_required
def profile_view(request):
    user = request.user
    
    reservations = []
    if user.role == 'general_supervisor' or user.is_superuser:
        reservations = Reservation.objects.all().order_by('-created_at')

    auditions = []
    if user.role in ['director_actor', 'general_supervisor'] or user.is_superuser:
        auditions = Audition.objects.all().order_by('-created_at')

    if request.method == 'POST' and request.FILES.get('avatar'):
        user.avatar = request.FILES['avatar']
        user.save()
        return JsonResponse({'status': 'success', 'avatar_url': user.avatar.url})
        
    context = {
        'user': user,
        'reservations': reservations,
        'auditions': auditions,
    }
    return render(request, 'core/profile.html', context)


# ۵. ویوی نمایشنامه‌ها
def plays_view(request):
    plays = Play.objects.all().order_by('-created_at')
    return render(request, 'core/plays.html', {'plays': plays})


# ۶. ویوی تاریخچه
def history_view(request):
    events = HistoryEvent.objects.all().order_by('-id')
    return render(request, 'core/history.html', {'events': events})


# ۷. ویوی گالری و آرشیو تصاویر
def gallery_list_view(request):
    albums = GalleryAlbum.objects.all().order_by('-created_at')
    return render(request, 'core/gallery_list.html', {'albums': albums})

def gallery_detail_view(request, album_id):
    album = GalleryAlbum.objects.get(id=album_id)
    photos = album.photos.all()
    return render(request, 'core/gallery_detail.html', {'album': album, 'photos': photos})


# ۸. ویوی صفحه هنرمندان (Actors)
def actors_view(request):
    actors = Actor.objects.all().order_by('id')
    return render(request, 'core/actors.html', {'actors': actors})
 # ۹. ویوی ثبت تست بازیگری (با دریافت ویدیو، جنسیت، علاقه‌مندی و ارسال به پنل کارگردان)
def audition_submit_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        interest = request.POST.get('interest')
        video_file = request.FILES.get('video_file')
        
        Audition.objects.create(
            full_name=full_name,
            phone=phone,
            gender=gender,
            interest=interest,
            video_file=video_file
        )
        messages.success(request, "درخواست تست بازیگری شما با موفقیت ثبت شد. در صورت تایید با شما تماس گرفته خواهد شد.")
        return redirect('home')
    return render(request, 'core/audition_form.html')


# ۱۰. ویوی ثبت فرم رزرو اجرا توسط کاربر (موافق با فرم جدید استان، شهر، صوت، نور و نمایشنامه)
def reservation_form_view(request):
    if request.method == 'POST':
        Reservation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            province=request.POST.get('province'),
            city=request.POST.get('city'),
            address=request.POST.get('address'),
            sound_capacity=request.POST.get('sound_capacity'),
            light_capacity=request.POST.get('light_capacity'),
            play_title=request.POST.get('play_title'),
            offered_price=request.POST.get('offered_price'),
        )
        messages.success(request, "درخواست رزرو اجرا با موفقیت ثبت شد. در صورت تایید با شما تماس گرفته خواهد شد ⚡️")
        return redirect('home')
    return render(request, 'core/reservation_form.html')


# ۱۱. ویوی صفحه کمک به گروه
def help_group_view(request):
    return render(request, 'core/help_group.html')
# ۱۲. ویوی صفحه آخرین اجراها و آرشیو (Past Shows)
def past_shows_view(request):
    # گرفتن تمام بنرها یا نمایش‌های ثبت شده به عنوان آرشیو اجراهای گذشته
    past_shows = HomeBanner.objects.all().order_by('-show_date')
    return render(request, 'core/past_shows.html', {'past_shows': past_shows})