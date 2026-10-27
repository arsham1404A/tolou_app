from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, AllowedActorPhone, HomeBanner, 
    GalleryAlbum, GalleryPhoto, Script, 
    Show, Reservation, Audition, Play, HistoryEvent
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اطلاعات تکمیلی سامانه طلوع', {'fields': ('phone_number', 'avatar', 'role', 'role_description')}),
    )

@admin.register(AllowedActorPhone)
class AllowedActorPhoneAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'role', 'role_description')

@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'show_date', 'is_active')

@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ('album', 'caption')

@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'is_audition_open')

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time', 'capacity')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'city', 'play_title', 'offered_price', 'created_at')

@admin.register(Audition)
class AuditionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'age', 'created_at')

@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')

@admin.register(HistoryEvent)
class HistoryEventAdmin(admin.ModelAdmin):
    list_display = ('year', 'title')