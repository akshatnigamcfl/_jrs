from rest_framework import serializers
from console.models import *


class GetEncSerializer(serializers.Serializer):
    enc=serializers.CharField()


class loginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    # password = serializers.CharField(write_only=True)
    class Meta:
        model=CustomModel
        fields=['email','password']


class ClientloginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model=Client
        fields=['email','password']


class reelsUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    class Meta:
        # models=all_identifiers
        fields=["file"]


class AddBookingSerializer_RW(serializers.Serializer):
    # package = serializers.IntegerField()
    # event_type = serializers.CharField()
    additional_service = serializers.ListField(allow_empty=True)
    shoot_date = serializers.DateField()

class AddBookingPreWeddingSerializer_RW(serializers.Serializer):
    shoot_date = serializers.DateField()
    event_type = serializers.CharField()


class BookingDateSerializer(serializers.ModelSerializer):
    # event_type = serializers.CharField()
    user = serializers.IntegerField()
    package = serializers.IntegerField()
    additional_service = serializers.ListField(allow_empty=True)
    class Meta:
        model = Booking_ShootDate
        fields = '__all__'

    def validate(self, data):
        for d in data['additional_service']:
            count = d['count']
            try:
                additional_service = AdditionalService.objects.get(id = d['id'])
                if not additional_service:
                    serializers.ValidationError('additional service id not valid')
            except:
                    serializers.ValidationError('additional service id not valid')

            if not isinstance(count, int):
                serializers.ValidationError('count should be integer value')

        try:
            package = Package.objects.get(id = d['id'])
            if not package:
                serializers.ValidationError('package id not valid')
        except:
            serializers.ValidationError('package id not valid')

        try:
            user = UserAccount.objects.get(id = d['user'])
            if not user:
                serializers.ValidationError('user id not valid')
        except:
            serializers.ValidationError('user id not valid')
            
        # print('data',data)

        return data
    
    def create(self, validated_data):
        additional_service = validated_data['additional_service']
        package = validated_data['package']
        user = validated_data['user']
        del validated_data['additional_service']
        del validated_data['package']
        del validated_data['user']
        booking = Booking_ShootDate.objects.create(**validated_data)
        for d in additional_service:
            additional_service_bookings_serializer = additional_service_bookings.objects.create(additional_service= AdditionalService.objects.get(id = d['id']) ,count=d['count'] )
            booking.additional_service.add(additional_service_bookings_serializer)


        booking_serializer = Booking.objects.create(user = Client.objects.get(id=user), package = Package.objects.get(id=package))
        booking_serializer.shoot_date.add(booking)


        return booking_serializer



class BookingDatePreWeddingSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField()
    package = serializers.IntegerField()
    event_type = serializers.CharField()
    class Meta:
        model = Booking_ShootDate
        exclude = ['additional_service']

    def validate(self, data):
        try:
            package = Package.objects.get(id = data['package'])
            if not package:
                serializers.ValidationError('package id not valid')
        except:
            serializers.ValidationError('package id not valid')

        try:
            user = UserAccount.objects.get(id = data['user'])
            if not user:
                serializers.ValidationError('user id not valid')
        except:
            serializers.ValidationError('user id not valid')
            
        return data
    
    def create(self, validated_data):
        pass
        print('validated', validated_data)
        # additional_service = validated_data['additional_service']
        package = validated_data['package']
        user = validated_data['user']
        # del validated_data['additional_service']
        del validated_data['package']
        del validated_data['user']
        booking = Booking_ShootDate.objects.create(**validated_data)
        # for d in additional_service:
        #     additional_service_bookings_serializer = additional_service_bookings.objects.create(additional_service= AdditionalService.objects.get(id = d['id']) ,count=d['count'] )
        #     booking.additional_service.add(additional_service_bookings_serializer)


        booking_serializer = Booking.objects.create(user = Client.objects.get(id=user), package = Package.objects.get(id=package))
        booking_serializer.shoot_date.add(booking)


        return booking_serializer
    


class UpdateBookingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model=Booking
        fields = ['booking_status']




class AddBookingSerializer(serializers.ModelSerializer):
    # shoot_date = serializers.IntegerField()
    # user = serializers.IntegerField()
    # package = serializers.IntegerField()
    # additional_service = serializers.ListField(allow_empty=True)
    # # additional_service = serializers.IntegerField(many=True)
    # shoot_date = serializers.DateField()
    class Meta:
        model = Booking
        # exclude = ['shoot_date']
        fields = '__all__'

    def validate(self, data):
        if data['user'] is None or not ['user']:
            raise serializers.ValidationError('invalid user id')
        if not Package.objects.get(package = data['package']):
            raise serializers.ValidationError('invalid package id')
        # for d in data['additional_service']:
        #     if not AdditionalService.objects.get(id = d):
        #         raise serializers.ValidationError('invalid additional service id')
        return data
    

    def create(self, validated_data):
        additional_services = validated_data['additional_service']
        shoot_date = validated_data['shoot_date']

        print(shoot_date, additional_services)

        data = validated_data
        del data['additional_service']
        del data['shoot_date']


        
        booking = Booking.objects.create(**validated_data)
        for d in additional_services:
            booking.additional_service.add(AdditionalService.objects.get(id = d))
        booking.shoot_date.add(Booking_ShootDate.objects.get(id = shoot_date))
        return booking
    
        # return super().create(validated_data)
    

class GetBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    shoot_date_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    booking_id = serializers.IntegerField()
    date = serializers.CharField()
    client_name = serializers.CharField()
    event_type = serializers.CharField()
    additional_service = serializers.ListField()



class GetQuotationInfoSerializer(serializers.Serializer):
    package_info = serializers.ListField()
    pricing_info = serializers.ListField()
    additional = serializers.ListField()
    camera_equipment_details = serializers.ListField()
    production_process = serializers.ListField()
    deliverables = serializers.ListField()
    terms_condition = serializers.ListField()



class GetIndvBookingSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    booking_date = serializers.CharField()
    package = serializers.DictField()
    booking_status = serializers.DictField()
    discount = serializers.IntegerField(allow_null=True)
    wedding_date = serializers.CharField(allow_null=True)
    groom_name = serializers.CharField(allow_null=True)
    groom_email_id = serializers.EmailField(allow_null=True)
    groom_contact_number = serializers.CharField(allow_null=True)
    groom_date_of_birth = serializers.CharField(allow_null=True)
    bride_name = serializers.CharField(allow_null=True)
    bride_email_id = serializers.EmailField(allow_null=True)
    bride_date_of_birth = serializers.CharField(allow_null=True)
    wedding_venue = serializers.CharField(allow_null=True)
    shoot_date = serializers.ListField()

        


class UpdateBookingServiceSerializer(serializers.ModelSerializer):
    # package = serializers.ListField(allow_empty=True)
    # package
    date = serializers.DateField()
    # event_type = serializers.CharField()
    additional_service = serializers.ListField(allow_empty=True)
    class Meta:
        model = Booking
        fields = ['date', 'additional_service']

    def validate(self, data):
        # print('attrs',data)
        for d in data['additional_service']:
            count = d['count']
            try:
                additional_service = AdditionalService.objects.get(id = d['id'])
                if not additional_service:
                    serializers.ValidationError('additional service id not valid')
            except:
                    serializers.ValidationError('additional service id not valid')

            if not isinstance(count, int):
                serializers.ValidationError('count should be integer value')
        # try:
        #     package = Package.objects.get(id = d['id'])
        #     if not package:
        #         serializers.ValidationError('package id not valid')
        # except:
        #     serializers.ValidationError('package id not valid')
        return data

    def update(self, instance, validated_data):
        # instance.package = validated_data['package']
        new_date = True
        for d in instance.shoot_date.all():
            if str(d.date) == str(validated_data['date']):
                new_date = False
                # print('validated_data["event_type"]',validated_data['event_type'])
                # d.event_type = validated_data['event_type']
                d.additional_service.clear()
                for s in validated_data['additional_service']:
                    additional_service_bookings_serializer = additional_service_bookings.objects.create(additional_service=AdditionalService.objects.get(id = s['id']) ,count=s['count'] )
                    d.additional_service.add(additional_service_bookings_serializer)
                d.save()

        if new_date:

            additional_service = validated_data['additional_service']
            # instance.package = validated_data['package']
            del validated_data['additional_service']
            # del validated_data['package']

            booking = Booking_ShootDate.objects.create(**validated_data)
            for d in additional_service:
                print(booking, 'asdf', d['id'])
                additional_service_bookings_serializer = additional_service_bookings.objects.create(additional_service=AdditionalService.objects.get(id=d['id']),count=d['count'])
                booking.additional_service.add(additional_service_bookings_serializer)
            instance.shoot_date.add(booking)
        instance.save()

        # additional_service = validated_data['additional_service']

        # for d in additional_service:
        #     print('d',d)

        # instance.date = validated_data['']
        # instance.event_type = validated_data['event_type']
        # instance.additional_service.clear()


        # package = validated_data['package']
        # user = validated_data['user']
        # del validated_data['additional_service']
        # del validated_data['package']
        # del validated_data['user']
        # booking = Booking_ShootDate.objects.create(**validated_data)
        # for d in additional_service:
        #     additional_service_bookings_serializer = additional_service_bookings.objects.create(additional_service= AdditionalService.objects.get(id = d['id']) ,count=d['count'] )
        #     booking.additional_service.add(additional_service_bookings_serializer)
        # booking_serializer = Booking.objects.create(user = Client.objects.get(id=user), package = Package.objects.get(id=package))
        # booking_serializer.shoot_date.add(booking)
        # return booking_serializer

        # print('asdfasdfsadfsdf***********',validated_data)

        return instance


class UpdateBookingPreWeddingServiceSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    event_type = serializers.CharField()
    class Meta:
        model = Booking
        fields = ['date','event_type']

    # def validate(self, data):
    #     print('data',data)
    def update(self, instance, validated_data):
        print('instance **********88',instance)
        booking = Booking_ShootDate.objects.create(**validated_data)
        instance.shoot_date.add(booking)
        instance.save()

        return instance
        # return super().update(instance, validated_data)
    # return data


class PackageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['package']

        
class addBookingTeamSerializer(serializers.Serializer):
    title = serializers.CharField()



class GetServicesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Service
        fields = '__all__'


class GetPackageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    price = serializers.IntegerField()
    package = serializers.CharField()
    segment = serializers.CharField()
    booked_package = serializers.DictField()
    deliverables = serializers.ListField()



class AdditionalServiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    # segment = serializers.CharField()
    class Meta:
        model = AdditionalService
        exclude = ['segment']


class ShootCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    service_name = serializers.CharField()


class ServiceMainSerializer(serializers.Serializer):
    additional_service = serializers.ListField()


# class preWeddingUploadSerializer(serializers.Serializer):
#     poster = serializers.FileField()
#     class Meta:
        

class GetBookedServicesSerializer(serializers.Serializer):
    shoot_date = serializers.DictField()
    # booked_service = serializers.ListField()
    booked_additional_service = serializers.ListField()


class GetServicesInvoiceSerializer(serializers.Serializer):
    package = serializers.CharField()
    package_price = serializers.IntegerField()
    additionals_total_price = serializers.IntegerField()
    total_price = serializers.IntegerField()
    remaining_payment = serializers.IntegerField()
    discount = serializers.IntegerField()
    service = serializers.ListField()
    additionals = serializers.ListField()



# class GenerateInvoiceSerializer(serializers.Serializer):
#     discount = serializers.IntegerField()


class PendingPaymentSerializer(serializers.Serializer):
    pending_payment = serializers.IntegerField()



class getPaymentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    date = serializers.CharField()
    class Meta:
        model = Payments
        fields = ['id', 'date', 'amount', 'payment_mode', 'payment_note']


class getReviewsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    review_id = serializers.IntegerField()
    profile_picture = serializers.CharField()
    name = serializers.CharField()
    date = serializers.CharField()
    class Meta:
        model = Reviews
        fields = ['id', 'user_id', 'review_id', 'profile_picture', 'name', 'date', 'title', 'content', 'ratings', 'visibility']



class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'

class BookingDiscountPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class UpdateDiscountSerializer(serializers.ModelSerializer):
    discount = serializers.IntegerField()
    class Meta:
        model = Booking
        fields = ['discount']


class GetTeamMemberSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class GenerateInvoiceSerializer(serializers.Serializer):
    invoice = serializers.FileField()

class GenerateQuotationSerializer(serializers.Serializer):
    quotation = serializers.FileField()

class SaveQuotationSerializer(serializers.Serializer):
    discount = serializers.IntegerField()


class PreWeddingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    cover_picture = serializers.CharField()
    video_link = serializers.CharField(allow_null=True)

    class Meta:
        model = Pre_Wedding
        fields = '__all__'

class mediaDataReponseSerializer(serializers.Serializer):
    data=serializers.ListField()
    page_count=serializers.IntegerField()
    current_page=serializers.IntegerField()
    table=serializers.CharField()

# class ReelsSerializer(serializers.ModelSerializer):
#     # cover_picture = serializers.CharField()
#     # video_link = serializers.CharField(allow_null=True)

#     class Meta:
#         model = Reels
#         fields = '__all__'    


class WeddingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    cover_picture = serializers.CharField()
    video_link = serializers.CharField(allow_null=True)

    class Meta:
        model = Wedding
        fields = '__all__'


class EventsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    cover_picture = serializers.CharField()
    video_link = serializers.CharField(allow_null=True)

    class Meta:
        model = Events
        fields = '__all__'

class SegmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    segment = serializers.CharField()


class GetSegmentSerializer(serializers.Serializer):
    segment = serializers.DictField()

class getSegmentPackageListSerializer(GetSegmentSerializer):
    package = serializers.ListField()

class getServiceListSerializer(GetSegmentSerializer):
    service = serializers.ListField()

class getAdditionalServiceListSerializer(GetSegmentSerializer):
    additional_service = serializers.ListField()


class GetServiceSerializer(serializers.ModelSerializer):
    segment = serializers.DictField()
    class Meta:
        model = Service
        fields = '__all__'


class getPackageSectionListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    trash = serializers.BooleanField()


class HomepageMediaSerializer(serializers.Serializer):
    masterpiece = serializers.ListField()
    handpicked = serializers.ListField()
    latest_creations = serializers.ListField()
    image_gallery = serializers.ListField()
    # cover_picture = serializers.URLField()
    # class Meta:
    #     model = homepage_media
    #     fields = '__all__'




class AddServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class AddAdditionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalService
        fields = '__all__'


class GetAdditionalServiceSerializer(serializers.ModelSerializer):
    segment = serializers.DictField()
    class Meta:
        model = AdditionalService
        fields = '__all__'


class GetCameraEquipmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraEquipments
        fields = '__all__'


class GetProductionProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionProcess
        fields = '__all__'


class GetDeliverablesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliverables
        fields = '__all__'

class GetAllDeliverablesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Deliverables
        fields = '__all__'



class GetTermsConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terms_Conditions
        fields = '__all__'


# class GetShootCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShootCategory
#         fields = '__all__'



class AddPackageSerializer(serializers.ModelSerializer):
    deliverables = serializers.ListField()
    class Meta:
        model = Package
        fields = '__all__'

    def validate(self, attrs):
        print('attrs',attrs)
        # for s in attrs.get('deliverables'):
            # try:
            #     Deliverables.objects.filter(id=s)
            # except:
            #     raise serializers.ValidationError('no deliverable found')
            
        return attrs
    
    def update(self, instance, validated_data):
        print('validated_data', validated_data)
        # service = validated_data['service']
        # del validated_data['service']
        instance.package = validated_data['package']
        instance.price = validated_data['price']
        instance.segment = validated_data['segment']
        instance.deliverables.clear()

        # instance.service = validated_data['service']
        # package = Package.objects.create(**validated_data)
        print('service',validated_data['deliverables'])

        if len(validated_data['deliverables']) > 0:

            instance.deliverables.clear()
            
            for s in validated_data['deliverables']:
                instance.deliverables.add(s)
        
        instance.save()
        print('validated_data[service]',validated_data['deliverables'])
        # return super().create(validated_data)
        return instance


    #     return super().update(instance, validated_data)
    
    # def upda(self, validated_data):
    #     # print('validated_data',validated_data)

    #     # return
    

class getPackageSerializer(serializers.Serializer):
    class Meta:
        model = Package
        fields = '__all__'


class HomeBannerVideoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    file = serializers.CharField()
    title = serializers.CharField()
    # class Meta:
    #     model = Banner_video
    #     fields = '__all__'


class TeamMemberSerializer(serializers.ModelSerializer):
    skills = serializers.ListField(allow_empty=True)
    class Meta:
        model = Team_member
        fields = ['skills', 'user', 'user_token', 'description']


class TeamMemberViewSerializer(serializers.ModelSerializer):
    skills = serializers.ListField(allow_empty=True)
    user = serializers.DictField()
    class Meta:
        model = Team_member
        fields = ['skills', 'user', 'user_token']


class ConsoleDashboardSerializer(serializers.Serializer):
    total_payment = serializers.IntegerField()
    booking = serializers.IntegerField()
    client = serializers.IntegerField()
    pre_wedding = serializers.IntegerField()
    wedding = serializers.IntegerField()
    events = serializers.IntegerField()
    reels = serializers.IntegerField()


class teamAddFundSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    # booking = serializers.IntegerField()
    note = serializers.CharField(max_length=100)
    class Meta:
        model = fund_history
        fields = '__all__'


class TeamDepositeSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    note = serializers.CharField(max_length=100)
    class Meta:
        model = payments_history
        fields = '__all__'
    


class GetBookingAjaxSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.DateField()
    name = serializers.CharField()


class CreateWalkinClientSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    contact_number = serializers.CharField()
    # wedding_date = serializers.DateField()
    class Meta:
        model = CustomModel
        fields = ['name', 'email', 'contact_number']


class AddHomepageMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = homepage_media
        fields = '__all__'

class ImageGalleryUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    class Meta:
        # models=all_identifiers
        fields=["file"]


class CreateReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = '__all__'

class reviewVisibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = ['visibility']

# class addBannersSerializer(serializers.ModelSerializer):
#     pass



class get_banners_allSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Banner_image
        fields = '__all__'



class getBookingHistorySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.DateField()
    status = serializers.CharField()



class getClientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    client_name = serializers.CharField()
    email = serializers.EmailField()
    contact_number = serializers.CharField()
    profile_picture = serializers.CharField()



class getBookingStatusListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


class GetContentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    cover_picture = serializers.CharField()
    is_youtube_video = serializers.BooleanField()
    video_link = serializers.CharField(allow_null=True, allow_blank=True)
    video_youtube_link = serializers.CharField(allow_null=True, allow_blank=True)



class GetReelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    file = serializers.CharField(allow_null=True, allow_blank=True)



class GetTeamMemberListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.CharField()
    contact_number = serializers.CharField()


class GetTeamMemberPaymentInfoSerializer(serializers.Serializer):
    fund = serializers.ListField()
    paid = serializers.ListField()


    


# class getPackageServicesSerializer(serializers.ModelSerializer):

#     class Meta:
#         model: Package
#         fields: '__all__'

    # def validate(self, attrs):
    #     print('attrs',)
        # return super().validate(attrs)

        # return super().validate(attrs)

# class TrashServiceSerializer(serializers.Serializer):
#     trash = serializers.BooleanField()


