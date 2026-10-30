from django.contrib import admin
from .models import (
    AllowedActorPhone, 
    HomeBanner, 
    GalleryAlbum, 
    GalleryPhoto, 
    Script, 
    Show, 
    Reservation, 
    Audition, 
    Play, 
    HistoryEvent, 
    Actor
)

@admin.register(AllowedActorPhone)
class AllowedActorPhoneAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'role', 'role_description', 'display_password')
    list_filter = ('role',)
    search_fields = ('full_name', 'phone_number')
    
    # اضافه کردن فیلدهای بیوگرافی و عکس به پنل ادمین
    fieldsets = (
        ('اطلاعات اصلی و حساب کاربری', {
            'fields': ('full_name', 'phone_number', 'password', 'role', 'role_description')
        }),
        ('اطلاعات صفحه بیوگرافی بازیگران', {
            'fields': ('bio_image', 'bio_text')
        }),
    )

    def display_password(self, obj):
        return "****"
    display_password.short_description = "رمز عبور"


# این بخش به ادمین اجازه میده موقع ساخت یا ویرایش آلبوم، تا ۵۰ عکس رو یکجا آپلود کنه
class GalleryPhotoInline(admin.TabularInline):
    model = GalleryPhoto
    extra = 10  # تعداد کادرهای پیش‌فرض
    max_num = 50  # حداکثر سقف عکس‌ها در هر آلبوم


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    inlines = [GalleryPhotoInline]


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'show_date', 'is_active')
    list_filter = ('is_active',)


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'is_audition_open')
    list_filter = ('is_audition_open',)


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time', 'capacity')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'play_title', 'city', 'phone', 'created_at')
    list_filter = ('play_title', 'city')
    search_fields = ('full_name', 'phone', 'city')


@admin.register(Audition)
class AuditionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'gender', 'interest', 'created_at')
    list_filter = ('gender', 'interest')
    search_fields = ('full_name', 'phone')


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(HistoryEvent)
class HistoryEventAdmin(admin.ModelAdmin):
    list_display = ('year', 'title')


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'created_at')
    search_fields = ('name', 'role')