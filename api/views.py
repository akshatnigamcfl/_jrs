from django.shortcuts import render
from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from django.db.models import F


import secrets
import string
import math
import random


from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .serializer import *
from console.forms import *
# from console.models import *

from datetime import datetime, timedelta

from io import BytesIO
from xhtml2pdf import pisa


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import locale

# from weasyprint import HTML

# import pdfkit
from django.template.loader import render_to_string

from django.http import FileResponse
from collections import Counter

import os



def dec(enc, val):
    def flatten(val):
        strV = ''
        i = 0
        while i < len(val):
            if val[i] == '.':
                strV += val[i:i+3] + ','
                i+=3
            else:
                strV += val[i:i+1] + ','
                i+=1

        # print('strV')
        strV = ','.join([s for s in strV.split(",") if s!='' ])
        return strV
    
    
    enc = flatten(enc).split(',')
    value = [ enc.index(v) for v in flatten(val).split(',')]
    return value


def sendEmail(email,message, subject):
    subject = subject
    from_email = 'akshatnigamcfl1@gmail.com'
    recipient_list = email
    text = 'email sent from Evitamin'
    email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
    email.attach_alternative(message, 'text/html')
    # email.attach(f'{booking.first().user.user.name}', buffer.read(), 'application/pdf')
    email.send()


def resFun(status,message,data):
    res = Response()
    res.status_code = status
    res.data = {
        'status': status,
        'message': message,
        'data': data,
    }
    return res

# Create your views here.


class IgnoreBearerTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']

            if auth_header.startswith('Bearer'):
                return None
        return super().authenticate(request)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generate_random_code(length=25):
    alphabet = string.ascii_letters + string.digits
    random_code = ''.join(secrets.choice(alphabet) for _ in range(length))
    return random_code
    


def login_func_validate(request, login_type):

    # for i in request.headers['ed']:
    try:
        encd = request.headers['ed']
    except:
        return resFun(status.HTTP_400_BAD_REQUEST, 'encoder not found', [])

    em = dec(encd, request.data['email'])
    pw = dec(encd, request.data['password'])
    data = {'email' : str(''.join([chr(e+32) for e in em])), 'password': ''.join([chr(e+32) for e in pw]) }
    
    # for (var i=0; i<val.length; ){
    #     if (val[i] === '.') {
    #         str += val.substring(i, i+3) + ','
    #         i+=3

    #     } else {
    #         str += val.substring(i, i+1 ) + ','
    #         i++
    #     }
    # } 
    # return str;

    # em = [ enc.index(p)  for p in request.data['email']]
    # pw = [ enc.index(p)  for p in request.data['password']]

    # print(em)
    # print(pw)
    
    # strV = ''
    # for i in range(len(request.headers['ed'])):
    # # for e in request.headers['ed']:
    #     strV += str(i)
    # print('str', strV)

    serializer = loginSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        res = Response()
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        print(email, password)
        try:
            user = CustomModel.objects.get(email=email) 
            if login_type == 'admin': 
                user_instance = UserAccount.objects.get(user=user)
            else:
                user_instance = Team_member.objects.get(user=user)
        except:
            return Response({'status': status.HTTP_404_NOT_FOUND,'message':'no user account with this email id','data':[]}, status=status.HTTP_404_NOT_FOUND)

        user = authenticate(username=email, password=password)
        print(user)
        if user != None:
            token = get_tokens_for_user(user)
            # token = Token.objects.get_or_create(user=user)
            print('user logged in')
            res.status_code = status.HTTP_200_OK
            res.data = {
                'data': {'token': token},
                'message': 'login successful',
                'status': status.HTTP_200_OK
            }
            res.set_cookie(
                key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=token['access'],
                expires= settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            res.set_cookie(
                key = settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=token['refresh'],
                expires= settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            # res.data = {'token':token, 'message': 'user registered'}
            # res.status_code = status.HTTP_201_CREATED
            # redirect_response = HttpResponseRedirect('/dashboard')
            # redirect_response.set_cookie('')
            # return redirect_response
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'login failed', [])
        return res

    else:
        res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])



class GetEnc(GenericAPIView):
    serializer_class = GetEncSerializer
    authentication_classes = [IgnoreBearerTokenAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        
        encCount = EncoderDecoder.objects.count()
        int = random.randint(0, encCount - 1)
        enc = EncoderDecoder.objects.filter(id=int).first().code

        serializer = GetEncSerializer(data={'enc': enc}, many=False)
        if serializer.is_valid():
            return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
    



# @method_decorator(csrf_exempt, name='csrftoken')
class api_login(GenericAPIView):
    authentication_classes = [IgnoreBearerTokenAuthentication]
    serializer_class = loginSerializer
    def post(self, request, format=None, *args, **kwargs):


        res = login_func_validate(request, 'admin')
        # serializer = loginSerializer(data=request.data)
        # if serializer.is_valid(raise_exception=True):
        #     res = Response()
        #     email = serializer.data.get('email')
        #     password = serializer.data.get('password')
        # try:
        #     user = CustomModel.objects.get(email=email)
        #     user_instance = UserAccount.objects.get(user=user)
        # except:
        #     return Response({'status': status.HTTP_404_NOT_FOUND,'message':'no user account with this email id','data':[]}, status=status.HTTP_404_NOT_FOUND)
            
        # user = authenticate(username=email, password=password)
        # if user != None:
        #     token = get_tokens_for_user(user)
        #     # token = Token.objects.get_or_create(user=user)
        #     res.status_code = status.HTTP_200_OK
        #     res.data = {
        #         'data': {'token': token},
        #         'message': 'login successful',
        #         'status': status.HTTP_200_OK
        #     }
        #     res.set_cookie(
        #         key = settings.SIMPLE_JWT['AUTH_COOKIE'],
        #         value=token['access'],
        #         expires= settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        #         secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        #         httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        #         samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        #     )
        #     res.set_cookie(
        #         key = settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        #         value=token['refresh'],
        #         expires= settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        #         secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        #         httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        #         samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        #     )
        #     # res.data = {'token':token, 'message': 'user registered'}
        #     # res.status_code = status.HTTP_201_CREATED
        #     # redirect_response = HttpResponseRedirect('/dashboard')
        #     # redirect_response.set_cookie('')
        #     # return redirect_response
        # else:
        #     res = resFun(status.HTTP_400_BAD_REQUEST, 'login failed', [])

        return res
    

class team_login(GenericAPIView):
    authentication_classes = [IgnoreBearerTokenAuthentication]
    serializer_class = loginSerializer
    def post(self, request, format=None, *args, **kwargs):

        res = login_func_validate(request, 'team')

        # serializer = loginSerializer(data=request.data)
        # if serializer.is_valid(raise_exception=True):
        #     res = Response()
        #     email = serializer.data.get('email')
        #     password = serializer.data.get('password')
        #     try:
        #         user = CustomModel.objects.get(email=email)
        #         user_instance = UserAccount.objects.get(user=user)
        #     except:
        #         return Response({'status': status.HTTP_404_NOT_FOUND,'message':'no user account with this email id','data':[]}, status=status.HTTP_404_NOT_FOUND)
            
        #     user = authenticate(username=email, password=password)
        #     if user != None:
        #         token = get_tokens_for_user(user)
        #         # token = Token.objects.get_or_create(user=user)
        #         res.status_code = status.HTTP_200_OK
        #         res.data = {
        #             'data': {'token': token},
        #             'message': 'login successful',
        #             'status': status.HTTP_200_OK
        #         }

        #         res.set_cookie(
        #             key = settings.SIMPLE_JWT['AUTH_COOKIE'],
        #             value=token['access'],
        #             expires= settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        #             secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        #             httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        #             samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        #         )
        #         res.set_cookie(
        #             key = settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        #             value=token['refresh'],
        #             expires= settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        #             secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        #             httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        #             samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        #         )
        #         # res.data = {'token':token, 'message': 'user registered'}
        #         # res.status_code = status.HTTP_201_CREATED
        #         # redirect_response = HttpResponseRedirect('/dashboard')
        #         # redirect_response.set_cookie('')
        #         # return redirect_response
        #     else:
        #         res = resFun(status.HTTP_400_BAD_REQUEST, 'login failed', [])
        # else:
        #     res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
        return res
    



class generate_password(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = loginSerializer
    def post(self, request, type, id, token, format=None, *args, **kwargs):
        # try:
        if type == 'admin':
            user = UserAccount.objects.get(user=id)
        elif type =='team':
            user = Team_member.objects.get(user=id)
        
        if user:
            user.user.set_password(request.data.get('password'))
            user.user_token = generate_random_code()
            user.first_login = False
            user.user.save()
            user.save()
            res = resFun(status.HTTP_200_OK, 'request successful', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'no user found', [])
        return res
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])


    

# class api_client_login(GenericAPIView):
#     authentication_classes = [IgnoreBearerTokenAuthentication]
#     serializer_class = loginSerializer
#     def post(self, request, format=None, *args, **kwargs):
#         serializer = ClientloginSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             res = Response()
#             email = serializer.data.get('email')
#             password = serializer.data.get('password')
#             try:
#                 UserAccount.objects.get(email=email)
#             except:
#                 # return Response({'status': status.HTTP_404_NOT_FOUND,'message':,'data':[]}, status=status.HTTP_404_NOT_FOUND)
#                 return resFun(status.HTTP_400_BAD_REQUEST,'no user account with this email id', [])
#             user = authenticate(email=email, password=password)
#             if user != None:

#                 token = get_tokens_for_user(user)
#                 res = resFun(status.HTTP_200_OK, 'login successful', {'token': token})
#                 res.set_cookie(
#                     key = settings.SIMPLE_JWT['AUTH_COOKIE'],
#                     value=token['access'],
#                     expires= settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
#                     secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
#                     httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
#                     samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
#                 )
#                 res.set_cookie(
#                     key = settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
#                     value=token['refresh'],
#                     expires= settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
#                     secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
#                     httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
#                     samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
#                 )                
#             else:
#                 res = resFun(status.HTTP_400_BAD_REQUEST, 'login failed', [])

#         else:
#             res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
#         return res




class upload_reels(CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = reelsUploadSerializer
    def post(self, request, format=None, *args, **kwargs):
            print(request.FILES.get('file  '))
        # try:
            file = request.FILES
            res = Response()
            if file:
                if request.FILES.get('file').content_type == 'video/mp4':
                    upload = Reels_Upload_Form(request.POST, request.FILES)
                    if upload.is_valid():
                        upload.save()
                        
                        res.status_code = status.HTTP_200_OK
                        res.data = {
                            'status': status.HTTP_200_OK,
                            'message': 'reel upload successfully',
                            'data': []
                        }                        
                    else:
                        res.status_code = status.HTTP_400_BAD_REQUEST
                        res.data = {
                            'status': status.HTTP_400_BAD_REQUEST,
                            'message': 'request failed',
                            'data': []
                        }
                else:
                    res.status_code = status.HTTP_400_BAD_REQUEST
                    res.data = {
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'file format not supported',
                        'data': []
                    }
                return res
            


class delete_reels(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Reels_Upload_Form
    def delete(self, request, id, format=None, *args, **kwargs):
        res = Response()
        if request.user.is_admin:
            del_INST = Reels.objects.filter(id = id)
            if del_INST.exists():
                file_location = del_INST.first()
                print('file_location.file',file_location.file)
                if os.path.exists('media/'+str(file_location.file)):
                        os.remove('media/'+str(file_location.file))
                        del_INST.delete()
                        res.status_code = status.HTTP_200_OK
                        res.data = {
                            'status': status.HTTP_200_OK,
                            'data': [],
                            'message': 'deleted successfully'
                            }   
                else:
                    res.status_code = status.HTTP_404_NOT_FOUND
                    res.data = {
                        'status': status.HTTP_404_NOT_FOUND,
                        'data': [],
                        'message': 'file not found'
                        }
            else:
                res.status_code = status.HTTP_400_BAD_REQUEST
                res.data = {
                    'status': status.HTTP_400_BAD_REQUEST,
                    'data': [],
                    'message': 'request failed'
                    }
        else:
            res.status_code = status.HTTP_401_UNAUTHORIZED
            res.data = {
                'status': status.HTTP_401_UNAUTHORIZED,
                'data': [],
                'message': 'you are not authorized to delete this data'
            }
        return res
                

                
            # if upload:
        # except:
        #     print('not uploaded')
        


class upload_pre_wedding(CreateAPIView):
    # authentication_classes = [IgnoreBearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = Pre_Wedding_Upload_Form_VIDEOFILE
    def post(self, request, format=None, *args, **kwargs):

        # try:

        print(request.POST)


        file = request.FILES
        # res = Response()

        if file:
            if request.FILES.get('video_link'):
                if  'video' in request.FILES.get('video_link').content_type:
                    pass
                elif 'mp4' in str(request.FILES.get('video_link') ) :
                    pass
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'video format not supported', [] )

                
            if 'image' in request.FILES.get('cover_picture').content_type or 'jpg' in str(request.FILES.get('cover_picture')):
                if request.POST.get('is_youtube_video') == 'true':
                    upload = Pre_Wedding_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES)
                else:
                    upload = Pre_Wedding_Upload_Form_VIDEOFILE(request.POST, request.FILES)
                if upload.is_valid():
                    upload.save()
                    
                    return resFun(status.HTTP_200_OK, 'pre wedding upload successfully', [] )
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [] )
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported', [] )
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'no files', [] )

            

class get_pre_wedding_all(GenericAPIView):
    serializer_class = PreWeddingSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, page, format=None, *args, **kwargs):

            
        try:
            limit = 10
            offset = (page-1)*limit

            pre_wedding = Pre_Wedding.objects.all().order_by('-id')[offset: offset+limit]

            if pre_wedding.exists():


                data = []
                for items in pre_wedding.values():
                    obj={}
                    for k,v in items.items():
                        if v =='' or v == None:
                            obj[k] = '-'
                        else:
                            obj[k] = v
                    data.append(obj)

                serializer = PreWeddingSerializer(data=data, many=True)
                if serializer.is_valid():
                    page_count = math.ceil(Pre_Wedding.objects.count()/10)
                    responseSerializer = mediaDataReponseSerializer(data={'data': serializer.data, 'page_count': page_count, 'current_page': page, 'table': 'pre_wedding' }, many=False)
                    if responseSerializer.is_valid():
                        return resFun(status.HTTP_200_OK, 'request successful', responseSerializer.data)
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', responseSerializer.errors)
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
            else:
                return resFun(status.HTTP_204_NO_CONTENT, 'no data', [])
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
            

            # return res

            

class get_pre_wedding_indv(GenericAPIView):
    serializer_class = PreWeddingSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None, *args, **kwargs):
        pre_wedding = Pre_Wedding.objects.filter(id = id)
        res = Response()
        if pre_wedding.exists():

            data = {}
            for k,v in pre_wedding.values().first().items():
                if v =='' or v == None:
                    data[k] = '-'
                else:
                    data[k] = v
            
            serializer = PreWeddingSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'request successful',
                'data': serializer.data,
            }

        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'no pre wedding found with this id',
                'data': [],
            }

        return res
    

class edit_pre_wedding_indv(GenericAPIView):
    serializer_class = Pre_Wedding_Upload_Form_VIDEOFILE
    permission_classes = [IsAuthenticated]
    def put(self, request, id, format=None, *args, **kwargs):

        print('this func working', id)
        print(request.FILES)
        print(request.POST)


        file = request.FILES
        pre_wedding = Pre_Wedding.objects.get(id = id)
        if file:
            if request.FILES.get('video_link'):
                if  'video' in request.FILES.get('video_link').content_type:
                    pass
                elif 'mp4' in str(request.FILES.get('video_link') ) :
                    pass
                else:
                    print('image issue')
                    return resFun(status.HTTP_400_BAD_REQUEST, 'video format not supported', [] )
                
            
            if request.FILES.get('cover_picture'):
                print( not 'jpg' in str(request.FILES.get('cover_picture')) )
                print( not 'image' in request.FILES.get('cover_picture').content_type )

                
                if not ( 'image' in request.FILES.get('cover_picture').content_type or 'jpg' in str(request.FILES.get('cover_picture')) ):
                    print('image issue')
                    return resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported', [])

            if request.POST.get('is_youtube_video') == 'true':
                upload = Pre_Wedding_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES, instance=pre_wedding)
            else:
                upload = Pre_Wedding_Upload_Form_VIDEOFILE(request.POST, request.FILES, instance=pre_wedding)

        elif not file:
            if request.POST.get('is_youtube_video') == 'true':
                print('if working')
                upload = Pre_Wedding_Upload_Form_YOUTUBE_LINK(request.POST, instance=pre_wedding)
                print('upload',upload)
            else:
                upload = Pre_Wedding_Upload_Form_VIDEOFILE(request.POST, instance=pre_wedding)

        if upload.is_valid():
            upload.save()
            
            return resFun(status.HTTP_200_OK, 'pre wedding edited successfully', [] )
        else:
            print('else working', upload.errors)
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [] )   



            

class delete_pre_wedding(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Pre_Wedding_Upload_Form_VIDEOFILE
    def delete(self, request, id, format=None, *args, **kwargs):
        res = Response()
        if request.user.is_admin:
            del_INST = Pre_Wedding.objects.filter(id = id)

            print('del_INSTdel_INST',)
            if del_INST.exists():
                file_location = del_INST.first()


                print('file_location.cover_picture',file_location.cover_picture)
                print('file_location.video_link',file_location.video_link)
                if os.path.exists('media/'+str(file_location.cover_picture)):
                    os.remove('media/'+str(file_location.cover_picture))
                    if del_INST.first().is_youtube_video == False:
                        if os.path.exists('media/'+str(file_location.video_link)):
                            os.remove('media/'+str(file_location.video_link))
                        

                    del_INST.delete()
                    res.status_code = status.HTTP_200_OK
                    res.data = {
                        'status': status.HTTP_200_OK,
                        'data': [],
                        'message': 'deleted successfully'
                        }   
                else:
                    res.status_code = status.HTTP_404_NOT_FOUND
                    res.data = {
                        'status': status.HTTP_404_NOT_FOUND,
                        'data': [],
                        'message': 'file not found'
                        }
            else:
                res.status_code = status.HTTP_400_BAD_REQUEST
                res.data = {
                    'status': status.HTTP_400_BAD_REQUEST,
                    'data': [],
                    'message': 'request failed'
                    }
        else:
            res.status_code = status.HTTP_401_UNAUTHORIZED
            res.data = {
                'status': status.HTTP_401_UNAUTHORIZED,
                'data': [],
                'message': 'you are not authorized to delete this data'
            }
        return res

            

class upload_wedding(CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = Wedding_Upload_Form_VIDEOFILE
    def post(self, request, format=None, *args, **kwargs):
        # try:
            file = request.FILES

            if file:
                if request.FILES.get('video_link'):
                    if  'video' in request.FILES.get('video_link').content_type:
                        pass
                    elif 'mp4' in str(request.FILES.get('video_link') ) :
                        pass
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'video format not supported', [] )
                    

                if 'image' in request.FILES.get('cover_picture').content_type or 'jpg' in str(request.FILES.get('cover_picture')):
                    if request.POST.get('is_youtube_video') == 'true':
                        upload = Wedding_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES)
                    else:
                        upload = Wedding_Upload_Form_VIDEOFILE(request.POST, request.FILES)
                    if upload.is_valid():
                        upload.save()

                        return resFun(status.HTTP_200_OK, 'wedding upload successfully', [] )
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [] )
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported', [] )
            



class get_wedding_all(GenericAPIView):
    serializer_class = WeddingSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, page, format=None, *args, **kwargs):
            
        try:
            limit = 10
            offset = (page-1)*limit

            wedding = Wedding.objects.all().order_by('-id')[offset: offset+limit]

            # res = Response()
            if wedding.exists():

                data = []
                for items in wedding.values():
                    obj={}
                    for k,v in items.items():
                        if v =='' or v == None:
                            obj[k] = '-'
                        else:
                            obj[k] = v
                    data.append(obj)

                serializer = WeddingSerializer(data=data, many=True)
                if serializer.is_valid():
                    page_count = math.ceil(Wedding.objects.count()/10)
                    responseSerializer = mediaDataReponseSerializer(data={'data': serializer.data, 'page_count': page_count, 'current_page': page, 'table': 'wedding' }, many=False)
                    if responseSerializer.is_valid():
                        return resFun(status.HTTP_200_OK, 'request successful', responseSerializer.data)
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', responseSerializer.errors)
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)

            else:
                return resFun(status.HTTP_204_NO_CONTENT, 'no data', [])

        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])




            

class get_wedding_indv(GenericAPIView):
    serializer_class = WeddingSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None, *args, **kwargs):
        wedding = Wedding.objects.filter(id = id)
        res = Response()
        if wedding.exists():

            data = {}
            for k,v in wedding.values().first().items():
                if v =='' or v == None:
                    data[k] = '-'
                else:
                    data[k] = v
            
            serializer = WeddingSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'request successful',
                'data': serializer.data,
            }
        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'no wedding found with this id',
                'data': [],
            }

        return res
    

class edit_wedding_indv(GenericAPIView):
    serializer_class = Wedding_Upload_Form_VIDEOFILE
    permission_classes = [IsAuthenticated]
    def put(self, request, id, format=None, *args, **kwargs):

        file = request.FILES
        res = Response()
        wedding = Wedding.objects.get(id = id)
        if file:
            if request.FILES.get('video_link'):
                if not 'video' in request.FILES.get('video_link').content_type:
                    res.status_code = status.HTTP_400_BAD_REQUEST
                    res.data = {
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'video format not supported',
                        'data': []
                    }
                    return res
            
            if request.FILES.get('cover_picture'):
                if not 'image' in request.FILES.get('cover_picture').content_type:
                    res.status_code = status.HTTP_400_BAD_REQUEST
                    res.data = {
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'file format not supported',
                        'data': []
                    }
                    return res
            
            if request.POST.get('is_youtube_video') == 'true':
                upload = Wedding_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES, instance=wedding)
            else:
                upload = Wedding_Upload_Form_VIDEOFILE(request.POST, request.FILES, instance=wedding)

            # else:


        elif not file:
            if request.POST.get('is_youtube_video') == 'true':
                print('if working')
                upload = Wedding_Upload_Form_YOUTUBE_LINK(request.POST, instance=wedding)
                print('upload',upload)
            else:
                upload = Wedding_Upload_Form_VIDEOFILE(request.POST, instance=wedding)
                print(upload)


        if upload.is_valid():
            upload.save()
            
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'pre wedding upload successfully',
                'data': []
            }                        
        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'request failed',
                'data': []
            }

        return res

            

class delete_wedding(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Wedding_Upload_Form_VIDEOFILE
    def delete(self, request, id, format=None, *args, **kwargs):
        print("request", request)
        res = Response()
        if request.user.is_admin:
            del_INST = Wedding.objects.filter(id = id)
            if del_INST.exists():
                file_location = del_INST.first()

                print('file_location.cover_picture',file_location.cover_picture)
                if os.path.exists('media/'+str(file_location.cover_picture)):
                    os.remove('media/'+str(file_location.cover_picture))
                    if del_INST.first().is_youtube_video == False:
                        if os.path.exists('media/'+str(file_location.video_link)):
                            os.remove('media/'+str(file_location.video_link))


                # print('file_location.file',file_location.file)
                # if os.path.exists('media/'+str(file_location.file)):
                #         os.remove('media/'+str(file_location.file))
                    del_INST.delete()
                    res.status_code = status.HTTP_200_OK
                    res.data = {
                        'status': status.HTTP_200_OK,
                        'data': [],
                        'message': 'deleted successfully'
                        }   
                else:
                    res.status_code = status.HTTP_404_NOT_FOUND
                    res.data = {
                        'status': status.HTTP_404_NOT_FOUND,
                        'data': [],
                        'message': 'file not found'
                        }
            else:
                res.status_code = status.HTTP_400_BAD_REQUEST
                res.data = {
                    'status': status.HTTP_400_BAD_REQUEST,
                    'data': [],
                    'message': 'request failed'
                    }
        else:
            res.status_code = status.HTTP_401_UNAUTHORIZED
            res.data = {
                'status': status.HTTP_401_UNAUTHORIZED,
                'data': [],
                'message': 'you are not authorized to delete this data'
            }
        return res




            

class upload_events(CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = Events_Upload_Form_VIDEOFILE
    def post(self, request, format=None, *args, **kwargs):
        try:
            file = request.FILES
                
            if file:
                if request.FILES.get('video_link'):
                    if  'video' in request.FILES.get('video_link').content_type:
                        pass
                    elif 'mp4' in str(request.FILES.get('video_link') ) :
                        pass
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'video format not supported', [] )
                    
                if 'image' in request.FILES.get('cover_picture').content_type or 'jpg' in str(request.FILES.get('cover_picture')):
                    if request.POST.get('is_youtube_video') == 'true':
                        upload = Events_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES)
                    else:
                        upload = Events_Upload_Form_VIDEOFILE(request.POST, request.FILES)

                    if upload.is_valid():
                        upload.save()

                        return resFun(status.HTTP_200_OK, 'event upload successfully', [])
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported', [])
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported', [])
            


class get_events_all(GenericAPIView):
    serializer_class = EventsSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, page, format=None, *args, **kwargs):
        try:
            limit = 10
            offset = (page-1)*limit

            events = Events.objects.all().order_by('-id')[offset: offset+limit]
            print(events)

            res = Response()
            if events.exists():

                data = []
                for items in events.values():
                    obj={}
                    for k,v in items.items():
                        if v =='' or v == None:
                            obj[k] = '-'
                        else:
                            obj[k] = v
                    data.append(obj)

                serializer = EventsSerializer(data=data, many=True)
                if serializer.is_valid():
                    page_count = math.ceil(Events.objects.count()/10)
                    responseSerializer = mediaDataReponseSerializer(data={'data': serializer.data, 'page_count': page_count, 'current_page': page, 'table': 'events' }, many=False)
                    if responseSerializer.is_valid():
                        return resFun(status.HTTP_200_OK, 'request successful', responseSerializer.data)
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', responseSerializer.errors)
                else:
                    return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
            else:
                return resFun(status.HTTP_204_NO_CONTENT, 'no data', [])
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])





class get_events_indv(GenericAPIView):
    serializer_class = EventsSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None, *args, **kwargs):
        events = Events.objects.filter(id = id)
        res = Response()
        if events.exists():

            data = {}
            for k,v in events.values().first().items():
                if v =='' or v == None:
                    data[k] = '-'
                else:
                    data[k] = v
            
            serializer = EventsSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'request successful',
                'data': serializer.data,
            }
        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'no events found with this id',
                'data': [],
            }

        return res
    


class edit_events_indv(GenericAPIView):
    serializer_class = Events_Upload_Form_VIDEOFILE
    permission_classes = [IsAuthenticated]
    def put(self, request, id, format=None, *args, **kwargs):

        file = request.FILES
        res = Response()
        events = Events.objects.get(id = id)
        if file:

            if  'video' in request.FILES.get('video_link').content_type:
                pass
            elif 'mp4' in str(request.FILES.get('video_link') ) :
                pass
            else:
                print('image issue')
                return resFun(status.HTTP_400_BAD_REQUEST, 'video format not supported', [] )
                
            
            if request.FILES.get('cover_picture'):
                print( not 'jpg' in str(request.FILES.get('cover_picture')) )
                print( not 'image' in request.FILES.get('cover_picture').content_type )
                
                if not ( 'image' in request.FILES.get('cover_picture').content_type or 'jpg' in str(request.FILES.get('cover_picture')) ):
                    print('image issue')
                    return resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported', [])

                
            if request.POST.get('is_youtube_video') == 'true':
                upload = Events_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES, instance=events)
            else:
                upload = Events_Upload_Form_VIDEOFILE(request.POST, request.FILES, instance=events)



        elif not file:
            if request.POST.get('is_youtube_video') == 'true':
                print('if working')
                upload = Events_Upload_Form_YOUTUBE_LINK(request.POST, instance=events)
                print('upload',upload)
            else:
                upload = Events_Upload_Form_VIDEOFILE(request.POST, instance=events)
                print(upload)


        if upload.is_valid():
            upload.save()
            
            return resFun(status.HTTP_200_OK, 'pre events upload successfully', [] )               
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [] )
        # return res
            



class delete_events(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Events_Upload_Form_VIDEOFILE
    def delete(self, request, id, format=None, *args, **kwargs):
        print("request", request)
        res = Response()
        if request.user.is_admin:
            del_INST = Events.objects.filter(id = id)
            if del_INST.exists():
                file_location = del_INST.first()

                print('file_location.cover_picture',file_location.cover_picture)
                print('file_location.cover_picture',file_location.video_link)
                if os.path.exists('media/'+str(file_location.cover_picture)):
                    os.remove('media/'+str(file_location.cover_picture))
                    if del_INST.first().is_youtube_video == False:
                        if os.path.exists('media/'+str(file_location.video_link)):
                            os.remove('media/'+str(file_location.video_link))

                    # print('file_location.file',file_location.file)
                    # if os.path.exists('media/'+str(file_location.file)):
                    #    os.remove('media/'+str(file_location.file))
                    del_INST.delete()
                    res.status_code = status.HTTP_200_OK
                    res.data = {
                        'status': status.HTTP_200_OK,
                        'data': [],
                        'message': 'deleted successfully'
                        }   
                else:
                    res.status_code = status.HTTP_404_NOT_FOUND
                    res.data = {
                        'status': status.HTTP_404_NOT_FOUND,
                        'data': [],
                        'message': 'file not found'
                        }
            else:
                res.status_code = status.HTTP_400_BAD_REQUEST
                res.data = {
                    'status': status.HTTP_400_BAD_REQUEST,
                    'data': [],
                    'message': 'request failed'
                    }
        else:
            res.status_code = status.HTTP_401_UNAUTHORIZED
            res.data = {
                'status': status.HTTP_401_UNAUTHORIZED,
                'data': [],
                'message': 'you are not authorized to delete this data'
            }
        return res



class add_banners_all(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = banners_image_upload
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        try:

            file = request.FILES['file']
            if file:
                if 'image' in request.FILES.get('file').content_type:
                    upload = banners_image_upload(request.POST, request.FILES)
                    if upload.is_valid():
                        upload.save()
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'no file to upload' ,[])

            return res
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed' ,[])


class get_banners_all(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = get_banners_allSerializer
    def get(self, request, page):
        # try:
            limit = 10
            offset = (page-1)*10
            data = Banner_image.objects.all()[offset: offset+limit]
            print("data",data)
            serializer = get_banners_allSerializer(data=list(data.values()),many=True)
            if serializer.is_valid():
                res = resFun(status.HTTP_200_OK, 'request successful', serializer.data)
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
            return res
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])

# class vp(GenericAPIView):
#     authentication_classes = [IgnoreBearerTokenAuthentication]
#     # permission_classes =  [IsAuthenticated]
#     def post(self, request, format=None):
#         print('headers', request.headers)
#         print('request', request.data)



class AddClient(CreateAPIView):
    serializer_class = AddClientForm
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None, *args, **kwargs):

        # try:
            
            # print('asdfasdf',Client.objects.filter(user__email=request.POST.get('email_id')))
        
            if not CustomModel.objects.filter(email=request.POST.get('email_id')).exists():
                if not CustomModel.objects.filter(contact_number=request.POST.get('contact_number')).exists():


                    data_1 = {}
                    data_1['name'] = request.POST['name']
                    data_1['contact_number'] = request.POST['contact_number']
                    data_1['email'] = request.POST['email_id']

                    upload_1 = AddCustomModel(data_1)
                    print(upload_1)
                    if upload_1.is_valid():
                        upload_1_instance = upload_1.save()
                        password = generate_random_code()
                        # custom_model_instance = CustomModel.objects.get(id=upload_1_instance.id)
                        upload_1_instance.password = make_password(password)
                        upload_1_instance.save()    
                    else:
                        return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', []) 

                    data_2 = {}
                    data_2['user'] = upload_1_instance.id
                    data_2['source'] = ClientSource.objects.get(title = 'console')
                    data_2['client_token'] = generate_random_code()
                    upload_2 = AddClientForm(data_2)
                    if upload_2.is_valid():
                        upload_2_inst = upload_2.save()
                        # instance = upload.save()

                        # booking_instance = Booking.objects.create(user=upload_2_inst, booking_status= Drp_booking_status.objects.filter(title='in progress').first())
                        # upload_2_inst.booking.add(booking_instance)
                        
                        email_id = upload_1_instance.email

                        message = canned_email.objects.get(email_type = 'welcome_email')
                        message = message.email
                        message = str(message).replace("{{{email}}}", email_id)
                        message = str(message).replace("{{{password}}}", password)
                        message = str(message).replace("{{{link}}}", f'<a href="http://127.0.0.1:8000/client-info/{upload_2_inst.id}/{upload_2_inst.client_token}">fill more details</a>')


                        subject = 'Welcome to Jrs Studios!'
                        from_email = 'akshatnigamcfl@gmail.com'
                        recipient_list = [email_id]
                        text = 'email sent from MyDjango'

                        # if send_mail(subject, message, from_email, recipient_list):

                        email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
                        email.attach_alternative(message, 'text/html')
                        # email.attach_file('files/uploadFile_0dTGU7A.csv', 'text/csv')
                        email.send()

                        res = resFun(status.HTTP_200_OK, 'client added successfully', [])           
                    else:
                        res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])   
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'user already registered with this contact number', [])           
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'user already registered with this email id', [])           
            
            return res
        
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])

class EditClient(CreateAPIView):
    serializer_class = EditCustomModel
    permission_classes = [IsAuthenticated]
    def put(self, request, id, format=None, *args, **kwargs):

        print('request.POST', request.POST)

        data_client = {}
        data_CustomModel = {}
        CustomModelFields = ['name', 'contact_number', 'email', 'profile_picture']

        # for k,v in request.data.items():
        #     if k in CustomModelFields:
        #         data_CustomModel[k] = v
        #     else:
        #         data_client[k] = [v]

        # # print('data_client', data_client)
        # # print('data_CustomModel', data_CustomModel)
        # print('formData_client',data_client)

        # res = Response()

    # ************************ client booking update ************************
        client = Client.objects.filter(id = id).first()
        # formData_client = EditClientForms(request.POST, instance=client)
        # print('formData_client',formData_client)
        # if formData_client.is_valid():
        #     formData_client.save()
        # else:
        #     print(formData_client.errors)

        
        if request.FILES:
            formData_custom_model = EditCustomModelWithFile(request.POST, request.FILES, instance=client.user,)
        else:
            formData_custom_model = EditCustomModel(request.POST, instance=client.user)

        
        if formData_custom_model.is_valid():
            formData_custom_model.save()
            print('working',formData_custom_model)
            res = resFun(status.HTTP_200_OK, 'user edited successfully', [])
        else:
            res = resFun(status.HTTP_200_OK, formData_custom_model.errors, [])
        return res




class EditBookingUserEdit(GenericAPIView):
    serializer_class = EditBookingForms
    # authentication_classes = [IsAuthenticated]
    permission_classes = [IsAuthenticated]
    def put(self, request, booking_id, format=None, *args, **kwargs):

        res = Response()
        booking = Booking.objects.filter(id = booking_id).first()
        # if request.FILES:
        #     print('request.FILES',request.FILES)
        #     formData = EditBookingForms(request.POST, request.FILES, instance=bookings)
        # else:
        formData = EditBookingForms(request.POST, instance=booking)

        if formData.is_valid():
           formData.save()

           res = resFun(status.HTTP_200_OK, 'user edited successfully', [] ) 
        else:
           print()
           res = resFun(status.HTTP_400_BAD_REQUEST, formData.errors, [] ) 

        return res


class updateUserProfilePicture(GenericAPIView):
    serializer_class = updateUserProfilePictureForm
    # authentication_classes = [IgnoreBearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self, request, user_id, format=None, *args, **kwargs):
        res = Response()

        custom_model = CustomModel.objects.filter(id=user_id).first()

        if custom_model:
            if request.FILES:
                formData = updateUserProfilePictureForm(request.POST, request.FILES, instance=custom_model)

                if formData.is_valid():
                   formData.save()
                   res = resFun(status.HTTP_200_OK, 'user edited successfully', [] ) 
                else:
                   res = resFun(status.HTTP_400_BAD_REQUEST, formData.errors, [] )
            else:
               res = resFun(status.HTTP_400_BAD_REQUEST, 'no changes detected', [] )
        else:
           res = resFun(status.HTTP_400_BAD_REQUEST, 'user not found', [] ) 

        return res




class EditClientBooking(CreateAPIView):
    serializer_class = EditCustomModel
    permission_classes = [IsAuthenticated]
    def put(self, request, id, format=None, *args, **kwargs):

        print('request.POST', request.POST)

        booking = Booking.objects.filter(id = id).first()
        formData_client = EditBookingForms(request.POST, instance=booking)
        if formData_client.is_valid():
            print('formData_client',formData_client)
            formData_client.save()
            res = resFun(status.HTTP_200_OK, 'Booking updated successfully', [])

        else:
            print(formData_client.errors)
            res = resFun(status.HTTP_400_BAD_REQUEST, formData_client.errors, [])

        # if request.FILES:
        #     formData_custom_model = EditCustomModelWithFile(request.POST, request.FILES, instance=client.user,)
        # else:
        #     formData_custom_model = EditCustomModel(request.POST, instance=client.user)

        return res





class AddTeamMember(CreateAPIView):
    serializer_class = AddTeamMemberForm
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None, *args, **kwargs):

        print('new function woorking')
        # try:
        def generate_random_code(length=25):
            alphabet = string.ascii_letters + string.digits
            random_code = ''.join(secrets.choice(alphabet) for _ in range(length))
            return random_code
        
        # print('asdfasdf',TeamMember.objects.filter(user__email=request.POST.get('email_id')))
    
        if not CustomModel.objects.filter(email=request.data.get('email')).exists():
            if not CustomModel.objects.filter(contact_number=request.data.get('contact_number')).exists():


                print('request.data',request.data)
                data_1 = {}
                data_1['name'] = request.data.get('name')
                data_1['contact_number'] = request.data.get('contact_number')
                data_1['email'] = request.data.get('email')
                upload_1 = AddCustomModel(data_1)
                print('upload_1', upload_1)
                if upload_1.is_valid():
                    upload_1_instance = upload_1.save()
                    password = generate_random_code()
                    # custom_model_instance = CustomModel.objects.get(id=upload_1_instance.id)
                    upload_1_instance.password = make_password(password)
                    upload_1_instance.save()    
                else:
                    print(upload_1.errors)
                    print('working')
                    return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', []) 
                
                print(upload_1_instance.id)


                data_2 = {}
                data_2['user'] = upload_1_instance.id
                # data_2['source'] = TeamMemberSource.objects.get(title = 'console')
                data_2['user_token'] = generate_random_code()
                data_2['skills'] = request.data.get('skills')
                form = TeamMemberSerializer(data=data_2,many=False)
                if form.is_valid():
                    form.save()
                    # res = resFun(status.HTTP_200_OK,'member saved successfully', [])
                # else:
                #     res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',form.errors)
                
                # upload_2 = AddTeamMemberForm(data_2)
                # if upload_2.is_valid():
                    # upload_2_inst = upload_2.save()
                    # instance = upload.save()
                    # booking_instance = Booking.objects.create(user=upload_2_inst, booking_status= Drp_booking_status.objects.filter(title='in progress').first())
                    # upload_2_inst.booking.add(booking_instance)
                    
                    email_id = upload_1_instance.email
                    message = canned_email.objects.get(email_type = 'welcome_email')
                    message = message.email
                    message = str(message).replace("{{{email}}}", email_id)
                    message = str(message).replace("{{{password}}}", password)
                    # message = str(message).replace("{{{link}}}", f'<a href="http://127.0.0.1:8000/TeamMember-info/{upload_2_inst.id}/{upload_2_inst.TeamMember_token}">fill more details</a>')
                    subject = 'Welcome to Jrs Studios!'
                    from_email = 'akshatnigamcfl@gmail.com'
                    recipient_list = [email_id]
                    text = ''
                    # if send_mail(subject, message, from_email, recipient_list):
                    email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
                    email.attach_alternative(message, 'text/html')
                    # email.attach_file('files/uploadFile_0dTGU7A.csv', 'text/csv')
                    email.send()
                    res = resFun(status.HTTP_200_OK, 'team member added successfully', [])           
                else:
                    print('form.erro',form.errors)
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])   
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'user already registered with this contact number', [])           
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'user already registered with this email id', [])           
        
        return res
        
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])
        

class EditTeamMember(CreateAPIView):
    serializer_class = EditTeamMemberForms
    permission_classes = [IsAuthenticated]
    def put(self, request, id, format=None, *args, **kwargs):

        print('request.data',request.data)

        data_TeamMember = {}
        data_CustomModel = {}
        CustomModelFields = ['name', 'contact_number', 'email', 'profile_picture']

        # for k,v in request.data.items():
        #     if k in CustomModelFields:
        #         data_CustomModel[k] = v
        #     else:
        #         data_TeamMember[k] = [v]

        # # print('data_TeamMember', data_TeamMember)
        # # print('data_CustomModel', data_CustomModel)
        # print('formData_TeamMember',data_TeamMember)

        res = Response()
        TeamMember = Team_member.objects.filter(id = id).first()
        formData_TeamMember = EditTeamMemberForms(request.POST, instance=TeamMember)
        print('formData_TeamMember',formData_TeamMember)
        if formData_TeamMember.is_valid():
            formData_TeamMember.save()
        else:
            print(formData_TeamMember.errors)

        
        if request.FILES:
            formData_custom_model = EditCustomModelWithFile(request.POST, request.FILES, instance=TeamMember.user,)
        else:
            formData_custom_model = EditCustomModel(request.POST, instance=TeamMember.user)

        
        if formData_custom_model.is_valid():
            formData_custom_model.save()
            print('working',formData_custom_model)
            res.status_code = status.HTTP_200_OK
            res.data={
                'status': status.HTTP_200_OK,
                'message': 'user edited successfully',
                'data': []
            }
        else:
            print(formData_custom_model.errors)
           
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data={
                'status': status.HTTP_400_BAD_REQUEST,
                'message': formData_custom_model.errors,
                'data': []
            
            
            }
        return res


# class EditTeamMemberUserEdit(GenericAPIView):
#     serializer_class = EditTeamMemberForms
#     authentication_classes = [IgnoreBearerTokenAuthentication]
#     def put(self, request, id, format=None, *args, **kwargs):
#         res = Response()
#         TeamMember = TeamMember.objects.filter(id = id).first()
#         if request.FILES:
#             print('request.FILES',request.FILES)
#             formData = EditTeamMemberForms(request.POST, request.FILES, instance=TeamMember)
#         else:
#             formData = EditTeamMemberForms(request.POST, instance=TeamMember,)

#         if formData.is_valid():
#            formData.save()
#            res.status_code = status.HTTP_200_OK
#            res.data={
#                'status': status.HTTP_200_OK,
#                'message': 'user edited successfully',
#                'data': []
#            }
#         else:
#            res.status_code = status.HTTP_400_BAD_REQUEST
#            res.data={
#                'status': status.HTTP_400_BAD_REQUEST,
#                'message': formData.errors,
#                'data': []
#            }
#         return res






class AddBooking(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBookingSerializer_RW
    def post(self, request, booking_id, format=None, *args, **kwargs):
        # shoot_date = request.data.get('shoot_date')

        res = Response()
        serializer = AddBookingSerializer_RW(data=request.data)
        serializer.is_valid(raise_exception=True)

        try: 
            booking = Booking.objects.filter(id = booking_id)
        except:
            booking = Booking.objects.filter(pk__in=[])


        if booking.exists():
            booking_date = None
            for d in booking.first().shoot_date.all():
                if str(d) == str(serializer.data.get('shoot_date')):
                    booking_date = d


            additional_service_list = [ ads['id'] for ads in serializer.data.get('additional_service') ]

            if not booking_date == None:

                for ads in booking_date.additional_service.all():
                    ads.delete()
                # if serializer.data.get('event_type') == 'wedding':
                

                service_update_serializer = UpdateBookingServiceSerializer(booking.first(),  data={ 'date':serializer.data.get('shoot_date'), 'additional_service': serializer.data.get('additional_service')}, partial=True)
                service_update_serializer.is_valid(raise_exception=True)
                # elif serializer.data.get('event_type') == 'pre_wedding':
                #     print('booing',booking)
                #     service_update_serializer = booking
                #     service_update_serializer.event_type = serializer.data.get('event_type')
                #     service_update_serializer.additional_service.clear()

                service_update_serializer.save()
                res = resFun(status.HTTP_200_OK, 'booking updated', [])

            else:
                print('else working')

                # if serializer.data.get('event_type') == 'wedding':
                service_update_serializer = UpdateBookingServiceSerializer(booking.first(),  data={ 'date':serializer.data.get('shoot_date'), 'additional_service': serializer.data.get('additional_service')}, partial=True)
                # elif serializer.data.get('event_type') == 'pre_wedding':
                #     print('jooing')
                #     service_update_serializer = UpdateBookingPreWeddingServiceSerializer(user.first(), data={'date':serializer.data.get('shoot_date'), 'event_type': serializer.data.get('event_type')})
                service_update_serializer.is_valid(raise_exception=True)
                service_update_serializer.save()
                res.status_code = status.HTTP_200_OK
                res.data = {
                    'data': [],
                    'message': 'booking updated',
                    'status': status.HTTP_200_OK
                }
                res = resFun(status.HTTP_200_OK, 'booking updated', [])
            
            return res


            # shoot_date__date = 



        #     service_update_serializer.is_valid(raise_exception=True)
        #     print('bookings',service_update_serializer.validated_data['additional_service'])

        #     # bookings.first().service.clear()
        #     bookings.first().additional_service.clear()

        #     # bookings.first().service.add(*service_update_serializer.validated_data['service'])
        #     bookings.first().additional_service.add(*service_update_serializer.validated_data['additional_service'])

        #     res.status_code = status.HTTP_200_OK
        #     res.data = {
        #         'status': status.HTTP_200_OK,
        #         'message': 'booking updated',
        #         'data': []
        #     }


        else:
            print('s3')

            print('serializer.data',serializer.data)

            # try:
            if serializer.data.get('event_type') == 'wedding':
                shoot_date_serializer = BookingDateSerializer(data={'user': id,'date':serializer.data.get('shoot_date'), 'event_type': serializer.data.get('event_type'), 'additional_service': serializer.data.get('additional_service'), 'package': serializer.data.get('package') }, many=False)
            elif serializer.data.get('event_type') == 'pre_wedding':
                print('working til here')
                shoot_date_serializer = BookingDatePreWeddingSerializer(data={'user': id,'date':serializer.data.get('shoot_date'), 'package': Package.objects.get(segment__segment = 'pre_wedding').id, 'event_type': serializer.data.get('event_type') }, many=False)
            # print(shoot_date_serializer)
            if shoot_date_serializer.is_valid():
                shoot_date_serializer.save()
            # print('shoot_date_serializer',shoot_date_serializer)
            # print('shoot_date_serializer.data',shoot_date_serializer)
            # shoot_date_serializer.add
            # shoot_date = Booking_ShootDate.objects.create(**shoot_date_serializer.data)
            # print(UserAccount.objects.get(id = id))
            # print('shoot_date_serializer',shoot_date_serializer)
            # booking_serializer = AddBookingSerializer(data={'user': id, 'shoot_date': shoot_date_serializer.data ,'package': serializer.data.get('package') })
            # print('booking_serializer',booking_serializer.shoot_date)
            # booking_serializer.shoot_date.add(serializer.data.get('shoot_date'))
            # booking_serializer.is_valid(raise_exception=True)
            # print('worig 2')
            # booking_serializer.save()
            # print('worig 3')
            # print(booking_serializer.data, serializer.data.get('shoot_date'))
            # booking_serializer.shoot_date.add(serializer.data.get('shoot_date'))
            # booking_serializer.shoot_date.add(shoot_date)
                res = resFun(status.HTTP_200_OK, 'booking added', [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors, [])
            # except:
            #         res = resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])


        return res
    


class createNewBooking(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBookingSerializer
    def post(self, request, client_id):
        try:
            try:
                client_instance = Client.objects.get(id=client_id)
            except:
                client_instance = None

            if client_instance != None:

                booking_instance = Booking.objects.create(user=client_instance, booking_status= Drp_booking_status.objects.filter(title='in progress').first())
                client_instance.booking.add(booking_instance)
                
                # Booking.objects.create(user=client_instance, )

                res =  resFun(status.HTTP_200_OK,'request successful',[])
            else:
                res =  resFun(status.HTTP_400_BAD_REQUEST,'request failed',[])
            
            return res
        except:
            return resFun(status.HTTP_400_BAD_REQUEST,'something went wrong',[])



class CancleBooking(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBookingSerializer
    def delete(self, request, shootDateId ,format=None, *args, **kwargs):

        print('shootDateId', shootDateId)

        try:
            try:
                # booking = Booking.objects.select_related().filter( shoot_date__date = request.data.get('shoot_date')).values('shoot_date')
                # booking = Booking.objects.select_related().filter(id = shootDateId).values('shoot_date')
                shoot_date = Booking_ShootDate.objects.get(id = shootDateId) 
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'no booking found with this date', [] )
            
            if shoot_date:
                
                for ads in shoot_date.additional_service.all():
                    for ads_team in ads.team.all():
                        ads_team.delete()
                    ads.delete()
                shoot_date.delete()
                    # if str(request.data.get('shoot_date')) == str(b.date):
                        # print('ba**************************************',b.data)
                    # else:
                        # print('else working')
                # booking.service.clear()
                # booking.additional_service.clear()
                # booking.delete()

                return resFun(status.HTTP_200_OK, 'booking cancled successfully', [] )
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])

    

class getBookings(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBookingSerializer
    def get(self, request, date, page, format=None, *args, **kwargs):

        print('date',date, page)
        print('date',request.data)

        # current_month = datetime.now()
        today = datetime.today().date()
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        if date == 'today':
            booking = Booking.objects.filter(shoot_date__date=today, booking_status__title='confirmed').distinct()
        elif date == 'this_month':
            booking = Booking.objects.filter(shoot_date__date__month=current_month, booking_status__title='confirmed').distinct()
        elif date == 'this_year':
            booking = Booking.objects.filter(shoot_date__date__year=current_year,  booking_status__title='confirmed').distinct()


        print('booking', booking)

        # try:
        #     package = Booking.objects.filter(user = id)
        # except:
        #     package = Booking.objects.filter(pk__in=[])

        if booking.exists():
            data=[]
            for b in booking:
                for sd in b.shoot_date.all():
                    # print(b,sd.date)

                    if date == 'today':
                        if sd.date == today:
                            d={
                                'id': b.id,
                                'shoot_date_id': sd.id,
                                'user_id': b.user.user.id,
                                'booking_id': b.user.id,
                                'date': sd.date.strftime('%d-%m-%Y'),
                                'client_name': b.user.user.name,                                
                                'event_type': b.package.segment.segment,
                                'additional_service': [ f'{ass.count} - {ass.additional_service.service_name}' for ass in sd.additional_service.all()]
                            }
                            data.append(d)
                            # break


                    elif date == 'this_month':
                        # for sd in b.shoot_date.all():
                            # print(sd, b)
                        if sd.date.month == current_month:
                            d={
                                'id': b.id,
                                'shoot_date_id': sd.id,
                                'user_id': b.user.user.id,
                                'booking_id': b.user.id,
                                'date': sd.date.strftime('%d-%m-%Y'),
                                'client_name': b.user.user.name,
                                'event_type': b.package.segment.segment,
                                'additional_service': [ f'{ass.count} - {ass.additional_service.service_name}' for ass in sd.additional_service.all()]
                            }
                            data.append(d)
                            # print('d',d)
                            # break
                            
                    elif date == 'this_year':
                        # for sd in b.shoot_date.all():
                            if sd.date.year == current_year:
                                d={
                                    'id': b.id,
                                    'shoot_date_id': sd.id,
                                    'user_id': b.user.user.id,
                                    'booking_id': b.user.id,
                                    'date': sd.date.strftime('%d-%m-%Y'),
                                    'client_name': b.user.user.name,
                                    'event_type': b.package.segment.segment,

                                    'additional_service': [ f'{ass.count} - {ass.additional_service.service_name}' for ass in sd.additional_service.all()]
                                }
                                data.append(d)
                                # break
                # data.append(d)

            # data.sort():
            sorted_data = sorted(data, key=lambda x: datetime.strptime(x['date'], '%d-%m-%Y'))

            serializer = GetBookingSerializer(data=sorted_data, many=True)
            if serializer.is_valid():
                print('serializer.data', serializer.data)
                res = resFun(status.HTTP_200_OK, 'request successful',serializer.data)
            else:
                print(serializer.errors)
                res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors,[])
        else:
            res = resFun(status.HTTP_204_NO_CONTENT, 'no data found',[])
        return res



class getIndvBookings(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetIndvBookingSerializer
    def get(self, request, booking_id, format=None, *args, **kwargs):

        try:
            booking = Booking.objects.get(id=booking_id)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'booking not found', [])

        if booking:
            # data=[]
            # for b in booking:
            dates = []
            for sd in booking.shoot_date.all():
                dates.append({
                    "shoot_date_id": sd.id,
                    "date" : sd.date.strftime('%d-%m-%Y'),
                    "additional_service" : [ f'{ass.count} - {ass.additional_service.service_name}' for ass in sd.additional_service.all()]
                })
                
            data = {
                "id": booking.id,
                "user_id": booking.user.id,
                'booking_date': booking.booking_date.strftime('%d-%m-$Y'),
                'booking_status': { 'id': booking.booking_status.id , 'status': booking.booking_status.title } ,
                'package': { 'id': booking.package.id, 'package': booking.package.package, 'price':  booking.package.price, 'segment_id': booking.package.segment.id, 'segment': booking.package.segment.segment } if booking.package != None else { 'id': None, 'package': None, 'price': None, 'segment_id': None, 'segment': None },
                "discount" : booking.discount if booking.discount !=None else None,
                "wedding_date" : booking.wedding_date.strftime('%d-%m-%Y') if booking.wedding_date !=None else None,
                "groom_name" : booking.groom_name if booking.groom_name !=None and booking.groom_name != '' else None,
                "groom_email_id" : booking.groom_email_id if booking.groom_email_id !=None and booking.groom_email_id !='' else None,
                "groom_contact_number" : booking.groom_contact_number if booking.groom_contact_number !=None and booking.groom_contact_number != '' else None,
                "groom_date_of_birth" : booking.groom_date_of_birth.strftime('%d-%m-%Y') if booking.groom_date_of_birth !=None else None,
                "bride_name" : booking.bride_name if booking.bride_name !=None and booking.bride_name !='' else None,
                "bride_email_id" : booking.bride_email_id if booking.bride_email_id !=None and booking.bride_email_id !='' else None,
                "bride_date_of_birth" : booking.bride_date_of_birth.strftime('%d-%m-%Y') if booking.bride_date_of_birth !=None else None,
                "wedding_venue" : booking.wedding_venue if booking.wedding_venue !=None and booking.wedding_venue !='' else None,
                "shoot_date" : dates
            }

            print('data',data)

            # sorted_data = sorted(data, key=lambda x: datetime.strptime(x['date'], '%d-%m-%Y'))

            serializer = GetIndvBookingSerializer(data=data, many=False)
            if serializer.is_valid():
                res = resFun(status.HTTP_200_OK, 'request successful',serializer.data)
            else:
                print(serializer.errors)
                res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors,[])
        else:
            res = resFun(status.HTTP_204_NO_CONTENT, 'no data found',[])
        return res
    



class getBookingsHistory(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = getBookingHistorySerializer
    def get(self, request, client_id, format=None, *args, **kwargs):
        try:
            try:
                client = Client.objects.get(id=client_id)
            except:
                client = None

            if client !=None:
                data = [{'id': b.id, 'date': b.booking_date, 'status': b.booking_status.title } for b in client.booking.all().order_by('-id') ]
                serializer = getBookingHistorySerializer(data=data, many=True)
                if serializer.is_valid():
                        res = resFun(status.HTTP_200_OK, 'request successful', serializer.data)        
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)   
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'invalid booking id', [])   
            return res

        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])   

    

class confirmBooking(GenericAPIView):
    authentication_classes = [IgnoreBearerTokenAuthentication]
    serializer_class = AddBookingSerializer
    def put(self, request, id, format=None, *args, **kwargs):
        
        try:
            booking = Booking.objects.filter(user = id)
        except:
            booking = Booking.objects.filter(user = id)

        if booking.exists():

            # try:
                # if Drp_booking_status.objects.get(id=request.data.get('booking_status')).title == 'completed':
                message = canned_email.objects.get(email_type = 'booking_confirmation_email')
                message = message.email
                message = message.replace("{{{client}}}", f"{booking.first().user.user.name}")

                subject = 'Congratulations! you booking with jrs studios has been confirmed'
                from_email = 'akshatnigamcfl@gmail.com'
                recipient_list = [booking.first().user.user.email]
                text = 'email sent from MyDjango'
                email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
                email.attach_alternative(message, 'text/html')
                # email.attach(f'{booking.first().user.name}', buffer.read(), 'application/pdf')
                email.send()
                res = resFun(status.HTTP_200_OK, 'quotation sent via email',[])

                serializer = UpdateBookingStatusSerializer(booking.first(), data={'booking_status': Drp_booking_status.objects.get(title='confirmed').id }, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    # print('serializer.data',serializer.data)
                    res = resFun(status.HTTP_200_OK,'status updated',[])
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST,'request failed',[])

                # booking.first().booking_status = Drp_booking_status.objects.filter(id=request.data.get('booking_status')).first()
                # booking.first().save()
            # except:
            #         res = resFun(status.HTTP_400_BAD_REQUEST,'request failed',[])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'no data found',[])
        return res

    



class SubmitPackage(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBookingSerializer
    def post(self, request, id, format=None, *args, **kwargs):
        print('request.data', request.data)
        try:
            package = Booking.objects.filter(id=id)
        except:
            package = Booking.objects.filter(pk__in=[])

        if package.exists():
            try:
                package_RW = request.data.get('package')
                package_obj = Package.objects.get(id=int(package_RW))

                booking = PackageUpdateSerializer(package.first(), data=request.data, partial=True)
                booking.is_valid(raise_exception=True)
                booking.save()
                
                res = resFun(status.HTTP_200_OK,'updated successfully',booking.data)
            except:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])
        else:
            try:
                client = Client.objects.get(id=id)
            except:
                client = Client.objects.filter(pk__in=[])
            
            if client:
                
                booking_instance = Booking.objects.create(user=client)
                # print()
                client.booking = booking_instance
                client.save()
                

                
                package = Booking.objects.filter(user=id)
                if package.exists():

                    try:
                        package_RW = request.data.get('package')
                        package_obj = Package.objects.get(id=int(package_RW))

                        booking = PackageUpdateSerializer(package.first(), data=request.data, partial=True)
                        booking.is_valid(raise_exception=True)
                        booking.save()

                        res = resFun(status.HTTP_200_OK,'submitted',booking.data)
                    except:
                        res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])
                    
                    # res = resFun(status.HTTP_200_OK, 'Booking Created',[])
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])

            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'user not found',[])
        return res



class getBookingStatusList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = getBookingStatusListSerializer
    def get(self, request, format=None, *args, **kwargs):
        try:

            booking_status_list_instance =  Drp_booking_status.objects.all()
            booking_status_list = [ { 'id': b.id, 'title': b.title } for b in booking_status_list_instance]

            serializer = getBookingStatusListSerializer(data=booking_status_list, many=True)
            if serializer.is_valid():
                # serializer.save()
                print('operation successful')
                return resFun(status.HTTP_200_OK, 'request successful', serializer.data)

            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])



class UpdateBookingStatus(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBookingSerializer
    def post(self, request, id, format=None, *args, **kwargs):

        print('request.data',request.data)
        
        try:
            booking = Booking.objects.filter(id = id)
        except:
            booking = Booking.objects.filter(id = id)

        if booking.exists():

            if Drp_booking_status.objects.get(id=request.data.get('booking_status')).title == 'confirmed':
                print('send email')
                message = canned_email.objects.get(email_type = 'welcome_email')
                message = message.email

                message = str(message).replace("{{{link}}}", f'<a href="http://127.0.0.1:8000/client-info/{booking.first().user.id}/{booking.first().id}/{booking.first().user.client_token}">fill more details</a>')

                subject = 'Welcome to Jrs Studios!'
                from_email = 'akshatnigamcfl@gmail.com'
                recipient_list = [booking.first().user.user.email]
                text = 'email sent from MyDjango'

                email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
                email.attach_alternative(message, 'text/html')
                # email.attach(f'{booking.first().user.name}', buffer.read(), 'application/pdf')
                email.send()


                res = resFun(status.HTTP_200_OK, 'quotation sent via email',[])
                print('request.data',request.data)

            elif Drp_booking_status.objects.get(id=request.data.get('booking_status')).title == 'completed':

                for b in booking.first().shoot_date.all():
                    for ads in b.additional_service.all():
                        additional_service = ads.additional_service.service_name
                        service_price = ads.additional_service.price
                        count = ads.count
                        team_list = ads.team.all()
                        print('ads',additional_service, count, service_price)

                        if not count == len(team_list):
                            return resFun(status.HTTP_400_BAD_REQUEST, 'required service count and team member count are not same', [])
                        
                        for tm in team_list:
                            tm.team.fund.add(fund_history.objects.create(**{ 'date': datetime.today().date() ,  'note': 'service completed' ,  'booking': booking.first() ,  'amount': service_price }))

                # review email
                message = canned_email.objects.get(email_type = 'welcome_email')
                message = message.email
                message = str(message).replace("{{{link}}}", f'<a href="http://127.0.0.1:8000/client-info/{booking.first().user.id}/{booking.first().user.client_token}">fill more details</a>')
                sendEmail([booking.first().user.user.email], message , 'Welcome to Jrs Studios!')




            serializer = UpdateBookingStatusSerializer(booking.first(), data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                res = resFun(status.HTTP_200_OK,'status updated',[])

            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'request failed',[])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'no data found',[])

        return res
    


class addBookingTeam(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = addBookingTeamSerializer
    def post(self, request, booking_id):
            print(request.data)
        # try:
            try:
                booking_id = Booking.objects.get(id = booking_id)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'booking id not valid', [])

            unique_team_mates = []
            for r in request.data:
                for b in booking_id.shoot_date.all():
                    for a in b.additional_service.filter(id = r.get('additional_service_count_id')):
                        # if r.get('additional_service_count_id') == a.id:

                        for at in a.team.all():
                            at.delete()

                        a.team.clear()
                        for tm in r.get('team'):
                            team_member_status_instance = teamMemberStatus.objects.create(team=Team_member.objects.get(id=tm), status=drp_teamMemberBookingStatus.objects.get(title='pending'))
                            print('team_member_status_instance',team_member_status_instance)
                            a.team.add(team_member_status_instance)
                            if not Team_member.objects.get(id=tm) in unique_team_mates:
                                unique_team_mates.append(Team_member.objects.get(id=tm))

            for ut in unique_team_mates:
                # print('unique_team_mates',ut.email_id)
                sendEmail([ut.user.email], '<p>invited to shoot photography event</p>', 'You have a new booking' )
                
            # data = []

            # for b in booking:
            #     for bb in b:
            #         data.append(bb)

            # print('data',data)

            # if not request.data.get('additional_service_count_id'):
            #     return resFun(status.HTTP_400_BAD_REQUEST, 'additional_service_count_id is a required field', [])
            # if not request.data.get('team'):
            #     return resFun(status.HTTP_400_BAD_REQUEST, 'options is a required field', [])
            
            res = resFun(status.HTTP_200_OK, 'request successful', [])
            return res
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])





class GetAdditionalServices(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetServicesSerializer
    def get(self, request, booking_id, format=None, *args, **kwargs):

        try:
            booking_instance = Booking.objects.get(id=booking_id)
        except:
            booking_instance = None

        if booking_instance != None:
            # service_instance = Service.objects.all().values()
            # serializer = GetServicesSerializer(data=list(service), many=True)
            # if not serializer.is_valid(raise_exception=True):
            #     res.status_code = status.HTTP_400_BAD_REQUEST
            #     res.data = {
            #         'status': status.HTTP_400_BAD_REQUEST,
            #         'message': serializer.errors if serializer.errors else 'request failed',
            #         'data': [] 
            #     }
            #     return res

            additional_service = AdditionalService.objects.filter(trash=False, segment=booking_instance.package.segment.id )
            data  = [{'service_name': s.service_name, 'price': s.price,'id':s.id}  for s in additional_service]
            serializer_2 = AdditionalServiceSerializer(data=data, many=True)
            if not serializer_2.is_valid(raise_exception=True):
                res = resFun(status.HTTP_200_OK, 'request failed', [serializer_2.errors if serializer_2.errors else 'request failed'])
                return res

            main_serializer = ServiceMainSerializer(data={'additional_service': serializer_2.data})
            if main_serializer.is_valid(raise_exception=True):
                res = resFun(status.HTTP_200_OK, 'request successful', main_serializer.data)
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [main_serializer.errors if main_serializer.errors else 'request failed'])
            return res
        
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'client id not valid', [])
    


class GetPackages(GenericAPIView):
    serializer_class = GetPackageSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, id, format=None, *args, **kwargs):
        # print('request', request)
        package = Package.objects.all()
        res = Response()
        data = []
        if package.exists():
            try:
                user = Booking.objects.filter(user = id)
            except:
                user = Booking.objects.filter(pk__in=[])

            for s in package:
                if s.segment.segment == 'wedding':
                    service = [str(serv) for serv in s.service.all()]
                    dt = {'id': int(s.id) ,'package': str(s), 'price': int(s.price), 'segment': str(s.segment),'service': service}
                    if user.first():
                        dt['booked_package'] = {'package': user.first().package.package, 'id': user.first().package.id}
                    else:
                        dt['booked_package'] = {'package': [], 'id': []}

                    data.append(dt)


            
            serializer = GetPackageSerializer(data=data, many=True)
            if serializer.is_valid():
                res = resFun(status.HTTP_200_OK, 'request successful', serializer.data)
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors, [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'packages not available', [])
        return res




class GetShootCategory(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShootCategorySerializer
    def get(self, request, format=None, *args, **kwargs):
        try:
            additional_service = AdditionalService.objects.filter(trash=False).exclude(service_name='pre wedding').values()
            serializer_2 = ShootCategorySerializer(data=list(additional_service), many=True)
            if not serializer_2.is_valid(raise_exception=True):
                return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [serializer_2.errors if serializer_2.errors else 'request failed'])

            res = resFun(status.HTTP_200_OK, 'request successful', serializer_2.data)
            return res
        
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])




class GetBookedServices(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetBookedServicesSerializer
    def get(self, request, booking_id, format=None, *args, **kwargs):
        res = Response()
        bookings=Booking.objects.filter(id=booking_id)
        if bookings.exists():
            booked_service = []
            for b in bookings:
                for d in b.shoot_date.all():
                    # print(d)
                    booked_service_obj = {}
                    booked_service_obj['shoot_date'] = {'id': d.id ,'full_date': str(d.date), 'date': d.date.day, 'month': d.date.month, 'year': d.date.year }
                    # booked_service_obj['booked_service'] = [{'service': c.service_name, 'segment': c.segment} for c in  b.service.all()]
                    booked_service_obj['booked_additional_service'] = [{'additional_service': str(c.additional_service), 'count': int(c.count)} for c in  d.additional_service.all()]
                    booked_service.append(booked_service_obj)
            print('booked_service', booked_service)

            serializer = GetBookedServicesSerializer(data=list(booked_service), many=True)
            serializer.is_valid(raise_exception=True)

            res = resFun( status.HTTP_200_OK, 'request successful' , serializer.data )
        else:
            res = resFun( status.HTTP_400_BAD_REQUEST, 'no booking available' ,[] )
        return res
    


def getBookingDetails(b, user_id):
    # print('booking',bookings)
    payment_structure = None
    additionals_total_price = 0
    # for b in bookings:
    packages = []
    # for c in b.service.all():
    #     if c.charges_application == 'complete_shoot':
    #             booking_pricing['services']['complete_shoot'].append({'service': c.service_name, 'price': c.price, 'charges_application': c.charges_application.replace('_', ' ')})
    #     elif c.charges_application == 'per_day':
    #             booking_pricing['services']['per_day'].append({'service': c.service_name, 'price': c.price, 'charges_application': c.charges_application.replace('_', ' ')})
    for c in b.shoot_date.all():
        additional_service_RW = []
        for s in c.additional_service.all():
            # print(s.additional_service.service_name)
            # if s:
            additionals_total_price += int(s.additional_service.price) * int(s.count)
            additional_service_RW.append({'additional_service': s.additional_service.service_name, 'price': s.additional_service.price, 'count': s.count, 'service_total_price': int(s.additional_service.price) * int(s.count) })
        
        # if len(additional_service_RW) > 0:
        packages.append({'date': str(c.date), 'event_type': c.event_type, 'service' : additional_service_RW})
    # if len(packages) > 0:
        # print('bbbbbbbbbb',Package.objects.get(id=b.package.id).service.all())
        payment_structure = {
            'package': b.package.package, 
            'package_price': b.package.price,
            'discount': b.discount,
            'additionals_total_price' : additionals_total_price, 
            'total_price': int(b.package.price) + int(additionals_total_price), 
            'service': [s.service_name for s in Package.objects.get(id=b.package.id).service.all()],
            'additionals': packages,
            'remaining_payment': int((int(b.package.price) + int(additionals_total_price)) ) - int(Payments.objects.filter(user=user_id).aggregate(Sum('amount'))['amount__sum'] if Payments.objects.filter(user=user_id).aggregate(Sum('amount'))['amount__sum'] != None else 0 )
            }
    
    # print('payment_structure',payment_structure)
        # if c.charges_application == 'complete_shoot':
        # booking_pricing['additional_services'].append({'service': c.service_name, 'price': c.price, 'charges_application': c.charges_application.replace('_', ' ')})
        # elif c.charges_application == 'per_day':
        #     booking_pricing['additional_services']['per_day'].append({'service': c.service_name, 'price': c.price, 'charges_application': c.charges_application.replace('_', ' ')})
            
    # service_data = {"additional_services": [], 'total_price': 0 }
    # for k in booking_pricing:
        # print(k)
        # if True:
            # for dt in k['additionals']:
        #         pass
                # for key, value in dt.items():
                #     print(key,value)
                # if key == 'complete_shoot':
                #     unique = set()
                #     for val in value:
                #         unique.add(tuple(sorted(val.items())))
                #     unique_list = [dict(t) for t in unique]
                    
                #     for u in unique_list:
                #         u['count'] = 1 
                #     if len(unique_list) > 0:
                #         for u in unique_list:
                #             service_data['services'].append(u)
                #             service_data['total_price'] = service_data['total_price'] + int(u['price'])
                
                # elif key == 'per_day':
                #     unique = set()
                #     for val in value:
                #         unique.add(tuple(sorted(val.items())))
                #     unique_list = [dict(t) for t in unique]
                #     count = Counter(tuple(sorted(v.items())) for v in value)
                #     service_repeat = []
                #     for d, count in count.items():
                #         service_repeat.append({"service": dict(d)['service'], 'count': count})
                #     for u in unique_list:
                #         for s in service_repeat:
                #             if u['service'] == s['service']:
                #                 u['count'] = s['count']
                #                 u['price'] = int(u['price']) * int(s['count']) 
                #     if len(unique_list) > 0:
                #         for u in unique_list:
                #             service_data['services'].append(u)
                #             service_data['total_price'] = service_data['total_price'] + int(u['price'])
                    
        # elif k=='additional_services':
        #     for key, value in v.items():
        #         if key == 'complete_shoot':
        #             unique = set()
        #             for val in value:
        #                 unique.add(tuple(sorted(val.items())))
        #             unique_list = [dict(t) for t in unique]
        #             for u in unique_list:
        #                 u['count'] = 1
        #             if len(unique_list) > 0:
        #                 for u in unique_list:
        #                     service_data['additional_services'].append(u)
        #                     service_data['total_price'] = service_data['total_price'] + int(u['price'])
        #         elif key == 'per_day':
        #             unique = set()
        #             for val in value:
        #                 unique.add(tuple(sorted(val.items())))
        #             unique_list = [dict(t) for t in unique]
        #             count = Counter(tuple(sorted(v.items())) for v in value)
        #             service_repeat = []
        #             for d, count in count.items():
        #                 service_repeat.append({"service": dict(d)['service'], 'count': count})

        #             for u in unique_list:
        #                 for s in service_repeat:
        #                     if u['service'] == s['service']:
        #                         u['count'] = s['count']
        #                         u['price'] = int(u['price']) * int(s['count']) 
        #             if len(unique_list) > 0:
        #                 for u in unique_list:
        #                     service_data['additional_services'].append(u)
        #                     service_data['total_price'] = service_data['total_price'] + int(u['price'])

    return payment_structure
            



class GetServicesInvoice(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetServicesInvoiceSerializer
    def get(self, request, id, format=None, *args, **kwargs):
        bookings = Booking.objects.get(user = id)
        res = Response()
        if bookings:
            service_data = getBookingDetails(bookings, id)
            print('service_data',service_data)
            serializer = GetServicesInvoiceSerializer(data=service_data)
            serializer.is_valid(raise_exception=True)
            res.status_code = status.HTTP_200_OK
            res.data={
                'status': status.HTTP_200_OK,
                'message': 'request successful',
                'data': serializer.data,
            }
        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data={
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'no booking found',
                'data': [],
            }
        return res

        # context = {'data' : service_data, 'client_data': client.first()}
    


class PendingPayment(GenericAPIView):
    serializer_class = PendingPaymentSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, bookingId):
        try:
            data = []
            package_price = 0
            additionalPrice = 0
            discount = 0
            total_payment = 0
            try:
                booking_instance = Booking.objects.get(id=bookingId)
                payment_instance = Payments.objects.filter(booking=bookingId)
            except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'invalid booking id', [])

            package_price = booking_instance.package.price
            discount = booking_instance.discount
            for sd in booking_instance.shoot_date.all():
                for ads in sd.additional_service.all():
                    additionalPrice += ads.additional_service.price*ads.count
            
            for p in payment_instance:
                total_payment += p.amount

            
            # booking_instance.shoot_date
            serializer = PendingPaymentSerializer(data={ 'pending_payment': (((package_price + additionalPrice) - discount)-total_payment) }, many=False)
            if serializer.is_valid():
                return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', serializer.errors )
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])



class GetTeamMember(GenericAPIView):
    serializer_class = GetTeamMemberSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, serviceId):
        # try:
        team_member_instance = Team_member.objects.filter(skills__id=serviceId)
        if team_member_instance.exists():
            team_member_instance = [ { 'id': tm.id, 'value': tm.user.name } for tm in team_member_instance]
            serializer = GetTeamMemberSerializer(data=team_member_instance, many=True)
            if serializer.is_valid():
                return resFun(status.HTTP_200_OK,'successful', serializer.data)
            else:
                print(serializer.errors)
                return resFun(status.HTTP_400_BAD_REQUEST,'something went wrong', serializer.errors)
        else:
            return resFun(status.HTTP_204_NO_CONTENT,'no team member found', [])

        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST,'request failed', [])




class GetPaymentList(GenericAPIView):
    serializer_class = getPaymentSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, dateSelector, limit, page):

        offset = int((page - 1)*limit)

        if dateSelector==None or dateSelector=='this_month':
            dateSelector=='this_month'
            date = datetime.now().month
            payment_instance = Payments.objects.filter(date__month=date).distinct().order_by('-id')[offset: offset+limit]
            total_pages = math.ceil(Payments.objects.filter(date__month=date).distinct().count()/limit)
        elif dateSelector=='this_year':
            date = datetime.now().year
            payment_instance = Payments.objects.filter(date__year=date).distinct().order_by('-id')[offset: offset+limit]
            total_pages = math.ceil(Payments.objects.filter(date__year=date).distinct().count()/limit)
        elif dateSelector=='today':
            date = datetime.today().date()
            payment_instance = Payments.objects.filter(date=date).order_by('-id')[offset: offset+limit]
            total_pages = math.ceil(Payments.objects.filter(date=date).distinct().count()/limit)
        elif dateSelector=='custom':
            date_from = request.GET.get("date_from")
            date_to = request.GET.get("date_to")
            date = {'date_from': date_from,'date_to': date_to } 
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date += timedelta(days=1)
            payment_instance = Payments.objects.filter(date__range=(start_date,end_date)).order_by('-id')[offset: offset+limit]
            total_pages = math.ceil(Payments.objects.filter(date__range=(start_date,end_date)).distinct().count()/limit)



        data = [ { 'id': p.id, 'date': p.date.strftime('%d-%m-%Y') ,'amount': p.amount, 'payment_mode': p.payment_mode, 'payment_note': p.payment_note }  for p in payment_instance ]
        # print('payment instance', payment_instance )
        if payment_instance.exists():
            serializer = getPaymentSerializer(data=data, many=True)
            if serializer.is_valid():
                print(serializer.data)
                return resFun(status.HTTP_200_OK, 'successful', { 'data': serializer.data, 'current_page' : page, 'total_pages': total_pages  } )
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', serializer.error_messages )
        else:
            return resFun(status.HTTP_204_NO_CONTENT, 'no data found', [])





class GetPayment(GenericAPIView):
    serializer_class = getPaymentSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, booking_id):
        print('request.data', request.data) 
        # try:
        

        payment_instance = Payments.objects.filter(booking=booking_id)
        # print(payment_instance)
        print('payment_instance',payment_instance)
        if payment_instance.exists():
            payment_instance_list = [ { 'id': p.id, 'date': p.date.strftime("%d-%m-%Y"), 'amount': p.amount, 'payment_mode' : p.payment_mode, "payment_note": p.payment_note  } for p in payment_instance ]
            print(payment_instance_list)
            serializer = getPaymentSerializer(data=payment_instance_list, many=True)
            if serializer.is_valid():
                print(serializer.data)
                return resFun(status.HTTP_200_OK, 'successful', serializer.data)
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', serializer.error_messages )
        else:
            return resFun(status.HTTP_204_NO_CONTENT, 'no data found', [])


        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])





class PaymentSubmit(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer
    def post(self, request, id, format=None, *args, **kwargs):

        print(request.data)

        # client = Client.objects.filter(id = id)

        # template = get_template('console-layout/invoice.html')
        # context = {
        #     'payment_date': 27/1/2024
        # }
        # html = template.render(context)
        # res = BytesIO()
        # result = pisa.CreatePDF(html, dest=res)
        # if result.err:
        #     return Response({
        #         'status': status.HTTP_400_BAD_REQUEST,
        #         'error': 'error generating pdf',
        #         'data': []
        #         })
        # res.seek(0)
        # return FileResponse(res, content_type='application/pdf', as_attachment=True, filename=f'{client.first().name}.pdf')

        if request.data.get('payment') == 0:
            res = resFun(status.HTTP_400_BAD_REQUEST, "amount should be more than 0", [])
            return res

    
        res = Response()
        # client = Client.objects.get(id = id)
        try:
            booking = Booking.objects.get(id = id)
        except:
            booking = None

        if booking != None:

            # print('request.data',request.data)

            # service_data = getBookingDetails(bookings, id)

            # if int(request.data.get('discount')) >= int(service_data.get('total_price'))/2:
            #     raise serializers.ValidationError('dicount can not be more than half of the total price')

            invoice = Invoice.objects.filter(user = booking.user.id)

            # if invoice.exists():
            #     raise serializers.ValidationError('already submitted')
            # else:
            #     print(booking.id)

            # print(request.data.get('discount'))

            # booking = BookingDiscountPriceSerializer(bookings, data={'total_price': service_data.get('total_price'),'package': request.data.get('package')}, partial=True)
            # booking.is_valid(raise_exception=True)
            # if booking.save():

            payment = PaymentsSerializer(data={'amount': request.data.get('payment'), 'payment_mode': request.data.get('payment_mode'), 'payment_note': request.data.get('payment_note'),  'user': booking.user.id, 'booking': booking.id })
            if payment.is_valid():
                if payment.save():
                    invoice = InvoiceSerializer(data={ 'user': booking.user.id, 'payment': payment.data['id'] })
                    invoice.is_valid(raise_exception=True)
                    if invoice.save():
                        pass
                    else:
                        serializers.ValidationError('payment not save')
                else:
                    serializers.ValidationError('payment not save')
                # else:
                #     serializers.ValidationError('discount and total price not updated')
                res = resFun(status.HTTP_200_OK,'payment submitted',[])
            else:
                # print(p)
                res = resFun(status.HTTP_400_BAD_REQUEST,'something went wrong', payment.errors )
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'invalid client id',[])
        return res
    


class GenerateInvoice(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateInvoiceSerializer
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request, id, format=None, *args, **kwargs):
        pass
    

        # template_path = 'your_template.html'
        # template = get_template(template_path)
        # context = {'my_variable': 'some value'}
        # html = template.render(context)
        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'filename="mypdf.pdf"'
        # pisa.CreatePDF(html, dest=response)
        # return response



        client = Client.objects.filter(id = id)
        if client.exists():

            template = get_template('console-layout/invoice.html')
            context = {
                'payment_date': 27/1/2024,
                'font_link': 'https://fonts.googleapis.com/css2?family=Allura&display=swap'
            }
            html = template.render(context)
            res = BytesIO()
            result = pisa.CreatePDF(html, dest=res)
            if result.err:
                return Response({
                    'status': status.HTTP_400_BAD_REQUEST,
                    'error': 'error generating pdf',
                    'data': []
                    })
            res.seek(0)
            return FileResponse(res, content_type='application/pdf', as_attachment=True, filename=f'{client.first().name}.pdf')
        else:
            res = Response()
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'data':[],
                'message':'client id invalid',
            }
            return res
        


def quotationGenerateFun(client, discount, additional_price, booking, booking_data):
    buffer = BytesIO()

        # response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = f'attachment; filename="{client.first().name}"'
    page_height = 792
    tb_gap = 42
    logo_gap = 50
    content_gap_out = 30
    content_gap_in = 25
    line_gap = 20
    bullets_gap = 15

    def nextPageAuth(pg_height, r,g,b, font_style, font_size):
        print('pg_height, tb_gap', pg_height, tb_gap)
        if pg_height <= tb_gap:
            pdf_canvas.showPage()
            pg_height = 792 - tb_gap
            pdf_canvas.setFillColorRGB(255/255, 255/255, 255/255)  # Yellow background
            pdf_canvas.rect(0, 0, letter[0], letter[1], fill=True)
            pdf_canvas.setFont(font_style, font_size)
            pdf_canvas.setFillColorRGB(r, g, b)  # Black text color
            print('newpage', pg_height)
        else:
            pass
        return pg_height
    
    def draw_list_with_bullets(pdf_canvas, items, x, y, r,g,b,font_style, font_size, bullet_radius=2, bullet_spacing=15, text_offset=15):
        pg_height = y
        new = True
        for item in items:
            pg_height = nextPageAuth(pg_height,r,g,b, font_style, font_size)
            if new:
                new=False
            else:
                pg_height -= text_offset
            pdf_canvas.setFillColorRGB(r, g, b)
            pdf_canvas.circle(x, pg_height+3, bullet_radius, fill=True,stroke=False)
            pdf_canvas.drawString(x + bullet_spacing, pg_height, item)
        return pg_height
    
    pdf_canvas = canvas.Canvas(buffer, pagesize=letter)
    pdf_canvas.setFillColorRGB(255/255, 255/255, 255/255)  # Yellow background
    pdf_canvas.rect(0, 0, letter[0], letter[1], fill=True)
        # # Add image
        # image_path = 'http://localhost:8000/static/assets/images/bg_fix_1.jpg'  # Replace with the actual path
        # pdf_canvas.drawImage(image_path, 100, 500, width=200, height=200)
        # Add text overlay 
    def drawStringsCustom(a):
        x = a['x']
        y = a['y']
        gap = a['gap']
        font_size = a['font_size']
        content = a['content']
        bullets = a['bullets']
        pdf_canvas = a['pdf_canvas']
        r = a['r']
        g = a['g']
        b = a['b']
        font_style = a['font_style']
        y = nextPageAuth(y,r,g,b, font_style, font_size)
        if not bullets == False:
            y -= gap
            pdf_canvas.setFont(font_style, font_size)
            pdf_canvas.setFillColorRGB(r,g,b)  # Black text color
            page_height = draw_list_with_bullets(pdf_canvas, content, x, y, r,g,b,font_style, font_size)
            return page_height
            # print('this working')
        else:
            # Helvetica
            y -= gap
            pdf_canvas.setFont(font_style, font_size)
            pdf_canvas.setFillColorRGB(r,g,b)  # Black text color
            pdf_canvas.drawString(x, y, content)
            # page_height = draw_list_with_bullets(pdf_canvas, content, x, y)
        return y
    
    # print('workng till here', bk)
    
    try:
        # booking = Booking.objects.filter(id=bk.id)
        # print('booking',)
        for b in booking.first().shoot_date.all():
            print(b.date)
            print([a.additional_service.service_name for a in b.additional_service.all()])
    except:
        booking = Booking.objects.filter(pk__in=[])

    
    if booking.exists():
        font_path = 'media/font/Julius_Sans_One/JuliusSansOne-Regular.ttf'  # Update with your actual path
        pdfmetrics.registerFont(TTFont('JuliusSansOne', font_path))
        font_path = 'media/font/Judson/Judson-Regular.ttf'  # Update with your actual path
        pdfmetrics.registerFont(TTFont('Judson-Regular', font_path))
        font_path = 'media/font/Judson/Judson-Bold.ttf'  # Update with your actual path
        pdfmetrics.registerFont(TTFont('Judson-Bold', font_path))
        locale.setlocale(locale.LC_NUMERIC, 'en_IN')


        camera_equipment_1 = []
        camera_equipment_2 = []

        for i in range(len(booking_data['camera_equipments'])):
            if i < math.ceil(len(booking_data['camera_equipments'])/2):
                camera_equipment_1.append(booking_data['camera_equipments'][i])
            else:
                camera_equipment_2.append(booking_data['camera_equipments'][i])

        print('camera_equipment_1',camera_equipment_1)
        print('camera_equipment_2',camera_equipment_2)

        # for b in booking_data['camera_equipments']:
        #     if (len(booking_data['camera_equipments'])/2+1):

        formatted_price = locale.format_string("%.2f", int((booking.first().package.price + additional_price ) - discount), grouping=True)
        formatted_price = formatted_price.rstrip("0").rstrip(".")
            
        text_width = pdf_canvas.stringWidth('Jrs Studios', "JuliusSansOne", 20)
        x_center = (pdf_canvas._pagesize[0] - text_width) / 2

        print('main_page_height', page_height, pdf_canvas)
            
        page_height = drawStringsCustom({'x':x_center, 'y':page_height, 'gap': tb_gap, 'font_style':"JuliusSansOne", 'font_size': 23, 'content': 'Jrs Studios', 'bullets': False, 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        pdf_canvas.setStrokeColorRGB(102/255, 102/255, 0) 
        pdf_canvas.line(x_center-10, page_height-10, x_center + text_width+20, page_height-10) 
            
        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': logo_gap, 'font_style':"Judson-Regular", 'font_size': 13, 'content': f'Dear {client.user.name.capitalize()},', 'bullets': False, 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        
        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': content_gap_in, 'font_style':"Judson-Regular", 'font_size': 13, 'content': 'As per your requirement for Wedding Event Shoot, I ‘ve shared below the detailed', 'bullets': False, 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': content_gap_in, 'font_style':"Judson-Regular", 'font_size': 13, 'content': 'quotation for the same', 'bullets': False, 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})

        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': content_gap_out, 'font_style':"Judson-Bold", 'font_size': 16, 'content': f'Package: {booking_data['package_name'].upper()}/-', 'bullets': False, 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': content_gap_out, 'font_style':"Judson-Bold", 'font_size': 18, 'content': f'Cost: {formatted_price}/-', 'bullets': False, 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': content_gap_out, 'font_style':"Judson-Bold", 'font_size': 13, 'content': 'The package is inclusive of:', 'bullets': False, 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        for b in booking.first().shoot_date.all().order_by('date'):
            page_height = drawStringsCustom({'x':75, 'y':page_height, 'gap': content_gap_in, 'font_style':"Judson-Bold", 'font_size': 13, 'content': f"{b.date}", 'bullets': False,'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
            page_height = drawStringsCustom({'x':90, 'y':page_height, 'gap': bullets_gap, 'font_style':"Judson-Regular", 'font_size': 11, 'content': [f'{a.count} - {a.additional_service.service_name}' for a in b.additional_service.all()], 'bullets': True , 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': content_gap_out, 'font_style':"Judson-Bold", 'font_size': 13, 'content': 'Cameras & Equipments details:', 'bullets': False,'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        drawStringsCustom({'x':250, 'y':page_height, 'gap': content_gap_in, 'font_style':"Judson-Regular", 'font_size': 11, 'content': camera_equipment_2, 'bullets': True , 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        page_height = drawStringsCustom({'x':75, 'y':page_height, 'gap': content_gap_in, 'font_style':"Judson-Regular", 'font_size': 11, 'content': camera_equipment_1, 'bullets': True , 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': content_gap_out, 'font_style':"Judson-Bold", 'font_size': 13, 'content': 'Production Process:', 'bullets': False,'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        page_height = drawStringsCustom({'x':75, 'y':page_height, 'gap': content_gap_in, 'font_style':"Judson-Regular", 'font_size': 11, 'content': booking_data['production_process'], 'bullets': True , 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})


        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': content_gap_out, 'font_style':"Judson-Bold", 'font_size': 13, 'content': 'What you get:', 'bullets': False,'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        page_height = drawStringsCustom({'x':75, 'y':page_height, 'gap': content_gap_in, 'font_style':"Judson-Regular", 'font_size': 11, 'content': booking_data['deliverables'], 'bullets': True , 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})


        print('page_height',page_height, content_gap_out)

        page_height = drawStringsCustom({'x':60, 'y':page_height, 'gap': content_gap_out, 'font_style':"Judson-Bold", 'font_size': 13, 'content': 'Terms & Condition:', 'bullets': False,'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        page_height = drawStringsCustom({'x':75, 'y':page_height, 'gap': content_gap_in, 'font_style':"Judson-Regular", 'font_size': 11, 'content': booking_data['terms_conditions'], 'bullets': True , 'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        text_width = pdf_canvas.stringWidth('we will be glad to create memories for you too', "JuliusSansOne", 13)
        
        x_center = (pdf_canvas._pagesize[0] - text_width) / 2
        # print('page_height', page_height, content_gap_out+content_gap_out+content_gap_out)

        # page_height = drawStringsCustom({'x':x_center, 'y':page_height, 'gap': content_gap_out*3, 'font_style':"JuliusSansOne", 'font_size': 13, 'content': '', 'bullets': False,'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})

        page_height = nextPageAuth(40, 102/255,102/255,102/255, "JuliusSansOne", 13)

        page_height = drawStringsCustom({'x':x_center, 'y':page_height, 'gap': content_gap_out+content_gap_out+content_gap_out, 'font_style':"JuliusSansOne", 'font_size': 13, 'content': 'we will be glad to create memories for you too', 'bullets': False,'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        pdf_canvas.setStrokeColorRGB(102/255, 102/255, 102/255)
        pdf_canvas.line(x_center+75, page_height-10, x_center + text_width-75, page_height-10)
        text_width = pdf_canvas.stringWidth('hope to see you soon', "JuliusSansOne", 13)
        x_center = (pdf_canvas._pagesize[0] - text_width) / 2
        print('page_height', page_height, content_gap_out)

        page_height = drawStringsCustom({'x':x_center, 'y':page_height, 'gap': content_gap_out, 'font_style':"JuliusSansOne", 'font_size': 13, 'content': 'hope to see you soon', 'bullets': False,'pdf_canvas':pdf_canvas, "r":102/255,'g':102/255,'b':102/255})
        

        pdf_canvas.save()
        buffer.seek(0)

        return buffer





class GenerateQuotation(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = GenerateQuotationSerializer
    # parser_classes = [MultiPartParser, FormParser]
    def post(self, request, id, discount, format=None, *args, **kwargs):

        booking = Booking.objects.filter(id=id)

        # deliverables = request.data.get('deliverables')
        # terms_conditions = request.data.get('terms_conditions')2

        # for d in deliverables:
        #     booking.first().deliverables.add(d)

        # for t in terms_conditions:
        #     booking.first().terms_conditions.add(t)

        serializer = UpdateDiscountSerializer(booking.first(), data={'discount': discount}, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'discount not valid', [])
            return res

        additional_price=0

        for d in booking.first().shoot_date.all():
            for e in d.additional_service.all():
                additional_price += int(e.additional_service.price*e.count)
                # print(int(e.additional_service.price*e.count))
        
        # print('Additional Price',additional_price)

        camera_equipments = [int(c) for c in request.data.get('camera_equipments')]
        camera_equipments_data = []
        for c in camera_equipments:
            for ce in CameraEquipments.objects.filter(id=c, trash=False):
                camera_equipments_data.append(ce.title)
        
        deliverables = [int(c) for c in request.data.get('deliverables')]
        deliverables_data = []
        for c in deliverables:
            for ce in Deliverables.objects.filter(id=c, trash=False):
                deliverables_data.append(ce.title)
        
        production_process = [int(c) for c in request.data.get('production_process')]
        production_process_data = []
        for c in production_process:
            for ce in ProductionProcess.objects.filter(id=c, trash=False):
                production_process_data.append(ce.title)
        
        terms_conditions = [int(c) for c in request.data.get('terms_conditions')]
        terms_conditions_data = []
        for c in terms_conditions:
            for ce in Terms_Conditions.objects.filter(id=c, trash=False):
                terms_conditions_data.append(ce.title)


        # booking_data = [ {'date': b.date, 'services': [ {'count': ads.count, 'service_name': ads.additional_service.service_name} for ads in b.additional_service.all()] } for b in booking.first().shoot_date.all()]


        booking_data = {
            'package_name': booking.first().package.package,
            'camera_equipments': camera_equipments_data,
            'deliverables': deliverables_data,
            'production_process': production_process_data,
            'terms_conditions': terms_conditions_data
        }

        print(booking_data)

            

        # client = Client.objects.filter(id = id)
        if booking.exists():
          buffer = quotationGenerateFun(booking.first().user, discount,additional_price, booking, booking_data)
          print('buffer',buffer)
          response = FileResponse(buffer, content_type='application/pdf', as_attachment=True, filename=f'quotation.pdf')
        else:
            response = resFun(status.HTTP_400_BAD_REQUEST,'booking not found',[])
        return response


        # response = quotationGenerateFun(id)
        # buffer = BytesIO()

        # pdf_canvas = canvas.Canvas(buffer, pagesize=letter)
        # pdf_canvas.setFillColorRGB(255/255, 255/255, 230/255)  # Yellow background
        # pdf_canvas.rect(0, 0, letter[0], letter[1], fill=True)

        # # ... (Add more drawing and content to the PDF)

        # # Save the canvas to BytesIO
        # pdf_canvas.save()

        # # Move the BytesIO cursor to the beginning
        # buffer.seek(0)

        # return FileResponse(buffer, content_type='application/pdf', as_attachment=True, filename=f'quotation.pdf')


        # Return the BytesIO object
        # return buffer
        
        # return response
    

class SaveQuotation(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SaveQuotationSerializer
    def post(self, request, id, format=None, *args, **kwargs):
        # try:
            # client = Client.objects.filter(id=id)
            try:
                booking = Booking.objects.get(id=id)
            except:
                booking = None

            if booking != None:

                if not isinstance(request.data.get('discount'), int):
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'discount should be integer value',[])
                    return res
                    
                # print('booking',booking)
                booking.discount = request.data.get('discount')
                booking.save()
                res = resFun(status.HTTP_200_OK, 'save successfully',[])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'invalid user', [])
            return res
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])


class EmailQuotation(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = GenerateQuotationSerializer
    def post(self, request, id,discount, format=None, *args, **kwargs):


        # client = Client.objects.filter(id=id)
        booking = Booking.objects.filter(id=id)
        if booking.exists():

            serializer = UpdateDiscountSerializer(booking.first(), data={'discount': discount}, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'discount not valid', [])
                return res

            additional_price=0

            for d in booking.first().shoot_date.all():
                for e in d.additional_service.all():
                    additional_price += int(e.additional_service.price*e.count)
                    # print(int(e.additional_service.price*e.count))

            # print('Additional Price',additional_price)


            # customer_name = 'Kashi'
            # customer_email = 'Kashi@kashi.com'
            # items = [ {'name' : 1,'description' : 2,'price' : 3,'quantity' : 4,'total' : 5}, {'name' : 1,'description' : 2,'price' : 3,'quantity' : 4,'total' : 5}]
            # total_amount = 400

            
            
            # for item in items:
            #     item['total'] = item['price'] * item['quantity']

            camera_equipments = [int(c) for c in request.data.get('camera_equipments')]
            camera_equipments_data = []
            for c in camera_equipments:
                for ce in CameraEquipments.objects.filter(id=c, trash=False):
                    camera_equipments_data.append(ce.title)

            deliverables = [int(c) for c in request.data.get('deliverables')]
            deliverables_data = []
            for c in deliverables:
                for ce in Deliverables.objects.filter(id=c, trash=False):
                    deliverables_data.append(ce.title)

            production_process = [int(c) for c in request.data.get('production_process')]
            production_process_data = []
            for c in production_process:
                for ce in ProductionProcess.objects.filter(id=c, trash=False):
                    production_process_data.append(ce.title)

            terms_conditions = [int(c) for c in request.data.get('terms_conditions')]
            terms_conditions_data = []
            for c in terms_conditions:
                for ce in Terms_Conditions.objects.filter(id=c, trash=False):
                    terms_conditions_data.append(ce.title)


            # booking_data = [ {'date': b.date, 'services': [ {'count': ads.count, 'service_name': ads.additional_service.service_name} for ads in b.additional_service.all()] } for b in booking.first().shoot_date.all()]

            booking_data = {
                'package_name': booking.first().package.package,
                'camera_equipments': camera_equipments_data,
                'deliverables': deliverables_data,
                'production_process': production_process_data,
                'terms_conditions': terms_conditions_data
            }

            # html_string = render_to_string('quotation_template.html', context)
            # buffer = BytesIO()
            # pisa_status = pisa.CreatePDF(html_string, dest=buffer)

            # if pisa_status.err:
                # return resFun(status.HTTP_200_OK, 'quotation pdf not generated',[])
                # return HttpResponse('We had some errors <pre>' + html_string + '</pre>')

            # buffer.seek(0)
            
            buffer = quotationGenerateFun(booking.first().user, discount, additional_price, booking, booking_data)

            if buffer:
                message = canned_email.objects.get(email_type = 'send_quotation_email')
                message = message.email
                message = str(message).replace("{{{link}}}", f'<a href="http://127.0.0.1:8000/client-info-confirm-booking/{booking.first().id}/{booking.first().user.client_token}"><button>Confirm Booking</button></a>')
                message = message.replace("{{{client}}}", f"{booking.first().user.user.name}")

                subject = 'Quotation for booking with Jrs studios'
                from_email = 'akshatnigamcfl@gmail.com'
                recipient_list = [booking.first().user.user.email]
                text = 'email sent from MyDjango'

                email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
                email.attach_alternative(message, 'text/html')
                email.attach(f'{booking.first().user.user.name}', buffer.read(), 'application/pdf')
                email.send()

                res = resFun(status.HTTP_200_OK, 'quotation sent via email',[])
            else:
                res = resFun(status.HTTP_200_OK, 'quotation pdf not generated',[])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'Email not sent',[])
        return res







class getQuotationInfo(GenericAPIView):
    serializer_class = GetQuotationInfoSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, bookingId):
        # try:

        try:
            booking_instance = Booking.objects.get(id=bookingId)
            print('booking_instance', booking_instance.package)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'booking not found', [])
        
        additionalPrice = 0
        additionals =  []
        for d in booking_instance.shoot_date.all():
            service_list = []
            for e in d.additional_service.all():
                service_list.append({ 'service':f'{e.count} - {e.additional_service}', 'price': e.additional_service.price*e.count })
                # additionals.append({ 'date': d.date.strftime('%d-%m-%Y') , 'services': { 'service':f'{e.count} - {e.additional_service}', 'price': e.additional_service.price*e.count } })
                additionalPrice += e.additional_service.price*e.count
            
            additionals.append({'date': d.date.strftime('%d-%m-%Y'), 'services': service_list })
            
        #         print(type(e.additional_service.price) , type(e.count))
                # [
                #     {% for d in data.first.shoot_date.all %}
                #       {% for e in d.additional_service.all %}
                #         Number({{ e.additional_service.price|multiply:e.count }}),
                #       {% endfor %}
                #     {% endfor %}
                #   ];
                #   selected_additionals_price.innerText = numberWithCommas(additional_price.reduce((a, b) => a + b));
        print('((((((()))))))', additionalPrice)
        deliverables = []
        selected_deliverables = booking_instance.package.deliverables.values_list('id', flat=True)
        for d in Deliverables.objects.all():
            print(d, d.id in selected_deliverables)
            deliverables.append( { 'id': d.id ,'value': d.title,'selected': d.id in selected_deliverables } )


        data = { 
            'package_info': [{'key': 'package', 'value': booking_instance.package.package }],
            'pricing_info': [ 
                {'key': 'package_price', 'value': booking_instance.package.price },
                {'key': 'additionals', 'value': additionalPrice },
                {'key': 'discount', 'value': booking_instance.discount },
                {'key': 'total_price', 'value': (booking_instance.package.price + additionalPrice) - booking_instance.discount },
                  ],
            'additional' : additionals,
            'camera_equipment_details': [ { 'id': c.id , 'value': c.title } for c in CameraEquipments.objects.all() ],
            'production_process': [  { 'id': c.id , 'value': c.title } for c in ProductionProcess.objects.all() ],
            'deliverables': deliverables ,
            'terms_condition':  [ { 'id': c.id , 'value': c.title } for c in Terms_Conditions.objects.all() ]
            }
        
        for d in additionals:
            print('***',d)
        
        serializer = GetQuotationInfoSerializer(data=data, many=False)
        if serializer.is_valid():
            return resFun(status.HTTP_200_OK, 'request success', serializer.data )
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])






class ConsoleDashboard(GenericAPIView):
    permission_classes =[IsAuthenticated]
    # authentication_classes = [IgnoreBearerTokenAuthentication]
    serializer_class = ConsoleDashboardSerializer
    def post(self,request,format=None, *args, **kwargs):

        try:
            total_payment = 0
            total_payment_list = []
            payment_received_list = []
            booking_list = []
            booking_list_sorted = []
            booking_data = 0
            
            today = datetime.today().date()
            current_month = datetime.now().month
            current_year = datetime.now().year

            if request.data.get('date_selector') == 'today':
                shoot_date = Booking_ShootDate.objects.filter(date__gte=today).order_by('date')
                client = Client.objects.filter(user__created_at__date=today)
                pre_wedding = Pre_Wedding.objects.filter(created_at=today)
                wedding = Wedding.objects.filter(created_at=today)
                events = Events.objects.filter(created_at=today)
                reels = Reels.objects.filter(created_at=today)
                payment_received_obj = Payments.objects.filter(date=today)

            elif request.data.get('date_selector') == 'this_month':
                shoot_date = Booking_ShootDate.objects.filter(date__month=current_month).order_by('date')
                client = Client.objects.filter(user__created_at__month=current_month,user__created_at__year=current_year)
                pre_wedding = Pre_Wedding.objects.filter(created_at__month=current_month,created_at__year=current_year)
                wedding = Wedding.objects.filter(created_at__month=current_month,created_at__year=current_year)
                events = Events.objects.filter(created_at__month=current_month,created_at__year=current_year)
                reels = Reels.objects.filter(created_at__month=current_month,created_at__year=current_year)
                payment_received_obj = Payments.objects.filter(date__month=current_month)

            elif request.data.get('date_selector') == 'this_year':
                shoot_date = Booking_ShootDate.objects.filter(date__year=current_year).order_by('date')
                client = Client.objects.filter(user__created_at__year=current_year)
                pre_wedding = Pre_Wedding.objects.filter(created_at__year=current_year)
                wedding = Wedding.objects.filter(created_at__year=current_year)
                events = Events.objects.filter(created_at__year=current_year)
                reels = Reels.objects.filter(created_at__year=current_year)
                payment_received_obj = Payments.objects.filter(date__year=current_year)


            if shoot_date.exists():
                # data = []
                # for s in shoot_date:
                #     booking = Booking.objects.filter(shoot_date=s.id, booking_status__title='confirmed').first()
                #     data.append({'date': s.date, 'data': 'booking'})

                # print('data')
                # for b in booking:
                    # print('b',b.shoot_date.all())
                # p = Paginator(booking, limit)
                # pages = p.page(page)
                # context = {'pages': pages, 'current_page': page}

                pending_payment = 0
                payment_received = 0
                pending_payment_list = []

                if request.data.get('date_selector') == 'today':
                    booking = Booking.objects.filter(shoot_date__date = today, booking_status__title='confirmed').distinct()
                elif request.data.get('date_selector') == 'this_month':
                    booking = Booking.objects.filter(shoot_date__date__month=current_month,shoot_date__date__year=current_year, booking_status__title='confirmed').distinct()
                elif request.data.get('date_selector') == 'this_year':
                    booking = Booking.objects.filter(shoot_date__date__year=current_year, booking_status__title='confirmed').distinct()



                if booking.exists():
                    for b in booking:
                        total_payment += (b.package.price - b.discount)
                        additional_price = b.shoot_date.all()
                        # shoot_date_data =[]
                        for a in additional_price:
                            requirements = []
                            for c in a.additional_service.all():
                                total_payment += (c.count * c.additional_service.price)
                                requirements.append(f'{c.count} - {c}')
                            
                            booking_list.append({ 'client_id': b.id, 'shoot_date_id' : a.id, 'client_name': b.user.user.name, 'event_type': b.package.segment.segment , 'date': a.date.strftime('%d-%m-%Y'), 'requirements': requirements })

                        # booking_data['date'] = a.date
                        # booking_data['event type'] = b.package.segment.segment
                        # booking_data['requirement'] = f'{c.count} - {c}'

                        print('booking_data', booking_list)

                    booking_list_sorted = sorted(booking_list, key=lambda x: datetime.strptime(x['date'], '%d-%m-%Y' ) )

                        # payment = Payments.objects.filter(user=b.user.id)
                        # for p in payment:
                        #     pending_payment += p.amount

                        # total_payment_list.append({'name': '', 'amount': total_payment, 
                                                #    'pending_payment': total_payment-pending_payment
                                                #    })
                        # pending_payment_list.append({'name':b, 'amount': pending_payment})

                        # total_payment = 0
                        # pending_payment= 0

                    # booking = booking.values()

                # else:
                    # payment = Payments.objects.filter(date=today)
                    # print('payment',payment)
                    # for p in payment:
                    #     pending_payment += p.amount

                total_payment_list.append({'name': '', 'amount': total_payment, 'payment_received': [ p.amount for p in payment_received_obj] })
                for p in payment_received_obj:
                    payment_received_list.append(p.amount)   
                # payment_received_list = [ p.amount for p in payment_received_obj]

                booking_data = booking.count()
            
            data = { 'payment': {'total_payment': total_payment_list, 'payment_received': [ p.amount for p in payment_received_obj], 'booking': booking_data, 'client': client.count(), 'pre_wedding': pre_wedding.count(), 'wedding': wedding.count(), 'events': events.count(), 'reels': reels.count()}, 'booking': booking_list_sorted }
            return resFun(status.HTTP_200_OK, 'request successful',data)
        except:
                return resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])



# class GenerateQuotation(GenericAPIView):
#     permission_classes=[IsAuthenticated]
#     serializer_class = GenerateQuotationSerializer
#     parser_classes = [MultiPartParser, FormParser]
#     def get(self, request, id, format=None, *args, **kwargs):
#         # pass

#         client = Client.objects.filter(id = id)
#         if client.exists():

#             template = get_template('console-layout/quotation.html')
#             context = {
#                 'name': 'Akshat Nigam',
#                 'booking': [{'date':'27/09/2024', 'additionals': ['additional service 1', 'additional service 2', 'additional service 3']}, {'date':'28/09/2024', 'additionals': ['additional service 3', 'additional service 4', 'additional service 5']}],
#                 "equipments": ['Sony a7s3', 'Sony Mark 4', 'SONY A7R iii', 'SONY a7c', 'Sony MARK 3', 'ALL SONY G MASTER LENSES',
#                                'DRONE', 'GIMBAL', 'LIGHTS', 'TRIPODS','MONOPODS'],
#                 "production_process": ['Production(Executing Shoot)', 'Finalization of Video (Post Production)'],
#                 "what_you_get": ['3-4 Wedding Reels for social media post.','1 cinematic teaser ( 60-90 seconds )','Wedding Film (5-6 minutes)','All photographs will be delivered in the digital soft copies.','300 Edited photographs','Algo al app for Photo sharing (Kwicpic)','4-5 hours video will be delivered  in MP4 Format with the resolution of Full HD 1920x1080 pixels.'],
#                 "terms_conditions": [
#                     "All digital data of photos including Candid's and traditional photographs will be delivered in one week.", "For finalising the deal, you must pay us 50%  booking amount for the shoot.", "35% when we deliver you the soft copies of the work.", "Rest 15% after the completion of the whole work."]
#             }
#             html = template.render(context)
#             res = BytesIO()
#             result = pisa.CreatePDF(html, dest=res)
#             if result.err:
#                 return Response({
#                     'status': status.HTTP_400_BAD_REQUEST,
#                     'error': 'error generating pdf',
#                     'data': []
#                     })
#             res.seek(0)
#             return FileResponse(res, content_type='application/pdf', as_attachment=True, filename=f'{client.first().name}.pdf')
#         else:
#             res = Response()
#             res.status_code = status.HTTP_400_BAD_REQUEST
#             res.data = {
#                 'status': status.HTTP_400_BAD_REQUEST,
#                 'data':[],
#                 'message':'client id invalid',
#             }
#             return res

#         # try:
#         # dynamic_data = {
#         #     'name': 'Akshat Nigam'
#         #     # 'booking': [{'date':'27/09/2024', 'additionals': ['additional service 1', 'additional service 2', 'additional service 3']}, {'date':'28/09/2024', 'additionals': ['additional service 3', 'additional service 4', 'additional service 5']}]
#         # }
#         # html_content = render_to_string('console-layout/quotation.html', {'dynamic_data': dynamic_data})
#         # config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
#         # pdf_bytes = pdfkit.from_string(html_content, False, configuration=config)
#         # print(pdf_bytes)
#         # # res = resFun(status.HTTP_200_OK,'wrking',[])
#         # # return res
#         # print(html_content)
#         # res = BytesIO()
#         # result = pisa.CreatePDF(html_content, dest=res)
#         # #     if result.err:
#         # #         return Response({
#         # #             'status': status.HTTP_400_BAD_REQUEST,
#         # #             'error': 'error generating pdf',
#         # #             'data': []
#         # #             })
#         # client = Client.objects.filter(id=id)
#         # res.seek(0)
#         # return FileResponse(res, content_type='application/pdf', as_attachment=True, filename=f'{client.first().name}.pdf')

#             # with BytesIO(pdf_bytes) as pdf_io:
            
#             #     pdf_io.seek(0)


#             #     if client.exists():
#             #         if pdf_io:
#             #             res = FileResponse(pdf_io, content_type='application/pdf', as_attachment=True, filename=f'{client.first().name}.pdf')
#             #         else:
#             #             print("Error: pdf_io object is not available")
#             #             res = None

#         # except Exception as e:
#         #     print(f"An error occurred: {e}")
#         #     res = None

#         # finally:
#         #     if pdf_io:
#         #         pdf_io.close()

#         # return res
        
        


class GetSegmentServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SegmentSerializer
    def get(self, request, format=None, *args, **kwargs):
        try:
            segment = Segment.objects.all()  
        except:
            segment = Segment.objects.filter(pk__in=[])  

        if segment.exists():
            serializer = SegmentSerializer(data=list(segment.values()), many=True)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK, 'request successful', serializer.data )
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'no data found', [] )
        return res
    


class getSegmentPackageList(GenericAPIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = getSegmentPackageListSerializer
    def get(self, request):
        # print('request', request)
        try:
            segment = Segment.objects.all()  
        except:
            segment = Segment.objects.filter(pk__in=[])

        data = []
        for s in segment:
            package = Package.objects.filter(segment = s.id)
            data.append({ 
                'segment': {'id': s.id, 'value': s.segment}, 
                'package': [ {'id': int(p.id) ,'value': p.package, 'price': int(p.price), 'segment': str(p.segment),'deliverables': [{ 'id':s.id, 'title': str(s.title)} for s in p.deliverables.all()], 'booked_package': {}} for p in package] } )
            

        if segment.exists():
            serializer = getSegmentPackageListSerializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK, 'request successful', serializer.data )
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'no data found', [] )
        return res


class getServiceList(GenericAPIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = getServiceListSerializer
    def get(self, request):
        try:
            segment = Segment.objects.all()  
        except:
            segment = Segment.objects.filter(pk__in=[])

        data = []
        for s in segment:
            package = Service.objects.filter(segment = s.id)
            data.append({ 
                'segment': {'id': s.id, 'value': s.segment}, 
                'service': [ {'id': int(p.id), 'segment': p.segment.segment ,'service_name': p.service_name, 'trash': p.trash } for p in package] } )
            
        if segment.exists():
            serializer = getServiceListSerializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK, 'request successful', serializer.data )
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'no data found', [] )
        return res



class getAdditionalServiceList(GenericAPIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = getAdditionalServiceListSerializer
    def get(self, request):
        try:
            segment = Segment.objects.all()  
        except:
            segment = Segment.objects.filter(pk__in=[])

        data = []
        for s in segment:
            package = AdditionalService.objects.filter(segment = s.id)
            data.append({ 
                'segment': {'id': s.id, 'value': s.segment}, 
                'additional_service': [ {'id': int(p.id), 'segment': p.segment.segment, 'service_name': p.service_name, 'trash': p.trash, 'price': p.price } for p in package] } )

            
        if segment.exists():
            serializer = getAdditionalServiceListSerializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK, 'request successful', serializer.data )
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'no data found', [] )
        return res



class getPackageSectionList(GenericAPIView):
    permission_classes = [IsAuthenticated]
    # serializer_class = getPackageSectionListSerializer
    def get(self, request, atr):

        print('atr', atr)

        if atr == 'camera_equipments':
            data = CameraEquipments.objects.all()
        elif atr == 'production_process':
            data = ProductionProcess.objects.all()
        elif atr == 'deliverables':
            data = Deliverables.objects.all()
        elif atr == 'terms_&_conditions':
            data = Terms_Conditions.objects.all()

        if data.exists():
            serializer = getPackageSectionListSerializer(data=list(data.values()), many=True )
            if serializer.is_valid():
                return resFun(status.HTTP_200_OK, 'request successful', serializer.data )
            else:
                return resFun(status.HTTP_204_NO_CONTENT, 'no data', serializer.errors )
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])




class AddServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddServiceSerializer
    def post(self, request, format=None, *args, **kwargs):

        res = Response()        
        serializer = AddServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        res.status_code = status.HTTP_200_OK
        res.data = {
            'status': status.HTTP_200_OK,
            'message': 'successfully added',
            'data': [],
        }

        return res
    

class TrashServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddServiceSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        print('((()))', id)

        res = Response()
        try:
            service = Service.objects.get(id = id, trash=False)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'service not found', [] )
             
            # service = Service.objects.filter(pk__in=[])

        print('service',service)
        
        # if service.exists():

        serializer = AddServiceSerializer(service, data={'trash':True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        res = resFun(status.HTTP_200_OK, 'moved to trash', serializer.data )
        # else:
            # res = resFun(status.HTTP_400_BAD_REQUEST, 'service not found', [] )
        
        return res
    

class RestoreServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddServiceSerializer
    def delete(self, request, id, format=None, *args, **kwargs):

        res = Response()
        try:
            service = Service.objects.get(id = id, trash=True)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'service not found', [] )
             
            # service = Service.objects.filter(pk__in=[])

        print('service',service)
        
        # if service.exists():

        serializer = AddServiceSerializer(service, data={'trash':False}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        res = resFun(status.HTTP_200_OK, 'restored successfully', serializer.data )
        # else:
            # res = resFun(status.HTTP_400_BAD_REQUEST, 'service not found', [] )
        
        return res


class GetServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetServiceSerializer
    def get(self, request, id, format=None, *args, **kwargs ):
        try:
            service = Service.objects.filter(id=id)
        except:
            service = Service.objects.filter(pk__in=[])

        res = Response()
        if service.exists():

            serializer = GetServiceSerializer(data={'service_name': service.first().service_name, 'segment': { 'id': service.first().segment.id, 'segment': service.first().segment.segment}, 'trash': service.first().trash}, many=False)
            serializer.is_valid(raise_exception=True)

            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'request successful',
                'data': serializer.data,
            }
        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'service not found',
                'data': [],
            }
        return res
    

class UpdateServicesAdmin(GenericAPIView):
    serializer_class = AddServiceSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, id, format=None, *args, **kwargs):
        print('working here', request.data)
        try:
            service_CH = Service.objects.filter(service_name=request.data.get('service_name'))
            if service_CH.first().id == id:
                service_CH=Service.objects.filter(pk__in=[])
                # return resFun(status.HTTP_400_BAD_REQUEST,'something went wrong', [])
        except:
            service_CH = Service.objects.filter(pk__in=[])
            # return resFun(status.HTTP_400_BAD_REQUEST,'something went wrong', [])


        if not service_CH.exists():
            try:
                service = Service.objects.filter(id=id)
                print(service)
            except:
                service = Service.objects.filter(pk__in=[])
            # print('service', service)
            if service.exists():
                print('***' ,service)
                
                serializer = AddServiceSerializer(service.first(), data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return resFun(status.HTTP_200_OK,'updated successfully', serializer.data)
                else:
                    print('error', serializer.errors)
                    return resFun(status.HTTP_400_BAD_REQUEST,'request failed', serializer.errors)

            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'no service found', [])
            # return res
        
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'service name already exist', [])
        
        return res






class AddAdditionalServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddAdditionalServiceSerializer
    def post(self, request, format=None, *args, **kwargs):
        res = Response()        
        serializer = AddAdditionalServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        res.status_code = status.HTTP_200_OK
        res.data = {
            'status': status.HTTP_200_OK,
            'message': 'successfully added',
            'data': [],
        }

        return res


class GetAdditionalServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetAdditionalServiceSerializer
    def get(self, request, id, format=None, *args, **kwargs):
        try:
            service = AdditionalService.objects.filter(id=id)
        except:
            service = AdditionalService.objects.filter(pk__in=[])

        res = Response()
        if service.exists():

            serializer = GetAdditionalServiceSerializer(data={'service_name': service.first().service_name, 'price': service.first().price,  'segment': { 'id': service.first().segment.id, 'segment': service.first().segment.segment}, 'trash': service.first().trash}, many=False)


            serializer.is_valid(raise_exception=True)
            print('serializer',serializer.data)

            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'request successful',
                'data': serializer.data,
            }
        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'service not found',
                'data': [],
            }
        return res


class UpdateAdditionalServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddAdditionalServiceSerializer
    def put(self, request, id, format=None, *args, **kwargs):
        print('request.data',request.data)
        try:
            service_CH = AdditionalService.objects.filter(service_name=request.data.get('service_name'))
            if service_CH.first().id == id:
                service_CH=AdditionalService.objects.filter(pk__in=[])
        except:
            service_CH = AdditionalService.objects.filter(pk__in=[])

        print('service_CH', service_CH)

        if not service_CH.exists():
            try:
                service = AdditionalService.objects.filter(id=id)
                print(service)
            except:
                # service = AdditionalService.objects.filter(pk__in=[])
                return resFun(status.HTTP_400_BAD_REQUEST,'no service found', [])

            # print('service', service)
            # if service.exists():
            serializer = AddAdditionalServiceSerializer(service.first(), data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                res = resFun(status.HTTP_200_OK,'updated successfully', serializer.data)
            else:
                print('serializer.errors', serializer.errors)
                return resFun(status.HTTP_400_BAD_REQUEST,'something went wrong', serializer.errors)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'service name already exist', [])
        
        return res


class TrashAdditionalServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddAdditionalServiceSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        try:
            service = AdditionalService.objects.filter(id = id, trash=False)
        except:
            service = AdditionalService.objects.filter(pk__in=[])

        
        if service.exists():
            serializer = AddServiceSerializer(service.first(), data={'trash':True}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return resFun(status.HTTP_200_OK, 'moved to trash', serializer.data)
        else:
            return resFun(status.HTTP_400_BAD_REQUEST,'service not found',[] )


class RestoreAdditionalServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddAdditionalServiceSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        try:
            service = AdditionalService.objects.filter(id = id, trash=True)
        except:
            service = AdditionalService.objects.filter(pk__in=[])


        print('service',service)
        
        if service.exists():
            serializer = AddServiceSerializer(service.first(), data={'trash':False}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return resFun(status.HTTP_200_OK, 'restored successfully', serializer.data)
        else:
            return resFun(status.HTTP_400_BAD_REQUEST,'service not found',[] )
    

class AddPackageAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddPackageSerializer
    def post(self, request, format=None, *args, **kwargs):
        print(request.data)
        try:            
            package = Package.objects.filter(package=request.data.get('package').lower(),segment = request.data.get('segment'))
            if package.exists():
                return resFun(status.HTTP_400_BAD_REQUEST, 'package name already exists' ,[])
            
            serializer = AddPackageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return resFun(status.HTTP_200_OK, 'package created',[])
            else:
                print(serializer.errors)
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong',serializer.errors)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed' ,[])


class GetPackageAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetPackageSerializer
    def get(self, request, id, format=None, *args, **kwargs):

        try:
            package = Package.objects.filter(id=id)
        except:
            package = Package.objects.filter(pk__in=[])

        if package.exists():
            serializer = GetPackageSerializer(data={'id': int(package.first().id) ,'package': package.first().package, 'price': int(package.first().price), 'segment': str(package.first().segment),'deliverables': [s.id for s in package.first().deliverables.all()], 'booked_package': {}}, many=False)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK, 'request successful', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])


        # serializer = GetPackageSerializer(data=)
        return res
    
class GetAllPackageAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetPackageSerializer
    def get(self, request, id, format=None,*args, **kwargs):
        try:
            package = Package.objects.filter(segment=id)
        except:
            package = Package.objects.filter(pk__in=[])

        print('package',package)

        if package.exists():
            data = []
            for p in package:
                data.append({'id': int(p.id) ,'package': p.package, 'price': int(p.price), 'segment': str(p.segment),'deliverables': [str(s.title) for s in p.deliverables.all()], 'booked_package': {}})
            serializer = GetPackageSerializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK, 'request successful', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'package not found', [])
        return res
    

class UpdatePackageAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddPackageSerializer
    def put(self, request, id,format=None, *args, **kwargs):

        # print('request.data',request.data)

        # try:
        #     package = Package.objects.filter(package = request.data.get('package').lower(),segment = request.data.get('segment'))
        #     if package.exists():
        #         if not int(package.first().id) == int(id):
        #             res = resFun(status.HTTP_400_BAD_REQUEST, 'package name already exists', [])
        #             return res
        # except:
        #     pass

        try:
            package = Package.objects.filter(id=id)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'package not found', [])

        # package = Package.objects.filter(pk__in=[])
        serializer = AddPackageSerializer(package.first(), data=request.data, many=False)
        if serializer.is_valid():
            serializer.save()
            # print(serializer.data)
            # serializer.update(package.first(), serializer['validated_data'])
            return resFun(status.HTTP_200_OK, 'package updated successfully', [])
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'package not found', serializer.errors)

        



# class AddHomeBannerVideoAdmin(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = HomeBannerVideoSerializer
#     def post(self, request, format=None, *args, **kwargs):
#         print(request.data)

#         serializer = HomeBannerVideoSerializer(data=request.data, many=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         res = resFun(status.HTTP_200_OK, 'Banner Video Saved', serializer.data)
#         return res
    

class AddHomeBannerVideoAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = BannerVideo_form
    def post(self, request, format=None, *args, **kwargs):
            # print(request.POST)
            # print(request.FILES)
        # try:
            file = request.FILES
            res = Response()

            if file:
                if request.FILES.get('file'):
            # if file:
            #     if request.FILES.get('file'):

                    if  'video' in request.FILES.get('file').content_type:
                        pass
                    elif 'mp4' in str(request.FILES.get('file') ) :
                        pass
                    else:
                        print('video error')
                        return resFun(status.HTTP_400_BAD_REQUEST, 'video format not supported', [] )

                    # if not 'video' in request.FILES.get('file').content_type:
                    #     res = resFun(status.HTTP_400_BAD_REQUEST, 'video format not supported',[])
                    #     return res

                    upload = BannerVideo_form(request.POST, request.FILES)
                    if upload.is_valid():
                        upload.save()
                        res = resFun(status.HTTP_200_OK, 'Banner video upload successful',[])
                    else:
                        print('video error 1', upload.errors)

                        res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])
                else:
                    print('video error 2')

                    res = resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported',[])
                return res
            



class GetHomeBannerVideoAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HomeBannerVideoSerializer
    def get(self, request, format=None, *args, **kwargs):
        res = Response()
        if request.user.is_admin:
            banner_INST = Banner_video.objects.all()
            if banner_INST .exists():
                # print('banner_INST',[ {'id': b.id, 'title': b.title, 'file': b.file.url}  for b in banner_INST])
                serializer = HomeBannerVideoSerializer(data = [ {'id': b.id, 'title': b.title, 'file': str(b.file)}  for b in banner_INST], many=True)
                if serializer.is_valid():
                    print('serializer.data', serializer.data)
                    return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
                else:
                    print('error', serializer.errors)

                    return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', serializer.errors)
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
        else:
            res = resFun(status.HTTP_401_UNAUTHORIZED, 'you are not authorized to delete this data', [])
        return res
    

class DeleteHomeBannerVideoAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BannerVideo_form
    def delete(self, request, id, format=None, *args, **kwargs):
        res = Response()
        if request.user.is_admin:
            del_INST = Banner_video.objects.filter(id = id)
            if del_INST.exists():
                file_location = del_INST.first()
                print('file_location.file',file_location.file)
                if os.path.exists('media/'+str(file_location.file)):
                        os.remove('media/'+str(file_location.file))
                        del_INST.delete()

                        res = resFun(status.HTTP_200_OK, 'deleted successfully', [])
                else:
                    res = resFun(status.HTTP_404_NOT_FOUND, 'file not found', [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
        else:
            res = resFun(status.HTTP_401_UNAUTHORIZED, 'you are not authorized to delete this data', [])
        return res

                
            # if upload:
        # except:
        #     print('not uploaded')
        
    

class AddShowcaseImageAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = Showcase_form
    def post(self, request, format=None, *args, **kwargs):
            file = request.FILES
            res = Response()
            if file:
                if request.FILES.get('file'):
                    if not 'image' in request.FILES.get('file').content_type:
                        res = resFun(status.HTTP_400_BAD_REQUEST, 'image format not supported',[])
                        return res
                    upload = Showcase_form(request.POST, request.FILES)
                    if upload.is_valid():
                        upload.save()
                        res = resFun(status.HTTP_200_OK, 'wedding upload successfully',[])
                        print('this workings')
                    else:
                        res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported',[])
                return res
            

class DeleteShowcaseImageAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Showcase_form
    def delete(self, request, id, format=None, *args, **kwargs):
        res = Response()
        if request.user.is_admin:
            del_INST = Showcase_images.objects.filter(id = id)
            if del_INST.exists():
                file_location = del_INST.first()
                print('file_location.file',file_location.file)
                if os.path.exists('media/'+str(file_location.file)):
                        os.remove('media/'+str(file_location.file))
                        del_INST.delete()

                        res = resFun(status.HTTP_200_OK, 'deleted successfully', [])
                else:
                    res = resFun(status.HTTP_404_NOT_FOUND, 'file not found', [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
        else:
            res = resFun(status.HTTP_401_UNAUTHORIZED, 'you are not authorized to delete this data', [])
        return res



class getClient(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = getClientSerializer
    def get(self, request, limit, page, format=None, *args, **kwargs):
        # res = Response()
        # try:
        print(request.user.is_admin)

        if request.user.is_admin:
            offset = (page-1)*limit
            client_instance = Client.objects.all().order_by(F('user__created_at'))[offset:offset+limit]
            data = []
            for c in client_instance:
                data.append({
                    'id': c.id,
                    'user_id': c.user.id,
                    'client_name': c.user.name,
                    'email': c.user.email,
                    'contact_number': c.user.contact_number,
                    'profile_picture': c.user.profile_picture.url,
                    })
                
            total_pages = math.ceil(Client.objects.count()/limit)
                
            serializer = getClientSerializer(data=data, many=True)
            if serializer.is_valid():

                print('serializer.data',serializer.data)
                
                res = resFun(status.HTTP_200_OK, 'request successful', {'data': serializer.data, 'current_page': page, 'total_pages': total_pages })
            else :
                print(serializer.errors)
                res = resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])
        else:
            res = resFun(status.HTTP_401_UNAUTHORIZED, 'you are not authorized to delete this data', [])
        return res
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
            












class AddTeamMemberAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer
    def post(self, request, format=None, *args, **kwargs):

        form = TeamMemberSerializer(data=request.data,many=False)
        if form.is_valid():
            form.save()
                # print(form.instance)
                # print(form.validated_data)
                # form.instance.shoot_category.set = form.validated_data['shoot_category']
                # form.instance.save()
            res = resFun(status.HTTP_200_OK,'member saved successfully', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',form.errors)
        return res



class GetTeamMemberIndvAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer
    def get(self, request, id, format=None, *args, **kwargs):
        try:
            member = Team_member.objects.filter(id=id)
        except:
            member = Team_member.objects.filter(pk__in=[])

        data = member.values().first()
        data['skills'] =  [m.id for m in member.first().skills.all()]
        data['user'] =  {'name': member.first().user.name , 'contact_number': member.first().user.contact_number, 'email': member.first().user.email } 
        
        
        if member.exists():
            serializer = TeamMemberViewSerializer(data=data, many=False)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK,'request successful', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'team member not found', [])
        return res


class UpdateTeamMemberIndvAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer
    def put(self, request, id, format=None, *args, **kwargs):

        print(request.data)
        try:
            member = Team_member.objects.filter(id=id)
        except:
            member = Team_member.objects.filter(pk__in=[])

        if member.exists():
            print('request.POST', request.data)

            formData_custom_model = EditCustomModel(request.data, instance=member.first().user)
            if formData_custom_model.is_valid():
                formData_custom_model.save()
            else:
                print('formData_custom_model',formData_custom_model.errors) 

            serializer = TeamMemberSerializer(member.first(), data=request.data ,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK,'request successful', [])

            # else:
            #     res = resFun(status.HTTP_200_OK,'request failed', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'team member not found', [])
        return res


class DeleteTeamMemberIndvAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer
    def delete(self,request, id,format=None, *args, **kwargs):
        try:
            member = Team_member.objects.filter(id=id)
        except:
            member = Team_member.objects.filter(pk__in=[])

        if member.exists():
            member = member.first()
            member.trash = True
            member.save()
            res = resFun(status.HTTP_200_OK,'member moved to trash', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'team member not found', [])
        return res
        






class GetCameraEquipmentsAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetCameraEquipmentsSerializer
    def get(self, request, id, format=None, *args, **kwargs):
        try:
            cameraEquipments = CameraEquipments.objects.filter(id=id)
        except:
            cameraEquipments = CameraEquipments.objects.filter(pk__in=[])

        res = Response()
        if cameraEquipments.exists():

            serializer = GetCameraEquipmentsSerializer(data={'title': cameraEquipments.first().title, 'trash': cameraEquipments.first().trash}, many=False)
            serializer.is_valid(raise_exception=True)

            res = resFun(status.HTTP_200_OK,'request successful',serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'service not found',[])
        return res
    


class UpdateCameraEquipments(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetCameraEquipmentsSerializer
    def put(self, request, id, format=None, *args, **kwargs):
        try:
            cameraEquipments_CH = CameraEquipments.objects.filter(CameraEquipments_name=request.data.get('title').lower())
            if cameraEquipments_CH.first().id == id:
                cameraEquipments_CH=CameraEquipments.objects.filter(pk__in=[])
        except:
            cameraEquipments_CH = CameraEquipments.objects.filter(pk__in=[])

        if not cameraEquipments_CH.exists():
            try:
                cameraEquipments = CameraEquipments.objects.filter(id=id)
            except:
                cameraEquipments = CameraEquipments.objects.filter(pk__in=[])
            # print('CameraEquipments', CameraEquipments)   
            if cameraEquipments.exists():
                serializer = GetCameraEquipmentsSerializer(cameraEquipments.first(), data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    res = resFun(status.HTTP_200_OK,'updated successfully', serializer.data)
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors['title'] if serializer.errors['title'] else serializer.errors , [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'no camera equipments found', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'camera equipments name already exist', [])
        return res



class TrashCameraEquipmentsAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetCameraEquipmentsSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        try:
            cameraequipments = CameraEquipments.objects.filter(id = id, trash=False)
        except:
            cameraequipments = CameraEquipments.objects.filter(pk__in=[])

        
        if cameraequipments.exists():
            serializer = GetCameraEquipmentsSerializer(cameraequipments.first(), data={'trash':True}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'moved to trash', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'camera equipments not found', [])
        return res
    

class RestoreCameraEquipmentsAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetCameraEquipmentsSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        try:
            cameraequipments = CameraEquipments.objects.filter(id = id, trash=True)
        except:
            cameraequipments = CameraEquipments.objects.filter(pk__in=[])

        if cameraequipments.exists():
            serializer = GetCameraEquipmentsSerializer(cameraequipments.first(), data={'trash':False}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'restored successfully', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'camera equipments not found', [])
        return res


class AddCameraEquipmentsAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetCameraEquipmentsSerializer
    def post(self, request, format=None, *args, **kwargs):
        res = Response()        
        serializer = GetCameraEquipmentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'successfully added',[])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors,[])
        return res






class GetProductionProcessAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetProductionProcessSerializer
    def get(self, request, id, format=None, *args, **kwargs):
        try:
            productionProcess = ProductionProcess.objects.filter(id=id)
        except:
            productionProcess = ProductionProcess.objects.filter(pk__in=[])

        res = Response()
        if productionProcess.exists():
            serializer = GetProductionProcessSerializer(data={'title': productionProcess.first().title, 'trash': productionProcess.first().trash}, many=False)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK,'request successful',serializer.data)

        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'service not found',[])
        return res
    


class UpdateProductionProcess(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetProductionProcessSerializer
    def put(self, request, id, format=None, *args, **kwargs):
        try:
            productionProcess_CH = ProductionProcess.objects.filter(ProductionProcess_name=request.data.get('title').lower())
            if productionProcess_CH.first().id == id:
                productionProcess_CH=ProductionProcess.objects.filter(pk__in=[])
        except:
            productionProcess_CH = ProductionProcess.objects.filter(pk__in=[])

        if not productionProcess_CH.exists():
            try:
                productionProcess = ProductionProcess.objects.filter(id=id)
            except:
                productionProcess = ProductionProcess.objects.filter(pk__in=[])
            # print('ProductionProcess', ProductionProcess)
            if productionProcess.exists():
                serializer = GetProductionProcessSerializer(productionProcess.first(), data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    res = resFun(status.HTTP_200_OK,'updated successfully', serializer.data)
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors['title'] if serializer.errors['title'] else serializer.errors , [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'no ProductionProcess found', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'ProductionProcess name already exist', [])
        return res



class TrashProductionProcessAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetProductionProcessSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        try:
            productionProcess = ProductionProcess.objects.filter(id = id, trash=False)
        except:
            productionProcess = ProductionProcess.objects.filter(pk__in=[])

        
        if productionProcess.exists():
            serializer = GetProductionProcessSerializer(productionProcess.first(), data={'trash':True}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'moved to trash', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'ProductionProcess not found', [])
        return res
    

class RestoreProductionProcessAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetProductionProcessSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        try:
            productionProcess = ProductionProcess.objects.filter(id = id, trash=True)
        except:
            productionProcess = ProductionProcess.objects.filter(pk__in=[])

        
        if productionProcess.exists():
            serializer = GetProductionProcessSerializer(productionProcess.first(), data={'trash':False}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'restored successfully', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'ProductionProcess not found', [])
        return res
    


class AddProductionProcessAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetProductionProcessSerializer
    def post(self, request, format=None, *args, **kwargs):
        res = Response()        
        serializer = GetProductionProcessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'successfully added',[])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors,[])
        return res









class GetDeliverablesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetDeliverablesSerializer
    def get(self, request, id, format=None, *args, **kwargs):
        try:
            deliverables = Deliverables.objects.filter(id=id)
        except:
            deliverables = Deliverables.objects.filter(pk__in=[])

        res = Response()
        if deliverables.exists():

            serializer = GetDeliverablesSerializer(data={'title': deliverables.first().title, 'trash': deliverables.first().trash}, many=False)
            serializer.is_valid(raise_exception=True)

            res = resFun(status.HTTP_200_OK,'request successful',serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'service not found',[])
        return res
    

class GetDeliverables(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetDeliverablesSerializer
    def get(self, request):

        try:
            deliverables = Deliverables.objects.all()
        # except:
        #     # res = resFun(status)
        #     deliverables = Deliverables.objects.filter(pk__in=[])

            if deliverables.exists():
                serializer = GetAllDeliverablesSerializer(data=[{'id': d.id, 'title': d.title, 'trash': d.trash} for d in deliverables], many=True)
                serializer.is_valid(raise_exception=True)

                return resFun(status.HTTP_200_OK,'request successful',serializer.data)
            else:
                return resFun(status.HTTP_400_BAD_REQUEST,'service not found',[])
        except:
            return resFun(status.HTTP_400_BAD_REQUEST,'request failed',[])



class UpdateDeliverables(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetDeliverablesSerializer
    def put(self, request, id, format=None, *args, **kwargs):
        try:
            deliverables_CH = Deliverables.objects.filter(deliverables_name=request.data.get('title').lower())
            if deliverables_CH.first().id == id:
                deliverables_CH=Deliverables.objects.filter(pk__in=[])
        except:
            deliverables_CH = Deliverables.objects.filter(pk__in=[])

        if not deliverables_CH.exists():
            try:
                deliverables = Deliverables.objects.filter(id=id)
            except:
                deliverables = Deliverables.objects.filter(pk__in=[])
            # print('deliverables', deliverables)
            if deliverables.exists():
                serializer = GetDeliverablesSerializer(deliverables.first(), data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    res = resFun(status.HTTP_200_OK,'updated successfully', serializer.data)
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors['title'] if serializer.errors['title'] else serializer.errors , [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'no deliverables found', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'deliverables name already exist', [])
        return res



class TrashDeliverablesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetDeliverablesSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        try:
            deliverables = Deliverables.objects.filter(id = id, trash=False)
        except:
            deliverables = Deliverables.objects.filter(pk__in=[])

        
        if deliverables.exists():
            serializer = GetDeliverablesSerializer(deliverables.first(), data={'trash':True}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'moved to trash', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'deliverables not found', [])
        return res
    

class RestoreDeliverablesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetDeliverablesSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        try:
            deliverables = Deliverables.objects.filter(id = id, trash=True)
        except:
            deliverables = Deliverables.objects.filter(pk__in=[])

        
        if deliverables.exists():
            serializer = GetDeliverablesSerializer(deliverables.first(), data={'trash':False}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'restored successfully', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'deliverables not found', [])
        return res


class AddDeliverablesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetDeliverablesSerializer
    def post(self, request, format=None, *args, **kwargs):
        res = Response()        
        serializer = GetDeliverablesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'successfully added',[])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors,[])
        return res










class GetTermsConditionAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetTermsConditionSerializer
    def get(self, request, id, format=None, *args, **kwargs):
        try:
            terms_conditions = Terms_Conditions.objects.filter(id=id)
        except:
            terms_conditions = Terms_Conditions.objects.filter(pk__in=[])

        res = Response()
        if terms_conditions.exists():

            serializer = GetTermsConditionSerializer(data={'title': terms_conditions.first().title, 'trash': terms_conditions.first().trash}, many=False)
            serializer.is_valid(raise_exception=True)

            res = resFun(status.HTTP_200_OK,'request successful',serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'service not found',[])
        return res
    


class UpdateTermsCondition(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetTermsConditionSerializer
    def put(self, request, id, format=None, *args, **kwargs):
        try:
            terms_conditions_CH = Terms_Conditions.objects.filter(terms_conditions_name=request.data.get('title').lower())
            if terms_conditions_CH.first().id == id:
                terms_conditions_CH=Terms_Conditions.objects.filter(pk__in=[])
        except:
            terms_conditions_CH = Terms_Conditions.objects.filter(pk__in=[])

        if not terms_conditions_CH.exists():
            try:
                terms_conditions = Terms_Conditions.objects.filter(id=id)
            except:
                terms_conditions = Terms_Conditions.objects.filter(pk__in=[])
            # print('terms_conditions', terms_conditions)
            if terms_conditions.exists():
                serializer = GetTermsConditionSerializer(terms_conditions.first(), data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    res = resFun(status.HTTP_200_OK,'updated successfully', serializer.data)
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors['title'] if serializer.errors['title'] else serializer.errors , [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'no terms_conditions found', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'terms conditions name already exist', [])
        return res



class TrashTermsConditionAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetTermsConditionSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        print(request.headers)
        try:
            terms_conditions = Terms_Conditions.objects.filter(id = id, trash=False)
        except:
            terms_conditions = Terms_Conditions.objects.filter(pk__in=[])

        if terms_conditions.exists():
            serializer = GetTermsConditionSerializer(terms_conditions.first(), data={'trash':True}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'moved to trash', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'terms conditions not found', [])
        return res
    

class RestoreTermsConditionAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetTermsConditionSerializer
    def delete(self, request, id, format=None, *args, **kwargs):
        print(request.headers)
        try:
            terms_conditions = Terms_Conditions.objects.filter(id = id, trash=True)
        except:
            terms_conditions = Terms_Conditions.objects.filter(pk__in=[])

        if terms_conditions.exists():
            serializer = GetTermsConditionSerializer(terms_conditions.first(), data={'trash':False}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'restored successfully', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'terms conditions not found', [])
        return res
    


class AddTermsConditionAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetTermsConditionSerializer
    def post(self, request, format=None, *args, **kwargs):
        serializer = GetTermsConditionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'successfully added',[])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors,[])
        return res
    

class CreateReviews(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateReviewsSerializer
    def post(self, request, booking_id, format=None, *args, **kwargs):

        print('request.data', request.data)
        try:
            booking_serializer = Booking.objects.get(id=booking_id)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'booking not found', [])

        
        serializer = CreateReviewsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        booking_serializer.review = serializer.instance
        booking_serializer.save()
        res = resFun(status.HTTP_200_OK, 'review created', [])
        return res


class reviewVisibility(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = reviewVisibilitySerializer
    def put(self, request, review_id, format=None, *args, **kwargs):

        try:
            review = Reviews.objects.get(id=review_id)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'invalid request id')
        
        print('review',review)

        serializers = reviewVisibilitySerializer(review, data=request.data, partial=True)
        serializers.is_valid(raise_exception=True) 
        serializers.save()

        return resFun(status.HTTP_200_OK, 'review updated', [{'review_id': review_id}])




# class TrashShootCategoryAdmin(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = GetShootCategorySerializer
#     def delete(self, request, id, format=None, *args, **kwargs):
#         try:
#             shoot_category = ShootCategory.objects.filter(id = id, trash=False)
#         except:
#             shoot_category = ShootCategory.objects.filter(pk__in=[])

#         if shoot_category.exists():
#             serializer = GetShootCategorySerializer(shoot_category.first(), data={'trash':True}, partial=True)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             res = resFun(status.HTTP_200_OK, 'moved to trash', serializer.data)
#         else:
#             res = resFun(status.HTTP_400_BAD_REQUEST, 'terms conditions not found', [])
#         return res


# class GetShootCategoryAdmin(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = GetShootCategorySerializer
#     def get(self, request, id, format=None, *args, **kwargs):
#         try:
#             shoot_category = ShootCategory.objects.filter(id=id)
#         except:
#             shoot_category = ShootCategory.objects.filter(pk__in=[])

#         res = Response()
#         if shoot_category.exists():

#             serializer = GetShootCategorySerializer(data={'title': shoot_category.first().title, 'trash': shoot_category.first().trash}, many=False)
#             serializer.is_valid(raise_exception=True)

#             res = resFun(status.HTTP_200_OK,'request successful',serializer.data)
#         else:
#             res = resFun(status.HTTP_400_BAD_REQUEST,'service not found',[])
#         return res
    

# class UpdateShootCategoryAdmin(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = GetShootCategorySerializer
#     def put(self, request, id, format=None, *args, **kwargs):
#         try:
#             shoot_category_CH = ShootCategory.objects.filter(shoot_category_name=request.data.get('title').lower())
#             if shoot_category_CH.first().id == id:
#                 shoot_category_CH=ShootCategory.objects.filter(pk__in=[])
#         except:
#             shoot_category_CH = ShootCategory.objects.filter(pk__in=[])

#         if not shoot_category_CH.exists():
#             try:
#                 shoot_category = ShootCategory.objects.filter(id=id)
#             except:
#                 shoot_category = ShootCategory.objects.filter(pk__in=[])
#             # print('shoot_category', shoot_category)
#             if shoot_category.exists():
#                 serializer = GetShootCategorySerializer(shoot_category.first(), data=request.data, partial=True)
#                 if serializer.is_valid():
#                     serializer.save()
#                     res = resFun(status.HTTP_200_OK,'updated successfully', serializer.data)
#                 else:
#                     res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors['title'] if serializer.errors['title'] else serializer.errors , [])
#             else:
#                 res = resFun(status.HTTP_400_BAD_REQUEST,'no shoot category found', [])
#         else:
#             res = resFun(status.HTTP_400_BAD_REQUEST,'terms conditions name already exist', [])
#         return res
    


# class AddShootCategoryAdmin(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = GetShootCategorySerializer
#     def post(self, request, format=None, *args, **kwargs):
#         serializer = GetShootCategorySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             res = resFun(status.HTTP_200_OK, 'successfully added',[])
#         else:
#             res = resFun(status.HTTP_400_BAD_REQUEST, serializer.errors,[])
#         return res
        
    

class GetBookingAjax(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetBookingAjaxSerializer
    def post(self, request, format=None, *args, **kwargs):
        try:
            data = request.data.get('booking')
            print('data',data)
            booking = Booking.objects.filter(user__name__icontains=data).order_by('-id')
            # print('booking',booking)
            main_data = [ {"id": b.id, 'date': b.booking_date, 'name': b.user.name} for b in booking]

            serializer = GetBookingAjaxSerializer(data=main_data, many=True)
            if serializer.is_valid():
                res = resFun(status.HTTP_200_OK, 'request successful',serializer.data)
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',serializer.errors)

            return res
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
            




class teamAddFund(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = teamAddFundSerializer
    def post(self,request, format=None, *args, **kwargs):
        print(request.data)
        try:
            data = {}
            if request.data.get('amount'):
                data['amount'] = int(request.data.get('amount'))
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'amount field is required', [])
            
            if request.data.get('booking_id'):
                data['booking'] = request.data.get('booking_id')
            
            if request.data.get('notes'):
                data['note'] = request.data.get('notes')

            if request.data.get('team_mate_id') == None:
                return resFun(status.HTTP_400_BAD_REQUEST, 'team_mate id is required', [])

            serializer = teamAddFundSerializer(data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                team = Team_member.objects.get(id=request.data.get('team_mate_id'))
                team.fund.add(serializer.instance)

                res = resFun(status.HTTP_200_OK, 'request successful', [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
            return res
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
        

class TeamDeposite(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamDepositeSerializer
    def post(self,request, format=None, *args, **kwargs):
        try:
            data = {}
            if request.data.get('amount'):
                data['amount'] = int(request.data.get('amount'))
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'amount field is required', [])
            
            if request.data.get('notes'):
                data['note'] = request.data.get('notes')

            if request.data.get('team_mate_id') == None:
                return resFun(status.HTTP_400_BAD_REQUEST, 'team_mate id is required', [])

            serializer = TeamDepositeSerializer(data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                
                team = Team_member.objects.get(id=request.data.get('team_mate_id'))
                team.payments.add(serializer.instance)
                
                res = resFun(status.HTTP_200_OK, 'request successful', [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
            return res
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
        


class CreateWalkinClient(GenericAPIView):
    # authentication_classes = [IgnoreBearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CreateWalkinClientSerializer
    def post(self,request, format=None, *args, **kwargs):
        # try:

        email = request.data.get('email')
        contact_number = request.data.get('contact_number')
        
        if email:
            client = Client.objects.filter(user__email=email)
        if contact_number:
            client = Client.objects.filter(user__contact_number=contact_number)
        
        if not client.exists():
            serializer = CreateWalkinClientSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()

                password = generate_random_code()
                # custom_model_instance = CustomModel.objects.get(id=upload_1_instance.id)
                serializer.instance.password = make_password(password)
                serializer.instance.save()    

                client_instance = Client.objects.create(user=serializer.instance, source = ClientSource.objects.get(title = 'website_walkin'), client_token = generate_random_code() )
                
                # booking = Booking.objects.create({})

                booking_instance = Booking.objects.create(user=client_instance, booking_status= Drp_booking_status.objects.filter(title='in progress').first(), wedding_date= request.data.get('wedding_date'))
                client_instance.booking.add(booking_instance)

                email_id = serializer.instance.email
                message = canned_email.objects.get(email_type = 'welcome_email')
                message = message.email
                message = str(message).replace("{{{email}}}", email_id)
                message = str(message).replace("{{{password}}}", password)
                message = str(message).replace("{{{link}}}", f'<a href="http://127.0.0.1:8000/client-info/{client_instance.id}/{client_instance.client_token}">fill more details</a>')
                subject = 'Welcome to Jrs Studios!'
                from_email = 'akshatnigamcfl@gmail.com'
                recipient_list = [email_id]
                text = 'email sent from MyDjango'
                # if send_mail(subject, message, from_email, recipient_list):
                email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
                email.attach_alternative(message, 'text/html')
                # email.attach_file('files/uploadFile_0dTGU7A.csv', 'text/csv')
                email.send()

                # serializer.save()
                res = resFun(status.HTTP_200_OK, 'request raised, you will get callback soon', [])
            else:
                print(serializer.errors)
                res = resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'user already registered with this email or contact number', [])
        return res
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])



class AddHomepageMedia(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddHomepageMediaSerializer
    def post(self, request, format=None, *args, **kwargs):
            
            print('request.data', request.data)

        # try:
            masterpiece = homepage_media.objects.filter(type="masterpiece")
            for h in masterpiece:
                h.delete()
            handpicked = homepage_media.objects.filter(type="handpicked")
            for h in handpicked:
                h.delete()
            latest_creations = homepage_media.objects.filter(type="latest_creations")
            for h in latest_creations:
                h.delete()

            # image_gallery = ImageGallery.objects.filter(type)

            serializer = AddHomepageMediaSerializer(data=request.data, many=True)
            if serializer.is_valid():
                serializer.save()
                res = resFun(status.HTTP_200_OK, 'request successful', [])
            else:
                print(serializer.errors)
                res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)
            return res
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])


class ImageGalleryUpload(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = image_gallery_Form
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, format=None, *args, **kwargs):
        # try:
        file = request.FILES['file']
        if file:

            if request.FILES.get('file'):
                print( not 'jpg' in str(request.FILES.get('file')) )
                print( not 'image' in request.FILES.get('file').content_type )

                if not ( 'image' in request.FILES.get('file').content_type or 'jpg' in str(request.FILES.get('file')) ):
                    print('image issue')
                    return resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported', [])


            # if 'image' in request.FILES.get('file').content_type:
            upload = ImageGallery.objects.create(file=file)
            # print()
            serializer = AddHomepageMediaSerializer(data={ 'file_id': int(upload.id) , 'table': 'image_gallery', 'type': 'image_gallery' }, many=False)
            # upload = image_gallery_Form(request.POST, request.FILES)
            if serializer.is_valid():
                serializer.save()
                return resFun(status.HTTP_200_OK, 'image upload successfuls', [])
            else:
                print(serializer.errors)
                return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
            # else:
            #     res = resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported', [])
            
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])



class GetHomepageMedia(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HomepageMediaSerializer
    def get(self, request):
        # try:
            media = homepage_media.objects.all()
            data = {'masterpiece': [], 'handpicked': [], 'latest_creations': [], 'image_gallery': []}

            for m in media:
                if m.table == 'pre_wedding':
                    inst =  list(Pre_Wedding.objects.filter(id=m.file_id).values('title', 'description', 'cover_picture'))
                    # print('inst', inst, m.file_id)
                    inst[0]['table'] ='pre_wedding'
                    inst[0]['file_id'] = m.file_id
                    inst[0]['item_id'] = m.id
                    data[m.type].append(inst[0])
                    # data.append({'table': 'pre_wedding', 'data': list(inst)[0] })
                elif m.table == 'wedding':
                    inst = list(Wedding.objects.filter(id=m.file_id).values('title', 'description', 'cover_picture'))
                    inst[0]['table'] ='wedding'
                    inst[0]['file_id'] = m.file_id
                    inst[0]['item_id'] = m.id
                    data[m.type].append(inst[0])
                    # print('inst',inst)
                    # data[m.type].append(list(inst)[0])
                    # data.append({'table': 'wedding', 'data': list(inst)[0] })
                elif m.table == 'events':
                    inst = list(Events.objects.filter(id=m.file_id).values('title', 'description', 'cover_picture'))
                    inst[0]['table'] ='events'
                    inst[0]['file_id'] = m.file_id
                    inst[0]['item_id'] = m.id
                    data[m.type].append(inst[0])
                elif m.table == 'image_gallery':
                    print('m.file_id', m.file_id)
                    inst = list(ImageGallery.objects.filter(id=m.file_id).values('file'))
                    inst[0]['table'] ='image_gallery'
                    inst[0]['file_id'] = m.file_id
                    inst[0]['item_id'] = m.id
                    data[m.type].append(inst[0])
                    # data[m.type].append(list(inst)[0])
                    # data.append({'table': 'events', 'data': list(inst) })
                    

            serializer = HomepageMediaSerializer(data=data, many=False)
            if serializer.is_valid():
                print('serializer.data',serializer.data)

                return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
            else:
                print(serializer.errors)
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', serializer.errors)
        # except:
        #     return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])



class DeleteHomepageMedia(GenericAPIView):
    serializer_class = HomepageMediaSerializer
    permission_classes = [IsAuthenticated]
    def delete(self, request, id):

        try:
            homepage_media_inst = homepage_media.objects.filter(id=id).first()
            if homepage_media_inst:
                homepage_media_inst.delete()
                return resFun(status.HTTP_200_OK, 'request successful', [])
            else:
                return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
            
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])





class getShootDate(GenericAPIView):
    serializer_class = [IsAuthenticated]
    # permission_classes = image_gallery_Form
    def get(self, request, id):
        try:

            booking_instance = Booking.objects.filter(id=id).first()
            if booking_instance:
                data = []
                for b in booking_instance.shoot_date.all():
                    data.append({ 
                        'id': b.id,  
                        'date': b.date.strftime('%d-%m-%Y') , 
                        'additional_service' : [ { 
                            'service' : { 'id': ads.additional_service.id, 'count_id': ads.id , 'value' : ads.additional_service.service_name }, 'count': ads.count, 'team': [ {'id': t.team.id, 'user_id': t.team.user.id, 'name': t.team.user.name }  for t in ads.team.all() ]  } for ads in b.additional_service.all() ] })
                    
                    # # for ads in b.additional_service.all():
                    #         print(t.team.id)
                # print('b((((((()))))))', data)
                
                res =  resFun(status.HTTP_200_OK, 'request successful', data)
            else:
                res =  resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])
            return res
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])



class GetContentList(GenericAPIView):
    serializer_class = GetContentListSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, title, limit, page):

        offset = (page - 1)*limit

        print('title',title)
        print('(((((((((((((((((Page)))))))))))))))))',page)

        if title == 'pre_wedding':
            instance = Pre_Wedding.objects.filter()[offset:offset+limit].values()
            total_pages = math.ceil(Pre_Wedding.objects.count()/limit)
        elif title == 'wedding':
            instance = Wedding.objects.filter()[offset:offset+limit].values()
            total_pages = math.ceil(Wedding.objects.count()/limit)
        elif title == 'event':
            instance = Events.objects.filter()[offset:offset+limit].values()
            total_pages = math.ceil(Events.objects.count()/limit)
        elif title == 'reel':
            instance = Reels.objects.filter()[offset:offset+limit].values()
            total_pages = math.ceil(Reels.objects.count()/limit)

            
        if title == 'reel':
            serializer = GetReelSerializer(data=list(instance), many=True)
        else:
            serializer = GetContentListSerializer(data=list(instance), many=True)
        if serializer.is_valid():
            print(serializer.data)
            return resFun(status.HTTP_200_OK, 'request successful', {'data': serializer.data, 'current_page': page, 'total_pages': total_pages })
        else:
            print(serializer.errors)
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializer.errors)



class GetTeamMemberList(GenericAPIView):
    serializer_class = GetTeamMemberListSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        teamInstance = [ {'id': t.id, 'user_id': t.user.id, 'name': t.user.name, 'contact_number': t.user.contact_number, 'email': t.user.email } for t in Team_member.objects.all()]
        serializers = GetTeamMemberListSerializer(data=teamInstance, many=True)
        if serializers.is_valid():
            return resFun(status.HTTP_200_OK, 'request successful', serializers.data)
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', serializers.errors)




class GetTeamMemberPaymentInfo(GenericAPIView):
    serializer_class = GetTeamMemberPaymentInfoSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):

        try:
            teamMemberInstance = Team_member.objects.filter(user=user_id)
        except:
            return resFun(status.HTTP_400_BAD_REQUEST, 'invalid team member id', [])


        totalFunds = []
        totalPayments = []

        for t in teamMemberInstance:
            for f in t.fund.all():
                # totalFunds += int(f.amount)
                totalFunds.append( { 'id': f.id, 'date': f.date.strftime("%d-%m-%Y") , 'booking': f.booking.user.user.email, 'note': f.note, 'amount': f.amount } )

            for p in t.payments.all():
                # totalPayments += int(p.amount)
                totalPayments.append( { 'id': p.id, 'date': p.date.strftime("%d-%m-%Y"), 'note': p.note, 'amount': p.amount } )

        serializer = GetTeamMemberPaymentInfoSerializer(data={'fund' : totalFunds, 'paid' : totalPayments}, many=False)
        if serializer.is_valid():
            print(serializer.data)
            return resFun(status.HTTP_200_OK, 'request successful', serializer.data)
        else:
            return resFun(status.HTTP_400_BAD_REQUEST, 'request failed', [])


        

class GetReviewsList(GenericAPIView):
    serializer_class = getPaymentSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, dateSelector, limit, page):

        print(dateSelector, limit, page)

        offset = int((page - 1)*limit)

        if dateSelector==None or dateSelector=='this_month':
            dateSelector=='this_month'
            date = datetime.now().month
            booking_instance = Booking.objects.filter(review__date__month=date).distinct().order_by('-id')[offset: offset+limit]
            # reviews_instance = Reviews.objects.filter(date__month=date).distinct().order_by('-id')
            total_pages = math.ceil(Reviews.objects.filter(date__month=date).distinct().count()/limit)
        elif dateSelector=='this_year':
            date = datetime.now().year

            booking_instance = Booking.objects.filter(review__date__year=date).distinct().order_by('-id')[offset: offset+limit]
            # reviews_instance = Reviews.objects.filter(date__year=date).distinct().order_by('-id')[offset: offset+limit]
            total_pages = math.ceil(Reviews.objects.filter(date__year=date).distinct().count()/limit)
        elif dateSelector=='today':
            date = datetime.today().date()

            booking_instance = Booking.objects.filter(review__date=date).distinct().order_by('-id')[offset: offset+limit]
            # reviews_instance = Reviews.objects.filter(date=date).order_by('-id')[offset: offset+limit]
            total_pages = math.ceil(Reviews.objects.filter(date=date).distinct().count()/limit)
        elif dateSelector=='custom':
            date_from = request.GET.get("date_from")
            date_to = request.GET.get("date_to")
            date = {'date_from': date_from,'date_to': date_to } 
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
            end_date += timedelta(days=1)

            booking_instance = Booking.objects.filter(review__date__range=(start_date,end_date)).distinct().order_by('-id')[offset: offset+limit]
            # reviews_instance = Reviews.objects.filter(date__range=(start_date,end_date)).order_by('-id')[offset: offset+limit]
            total_pages = math.ceil(Reviews.objects.filter(date__range=(start_date,end_date)).distinct().count()/limit)

        data = [ { 
            'id': p.id, 
            'user_id': p.user.id,
            'review_id': p.review.id,
            'profile_picture': p.user.user.profile_picture.url, 
            'name': p.user.user.name, 
            'date': p.review.date.strftime('%d-%m-%Y'),
            'title': p.review.title,
            'review': p.review.content,
            'content': p.review.content, 
            'ratings': p.review.ratings,
            'visibility': p.review.visibility,
            }  for p in booking_instance ]

        print(data)

        if booking_instance.exists():
            serializer = getReviewsSerializer(data=data, many=True)
            if serializer.is_valid(raise_exception=True):
                print(serializer.data)
                return resFun(status.HTTP_200_OK, 'successful', { 'data': serializer.data, 'current_page' : page, 'total_pages': total_pages  } )
            else:
                print(serializer.errors)
                return resFun(status.HTTP_400_BAD_REQUEST, 'something went wrong', serializer.errors )
        else:
            return resFun(status.HTTP_204_NO_CONTENT, 'no data found', [])