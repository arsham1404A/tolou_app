from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('actor-login/', views.actor_login, name='actor_login'),
    path('google-login/', views.google_login_view, name='google_login_view'),
    path('profile/', views.profile_view, name='profile'),
    path('plays/', views.plays_view, name='plays'),
    path('history/', views.history_view, name='history'),
    path('gallery/', views.gallery_list_view, name='gallery_list'),
    path('gallery/<int:album_id>/', views.gallery_detail_view, name='gallery_detail'),
    path('actors/', views.actors_view, name='actors'),path('reservation/', views.reservation_form_view, name='reservation_form'),
    path('audition/', views.audition_submit_view, name='audition_form'),
    path('help-group/', views.help_group_view, name='help_group'),
    path('past-shows/', views.past_shows_view, name='past_shows'),
]