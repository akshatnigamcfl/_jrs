from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('<int:client_id>/<int:booking_id>/<str:client_token>', home_client, name='home'),
    # path('home2', home2, name='home'),
    path('wedding', wedding, name='wedding'),
    path('cinematic', cinematic, name='cinematic'),
    path('pre-wedding', pre_wedding, name='pre-wedding'),
    path('pre-wedding/watch/<int:id>', pre_wedding_view, name='contact'),
    path('events', events, name='events'),
    path('reels', reels, name='reels'),
    path('team', team, name='team'),
    path('gallery', gallery, name='gallery'),
    path('about', about, name='about'),
    path('contact', contact, name='contact'),

    
    path('dashboard', client_dashboard, name='client_dashboard'),
    path('payment', client_payment, name='client_payment'),
    path('client-info/<int:client_id>/<int:booking_id>/<str:client_token>', client_info, name='client_info'),
    path('client-reviews/<int:client_id>/<int:booking_id>/<str:client_token>', client_reviews, name='client_reviews'),
    path('client-bookings', client_bookings, name='client_bookings'),
    path('client-info-confirm-booking/<int:booking_id>/<str:client_token>', client_info_confirm_booking, name='client_info_confirm_booking'),
    # path('scroller_test', scroller_test, name='scroller_test'),

    # path('generate_password/<int:id>/<str:user_token>', generate_password, name='generate_password'),



    path('login', user_login, name='login'),

    path('settings', settings, name='settings'),
    path('logout', user_logout, name='logout'),
    path('forgot_password', user_forgot_password, name='forgot_password'),
    path('reset_password/<int:id>/<str:client_token>', user_reset_password, name='reset_password'),
    # path('signup', user_signup, name='signup'),
    
    
]
