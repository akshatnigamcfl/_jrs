from django import forms
from console.models import *

class Reels_Upload_Form(forms.ModelForm):
    class Meta:
        model = Reels
        fields = ['title', 'description', 'file']


class Pre_Wedding_Upload_Form_VIDEOFILE(forms.ModelForm):
    class Meta:
        model = Pre_Wedding
        fields = ['title', 'description', 'cover_picture','is_youtube_video','video_link' ]

class Pre_Wedding_Upload_Form_YOUTUBE_LINK(forms.ModelForm):
    class Meta:
        model = Pre_Wedding
        fields = ['title', 'description', 'cover_picture','is_youtube_video','video_youtube_link' ]


class Wedding_Upload_Form_VIDEOFILE(forms.ModelForm):
    class Meta:
        model = Wedding
        fields = ['title', 'description', 'cover_picture' ,'is_youtube_video','video_link']


class banners_image_upload(forms.ModelForm):
    class Meta:
        model = Banner_image
        fields = ['title', 'file']



class Wedding_Upload_Form_YOUTUBE_LINK(forms.ModelForm):
    class Meta:
        model = Wedding
        fields = ['title', 'description', 'cover_picture' ,'is_youtube_video','video_youtube_link']


class BannerVideo_form(forms.ModelForm):
    class Meta:
        model = Banner_video
        fields = '__all__'

class Showcase_form(forms.ModelForm):
    class Meta:
        model = Showcase_images
        fields = '__all__'


class Events_Upload_Form_VIDEOFILE(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['title', 'description', 'cover_picture' ,'is_youtube_video','video_link']

class Events_Upload_Form_YOUTUBE_LINK(forms.ModelForm):
    class Meta:
        model = Events
        fields = ['title', 'description', 'cover_picture', 'is_youtube_video','video_youtube_link']



class AddCustomModel(forms.ModelForm):
    class Meta:
        model = CustomModel
        fields = [ 'name','contact_number', 'email']


class AddClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [ 'user','client_token','source']

class EditClientForms(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['user', 'booking']


class EditBookingForms(forms.ModelForm):
    class Meta:
        model = Booking
        exclude = ['user', 'booking_date', 'booking_status', 'package', 'discount', 'total_price', 'shoot_date', 'review']

class EditCustomModel(forms.ModelForm):
    class Meta:
        model = CustomModel
        fields = ['name', 'contact_number', 'email']


class AddTeamMemberForm(forms.ModelForm):
    class Meta:
        model = Team_member
        fields = [ 'user','user_token']


# class TeamMemberSerializer(serializers.ModelSerializer):
#     skills = serializers.ListField(allow_empty=True)
#     class Meta:
#         model = Team_member
#         exclude = ['fund', 'payments']


class EditTeamMemberForms(forms.ModelForm):
    class Meta:
        model = Team_member
        fields = ['user']


class EditCustomModelWithFile(forms.ModelForm):
    class Meta:
        model = CustomModel
        fields = ['name', 'contact_number', 'email', 'profile_picture']


class updateUserProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomModel
        fields = ['profile_picture']



class image_gallery_Form(forms.ModelForm):
    class Meta:
        model = ImageGallery
        fields = ['file']
