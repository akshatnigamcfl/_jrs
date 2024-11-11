from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.hashers import make_password


from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt import views as jwt_views

from console.models import UserAccount
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from api.main_functions import SendEmail
from api.views import generate_random_code
import random


from api.views import get_tokens_for_user
from collections import Counter


from django import template
register = template.Library()

@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    # you would need to do any localization of the result here
    return qty * unit_price


# Create your views here.

def validate_user(request):
    if request.COOKIES:

        try:
            if AccessToken(request.COOKIES.get('access')):
                token = AccessToken(request.COOKIES.get('access'))
                payload = token.payload
                if 'user_id' in payload:
                    user = UserAccount.objects.filter(user=payload['user_id'])
                    user_type = 'admin'
                    if not user.exists():
                        user = Team_member.objects.filter(user=payload['user_id'])
                        user_type = 'team'
                    return {'user': user.first(), 'status': user.exists(), 'user_type': user_type}
                else :
                    return {'user': None, 'status': False, 'user_type': None}

            # token_obj = Token.objects.get(key=request.COOKIES.get('access'))
            # current_time = timezone.now()
            # return token_obj.created < current_time - timezone.timedelta(days=1)  # Adjust the timedelta as needed    
        except:
            try:
                refreshToken = RefreshToken(str(request.COOKIES.get('refresh')))
                current_time = datetime.utcnow()

                token_created_at = refreshToken.payload['iat']
                token_life = refreshToken.lifetime.total_seconds()
                if token_created_at + token_life < current_time.timestamp():
                    return {'user': None, 'status': False}
                
                else:
                    user = UserAccount.objects.filter(user=refreshToken['user_id']).first()
                    user_type = 'admin'
                    if not user:
                        user = Team_member.objects.filter(user=payload['user_id'])
                        user_type = 'team'
                    return {'user':user, 'status': 'access_expired', 'user_type': user_type}
                    
            except:
                return {'user': None, 'status': False, 'user_type': None}
    else:
        return {'user': None, 'status': False, 'user_type': None }




def validate_loggedin(request):
    validation = validate_user(request)
    if validation['status'] == False:
        return redirect('/console/login')
    elif validation['status'] == 'access_expired':
        return validation
    elif validation['status'] == True:
        return validation

def regenerateToken(user, context):
    tokens = get_tokens_for_user(user)
    context['token'] = tokens['access']
    return tokens

def regenerateCookies(res,tokens):
    res.set_cookie(key = 'access', value = tokens['access'], expires= settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'], secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'], httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'], samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
    # res.set_cookie(key = 'refresh', value = tokens['refresh'], expires= settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'], secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'], httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'], samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])

def first_login_check(validation):
    pass
    if validation['user_type'] and validation['user_type'] == 'team':
        if validation['user'] == None:
            return redirect('/console/team/login')
        if validation['user'].first_login == True:
            return redirect(f'/console/generate_password/{validation['user'].user.id}/{validation['user'].user_token}')


# def getUserType(user_id):
#     user_type = ''
#     try:
#         user = UserAccount.objects.get(user__id=user_id)
#         user = 'admin'
#     except:
#         try:
#             user = Team_member.objects.get(user_id=user_id)
#             user_type = 'team'
#         except:
#             user = None
#             user_type = None
#     return {'user': user, 'user_type':user_type }

def login(request):
    # print('login worked')
    
    try:
        validation = validate_loggedin(request)
        if validation['status'] == True or validation['status'] == 'access_expired':
            return redirect('/console/dashboard')
        
        # return render(request, 'console_login.html')
    
        encCount = EncoderDecoder.objects.count()
        int = random.randint(0, encCount - 1)
        res = render(request, 'console_login.html')
        res.set_cookie('ed', EncoderDecoder.objects.filter(id=int).first().code, max_age=3600)
        return res
    
    except:

        encCount = EncoderDecoder.objects.count()
        int = random.randint(0, encCount - 1)
        res = render(request, 'console_login.html')
        res.set_cookie('ed', EncoderDecoder.objects.filter(id=int).first().code, max_age=3600)
        return res



def teamlogin(request):
    try:
        validation = validate_loggedin(request)
        if validation['status'] == True or validation['status'] == 'access_expired':
            return redirect('/console/dashboard')
    
        return render(request, 'console_team_login.html')
    
    except:
        return render(request, 'console_team_login.html')
    


def validation_admin_pages(request, user_type):
    try:
        validation = validate_loggedin(request)

        first_login = first_login_check(validation)
        print('first_login', first_login)
        if first_login: return first_login

        if validation['user'] !=None and validation['status'] == 'access_expired' or validation['status'] == True :
            print('expired access')
            return validation
        else:

            if user_type == 'all':
                if validation['status'] == False:
                    return redirect('/console/login')

            elif user_type == 'admin':
                if validation['status'] == False or not validation['user_type'] == 'admin':
                    return redirect('/console/login')

    except:
        return redirect('/console/login')
    


def tokenResponseCheck(validation, context):
    # print('validation', validation)
    if validation['status']=='access_expired':
        tokens = regenerateToken(validation['user'].user,context)
    else:
        tokens = None
    return tokens



def cookiesResponseCheck(validation, res,tokens):
    # print('validation', validation)
    if validation['status']=='access_expired':
        regenerateCookies(res, tokens)
    return res










def dashboard(request):
    validation = validation_admin_pages(request, 'all')
    if not isinstance(validation, dict):
        return validation
    

    today = datetime.today().date()
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    payment_received_obj = Payments.objects.filter(date__month=current_month)

    context = { 'user': validation['user'], 'user_type': validation['user_type'], }
    
    if validation['user_type'] == 'admin':

        client = Client.objects.filter(user__created_at__month=current_month, user__created_at__year=current_year).count()
        pre_wedding = Pre_Wedding.objects.filter(created_at__month=current_month,created_at__year=current_year).count()
        wedding = Wedding.objects.filter(created_at__month=current_month,created_at__year=current_year).count()
        events = Events.objects.filter(created_at__month=current_month,created_at__year=current_year).count()
        reels = Reels.objects.filter(created_at__month=current_month,created_at__year=current_year).count()
        total_payment_list = []
        payment_received = []
        booking_data = None


        shoot_date = Booking_ShootDate.objects.filter(date__gte=today).order_by('date')[0:10]
        if shoot_date.exists():
            data = []
            for s in shoot_date:
                booking = Booking.objects.filter(shoot_date=s, booking_status__title='confirmed').first()
                if booking != None:
                    print(s.id, booking)
                    data.append({'date': s, 'data': booking})

            total_payment = 0
            pending_payment = 0
            pending_payment_list = []
            booking = Booking.objects.filter(shoot_date__date__month=current_month,shoot_date__date__year=current_year, booking_status__title='confirmed').distinct()

            for b in booking:
                print(b.user)
                total_payment += (b.package.price - b.discount)
                additional_price = b.shoot_date.all()
                for a in additional_price:
                    for c in a.additional_service.all():
                        total_payment += (c.count * c.additional_service.price)

                payment = Payments.objects.filter(user=b.user.id)
                for p in payment:
                    pending_payment += p.amount

                # total_payment_list.append({'name': b, 'amount': total_payment, 'pending_payment': total_payment-pending_payment})
                total_payment_list.append(total_payment)
                total_payment = 0
                pending_payment= 0

            payment_received = [ p.amount for p in payment_received_obj ]
            booking_data = booking

            context['data']=data
        else:
            context['data']='no data'

        context['payment']={'total_payment': total_payment_list, 'payment_received': payment_received, 'booking': booking_data, 'client': client, 'pre_wedding': pre_wedding, 'wedding': wedding, 'events': events, 'reels': reels}

        print(context['data'])

    elif validation['user_type'] == 'team':
            
        if True:

            team_instance = Team_member.objects.filter(id=validation['user'].id)
            total_payment = [ t.amount for t in team_instance.first().fund.filter(date__month=current_month) ]
            payment_received = [ t.amount for t in team_instance.first().payments.filter(date__month=current_month) ]
            print(payment_received,'payment_received', team_instance.first().payments.filter(date__month=current_month))
            
            context['data']='no data'
            context['payment'] = {'total_payment': total_payment, 'payment_received': payment_received}
        else:
            context['data'] = 'no data'



    # context = {'data' : 'no data'}

    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_dashboard.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res







def booking(request):
    validation = validation_admin_pages(request, 'all')
    if not isinstance(validation, dict):
        return validation

    try:
        page = int(request.GET.get('page'))
    except:
        page = 1
    
    limit = 10

    try:
        dateSelector = request.GET.get('date')
        if dateSelector==None:
            dateSelector=='today'

        current_month = datetime.now().month
        client_instance = Booking.objects.filter(shoot_date__date__month=current_month, booking_status__title='confirmed').distinct()
        # if validation['user_type'] == 'admin':
            # print('client', validation['user'], client.first().shoot_date.all().first().additional_service.all().first().team.all().first().team == validation['user'] )

        if validation['user_type'] == 'team':
            client_instance = client_instance.filter(shoot_date__additional_service__team__team=validation['user'])

        data = []
        if client_instance.exists():

            p = Paginator(client_instance, limit)
            pages = p.page(page)

            data = []
            for p in pages:
                for s in p.shoot_date.all():

                    if validation['user_type'] == 'admin':
                        data.append({ 'user_id': p.user.user.id, 'booking_id': p.user.id,'date': s.date.strftime("%d %b %Y"), 'client_name': p.user.user.name, 'event_type': p.package.segment.segment, 'requirement': [ f'{r.count} - {r.additional_service}' for r in s.additional_service.all()]  })
                    elif validation['user_type'] == 'team':
                        for ads in s.additional_service.all():
                            for tm in ads.team.all():
                                if tm.team == validation['user']:
                                    data.append({ 'user_id': p.user.user.id, 'booking_id': p.user.id,'date': s.date.strftime("%d %b %Y"), 'client_name': p.user.user.name, 'event_type': p.package.segment.segment, 'requirement': [ f'{r.count} - {r.additional_service}' for r in s.additional_service.all()]  })

            sorted_data = sorted(data, key=lambda x: datetime.strptime(x['date'], '%d %b %Y' ))

            context = {'user': validation['user'], 'user_type': validation['user_type'], 'data': sorted_data, 'current_page': page, 'date': current_month}
        else:
            context = {'user': validation['user'], 'user_type': validation['user_type'], 'data': 'no data', 'current_page': page}
    except:
        context = {'user': validation, 'pages': 'no data', 'current_page': page}
        
    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_booking.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res



def clients(request):
    validation = validation_admin_pages(request, 'admin')
    if not isinstance(validation, dict):
        return validation

    try:
        page = int(request.GET.get('page'))
    except:
        page = 1
    limit = 10
    try:
        client = Client.objects.all().order_by('-id')
        if client.exists():
            p = Paginator(client, limit)
            pages = p.page(page)
            context = {'user': validation['user'], 'pages': pages, 'current_page': page}
        else:
            context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}
    except:
        context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}

    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_clients.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res




def client_edit(request):
    validation = validation_admin_pages(request, 'admin')
    if not isinstance(validation, dict):
        return validation

    try:
        id = int(request.GET.get('id'))
        sec = request.GET.get('sec')
        if sec == None:
            sec='client'
    except:
        page = 1
        sec = 'client'

    try:
        booking_id = request.GET.get('booking_id')
    except:
        booking_id = None

    try:
        selected_bookings = Booking.objects.filter(id=booking_id)
        client = Client.objects.filter(id = id)
        
        if sec == 'client':
            if selected_bookings.exists():
                hidden_fields = ['user_id', 'booking_date', 'booking_status_id', 'package_id', 'discount', 'total_price']
                data = {}
                for k,v in selected_bookings.values().first().items():
                    if not k in hidden_fields:
                        data[k] = v
                

                booking_status = Drp_booking_status.objects.all()
                # booking = Booking.objects.filter(user=data['id'])

                context = {'user': validation['user'], 'data': data, 'client': client.first(), 'booking_status_list': booking_status, 'booking': selected_bookings}
            else:
                context = {'user': validation['user'], 'data': 'no data'}
        elif sec == 'booking':
            # selected_bookings = Booking.objects.filter(id=booking_id)
            segment = Segment.objects.all()

            # booked_service = []
            # for b in selected_bookings:
            #     booked_service_obj = {}
            #     booked_service_obj['shoot_date'] = str(b.shoot_date)
            #     booked_service_obj['service'] = [c.service_name for c in  b.service.all()]
            #     booked_service_obj['additional_service'] = [c.service_name for c in  b.additional_service.all()]
            #     booked_service.append(booked_service_obj)

            week_days_list = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

            if selected_bookings.exists():
                data = []
                for b in selected_bookings:
                    for d in b.shoot_date.all():
                        data.append(str(d.date))

                # booking = Booking.objects.filter(user=id)
                # additional_service = AdditionalService.objects.filter(segment=int(booking.first().package.segment.id))
                # context = {'booking_data': selected_bookings, "booked_service": booked_service, 'client_data': client.first()}

                context = {'user': validation['user'], 'booking_data': data, "booked_service": selected_bookings, 'segment': segment, 'client_data': client.first(), 'week_days_list': week_days_list }
                
                if selected_bookings.first().package != None:
                    context['pre_selected'] = {
                        'package': {'id':selected_bookings.first().package.id, 'name': selected_bookings.first().package.package, 'price': selected_bookings.first().package.price, }, 
                        'booking': selected_bookings.first()}
            else:
                context = {'user': validation['user'], 'booking_data': '-', 'client_data': client.first(), 'week_days_list': week_days_list }

        elif sec == 'segment':
            
            client_data = Client.objects.filter(id=id)
            # selected_booking = Booking.objects.filter(id=booking_id)

            segment = Segment.objects.all()

            segment_title = ['segment', 'package', 'price', 'service']

            if selected_bookings.exists():
                context = {'user': validation['user'],
                            'user': validation['user'], 'segment': segment, 
                           'pre_selected' : {'booking': selected_bookings.first()},
                           'client_data': client_data.first(),
                           'segment_title': segment_title
                    }
                if selected_bookings.first().package != None:
                    context['pre_selected'] = {
                           'segment':{'id': selected_bookings.first().package.segment.id, 'name': selected_bookings.first().package.segment.segment.replace('_',' ')},
                           'package': {'id':selected_bookings.first().package.id, 'name': selected_bookings.first().package.package, 'price': selected_bookings.first().package.price },
                           'deliverables': selected_bookings.first().package.deliverables.all(),
                           'booking': selected_bookings.first(),
                        }
            else:
                context = {'user': validation['user'],
                        'user': validation['user'],
                        'segment': segment,
                        'pre_selected': {
                        'booking': selected_bookings.first()
                        #    'segment':{'id': selected_segment.first().package.segment.id, 'name': selected_segment.first().package.segment.segment.replace('_',' ')},
                        #    'package': {'id':selected_segment.first().package.id, 'name': selected_segment.first().package.package, 'price': selected_segment.first().package.price },
                        #    'service': selected_segment.first().package.service.all()
                        },
                           'client_data': client.first(),
                           'segment_title': segment_title

                    }

        elif sec == 'payment':
            # selected_bookings = Booking.objects.filter(id=booking_id)
            payment = Payments.objects.filter(booking=booking_id).order_by('-id')
            
            title_list = [
                # {'package info': ['package']}, {'pricing info': ['package price', 'additionals', 'discount', 'total price']}, 
                          {'payment': ['amount', 'payment mode', 'notes', 'remaining payment']}, {'payment history': ['']}]

            if selected_bookings.first().package:
                context = {'user': validation['user'], 'data' : selected_bookings, 'client_data': client.first(), 'payment' :payment, 'title_list': title_list}
            else:
                context = {'user': validation['user'], 'data' : None, 'client_data': client.first() , 'title_list': title_list}


        elif sec == 'quotation':
            bookings = Booking.objects.filter(id=booking_id)
            production_process = ProductionProcess.objects.filter(trash=False)
            camera_equipments = CameraEquipments.objects.filter(trash=False)
            deliverables = Deliverables.objects.filter(trash=False)
            terms_conditions = Terms_Conditions.objects.filter(trash=False)

            title_list = [{'package info': ['package']}, {'pricing info': ['package price', 'additionals', 'discount', 'total price']}, {'additionals': ['']}, {'camera & equipment details': ['']}, {'production process': ['']}, {'deliverables': ['']}, {'terms & conditions': [''], 'actions': ['']}]

            if bookings.first().package:
                context = {'user': validation['user'], 'data' : bookings, 'client_data': client.first(), 'production_process': production_process, 'camera_equipments' : camera_equipments ,'deliverables': deliverables, 'terms_conditions': terms_conditions, 'title_list': title_list}
            else:
                context = {'user': validation['user'], 'data' : None, 'client_data': client.first(), 'title_list': title_list}


        elif sec == 'team':
            if selected_bookings.first().package:
                team_member = Team_member.objects.all()
                context = {'user': validation['user'], 'data' : selected_bookings, 'client_data': client.first(), 'team_member': team_member }
            else:
                context = {'user': validation['user'], 'data' : None, 'client_data': client.first()}

    except:
        context = {'data': 'no data'}

    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_client_edit.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res





def uploads(request):
    validation = validation_admin_pages(request, 'admin')
    if not isinstance(validation, dict):
        return validation

    try:
        # id = int(request.GET.get('id'))
        sec = request.GET.get('sec')
        if sec == None:
            sec='pre_wedding'
    except:
        page = 1
        sec = 'pre_wedding'
    try:
        # client = Client.objects.filter(id = id).values()
        # print('client',client)
        if sec == 'pre_wedding':
            try:
                page = int(request.GET.get('page'))
            except:
                page = 1
            limit = 10
            
            try:
                reels = Pre_Wedding.objects.all().values()
                if reels.exists():
                    p = Paginator(reels, limit)
                    pages = p.page(page)
                    context = {'user': validation['user'], 'pages': pages, 'current_page': page}
                else:
                    context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}
            except:
                context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}

        if sec == 'homepage':
            # try:
            #     page = int(request.GET.get('page'))
            # except:
            #     page = 1
            #     limit = 10
            # try:
                # reels = Pre_Wedding.objects.all().values()
                # if reels.exists():
                    # p = Paginator(reels, limit)
                    # pages = p.page(page)
                    # context = {'pages': pages, 'current_page': page}
                # else:
                    context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}
            # except:
            #     context = {'pages': 'no data', 'current_page': page}


        elif sec == 'wedding':
            try:
                page = int(request.GET.get('page'))
            except:
                page = 1
            limit = 10
            try:
                reels = Wedding.objects.all().values()
                if reels.exists():
                    p = Paginator(reels, limit)
                    pages = p.page(page)
                    context = {'user': validation['user'], 'pages': pages, 'current_page': page}
                else:
                    context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}
            except:
                context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}

        elif sec == 'events':
            try:
                page = int(request.GET.get('page'))
            except:
                page = 1
            limit = 10
            try:
                reels = Events.objects.all().values()
                if reels.exists():
                    p = Paginator(reels, limit)
                    pages = p.page(page)
                    context = {'user': validation['user'], 'pages': pages, 'current_page': page}
                else:
                    context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}
            except:
                context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}

        elif sec == 'reels':
            try:
                page = int(request.GET.get('page'))
            except:
                page = 1
            limit = 10
            try:
                reels = Reels.objects.all().values()
                if reels.exists():
                    p = Paginator(reels, limit)
                    pages = p.page(page)
                    context = {'user': validation['user'], 'pages': pages, 'current_page': page}
                else:
                    context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}
            except:
                context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}
            # context = {'data' : 'no data', 'client_data': client.first()}

    except:
        context = {'data': 'no data'}

    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_uploads.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res      




# def pre_wedding(request):
#     try:
#         validation = validate_loggedin(request)
#         if validation['status'] == False:
#             return redirect('/console/login')
#     except:
#             return redirect('/console/login')
    
#     try:
#         page = int(request.GET.get('page'))
#     except:
#         page = 1
#     limit = 10
#     try:
#         reels = Pre_Wedding.objects.all().values()
#         if reels.exists():
#             p = Paginator(reels, limit)
#             pages = p.page(page)
#             context = {'pages': pages, 'current_page': page}
#         else:
#             context = {'pages': 'no data', 'current_page': page}
#     except:
#         context = {'pages': 'no data', 'current_page': page}

#     if validation['status']=='access_expired':
#         tokens = regenerateToken(validation['user'],context)
#     res = HttpResponse(render(request, 'console_pre-wedding.html', context))
#     if validation['status']=='access_expired':
#         regenerateCookies(res, tokens)
#     return res



# def wedding(request):
#     try:
#         validation = validate_loggedin(request)
#         if validation['status'] == False:
#             return redirect('/console/login')
#     except:
#             return redirect('/console/login')
    
#     try:
#         page = int(request.GET.get('page'))
#     except:
#         page = 1
#     limit = 10
#     try:
#         reels = Wedding.objects.all().values()
#         if reels.exists():
#             p = Paginator(reels, limit)
#             pages = p.page(page)
#             context = {'pages': pages, 'current_page': page}
#         else:
#             context = {'pages': 'no data', 'current_page': page}
#     except:
#         context = {'pages': 'no data', 'current_page': page}




#     if validation['status']=='access_expired':
#         tokens = regenerateToken(validation['user'],context)
#     res = HttpResponse(render(request, 'console_wedding.html', context))
#     if validation['status']=='access_expired':
#         regenerateCookies(res, tokens)
#     return res


# def events(request):
#     try:
#         validation = validate_loggedin(request)
#         if validation['status'] == False:
#             return redirect('/console/login')
#     except:
#             return redirect('/console/login')

#     try:
#         page = int(request.GET.get('page'))
#     except:
#         page = 1
#     limit = 10
#     try:
#         reels = Events.objects.all().values()
#         if reels.exists():
#             p = Paginator(reels, limit)
#             pages = p.page(page)
#             context = {'pages': pages, 'current_page': page}
#         else:
#             context = {'pages': 'no data', 'current_page': page}
#     except:
#         context = {'pages': 'no data', 'current_page': page}

#     if validation['status']=='access_expired':
#         tokens = regenerateToken(validation['user'],context)
#     res = HttpResponse(render(request, 'console_events.html', context))
#     if validation['status']=='access_expired':
#         regenerateCookies(res, tokens)
#     return res



# def reels(request):
#     try:
#         validation = validate_loggedin(request)
#         if validation['status'] == False:
#             return redirect('/console/login')
#     except:
#             return redirect('/console/login')
    
#     try:
#         page = int(request.GET.get('page'))
#     except:
#         page = 1
#     limit = 10
#     try:
#         reels = Reels.objects.all().values()
#         if reels.exists():
#             p = Paginator(reels, limit)
#             pages = p.page(page)
#             context = {'pages': pages, 'current_page': page}
#         else:
#             context = {'pages': 'no data', 'current_page': page}
#     except:
#         context = {'pages': 'no data', 'current_page': page}
    
#     if validation['status']=='access_expired':
#         tokens = regenerateToken(validation['user'],context)
#     res = HttpResponse(render(request, 'console_reels.html', context))
#     if validation['status']=='access_expired':
#         regenerateCookies(res, tokens)
#     return res


def payments(request):

    validation = validation_admin_pages(request, 'all')
    if not isinstance(validation, dict):
        return validation

    try:    
        page = int(request.GET.get('page'))
    except:
        page = 1

    limit = 10
    offset = int((page - 1)*limit)

    # print(limit, offset, 'offset')
    dateSelector = request.GET.get('date')

    if dateSelector==None or dateSelector=='this_month':
        dateSelector=='this_month'
        date = datetime.now().month
        client = Payments.objects.filter(date__month=date).distinct().order_by('-id')
    elif dateSelector=='this_year':
        date = datetime.now().year
        client = Payments.objects.filter(date__year=date).distinct().order_by('-id')
        print('client', client)
    elif dateSelector=='today':
        date = datetime.today().date()
        client = Payments.objects.filter(date=date).order_by('-id')
        print('this working', date, client)
    elif dateSelector=='custom':
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        date = {'date_from': date_from,'date_to': date_to } 
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        end_date += timedelta(days=1)
        client = Payments.objects.filter(date__range=(start_date,end_date)).order_by('-id')

    context = { 'user': validation['user'], 'user_type': validation['user_type'], 'current_page': page, 'date': date, 'dateSelector':  dateSelector.replace('_',' ') if dateSelector != None else 'this month' }

    # try:
    if validation['user_type'] == 'team':
        
        payment_instance = Team_member.objects.filter(id=validation['user'].id).first()

        if dateSelector=='today':
            client = payment_instance.payments.filter(date=date)
        elif dateSelector=='this_month' or dateSelector==None:
            client = payment_instance.payments.filter(date__month=date)
        elif dateSelector=='this_year':
            client = payment_instance.payments.filter(date__year=date)
        elif dateSelector=='custom':
            client = payment_instance.payments.filter(date__range=(start_date,end_date))

    data = []
    if client.exists():
        p = Paginator(client, limit)
        pages = p.page(page)
        context['pages'] = pages
    else:
        context['pages'] = 'no data'
    # except:
    #     context = { 'user': validation['user'], 'pages': 'no data', 'current_page': page}

    # try:
    #     invoice = Invoice.objects.all()
    #     if invoice.exists():
    #         p = Paginator(invoice, limit)
    #         pages = p.page(page)
    #         context = {'pages': pages, 'current_page': page}
    #     else:
    #         context = {'pages': 'no data', 'current_page': page}
    # except:
    #     context = {'pages': 'no data', 'current_page': page}

    # context = {'data': 'no data',}
    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_payment.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res




def reviews(request):
    validation = validation_admin_pages(request, 'admin')
    print('validation', validation)
    if not isinstance(validation, dict):
        return validation

    try:    
        page = int(request.GET.get('page'))
    except:
        page = 1
    limit = 10
    try:    
        dateSelector = request.GET.get('date')
        if not dateSelector:
            dateSelector = 'this_month'
    except:
        dateSelector = 'this_month'

    context = {'user': validation['user'], 'user_type': validation['user_type'], 'current_page': page, 'dateSelector':  dateSelector.replace('_',' ')}

    if dateSelector==None or dateSelector=='this_month' :
        dateSelector=='this_month'
        date = datetime.now().month
        reviews = Reviews.objects.filter(date__month=date).distinct().order_by('-id')
    elif dateSelector=='this_year':
        date = datetime.now().year
        reviews = Reviews.objects.filter(date__year=date).distinct().order_by('-id')
    elif dateSelector=='today':
        print('wrokignaosidfjlasidjf')
        date = datetime.today().date()
        reviews = Reviews.objects.filter(date=date).order_by('-id')
    elif dateSelector=='custom':
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        date = {'date_from': date_from,'date_to': date_to } 
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
        end_date += timedelta(days=1)
        reviews = Reviews.objects.filter(date__range=(start_date,end_date)).order_by('-id')

    if reviews.exists():
        p = Paginator(reviews, limit)
        pages = p.page(page)
        context['pages'] = pages
    else:
        context['pages'] = 'no data'

    
    # context['reviews'] = reviews
    context['date'] = date

    print('reviews',reviews)
 
    # context = {'data': 'no data',}
    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_reviews.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res



# def quotation(request):
#     try:
#         validation = validate_loggedin(request)
#         if validation['status'] == False:
#             return redirect('/console/login')
#     except:
#             return redirect('/console/login')
    
#     context = {'data': 'no data',}
#     if validation['status']=='access_expired':
#         tokens = regenerateToken(validation['user'],context)
#     res = HttpResponse(render(request, 'console_quotation.html', context))
#     if validation['status']=='access_expired':
#         regenerateCookies(res, tokens)
#     return res


def invoice_template(request):
    validation = validation_admin_pages(request, 'admin')
    if not isinstance(validation, dict):
        return validation
    
    context = {'data': 'no data',}

    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console-layout/invoice.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res


def generate_password(request, id, user_token):
    try:
        validation = validate_loggedin(request)
        if validation['status'] == False or not validation['user_type'] == 'admin' and validation['status'] == False:
            print("validation['status']", validation['status'])
            return redirect('/console/login')
    except:
        return redirect('/console/login')
        
    first_login = first_login_check(validation)
    if not first_login: return redirect('/console/dashboard')


    context = {'user': validation['user'], 'user_id': id, 'user_token': user_token}
    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_generate_password.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)

    return res         






def administration(request):
    validation = validation_admin_pages(request, 'admin')
    if not isinstance(validation, dict):
        return validation
    
    try:
        # id = int(request.GET.get('id'))
        sec = request.GET.get('sec')
        if sec == None:
            sec='homepage'
    except:
        page = 1
        sec = 'homepage'
    try:
        # client = Client.objects.filter(id = id).values()
        # print('client',client)

        if sec == 'homepage':
            try:
                page = int(request.GET.get('page'))
            except:
                page = 1
                limit = 10
            try:
                banner = Banner_video.objects.all().values()
                media = homepage_media.objects.all()
                masterpiece = []
                handpicked = []
                banners = []
                latest_creations = []
                image_gallery = []
                for m in media:
                    print(m)
                    if m.type == 'masterpiece':
                        if m.table == 'pre_wedding':
                            masterpiece.append({ 'id': int(m.file_id),'table': m.table,'data': Pre_Wedding.objects.filter(id=int(m.file_id)).first()})
                        if m.table == 'wedding':
                            masterpiece.append({ 'id': int(m.file_id),'table': m.table,'data': Wedding.objects.filter(id=int(m.file_id)).first()})
                        if m.table == 'events':
                            masterpiece.append({ 'id': int(m.file_id),'table': m.table,'data': Events.objects.filter(id=int(m.file_id)).first()})

                    if m.type == 'latest_creations':
                        if m.table == 'pre_wedding':
                            latest_creations.append({ 'id': int(m.file_id),'table': m.table,'data': Pre_Wedding.objects.filter(id=int(m.file_id)).first()})
                        if m.table == 'wedding':
                            latest_creations.append({ 'id': int(m.file_id),'table': m.table,'data': Wedding.objects.filter(id=int(m.file_id)).first()})
                        if m.table == 'events':
                            latest_creations.append({ 'id': int(m.file_id),'table': m.table,'data': Events.objects.filter(id=int(m.file_id)).first()})

                    if m.type == 'handpicked':
                        if m.table == 'pre_wedding':
                            handpicked.append({ 'id': int(m.file_id),'table': m.table,'data': Pre_Wedding.objects.filter(id=int(m.file_id)).first()})
                        if m.table == 'wedding':
                            handpicked.append({ 'id': int(m.file_id),'table': m.table,'data': Wedding.objects.filter(id=int(m.file_id)).first()})
                        if m.table == 'events':
                            handpicked.append({ 'id': int(m.file_id),'table': m.table,'data': Events.objects.filter(id=int(m.file_id)).first()})

                    if m.type == 'image_gallery':
                        image_gallery.append({ 'id': int(m.file_id),'table': m.table,'data': ImageGallery.objects.filter(id=int(m.file_id)).first()})

                    # if m.type == 'banners':
                    #     banners.append({ 'id': int(m.file_id),'table': m.table,'data': Banner_image.objects.filter(id=int(m.file_id)).first()})


                print('handpicked',banners)

                showcase_image = Showcase_images.objects.all().values()
                if banner.exists():
                    # p = Paginator(banner, limit)
                    # pages = p.page(page)
                    context = {'user': validation['user'], 'banner': banner, 'media': media, 'showcase_image': showcase_image, 'current_page': page, 'media': media, 'masterpiece': masterpiece, 'handpicked': handpicked, 'latest_creations': latest_creations, 'image_gallery': image_gallery, 'banners': banners }
                else:
                    context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}
            except:
                context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}


        elif sec == 'packages':
            try:
                page = int(request.GET.get('page'))
            except:
                page = 1
            limit = 10
            try:
                package = Package.objects.all()
                service = Service.objects.all()
                additional_service = AdditionalService.objects.all()
                cameraequipments = CameraEquipments.objects.all()
                production_process = ProductionProcess.objects.all()
                deliverables = Deliverables.objects.all()
                terms_conditions = Terms_Conditions.objects.all()
                # shoot_category = ShootCategory.objects.all()
                print(package)
                if package.exists():
                    # p = Paginator(reels, limit)
                    # pages = p.page(page)
                    context = {'user': validation['user'], 'packages': package, 'service': service, 'additional_service': additional_service, 'cameraequipments': cameraequipments, 'production_process': production_process, 'deliverables': deliverables, 'terms_conditions': terms_conditions}
                else:
                    context = {'user': validation['user'], 'pages': 'no data'}
            except:
                context = {'user': validation['user'], 'pages': 'no data', 'current_page': page}


            # context = {'data' : 'no data', 'client_data': client.first()}

    except:
        context = {'data': 'no data'}

    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_administration.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)

    return res      



def team(request):
    validation = validation_admin_pages(request, 'admin')
    if not isinstance(validation, dict):
        return validation

    try:
        # id = int(request.GET.get('id'))
        sec = request.GET.get('sec')
        if sec == None:
            sec='members'
    except:
        page = 1
        sec = 'members'
    try:
        # client = Client.objects.filter(id = id).values()
        # print('client',client)

        try:
            page = int(request.GET.get('page'))
        except:
            page = 1
        limit = 10
        
        if sec == 'members':

            try:
                reels = Team_member.objects.filter(trash=False)
                if reels.exists():
                    p = Paginator(reels, limit)
                    pages = p.page(page)
                    context = {'user': validation['user'], 'data': pages, 'current_page': page}
                else:
                    context = {'user': validation['user'], 'data': 'no data', 'current_page': page}
            except:
                context = {'user': validation['user'], 'data': 'no data', 'current_page': page}


        elif sec == 'payments':

            try:
                team = Team_member.objects.all()
                team_mates_ind=None

                if request.GET.get('team_mate'):
                    team_mate = int(request.GET.get('team_mate'))
                    # print(team)
                    team_mates_ind = Team_member.objects.filter(id=team_mate)
                    # print('else woking')

                    # if tab == 'fund_history':
                    #     tab_instance = fund_history.objects.filter()
                    # elif tab == 'payment_history':
                    #     tab_instance = payments_history.objects.all()

                    # tab_paginator = Paginator(tab_instance, limit)
                    # tab_data = tab_paginator.page(page)

                if not request.GET.get('tab'):
                    tab = 'fund_history'
                else:
                    tab = request.GET.get('tab')

                if team.exists():
                    # print(team)
                    p = Paginator(team, limit)
                    pages = p.page(page)

                    # context = {'user': validation['user'], 'data': pages, 'current_page': page}
                    context = {'user': validation['user'], 'data': pages, "data_indv":  team_mates_ind if team_mates_ind != None else "no data",'current_page': page}

                    if team_mates_ind != None:
                        context['payment'] = {'fund_history': [t for t in team_mates_ind.first().fund.all().order_by('-id') ], 'payment_history': [t for t in team_mates_ind.first().payments.all().order_by('-id') ]} 

                else:
                    context = {'user': validation['user'], 'data': 'no data', "data_indv": 'no data', 'tab_data': 'no data' , 'current_page': page}
            except:
                context = {'user': validation['user'], 'data': 'no data', "data_indv": 'no data', 'tab_data': 'no data', 'current_page': page}

            # try:

                # try:
            # if not request.GET.get('tab'):
            #     tab = 'fund_history'
            # else:
            #     tab = request.GET.get('tab')

            # team = Team_member.objects.all().values()

            # if team.exists():
                # p = Paginator(team, limit)
                # pages = p.page(page)

                # if tab == 'fund_history':
                #     tab_instance = fund_history.objects.all()
                # elif tab == 'payment_history':
                #     tab_instance = payments_history.objects.all()

                # tab_paginator = Paginator(tab_instance, limit)
                # tab_data = tab_paginator.page(page)
                # print('tab_data',tab_data)

            #     context = {'data': team, "data_indv":  team_mates_ind if team_mates_ind.exists() else "no data" ,'current_page': page}
            # else:
            #     context = {'data': 'no data', "data_indv": "no data", 'tab_data': 'no data', 'current_page': page}

            # except:
            #     context = {'data': 'no data', "data_indv": "no data", 'tab_data': 'no data', 'current_page': page}
            

    except:
        context = {'data': 'no data'}


    print('context', context)

    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_team.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res      






def team_profile(request, id, token):
    validation = validation_admin_pages(request, 'admin')
    if not isinstance(validation, dict):
        return validation

    team_member = Team_member.objects.filter(id=id, user_token=token)
    print('team_member', team_member.first().skills.all())
    context = {'user': validation['user'], 'data': team_member.first()}

    additional_service = AdditionalService.objects.filter(trash=False).exclude(service_name='pre wedding').values()
    context['additional_service'] = additional_service

    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'console_team_profile.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res




def logout(request):
    validation =  validate_loggedin(request)
    if validation['status'] == True or validation['status'] == 'access_expired':
        if validation['user_type'] == 'admin':
            resp = HttpResponseRedirect('/console/login')
        elif validation['user_type'] == 'team':
            resp = HttpResponseRedirect('/console/team/login')

        resp.delete_cookie('access')
        resp.delete_cookie('refresh')
        resp.delete_cookie('csrftoken')

        return resp
    else:
        return redirect('/console/login')
    

    



def user_forgot_password(request):
    # validation = validate_loggedin(request)
    if request.POST:
        email = request.POST.get('email')
        try:
            user = UserAccount.objects.get(user__email=email)
        except:
            user = None
            messages.error(request, 'This email is not registered!')
        if user != None:
            SendEmail([email], 'Reset Password!', f'<p>Click to the link to <a href="http://localhost:8000/console/reset_password/{user.pk}/{user.user_token}">reset password</a>!</p><br><p></p>')
            messages.success(request, 'An email has been sent to your registered email, check email to proceed further !')
        # user = authenticate(email=email, password=password)
    return render(request, 'user_forgot_password.html')





def user_reset_password(request, id, client_token):
    try:
        user = UserAccount.objects.get(id=id, user_token=client_token)
    except:
        user = None
    if request.POST:
        if request.POST.get('password') == request.POST.get('repeat_password'):
            user.first_login = False
            user.client_token = generate_random_code()
            user.save()
            user.user.password = make_password(request.POST.get('password'))
            user.user.save()
            messages.success(request, 'Password reset successful!')
            return redirect('/console/login')
    else:
        if user != None:
            pass
        else:
            messages.error(request,'user not found')
    return render(request, 'user_reset_password.html')





    
def team_forgot_password(request):
    # validation = validate_loggedin(request)
    if request.POST:
        email = request.POST.get('email')
        try:
            user = Team_member.objects.get(user__email=email)
        except:
            user = None
            messages.error(request, 'This email is not registered!')
        if user != None:
            SendEmail([email], 'Reset Password!', f'<p>Click to the link to <a href="http://localhost:8000/console/team/reset_password/{user.pk}/{user.user_token}">reset password</a>!</p><br><p></p>')
            messages.success(request, 'An email has been sent to your registered email, check email to proceed further !')
        # user = authenticate(email=email, password=password)
    return render(request, 'console_forgot_password.html')




def team_reset_password(request, id, client_token):
    try:
        user = Team_member.objects.get(id=id, user_token=client_token)
    except:
        user = None
    if request.POST:
        if request.POST.get('password') == request.POST.get('repeat_password'):
            user.first_login = False
            user.client_token = generate_random_code()
            user.save()
            user.user.password = make_password(request.POST.get('password'))
            user.user.save()
            messages.success(request, 'Password reset successful!')
            return redirect('/console/team/login')
    else:
        if user != None:
            pass
        else:
            messages.error(request,'user not found')
    return render(request, 'user_reset_password.html')
    
