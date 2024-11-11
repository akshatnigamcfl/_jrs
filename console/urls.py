from django.urls import path
from .views import *


urlpatterns = [
    
path('', dashboard, name='dashboard_be'),
path('dashboard', dashboard, name='dashboard_be'),
path('booking', booking, name='booking_be'),
path('clients', clients, name='clients_be'),
path('client-edit', client_edit, name='client_edit_be'),
path('uploads', uploads, name='uploads_be'),
# path('pre-wedding', pre_wedding, name='pre_wedding_be'),
# path('events', events, name='events_be'),
# path('wedding', wedding, name='wedding_be'),
# path('reels', reels, name='reels_be'),
path('payment', payments, name='payment_be'),
path('reviews', reviews, name='reviews_be'),
# path('quotation', quotation, name='quotation_be'),
path('administration', administration, name='administration_be'),
path('team', team, name='team_be'),
path('team_profile/<int:id>/<str:token>', team_profile, name='team_profile_be'),
path('login', login, name='login_be'),
path('team/login', teamlogin, name='team_login_be'),
path('logout', logout, name='logout_be'),
path('invoice_template', invoice_template, name='invoice_template'),

path('generate_password/<int:id>/<str:user_token>', generate_password, name='generate_password'),


path('forgot_password', user_forgot_password, name='user_forgot_password'),
path('reset_password/<int:id>/<str:client_token>', user_reset_password, name='user_reset_password'),

path('team/forgot_password', team_forgot_password, name='team_forgot_password'),    
path('team/reset_password/<int:id>/<str:client_token>', team_reset_password, name='team_reset_password'),

# path('test', test, name='test'),



]