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
    ('lighting', 'مسئول نور'),
    ('stage_manager', 'مدیر صحنه'),
    ('director_actor', 'کارگردان/بازیگر'),
    ('women_supervisor', 'سرپرست بانوان'),
    ('general_supervisor', 'سرپرست کل'),
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


# ۲. لیست شماره‌های مجاز بازیگران و عوامل (تولید اتوماتیک پسورد رندوم در صورت خالی گذاشتن ادمین)
class AllowedActorPhone(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    phone_number = models.CharField(max_length=11, unique=True, verbose_name="شماره همراه")
    password = models.CharField(max_length=128, blank=True, null=True, verbose_name="رمز عبور (اگر خالی بگذارید، سیستم خودکار رمز رندوم می‌سازد)")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='actor', verbose_name="نقش")
    role_description = models.CharField(max_length=100, default="عوامل/بازیگر", verbose_name="نقش / سمت")
    
    # فیلدهای عکس و بیوگرافی برای صفحه بیوگرافی بازیگران
    bio_image = models.ImageField(upload_to='actors/bio/', blank=True, null=True, verbose_name="عکس بیوگرافی (صفحه هنرمندان)")
    bio_text = models.TextField(blank=True, null=True, verbose_name="بیوگرافی کوتاه")

    def save(self, *args, **kwargs):
        # اگر ادمین پسورد را خالی گذاشت، سیستم خودکار یک رمز رندوم ۸ رقمی می‌سازد و هش می‌کند
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
        verbose_name = "شماره مجاز بازیگر"
        verbose_name_plural = "لیست شماره‌های مجاز بازیگران"


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


# ۵. نمایشنامه‌ها و تست نقش (Script)
class Script(models.Model):
    title = models.CharField(max_length=200, verbose_name="نام نمایشنامه")
    writer = models.CharField(max_length=100, verbose_name="نویسنده")
    file = models.FileField(upload_to="scripts/", verbose_name="فایل PDF نمایشنامه")
    is_audition_open = models.BooleanField(default=False, verbose_name="تست فعال است؟")

    class Meta:
        verbose_name = "نمایشنامه"
        verbose_name_plural = "نمایشنامه‌ها"

    def str(self):
        return self.title


# ۶. رزرو اجرا برای کاربران عادی (Show & Reservation)
class Show(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان نمایش")
    date_time = models.DateTimeField(verbose_name="زمان برگزاری")
    capacity = models.PositiveIntegerField(verbose_name="ظرفیت سالن")

    class Meta:
        verbose_name = "نمایش / اجرا"
        verbose_name_plural = "رزرو اجراها"

    def str(self):
        return self.title


class Reservation(models.Model):
    PLAY_CHOICES = [
        ('یاس پرپر', 'یاس پرپر'),
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


# ۷. فرم تست بازیگری
class Audition(models.Model):
    GENDER_CHOICES = [
        ('male', 'آقا'),
        ('female', 'خانم'),
    ]

    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    phone = models.CharField(max_length=11, verbose_name="شماره تماس")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="سن")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male', verbose_name="جنسیت")
    interest = models.CharField(max_length=100, null=True, blank=True, verbose_name="علاقه‌مندی")
    video_file = models.FileField(upload_to='auditions/videos/', null=True, blank=True, verbose_name="ویدیو ارسالی تست")
    experience = models.TextField(blank=True, null=True, verbose_name="سابقه کاری")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
class Meta:
        verbose_name = "درخواست تست بازیگری"
        verbose_name_plural = "درخواست‌های تست بازیگری"
        
def str(self):
        return f"{self.full_name} - {self.interest if self.interest else 'تست بازیگری'}"


# ۸. مدل نمایشنامه‌ها (Play) - با پوستر، تیزر و توضیحات کامل
class Play(models.Model):
    title = models.CharField(max_length=200, verbose_name="عنوان نمایشنامه") 
    poster = models.ImageField(upload_to='plays/posters/', verbose_name="پوستر نمایشنامه")
    teaser = models.FileField(upload_to='plays/teasers/', blank=True, null=True, verbose_name="ویدیو تیزر")
    short_description = models.TextField(max_length=300, verbose_name="توضیحات کوتاه")
    full_description = models.TextField(verbose_name="توضیحات کامل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "نمایشنامه"
        verbose_name_plural = "نمایشنامه‌ها"

    def str(self):
        return self.title


# ۹. مدل رویدادهای تاریخچه (HistoryEvent)
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


# ۱۰. مدل هنرمندان و بازیگران (Actor)
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