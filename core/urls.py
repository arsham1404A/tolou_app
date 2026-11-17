from django.urls import path
from . import views

urlpatterns = [
    # صفحه اصلی و احراز هویت
    path("", views.home_view, name="home"),
    path("actor-login/", views.actor_login, name="actor_login"),
    path("logout/", views.logout_view, name="logout"), # اضافه شدن خروج از حساب
    path("google-login/", views.google_login_view, name="google_login_view"),
    
    # پروفایل و پنل کاربری (منوی سه خط)
    path("profile/", views.profile_view, name="profile"),
    path("add-actor/", views.add_actor_view, name="add_actor"), # ثبت بازیگر/عامل جدید توسط کارگردان یا سرپرست
    
    # نمایشنامه‌ها و تست‌ها
    path("plays/", views.plays_view, name="plays"),
    path("plays/add/", views.add_play_view, name="add_play"), # افزودن نمایشنامه و نقش‌ها توسط کارگردان
    path("audition/", views.audition_submit_view, name="audition_form"),
    
    # آرشیو تصاویر و هوش مصنوعی
    path("gallery/", views.gallery_list_view, name="gallery_list"),
    path("gallery/<int:album_id>/", views.gallery_detail_view, name="gallery_detail"),
    
    # سایر بخش‌ها
    path("actors/", views.actors_view, name="actors"),
    path("reservation/", views.reservation_form_view, name="reservation_form"),
    path("history/", views.history_view, name="history"),
    path("past-shows/", views.past_shows_view, name="past_shows"),
    path("help-group/", views.help_group_view, name="help_group"),
    
    # بخش مشکلات تجهیزات (صوت، نور و تدارکات)
    path("report-issue/", views.report_issue_view, name="report_issue"), 
]