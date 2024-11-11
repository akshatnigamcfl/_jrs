from django.shortcuts import render, redirect
from console.models import *
import random
from django.contrib.auth import authenticate
from django.contrib import messages
# from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from console.views import validate_loggedin
from datetime import datetime

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.urls import reverse
from console.views import get_tokens_for_user, regenerateToken, regenerateCookies
from api.views import generate_random_code
from api.main_functions import SendEmail






def validate_client(request):
    if request.COOKIES:
        try:
            if AccessToken(request.COOKIES.get('access')):
                token = AccessToken(request.COOKIES.get('access'))
                payload = token.payload
                if 'user_id' in payload:
                    print("payload['user_id']", payload['user_id'])
                    user = Client.objects.filter(user = payload['user_id'])
                    print('user', user)
                    user_type = 'client'
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
                    return {'user': None, 'status': False, 'user_type': None}
                else:
                    user = Client.objects.filter(user = refreshToken['user_id']).first()
                    user_type = 'client'
                    return {'user':user, 'status': 'access_expired', 'user_type': user_type}
            except:
                return {'user': None, 'status': False, 'user_type': None}
    else:
        return {'user': None, 'status': False, 'user_type': None }



def validate_loggedin(request):
    validation = validate_client(request)
    if validation['status'] == False:
        return redirect('/login')
    elif validation['status'] == 'access_expired':
        return validation
    elif validation['status'] == True:
        return validation

# def regenerateToken(user, context):
#     tokens = get_tokens_for_user(user)
#     context['token'] = tokens['access']
#     return tokens

# def regenerateCookies(res,tokens):
#     print('tokens', tokens, settings)
#     res.set_cookie(key = 'access', value = tokens['access'], expires= settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'], secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'], httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'], samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])
    # res.set_cookie(key = 'refresh', value = tokens['refresh'], expires= settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'], secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'], httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'], samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'])

def first_login_check(validation):
    print('valida', validation['status'], validation['user_type'] )
    if validation['user_type'] and validation['user_type'] == 'client':
        if validation['user'] == None:
            return redirect('/login')
        if validation['user'].first_login == True:
            return redirect(f'/reset_password/{validation['user'].id}/{validation['user'].client_token}')
    else:
        return None
    



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




def validation_admin_pages(request, user_type):
    try:
        validation = validate_loggedin(request)
        print('validation *** ', validation)

        first_login = first_login_check(validation) 
        print('first_login', first_login)
        if first_login !=None: return first_login

        if validation['user'] !=None and validation['status'] == 'access_expired' or validation['status'] == True :
            print('expired access', validation)
            print('this working')
            return validation
        else:
            print('else working *****')
            if validation['status'] == False:
                return redirect('/login')

        print('this working ***')

    except:
        return redirect('/login')
    






# def validate_user(request):
#     if request.COOKIES:

#         try:
#             if AccessToken(request.COOKIES.get('access')):
#                 token = AccessToken(request.COOKIES.get('access'))
#                 payload = token.payload
#                 if 'user_id' in payload:
#                     print("payload['user_id']", payload['user_id'])
#                     user = Client.objects.filter(id = payload['user_id'])
#                     print("payload['user_id']", user)
#                     user_type = 'client'
#                     return {'user': user.first(), 'status': user.exists(), 'user_type': user_type}
#                 else :
#                     return {'user': None, 'status': False, 'user_type': None}

#             # token_obj = Token.objects.get(key=request.COOKIES.get('access'))
#             # current_time = timezone.now()
#             # return token_obj.created < current_time - timezone.timedelta(days=1)  # Adjust the timedelta as needed
#         except:
#             try:
#                 refreshToken = RefreshToken(str(request.COOKIES.get('refresh')))
#                 current_time = datetime.utcnow()

#                 token_created_at = refreshToken.payload['iat']
#                 token_life = refreshToken.lifetime.total_seconds()
#                 if token_created_at + token_life < current_time.timestamp():
#                     return {'user': None, 'status': False}
                
#                 else:
#                     user = UserAccount.objects.filter(id = refreshToken['user_id']).first()
#                     return {'user':user, 'status': 'access_expired', 'user_type': None}
#             except:
#                 return {'user': None, 'status': False, 'user_type': None}
#     else:
#         return {'user': None, 'status': False, 'user_type': None }



# def validate_loggedin(request):
#     validation = validate_user(request)
#     print(validation,validation)    
#     if validation['status'] == False:
#         return redirect('/console/login')
#     elif validation['status'] == 'access_expired':
#         # user = validation['user']
#         # generate_access = True
#         return validation
#     elif validation['status'] == True:
#         return validation


# Create your views here.


def homeFunction():
    banner_video = Banner_video.objects.all().values()
    homepageMedia = homepage_media.objects.all()

    handpicked = []
    image_gallery = [[],[]]
    masterpiece = [[],[],[]]
    latest_creations = [[],[],[]]
    index = 0
    index2 = 0
    index3 = 0
    for m in homepageMedia:
        print('masterpiece',masterpiece)
        if index < 3 and len(masterpiece[index]) >= 3:
            index += 1
        if m.type == 'masterpiece':
            if m.table == 'pre_wedding':
                masterpiece[index].append({ 'id': int(m.file_id),'table': m.table,'data': Pre_Wedding.objects.filter(id=int(m.file_id)).first()})
            if m.table == 'wedding':
                masterpiece[index].append({ 'id': int(m.file_id),'table': m.table,'data': Wedding.objects.filter(id=int(m.file_id)).first()})
            if m.table == 'events':
                masterpiece[index].append({ 'id': int(m.file_id),'table': m.table,'data': Events.objects.filter(id=int(m.file_id)).first()})

        if index2 < 3 and len(latest_creations[index2]) >= 3:
            index2 += 1
        if m.type == 'latest_creations':
            print('index2',index2)
            if m.table == 'pre_wedding':
                latest_creations[index2].append({ 'id': int(m.file_id),'table': m.table,'data': Pre_Wedding.objects.filter(id=int(m.file_id)).first()})
            if m.table == 'wedding':
                latest_creations[index2].append({ 'id': int(m.file_id),'table': m.table,'data': Wedding.objects.filter(id=int(m.file_id)).first()})
            if m.table == 'events':
                latest_creations[index2].append({ 'id': int(m.file_id),'table': m.table,'data': Events.objects.filter(id=int(m.file_id)).first()})

        if m.type == 'handpicked':
            if m.table == 'pre_wedding':
                handpicked.append({ 'id': int(m.file_id),'table': m.table,'data': Pre_Wedding.objects.filter(id=int(m.file_id)).first()})
            if m.table == 'wedding':
                handpicked.append({ 'id': int(m.file_id),'table': m.table,'data': Wedding.objects.filter(id=int(m.file_id)).first()})
            if m.table == 'events':
                handpicked.append({ 'id': int(m.file_id),'table': m.table,'data': Events.objects.filter(id=int(m.file_id)).first()})

        if index3 < 10 and len(latest_creations[index3]) >= 10:
            index3 += 1
        if m.type == 'image_gallery':
            if m.table == 'ImageGallery':
                image_gallery[index3].append({ 'id': int(m.file_id),'table': m.table,'data': ImageGallery.objects.filter(id=int(m.file_id)).first()})
    if banner_video.exists():
        randint = random.randint(0, len(banner_video) - 1)
        context = {'data': banner_video[randint], 'masterpiece': masterpiece, 'handpicked': handpicked, 'latest_creations': latest_creations, 'image_gallery': image_gallery }
    
        context['reviews'] = Reviews.objects.filter(visibility=True)
        print("context['reviews']", context['reviews'])

        return context



    return None


def home(request):
    context = homeFunction()
    if context != None:
        return render(request, 'home_adarsh.html', context )
    return render(request, 'home_adarsh.html')


def home_client(request, client_id, client_token):

    context = homeFunction()
    if context != None:

        context = {}
        client = Client.objects.filter(id = client_id, client_token = client_token )
        main_data = client

        if client.exists():
            # data = {}
            # print('client.first().booking', client.first().booking.all())
                # data[k.replace('_', ' ')] = v  
            context['client']= client
        else:
            context['data']= 'no data'

        return render(request, 'home_adarsh.html', context )
    return render(request, 'home_adarsh.html')


            # context['data']= 'no data'


def home2(request):
    banner_video = Banner_video.objects.all().values()
    if banner_video.exists():
        int = random.randint(0, len(banner_video) - 1)
        return render(request, 'home_2.html', {'data': banner_video[int]})
    return render(request, 'home_2.html')
    

def wedding(request):
    context = Wedding.objects.all().values()
    return render(request, 'wedding.html', {'data':context})

def cinematic(request):
    context = Wedding.objects.all().values()
    return render(request, 'cinematic.html', {'data':context})

def pre_wedding(request):
    context = Pre_Wedding.objects.all().values()
    return render(request, 'pre-wedding.html', {'data':context})

def pre_wedding_view(request, id):
    context = Pre_Wedding.objects.filter(id=id).values()
    recommended = Pre_Wedding.objects.all().values()
    return render(request, 'pre-wedding-view.html', {'data': context, 'recommended': recommended, 'most_recent': recommended})

def events(request):
    context = Events.objects.all().values()
    return render(request, 'events.html', {'data':context})


def reels(request):

    reels = Reels.objects.all().values()
    return render(request, 'reels.html', {'reels' : reels})



def team(request):
    return render(request, 'team.html')


def gallery(request):

    index3 = 0
    image_gallery = [[],[]]
    # latest_creations = [[],[],[]]

    
    if index3 < 10 and len(image_gallery[index3]) >= 10:
        index3 += 1
        # if m.type == 'image_gallery':
            # if m.table == 'ImageGallery':
        image_gallery[index3].append({ 'id': int(m.file_id),'table': m.table,'data': ImageGallery.objects.filter(id=int(m.file_id)).first()})


    return render(request, 'gallery.html')


# def booking(request):
#     print('this working')
#     return render(request, 'booking.html')

def about(request):
    context = {}
    team_member = Team_member.objects.all()
    context['team'] = team_member
    print('team_member', team_member)
    return render(request, 'about.html', context)



def contact(request):
    return render(request, 'contact.html')





def clientPaymentFunction(request):
    context = {}
    client = Client.objects.filter(user=request.user)
    total_payment = 0
    package_price = 0
    paid = 0
    remaining = 0

    for c in client.first().booking.all():
        # print('request.user.id', request.user.id)
        payment = Payments.objects.filter(user=client.first(), booking=c)

        for p in payment:
            paid += p.amount

        if c.package:
            package_price = c.package.price
            additional_price = 0
            for sd in c.shoot_date.all():
                for ads in sd.additional_service.all():
                    additional_price += additional_price + (ads.count * ads.additional_service.price)

        context['total_payment'] = (package_price-c.discount) + additional_price
        context['paid'] = paid
        context['remaining'] = ((package_price-c.discount) + additional_price) - paid
        context['payment'] = payment
        context['client'] = client.first()
    
    return context





@login_required(login_url='/login')
def client_dashboard(request):

    validation = validation_admin_pages(request, 'all')
    if not isinstance(validation, dict):
        return validation

    context =  clientPaymentFunction(request)

    # context = {}
    # client = Client.objects.filter(user=request.user)
    # total_payment = 0
    # package_price = 0
    # paid = 0
    # remaining = 0

    # for c in client.first().booking.all():
    #     # print('request.user.id', request.user.id)
    #     payment = Payments.objects.filter(booking=c)

    #     for p in payment:
    #         paid += p.amount

    #     if c.package:
    #         package_price = c.package.price
    #         additional_price = 0
    #         for sd in c.shoot_date.all():
    #             for ads in sd.additional_service.all():
    #                 additional_price += additional_price + (ads.count * ads.additional_service.price)

    #     context['total_payment'] = (package_price-c.discount) + additional_price
    #     context['paid'] = paid
    #     context['remaining'] = ((package_price-c.discount) + additional_price) - paid


    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'client_dashboard.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)

    return res


def client_payment(request):

    validation = validation_admin_pages(request, 'all')
    if not isinstance(validation, dict):
        return validation

    context = clientPaymentFunction(request)

    client = Client.objects.filter(user=request.user)
    if client.exists():
        payment = Payments.objects.filter(user=client.first())
    context['payment'] = payment



    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'client_payments.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res



@login_required(login_url='/login')
def client_info(request, client_id, booking_id, client_token):

    validation = validation_admin_pages(request, 'all')
    if not isinstance(validation, dict):
        return validation

    try:
        title_list = [{'package info': ['package', 'price']  }]
        context = {'title_list': title_list}
        client = Client.objects.filter(id = client_id, client_token = client_token)
        selected_bookings = Booking.objects.filter(id=booking_id)
        
        if selected_bookings.exists():
            hidden_fields = ['user_id', 'booking_date', 'booking_status_id', 'package_id', 'discount', 'total_price']
            data = {}
            for k,v in selected_bookings.values().first().items():
                if not k in hidden_fields:
                    data[k] = v
        # if client:
        #     booking = Booking.objects.filter(id=booking_id)
        
        main_data = client
        if client.exists():
            # booking = Booking.objects.filter()
            payment = Payments.objects.filter(user=client.first(), booking=selected_bookings.first())
            
            context['payment'] = payment
            context['data'] = data
            context['booking'] = selected_bookings
            context['client'] = main_data
        else:
            context['data'] = 'no data'
    except:
            context['data'] = 'no data'


    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'client_info.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res




@login_required(login_url='/login')
def client_reviews(request, client_id, booking_id, client_token):

    validation = validation_admin_pages(request, 'all')
    if not isinstance(validation, dict):
        return validation

    try:
        title_list = [{'package info': ['package', 'price']  }]
        context = {'title_list': title_list}

        client = Client.objects.filter(id = client_id, client_token = client_token)    
        selected_bookings = Booking.objects.filter(id=booking_id)
        
        # if selected_bookings.exists():
        #     hidden_fields = ['user_id', 'booking_date', 'booking_status_id', 'package_id', 'discount', 'total_price']
        #     data = {}
        #     for k,v in selected_bookings.values().first().items():
        #         if not k in hidden_fields:
        #             data[k] = v
        # if client:
        #     booking = Booking.objects.filter(id=booking_id)
        
        # main_data = client
        # if client.exists():
            # booking = Booking.objects.filter()
            # payment = Payments.objects.filter(user=client.first(), booking=selected_bookings.first())
            
            # context['payment'] = payment
            # context['data'] = data
        context['booking'] = selected_bookings.first()
        context['client'] = client.first()
    except:
            context['data'] = 'no data'


    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'client_reviews.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res



@login_required(login_url='/login')
def client_bookings(request):

    validation = validation_admin_pages(request, 'all')
    if not isinstance(validation, dict):
        return validation

    # try:
    context = {}
    #     client = Client.objects.filter(id = client_id, client_token = client_token )
    #     main_data = client
    #     print('client', client)
    #     if client.exists():
    #         # data = {}
    #         # print('client.first().booking', client.first().booking.all())
    #             # data[k.replace('_', ' ')] = v


    #         context['client']= client
    #     else:
    #         context['data']= 'no data'
    # except:
    #         context['data']= 'no data'


    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'client_booking.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res







def client_info_confirm_booking(request, booking_id, client_token):

    # validation = validate_loggedin(request)

    try:
        booking = Booking.objects.filter(id = booking_id, user__client_token = client_token )
        if booking.exists():
            # data = {}
            # for c in client:
            #     for k,v in c.items():
            #         data[k.replace('_', ' ')] = v
            context = {'data': booking.first()}
        else:
            context = {'data': 'no data'}
    except:
            context = {'data': 'no data'}


    return render(request, 'confirm_booking.html', context)


def scroller_test(request):
    return render(request, 'scroller_test.html')



def user_login(request):
 
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(email, password)

        # user = Client.objects.get(user__email=email)
        # if user.check_password(request.POST.get('password')):

        user = authenticate(username=email, password=password)
        
        if user != None:
            client = Client.objects.filter(user=user)
            if client.exists():
                login(request,user)
                token = get_tokens_for_user(user)
                # response =  HttpResponseRedirect(reverse(client_info))
                # return response
                response =  HttpResponseRedirect('/dashboard')
                response.set_cookie('access', token['access'], max_age=360000)
                response.set_cookie('refresh', token['refresh'], max_age=360000)
                return response
                # return redirect()
        else:
            messages.error(request, 'Invalid Username or Password')

    # return render(request, 'user_login.html')
    encCount = EncoderDecoder.objects.count()
    intV = random.randint(0, encCount - 1)
    res = render(request, 'user_login.html')
    res.set_cookie('ed', EncoderDecoder.objects.filter(id=intV).first().code, max_age=3600)
    return res



@login_required(login_url='/login')
def settings(request):


    validation = validation_admin_pages(request, 'all')
    if not isinstance(validation, dict):
        return validation

    # try:
    context = {}
    #     main_data = client
    #     print('client', client)
    #     if client.exists():
    #         # data = {}
    #         # print('client.first().booking', client.first().booking.all())
    #             # data[k.replace('_', ' ')] = v
            
            
    #         context['client']= client
    #     else:
    #         context['data']= 'no data'
    # except:
    #         context['data']= 'no data'

    tokens = tokenResponseCheck(validation, context)
    res = HttpResponse(render(request, 'settings.html', context))
    if tokens != None: cookiesResponseCheck(validation, res, tokens)
    return res


@login_required(login_url='/login')
def user_logout(request):
    logout(request)
    res = redirect('/')
    res.delete_cookie('access')
    res.delete_cookie('refresh')
    res.delete_cookie('csrftoken')
    return res


def user_signup(request):
    return render(request, 'user_signup.html')







def user_forgot_password(request):

    # validation = validate_loggedin(request)

    if request.POST:
        email = request.POST.get('email')
        try:
            user = Client.objects.get(user__email=email)
        except:
            user = None
            messages.error(request, 'This email is not registered!')
        

        if user != None:

            SendEmail([email], 'Reset Password!', f'<p>Click to the link to <a href="http://localhost:8000/reset_password/{user.pk}/{user.client_token}">reset password</a>!</p><br><p></p>')
            
            messages.success(request, 'An email has been sent to your registered email, check email to proceed further !')

        # user = authenticate(email=email, password=password)

    return render(request, 'user_forgot_password.html')




def user_reset_password(request, id, client_token):

    try:
        user = Client.objects.get(id=id, client_token=client_token)
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
            return redirect('/login')
            
    else:

        if user != None:
            pass
        
        else:
            messages.error(request,'user not found')

    return render(request, 'user_reset_password.html')
    