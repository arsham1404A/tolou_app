from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
import random
import string

# 🎭 تعریف نقش‌های رسمی گروه تئاتر طلوع
ROLE_CHOICES = [
    ('actor', 'بازیگر'),
    ('logistics', 'تدارکات'),
    ('lighting', 'مسئول نور و صوت'),
    ('stage_manager', 'مدیر صحنه'),
    ('director_actor', 'کارگردان/بازیگر'),
    ('women_supervisor', 'سرپرست بانوان'),
    ('general_supervisor', 'سرپرست کل'),
    ('photographer', 'عکاس'),
]

PLAY_CHOICES = [
    ('یاس پرپر', 'یاس پرپر'),
    ('بانوی بهشت', 'بانوی بهشت'),
    ('حضرت عباس', 'حضرت عباس'),
    ('امام حسین', 'امام حسین'),
    ('حضرت علی اکبر', 'حضرت علی اکبر'),
    ('حضرت قاسم', 'حضرت قاسم'),
    ('حضرت رقیه', 'حضرت رقیه'),
]

QUALITY_CHOICES = [
    ('ندارد', 'ندارد'),
    ('ضعیف', 'ضعیف'),
    ('خوب', 'خوب'),
    ('خیلی خوب', 'خیلی خوب'),
]


# ۱. مدل کاربر سفارشی برای سامانه
class User(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name="شماره همراه")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, verbose_name="تصویر پروفایل")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='actor', verbose_name="نقش در گروه")
    role_description = models.CharField(max_length=100, default="عوامل/بازیگر", verbose_name="عنوان سمت")

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def str(self):
        return f"{self.username} - {self.get_role_display()}"


# ۲. لیست شماره‌های مجاز بازیگران و عوامل (تولید اتوماتیک پسورد رندوم)
class AllowedActorPhone(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    phone_number = models.CharField(max_length=11, unique=True, verbose_name="شماره همراه")
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name="رمز عبور")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='actor', verbose_name="نقش")
    role_description = models.CharField(max_length=100, default="عوامل/بازیگر", verbose_name="نقش / سمت")

    bio_image = models.ImageField(upload_to='actors/bio/', blank=True, null=True, verbose_name="عکس بیوگرافی")
    bio_text = models.TextField(blank=True, null=True, verbose_name="بیوگرافی کوتاه")

    def save(self, *args, **kwargs):
        if not self.password:
            random_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            self.password = make_password(random_pass)
        elif not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def check_user_password(self, raw_password):
        return check_password(raw_password, self.password)

    def str(self):
        return f"{self.full_name} - {self.get_role_display()} ({self.phone_number})"

    class Meta:
        verbose_name = "شماره مجاز بازیگر/عامل"
        verbose_name_plural = "لیست شماره‌های مجاز عوامل"


# ۳. پوستر روزشمار / آخرین اجرا (HomeBanner)
class HomeBanner(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان نمایش / پوستر")
    image = models.ImageField(upload_to="banners/", verbose_name="تصویر پوستر")
    show_date = models.DateTimeField(null=True, blank=True, verbose_name="روزشمار")
    is_active = models.BooleanField(default=True, verbose_name="فعال در صفحه اصلی")

    class Meta:
        verbose_name = "پوستر صفحه اصلی"
        verbose_name_plural = "پوسترهای صفحه اصلی"

    def str(self):
        return self.title


# ۴. آرشیو تصاویر و مناسبت‌ها (Gallery Album & Photos)
class GalleryAlbum(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان مناسبت / آلبوم")
    cover_image = models.ImageField(upload_to='gallery/covers/', verbose_name="تصویر کاور آلبوم")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
class Meta:
        verbose_name = "آلبوم گالری"
        verbose_name_plural = "آرشیو تصاویر و آلبوم‌ها"
        def str(self):
            return self.title


class GalleryPhoto(models.Model):
    album = models.ForeignKey(GalleryAlbum, on_delete=models.CASCADE, related_name='photos', verbose_name="آلبوم مربوطه")
    image = models.ImageField(upload_to='gallery/photos/', verbose_name="تصویر")
    caption = models.CharField(max_length=255, blank=True, null=True, verbose_name="توضیح کوتاه عکس")

    class Meta:
        verbose_name = "تصویر گالری"
        verbose_name_plural = "تصاویر آلبوم‌ها"

    def str(self):
        return f"عکس آلبوم {self.album.title}"


# ۵. مدل نمایشنامه‌ها (Play) - با پوستر، تیزر و توضیحات کامل
class Play(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان نمایشنامه")
    writer = models.CharField(max_length=100, blank=True, null=True, verbose_name="نویسنده")
    poster = models.ImageField(upload_to='plays/posters/', verbose_name="پوستر نمایشنامه")
    teaser = models.FileField(upload_to='plays/teasers/', blank=True, null=True, verbose_name="ویدیو تیزر")
    file = models.FileField(upload_to="scripts/", blank=True, null=True, verbose_name="فایل PDF نمایشنامه")
    short_description = models.TextField(max_length=300, verbose_name="توضیحات کوتاه")
    full_description = models.TextField(verbose_name="توضیحات کامل")
    is_audition_open = models.BooleanField(default=False, verbose_name="تست برای این نمایشنامه فعال است؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "نمایشنامه"
        verbose_name_plural = "نمایشنامه‌ها"

    def str(self):
        return self.title


# ۶. مدل نقش‌های هر نمایشنامه (جهت تخصیص به بازیگران یا تست دادن)
class PlayRole(models.Model):
    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name='roles', verbose_name="نمایشنامه")
    role_name = models.CharField(max_length=100, verbose_name="نام نقش")
    description = models.TextField(blank=True, null=True, verbose_name="ویژگی‌های نقش")
    assigned_actor = models.ForeignKey(AllowedActorPhone, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_roles', verbose_name="بازیگر انتخاب شده")
    is_filled = models.BooleanField(default=False, verbose_name="نقش پر شده است؟")

    class Meta:
        verbose_name = "نقش نمایشنامه"
        verbose_name_plural = "نقش‌های نمایشنامه‌ها"

    def str(self):
        return f"{self.role_name} در {self.play.title}"


# ۷. فرم تست بازیگری (برای درخواست‌های ورودی کاربران)
class Audition(models.Model):
    GENDER_CHOICES = [
        ('male', 'آقا'),
        ('female', 'خانم'),
    ]

    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=11, verbose_name="شماره تماس")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="سن")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male', verbose_name="جنسیت")
    interest = models.CharField(max_length=100, null=True, blank=True, verbose_name="علاقه‌مندی / نقش")
    target_play = models.ForeignKey(Play, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="مربوط به نمایشنامه")
    video_file = models.FileField(upload_to='auditions/videos/', null=True, blank=True, verbose_name="ویدیو ارسالی تست")
    experience = models.TextField(blank=True, null=True, verbose_name="سابقه کاری")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "درخواست تست بازیگری"
        verbose_name_plural = "درخواست‌های تست بازیگری"

    def str(self):
        return f"{self.full_name} - {self.interest if self.interest else 'تست بازیگری'}"
 # ۸. رزرو اجرا و درخواست‌های سالن
class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="کاربر ثبت‌کننده", null=True, blank=True)
    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=11, verbose_name="شماره همراه")
    province = models.CharField(max_length=50, verbose_name="استان")
    city = models.CharField(max_length=50, verbose_name="شهر")
    address = models.TextField(verbose_name="آدرس دقیق محل مورد نظر")
    sound_capacity = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='خوب', verbose_name="ظرفیت صوت مکان")
    light_capacity = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='خوب', verbose_name="ظرفیت نور")
    play_title = models.CharField(max_length=50, choices=PLAY_CHOICES, verbose_name="نمایشنامه مورد نظر برای اجرا")
    offered_price = models.CharField(max_length=50, verbose_name="مبلغ پیشنهادی (به ریال)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت درخواست")

    class Meta:
        verbose_name = "رزرو اجرا"
        verbose_name_plural = "درخواست‌های رزرو اجرا"

    def str(self):
        return f"{self.full_name} - {self.play_title} ({self.city})"


# ۹. مدل گزارش مشکلات تجهیزات (صوت، نور، تدارکات) برای نمایش در داشبورد سرپرست
class TechnicalIssue(models.Model):
    SECTION_CHOICES = [
        ('sound_light', 'صوت و نور'),
        ('logistics', 'تدارکات'),
        ('stage', 'صحنه'),
    ]

    reporter = models.ForeignKey(AllowedActorPhone, on_delete=models.CASCADE, verbose_name="گزارش‌دهنده")
    section = models.CharField(max_length=30, choices=SECTION_CHOICES, verbose_name="بخش مربوطه")
    title = models.CharField(max_length=150, verbose_name="عنوان مشکل / تجهیز معیوب")
    description = models.TextField(verbose_name="شرح کامل مشکل")
    is_resolved = models.BooleanField(default=False, verbose_name="برطرف شده؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ گزارش")

    class Meta:
        verbose_name = "مشکل تجهیزات"
        verbose_name_plural = "گزارش مشکلات تجهیزات (فنی و تدارکات)"

    def str(self):
        status = "حل شده" if self.is_resolved else "در انتظار بررسی"
        return f"{self.get_section_display()}: {self.title} ({status})"


# ۱۰. مدل رویدادهای تاریخچه (HistoryEvent)
class HistoryEvent(models.Model):
    year = models.CharField(max_length=20, verbose_name="سال / تاریخ")
    title = models.CharField(max_length=200, verbose_name="عنوان رویداد")
    description = models.TextField(verbose_name="توضیحات کامل")
    image = models.ImageField(upload_to='history/', blank=True, null=True, verbose_name="تصویر رویداد")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "رویداد تاریخچه"
        verbose_name_plural = "تاریخچه و رویدادها"

    def str(self):
        return f"{self.year} - {self.title}"


# ۱۱. مدل هنرمندان و بازیگران بخش بیوگرافی (Actor)
class Actor(models.Model):
    name = models.CharField(max_length=150, verbose_name="نام هنرمند")
    role = models.CharField(max_length=150, verbose_name="نقش در تئاتر", blank=True, null=True)
    image = models.ImageField(upload_to='actors/', blank=True, null=True, verbose_name="تصویر هنرمند")
    bio = models.TextField(blank=True, null=True, verbose_name="بیوگرافی و توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "هنرمند"
        verbose_name_plural = "هنرمندان و بازیگران"

    def str(self):
        return self.name