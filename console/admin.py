from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register([canned_email,Drp_booking_status, Service, AdditionalService ,Package, Booking, Segment])