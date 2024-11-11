from django.shortcuts import render
from django.contrib.auth import authenticate
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum

import secrets
import string




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

from datetime import datetime

from io import BytesIO
from xhtml2pdf import pisa
from django.http import FileResponse


from collections import Counter

import os






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
    

# @method_decorator(csrf_exempt, name='csrftoken')
class api_login(GenericAPIView):
    authentication_classes = [IgnoreBearerTokenAuthentication]
    serializer_class = loginSerializer
    def post(self, request, format=None, *args, **kwargs):
        serializer = loginSerializer(data=request.data)
        resp = Response()
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            try:
                UserAccount.objects.get(email=email)
            except:
                return Response({'status': status.HTTP_404_NOT_FOUND,'message':'no user account with this email id','data':[]}, status=status.HTTP_404_NOT_FOUND)
            user = authenticate(email=email, password=password)
            if user != None:

                token = get_tokens_for_user(user)
                # token = Token.objects.get_or_create(user=user)
                resp.status_code = status.HTTP_200_OK
                resp.data = {
                    'data': {'token': token},
                    'message': 'login successful'
                }

                resp.set_cookie(
                    key = settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=token['access'],
                    expires= settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure= settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly= settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite= settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
                resp.set_cookie(
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
                resp.status_code = status.HTTP_400_BAD_REQUEST
                resp.data = {
                    'data': [], 
                    'message': 'login failed', 
                }

        else:
            resp.status_code = status.HTTP_400_BAD_REQUEST
            resp.data = {
                'data': [], 
                'message': 'request failed' 
            }
        
        return resp





class upload_reels(CreateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = reelsUploadSerializer
    def post(self, request, format=None, *args, **kwargs):
            print(request.FILES.get('file   '))
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
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = Pre_Wedding_Upload_Form_VIDEOFILE
    def post(self, request, format=None, *args, **kwargs):
        # try:
            file = request.FILES
            res = Response()
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
                    
                
                if 'image' in request.FILES.get('cover_picture').content_type:
                    if request.POST.get('is_youtube_video') == 'true':
                        upload = Pre_Wedding_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES)
                    else:
                        upload = Pre_Wedding_Upload_Form_VIDEOFILE(request.POST, request.FILES)

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
                else:
                    res.status_code = status.HTTP_400_BAD_REQUEST
                    res.data = {
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'file format not supported',
                        'data': []
                    }
                return res
            

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

        file = request.FILES
        res = Response()
        pre_wedding = Pre_Wedding.objects.get(id = id)
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
                upload = Pre_Wedding_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES, instance=pre_wedding)
            else:
                upload = Pre_Wedding_Upload_Form_VIDEOFILE(request.POST, request.FILES, instance=pre_wedding)

            # else:

        elif not file:
            if request.POST.get('is_youtube_video') == 'true':
                print('if working')
                upload = Pre_Wedding_Upload_Form_YOUTUBE_LINK(request.POST, instance=pre_wedding)
                print('upload',upload)
            else:
                upload = Pre_Wedding_Upload_Form_VIDEOFILE(request.POST, instance=pre_wedding)


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
            res = Response()
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


                if 'image' in request.FILES.get('cover_picture').content_type:
                    if request.POST.get('is_youtube_video') == 'true':
                        upload = Wedding_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES)
                    else:
                        upload = Wedding_Upload_Form_VIDEOFILE(request.POST, request.FILES)
                    
                    
                    if upload.is_valid():
                        upload.save()
                        
                        res.status_code = status.HTTP_200_OK
                        res.data = {
                            'status': status.HTTP_200_OK,
                            'message': 'wedding upload successfully',
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
        # try:
            file = request.FILES
            res = Response()
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
                    
                print(request.POST)
                    
                if 'image' in request.FILES.get('cover_picture').content_type:
                    if request.POST.get('is_youtube_video') == 'true':
                        upload = Events_Upload_Form_YOUTUBE_LINK(request.POST, request.FILES)
                    else:
                        upload = Events_Upload_Form_VIDEOFILE(request.POST, request.FILES)

                    if upload.is_valid():
                        upload.save()
                        
                        res.status_code = status.HTTP_200_OK
                        res.data = {
                            'status': status.HTTP_200_OK,
                            'message': 'event upload successfully',
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
                if 'image' in request.FILES.get('cover_picture').content_type:
                    res.status_code = status.HTTP_400_BAD_REQUEST
                    res.data = {
                        'status': status.HTTP_400_BAD_REQUEST,
                        'message': 'file format not supported',
                        'data': []
                    }
                    return res                

                
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
            
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'pre events upload successfully',
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

        def generate_random_code(length=25):
            alphabet = string.ascii_letters + string.digits
            random_code = ''.join(secrets.choice(alphabet) for _ in range(length))
            return random_code
        
        res = Response()
        data = {}
        data['name'] = request.POST['name']
        data['contact_number'] = request.POST['contact_number']
        data['email_id'] = request.POST['email_id']
        data['client_token'] = generate_random_code()
        upload = AddClientForm(data)
        if upload.is_valid():
            instance = upload.save()

            print('upload.data',instance.id)

            message = canned_email.objects.get(email_type = 'welcome_email')
            message = message.email
            message = str(message).replace("{{{link}}}", f'<a href="http://127.0.0.1:8000/client-info/{instance.id}/{instance.client_token}">fill more details</a>')

            email_id = upload.cleaned_data['email_id']

            subject = 'Welcome to Jrs Studios!'
            from_email = 'akshatnigamcfl@gmail.com'
            recipient_list = [email_id]
            text = 'email sent from MyDjango'

            # if send_mail(subject, message, from_email, recipient_list):

            email = EmailMultiAlternatives(subject, text, from_email, recipient_list)
            email.attach_alternative(message, 'text/html')
            # email.attach_file('files/uploadFile_0dTGU7A.csv', 'text/csv')
            email.send()

            
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'client added successfully',
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
        

class EditClient(CreateAPIView):
    serializer_class = EditClientForms
    permission_classes = [IsAuthenticated]
    def put(self, request, id, format=None, *args, **kwargs):
        res = Response()
        client = Client.objects.filter(id = id).first()
        if request.FILES:
            print(request.FILES)
            formData = EditClientForms(request.POST, request.FILES, instance=client,)
        else:
            formData = EditClientForms(request.POST, instance=client,)

        if formData.is_valid():
           formData.save()
           res.status_code = status.HTTP_200_OK
           res.data={
               'status': status.HTTP_200_OK,
               'message': 'user edited successfully',
               'data': []
           }
        else:
           res.status_code = status.HTTP_400_BAD_REQUEST
           res.data={
               'status': status.HTTP_400_BAD_REQUEST,
               'message': formData.errors,
               'data': []
           }
        return res


class EditClientUserEdit(GenericAPIView):
    serializer_class = EditClientForms
    authentication_classes = [IgnoreBearerTokenAuthentication]
    def put(self, request, id, format=None, *args, **kwargs):
        res = Response()
        client = Client.objects.filter(id = id).first()
        if request.FILES:
            print('request.FILES',request.FILES)
            formData = EditClientForms(request.POST, request.FILES, instance=client)
        else:
            formData = EditClientForms(request.POST, instance=client,)

        if formData.is_valid():
           formData.save()
           res.status_code = status.HTTP_200_OK
           res.data={
               'status': status.HTTP_200_OK,
               'message': 'user edited successfully',
               'data': []
           }
        else:
           res.status_code = status.HTTP_400_BAD_REQUEST
           res.data={
               'status': status.HTTP_400_BAD_REQUEST,
               'message': formData.errors,
               'data': []
           }
        return res



class AddBooking(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBookingSerializer_RW
    def post(self, request, id, format=None, *args, **kwargs):
        # print('request.data 111',request.data)
        shoot_date = request.data.get('shoot_date')
        # shoot_date = datetime.strptime(shoot_date, '%Y-%m-%d').date()
        # print(shoot_date)
        

        res = Response()
        # if request.data.get('event_type') == 'wedding':
        serializer = AddBookingSerializer_RW(data=request.data)
        # elif request.data.get('event_type') == 'pre_wedding':
        #     serializer = AddBookingPreWeddingSerializer_RW(data=request.data)
        # else:
        #     serializers.ValidationError('event type not valid')
        
        serializer.is_valid(raise_exception=True)
        # print('serializer.data',serializer.data)

        try: 
            user = Booking.objects.filter(user = id)
        except:
            user = Booking.objects.filter(pk__in=[])

        print('user',user)

        if user.exists():
            booking = None
            for d in user.first().shoot_date.all():
                if str(d) == str(serializer.data.get('shoot_date')):
                    booking = d


            if not booking == None:
                print('s1')
                # if serializer.data.get('event_type') == 'wedding':
                service_update_serializer = UpdateBookingServiceSerializer(user.first(),  data={ 'date':serializer.data.get('shoot_date'), 'additional_service': serializer.data.get('additional_service')}, partial=True)
                service_update_serializer.is_valid(raise_exception=True)
                # elif serializer.data.get('event_type') == 'pre_wedding':
                #     print('booing',booking)
                #     service_update_serializer = booking
                #     service_update_serializer.event_type = serializer.data.get('event_type')
                #     service_update_serializer.additional_service.clear()


                service_update_serializer.save()
                res.status_code = status.HTTP_200_OK
                res.data = {
                    'data': [],
                    'message': 'booking updated',
                    'status': status.HTTP_200_OK
                }
                return res

            else:
                print('s2')

                # if serializer.data.get('event_type') == 'wedding':
                service_update_serializer = UpdateBookingServiceSerializer(user.first(),  data={ 'date':serializer.data.get('shoot_date'), 'additional_service': serializer.data.get('additional_service')}, partial=True)
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

            # print('else working')

            if serializer.data.get('event_type') == 'wedding':
                shoot_date_serializer = BookingDateSerializer(data={'user': id,'date':serializer.data.get('shoot_date'), 'event_type': serializer.data.get('event_type'), 'additional_service': serializer.data.get('additional_service'), 'package': serializer.data.get('package') }, many=False)

            elif serializer.data.get('event_type') == 'pre_wedding':
                print('working til here')

                shoot_date_serializer = BookingDatePreWeddingSerializer(data={'user': id,'date':serializer.data.get('shoot_date'), 'package': Package.objects.get(segment__segment = 'pre_wedding').id, 'event_type': serializer.data.get('event_type') }, many=False)


            shoot_date_serializer.is_valid(raise_exception=True)
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
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'booking added',
                'data': []
            }
        return res
    




class CancleBooking(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBookingSerializer
    def delete(self, request, format=None, *args, **kwargs):
        res = Response()
        try:
            booking = Booking.objects.select_related().filter(shoot_date__date = request.data.get('shoot_date')).values('shoot_date')
        except:
            booking - Booking.objects.get(pk__in=[])
        
        if booking:
            shoot_date = Booking_ShootDate.objects.get(id = booking.first().get('shoot_date')) 
            
            shoot_date.delete()
                # if str(request.data.get('shoot_date')) == str(b.date):
                    # print('ba**************************************',b.data)
                # else:
                    # print('else working')
            # booking.service.clear()
            # booking.additional_service.clear()

            # booking.delete()

            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'booking cancled successfully',
                'data': [],
            }

        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'no booking found with this date',
                'data': [],
            }
        return res
    


class SubmitPackage(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddBookingSerializer
    def put(self, request, id, format=None, *args, **kwargs):
        try:
            package = Booking.objects.filter(user = id)
        except:
            package = Booking.objects.filter(user = id)

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
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'user not found',[])
        return res






class GetAdditionalServices(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetServicesSerializer
    def get(self, request, format=None, *args, **kwargs):
        res = Response()
        service = Service.objects.all().values()
        # serializer = GetServicesSerializer(data=list(service), many=True)
        # if not serializer.is_valid(raise_exception=True):
        #     res.status_code = status.HTTP_400_BAD_REQUEST
        #     res.data = {
        #         'status': status.HTTP_400_BAD_REQUEST,
        #         'message': serializer.errors if serializer.errors else 'request failed',
        #         'data': [] 
        #     }
        #     return res

        additional_service = AdditionalService.objects.filter(trash=False)
        data  = [{'service_name': s.service_name, 'price': s.price,'id':s.id}  for s in additional_service]
        serializer_2 = AdditionalServiceSerializer(data=data, many=True)
        if not serializer_2.is_valid(raise_exception=True):
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': serializer_2.errors if serializer_2.errors else 'request failed',
                'data': [] 
            }
            return res
        
        main_serializer = ServiceMainSerializer(data={'additional_service': serializer_2.data})
        if main_serializer.is_valid(raise_exception=True):
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'request successful',
                'data': main_serializer.data
            }
        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': main_serializer.errors if main_serializer.errors else 'request failed',
                'data': [] 
            }
        return res
    


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
            serializer.is_valid(raise_exception=True)
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'data': serializer.data,
                'message': 'request successful'
            } 

        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'packages not available',
                'data': []
            }
        return res





class GetBookedServices(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetBookedServicesSerializer
    def get(self, request, id, format=None, *args, **kwargs):
        res = Response()
        bookings=Booking.objects.filter(user = id)
        if bookings.exists():
            booked_service = []
            for b in bookings:
                for d in b.shoot_date.all():
                    # print(d)
                    booked_service_obj = {}
                    booked_service_obj['shoot_date'] = {'full_date': str(d.date), 'date': d.date.day, 'month': d.date.month, 'year': d.date.year }
                    # booked_service_obj['booked_service'] = [{'service': c.service_name, 'segment': c.segment} for c in  b.service.all()]
                    booked_service_obj['booked_additional_service'] = [{'additional_service': str(c.additional_service), 'count': int(c.count)} for c in  d.additional_service.all()]
                    booked_service.append(booked_service_obj)
            print('booked_service', booked_service)

            serializer = GetBookedServicesSerializer(data=list(booked_service), many=True)
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
                'message': 'no booking available',
                'data': [],
            }
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
    






class PaymentSubmit(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer
    def post(self, request, id, format=None, *args, **kwargs):

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
    
        res = Response()
        client = Client.objects.get(id = id)
        if client:

            bookings = Booking.objects.get(user = id)
            service_data = getBookingDetails(bookings, id)

            if int(request.data.get('discount')) >= int(service_data.get('total_price'))/2:
                raise serializers.ValidationError('dicount can not be more than half of the total price')

            invoice = Invoice.objects.filter(user = client.id)

            # if invoice.exists():
            #     raise serializers.ValidationError('already submitted')
            # else:
            #     print(client.first().id)

            print(request.data.get('discount'))

            booking = BookingDiscountPriceSerializer(bookings, data={'discount': request.data.get('discount'), 'total_price': service_data.get('total_price'),'package': request.data.get('package')}, partial=True)
            booking.is_valid(raise_exception=True)
            if booking.save():

                payment = PaymentsSerializer(data={'amount': request.data.get('payment'), 'user': client.id})
                payment.is_valid(raise_exception=True)
                if payment.save():

                    invoice = InvoiceSerializer(data={ 'user': client.id, 'payment': payment.data['id'] })
                    invoice.is_valid(raise_exception=True)
                    if invoice.save():
                        pass
                    else:
                        serializers.ValidationError('payment not save')
                else:
                    serializers.ValidationError('payment not save')
            else:
                serializers.ValidationError('discount and total price not updated')



            
            res.status_code = status.HTTP_200_OK
            res.data={
                'status': status.HTTP_200_OK,
                'message': 'payment submitted',
                'data': [],
            }
                
        else:
            res.status_code = status.HTTP_200_OK
            res.data={
                'status': status.HTTP_200_OK,
                'message': 'invalid client id',
                'data': [],
            }
        return res
    


class GenerateInvoice(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GenerateInvoiceSerializer
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request, id, format=None, *args, **kwargs):

        client = Client.objects.filter(id = id)
        if client.exists():

            template = get_template('console-layout/invoice.html')
            context = {
                'payment_date': 27/1/2024
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
        


class GenerateQuotation(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = GenerateQuotationSerializer
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request, id, format=None, *args, **kwargs):
        
        client = Client.objects.filter(id = id)
        if client.exists():

            template = get_template('console-layout/quotation.html')
            context = {
                'payment_date': 27/1/2024
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

        
        


class GetSegmentServicesAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SegmentSerializer
    def get(self, request, format=None, *args, **kwargs):

        res = Response()
        
        try:
            segment = Segment.objects.all()  
        except:
            segment = Segment.objects.filter(pk__in=[])  

        if segment.exists():
            serializer = SegmentSerializer(data=list(segment.values()), many=True)
            serializer.is_valid(raise_exception=True)
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'request successful',
                'data': serializer.data
            }
        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'no data found',
                'data': []
            }

        return res


        


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

        res = Response()
        try:
            service = Service.objects.filter(id = id, trash=False)
        except:
            service = Service.objects.filter(pk__in=[])

        
        if service.exists():

            serializer = AddServiceSerializer(service.first(), data={'trash':True}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res.status_code = status.HTTP_200_OK
            res.data = {
                'status': status.HTTP_200_OK,
                'message': 'moved to trash',
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
        # print('working here')
        try:
            service_CH = Service.objects.filter(service_name=request.data.get('service_name'))
            if service_CH.first().id == id:
                service_CH=Service.objects.filter(pk__in=[])
        except:
            service_CH = Service.objects.filter(pk__in=[])

        if not service_CH.exists():
            try:
                service = Service.objects.filter(id=id)
                print(service)
            except:
                service = Service.objects.filter(pk__in=[])
            # print('service', service)
            if service.exists():
                serializer = AddServiceSerializer(service.first(), data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                res = resFun(status.HTTP_200_OK,'updated successfully', serializer.data)
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
        try:
            service_CH = AdditionalService.objects.filter(service_name=request.data.get('service_name'))
            if service_CH.first().id == id:
                service_CH=AdditionalService.objects.filter(pk__in=[])
        except:
            service_CH = AdditionalService.objects.filter(pk__in=[])

        if not service_CH.exists():
            try:
                service = AdditionalService.objects.filter(id=id)
                print(service)
            except:
                service = AdditionalService.objects.filter(pk__in=[])
            # print('service', service)
            if service.exists():
                serializer = AddAdditionalServiceSerializer(service.first(), data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                res = resFun(status.HTTP_200_OK,'updated successfully', serializer.data)
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'no service found', [])
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
            res = resFun(status.HTTP_200_OK, 'moved to trash', serializer.data)

        else:
            res.status_code = status.HTTP_400_BAD_REQUEST
            res.data = {
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'service not found',
                'data': [],
            }
        
        return res
    

class AddPackageAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddPackageSerializer
    def post(self, request, format=None, *args, **kwargs):
        try:
            package = Package.objects.get(package=request.data.get('package').lower(),segment = request.data.get('segment'))
            if package:
                res = resFun(status.HTTP_400_BAD_REQUEST, 'package name already exists' ,[])
                return res
        except:
            pass

        serializer = AddPackageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        res = resFun(status.HTTP_200_OK, 'package created',[])
        return res


class GetPackageAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetPackageSerializer
    def get(self, request, id, format=None, *args, **kwargs):

        try:
            package = Package.objects.filter(id=id)
        except:
            package = Package.objects.filter(pk__in=[])

        if package.exists():
            serializer = GetPackageSerializer(data={'id': int(package.first().id) ,'package': package.first().package, 'price': int(package.first().price), 'segment': str(package.first().segment),'service': [s.id for s in package.first().service.all()], 'booked_package': {}}, many=False)
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
            package = Package.objects.filter(segment=id,trash=False)
        except:
            package = Package.objects.filter(pk__in=[])

        if package.exists():
            data = []
            for p in package:
                data.append({'id': int(p.id) ,'package': p.package, 'price': int(p.price), 'segment': str(p.segment),'service': [str(s.service_name) for s in p.service.all()], 'booked_package': {}})
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

        try:
            package = Package.objects.filter(package = request.data.get('package').lower(),segment = request.data.get('segment'))
            if package.exists():
                if not int(package.first().id) == int(id):
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'package name already exists', [])
                    return res
        except:
            pass

        try:
            package = Package.objects.filter(id=id)
        except:
            package = Package.objects.filter(pk__in=[])

        if package.exists():
            serializer = AddPackageSerializer(package.first(), data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK, 'package updated successfully', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'package not found', [])
        return res



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
                    if not 'video' in request.FILES.get('file').content_type:
                        res = resFun(status.HTTP_400_BAD_REQUEST, 'video format not supported',[])
                        return res
                    upload = BannerVideo_form(request.POST, request.FILES)
                    if upload.is_valid():
                        upload.save()
                        res = resFun(status.HTTP_200_OK, 'wedding upload successfully',[])
                    else:
                        res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])
                else:
                    res = resFun(status.HTTP_400_BAD_REQUEST, 'file format not supported',[])
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





class AddTeamMemberAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer
    def post(self, request, format=None, *args, **kwargs):
        print('POST', request.data)

        form = TeamMemberSerializer(data=request.data,many=False)
        if form.is_valid(raise_exception=True):
            if form.save():
                res = resFun(status.HTTP_200_OK,'member saved successfully', [])
            else:
                res = resFun(status.HTTP_400_BAD_REQUEST,'member not saved', [])
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST, 'request failed',[])
        return res



class GetTeamMemberIndvAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer
    def get(self, request, id, format=None, *args, **kwargs):
        try:
            member = Team_member.objects.filter(id=id)
        except:
            member = Team_member.objects.filter(pk__in=[])           
            
        if member.exists():
            serializer = TeamMemberSerializer(data=member.values().first(), many=False)
            serializer.is_valid(raise_exception=True)
            res = resFun(status.HTTP_200_OK,'request successful', serializer.data)
        else:
            res = resFun(status.HTTP_400_BAD_REQUEST,'team member not found', [])
        return res


class UpdateTeamMemberIndvAdmin(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TeamMemberSerializer
    def put(self, request, id, format=None, *args, **kwargs):
        try:
            member = Team_member.objects.filter(id=id)
        except:
            member = Team_member.objects.filter(pk__in=[])

        if member.exists():
            serializer = TeamMemberSerializer(member.first(), data=request.data ,partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            res = resFun(status.HTTP_200_OK,'request successful', [])
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
        

