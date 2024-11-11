from django.urls import path
from .views import *


urlpatterns = [
    
path('get_enc', GetEnc.as_view(), name='get_enc'),

path('admin_login', api_login.as_view(), name='admin_login'),
path('team_login', team_login.as_view(), name='team_login'),
path('generate_password/<str:type>/<int:id>/<str:token>', generate_password.as_view(), name='generate_password'),
# path('client_login', api_client_login.as_view(), name='client_login'),
path('upload_reels', upload_reels.as_view(), name='upload_reels'),
path('delete_reels/<int:id>', delete_reels.as_view(), name='delete_reels'),

path('upload_pre_wedding', upload_pre_wedding.as_view(), name='upload_pre_wedding'),   
path('get_pre_wedding_all/<int:page>', get_pre_wedding_all.as_view(), name='get_pre_wedding_all'),
path('get_pre_wedding/<int:id>', get_pre_wedding_indv.as_view(), name='get_pre_wedding_indv'),
path('edit_pre_wedding/<int:id>', edit_pre_wedding_indv.as_view(), name='edit_pre_wedding_indv'),
path('delete_pre_wedding/<int:id>/', delete_pre_wedding.as_view(), name='delete_pre_wedding'),


path('upload_wedding', upload_wedding.as_view(), name='upload_wedding'),
path('get_wedding_all/<int:page>', get_wedding_all.as_view(), name='get_wedding_all'),
path('get_wedding/<int:id>', get_wedding_indv.as_view(), name='get_wedding_indv'),
path('edit_wedding/<int:id>', edit_wedding_indv.as_view(), name='edit_wedding_indv'),
path('delete_wedding/<int:id>', delete_wedding.as_view(), name='delete_wedding'),

path('upload_events', upload_events.as_view(), name='upload_events'),
path('get_events_all/<int:page>', get_events_all.as_view(), name='get_events_all'),
path('get_events/<int:id>', get_events_indv.as_view(), name='get_events_indv'),
path('edit_events/<int:id>', edit_events_indv.as_view(), name='edit_events_indv'),
path('delete_events/<int:id>', delete_events.as_view(), name='delete_events'),

path('add_banners_all/<int:page>', add_banners_all.as_view(), name='add_banners_all'),
path('get_banners_all/<int:page>', get_banners_all.as_view(), name='get_banners_all'),

path('add_client', AddClient.as_view(), name='add_client'),
path('edit_client/<int:id>', EditClient.as_view(), name='edit_client'),

path('edit_booking_user_edit/<int:booking_id>', EditBookingUserEdit.as_view(), name='edit_booking_user_edit'),
path('update_user_profile_picture/<int:user_id>', updateUserProfilePicture.as_view(), name='update_user_profile_picture'),

path('edit_client_booking/<int:id>', EditClientBooking.as_view(), name='edit_client_booking'),

path('add_team_member_admin', AddTeamMember.as_view(), name='add_team_member_admin'),
path('edit_team_member/<int:id>', EditTeamMember.as_view(), name='edit_team_member'),
# path('edit_team_member_user_edit/<int:id>', EditTeamMemberUserEdit.as_view(), name='edit_team_member_user_edit'),


# path('add_team_member_admin', AddTeamMemberAdmin.as_view(), name='add_team_member_admin'),
path('get_team_member_indv_admin/<int:id>', GetTeamMemberIndvAdmin.as_view(), name='get_team_member_indv_admin'),
path('update_team_member_admin/<int:id>', UpdateTeamMemberIndvAdmin.as_view(), name='update_team_member_admin'),
path('delete_team_member_admin/<int:id>', DeleteTeamMemberIndvAdmin.as_view(), name='delete_team_member_admin'),


path('add_booking/<int:booking_id>', AddBooking.as_view(), name='add_booking'),
path('create_new_booking/<int:client_id>', createNewBooking.as_view(), name='create_new_booking'),

path('cancle_booking/<int:shootDateId>', CancleBooking.as_view(), name='cancle_booking'),

path('get_bookings/<str:date>/<int:page>', getBookings.as_view(), name='get_bookings'),
path('get_indv_booking/<int:booking_id>', getIndvBookings.as_view(), name='get_indv_bookings'),
path('get_bookings_history/<int:client_id>', getBookingsHistory.as_view(), name='get_bookings_history'),

path('confirm_bookings/<int:id>/', confirmBooking.as_view(), name='confirm_bookings'),

path('submit_package/<int:id>', SubmitPackage.as_view(), name='submit_package'),

path('get_booking_status_list', getBookingStatusList.as_view(), name='get_booking_status_list'),
path('update_booking_status/<int:id>', UpdateBookingStatus.as_view(), name='update_booking_status'),

path('add_booking_team/<int:booking_id>', addBookingTeam.as_view(), name='add_booking_team'),


path('get_packages/<int:id>', GetPackages.as_view(), name='get_packages'),

path('get_additional_services/<int:booking_id>', GetAdditionalServices.as_view(), name='get_additional_services'),
path('get_booked_services/<int:booking_id>', GetBookedServices.as_view(), name='get_booked_services'),


path('get_skills', GetShootCategory.as_view(), name='get_skills'),


path('get_services_invoice/<int:id>', GetServicesInvoice.as_view(), name='get_services_invoice'),

path('get_segment_service_admin', GetSegmentServicesAdmin.as_view(), name='get_segment_service_admin'),

path('get_segment_package_list', getSegmentPackageList.as_view(), name='get_segment_package_list'),
path('get_service_list', getServiceList.as_view(), name='get_service_list'),
path('get_additional_service_list', getAdditionalServiceList.as_view(), name='get_additional_service_list'),


path('get_package_section_list/<str:atr>', getPackageSectionList.as_view(), name='get_segment_package_list'),


path('add_service_admin', AddServicesAdmin.as_view(), name='add_service_admin'),
path('get_service_admin/<int:id>', GetServicesAdmin.as_view(), name='get_service_admin'),
path('update_service_admin/<int:id>', UpdateServicesAdmin.as_view(), name='update_service_admin'),
path('trash_service_admin/<int:id>', TrashServicesAdmin.as_view(), name='trash_service_admin'),
path('restore_service_admin/<int:id>', RestoreServicesAdmin.as_view(), name='restore_service_admin'),


path('add_additional_service_admin', AddAdditionalServicesAdmin.as_view(), name='add_additional_service_admin'),
path('get_additional_service_admin/<int:id>', GetAdditionalServicesAdmin.as_view(), name='get_additional_service_admin'),
path('update_additional_service_admin/<int:id>', UpdateAdditionalServicesAdmin.as_view(), name='update_additional_service_admin'),
path('trash_additional_service_admin/<int:id>', TrashAdditionalServicesAdmin.as_view(), name='trash_additional_service_admin'),
path('restore_additional_service_admin/<int:id>', RestoreAdditionalServicesAdmin.as_view(), name='restore_additional_service_admin'),

path('add_package_admin', AddPackageAdmin.as_view(), name='add_package_admin'),
path('get_package_admin/<int:id>', GetPackageAdmin.as_view(), name='get_package_admin'),

path('get_all_package_admin/<int:id>', GetAllPackageAdmin.as_view(), name='get_all_package_admin'),
path('update_package_admin/<int:id>', UpdatePackageAdmin.as_view(), name='update_package_admin'),

path('add_banner_video_admin', AddHomeBannerVideoAdmin.as_view(), name='add_banner_video_admin'),
path('get_banner_video_admin', GetHomeBannerVideoAdmin.as_view(), name='get_banner_video_admin'),
path('delete_banner_video_admin/<int:id>', DeleteHomeBannerVideoAdmin.as_view(), name='delete_banner_video_admin'),
path('add_showcase_image_admin', AddShowcaseImageAdmin.as_view(), name='add_showcase_image_admin'),
path('delete_showcase_image_admin/<int:id>', DeleteShowcaseImageAdmin.as_view(), name='delete_showcase_image_admin'),




#client
path('get_clients/<int:limit>/<int:page>', getClient.as_view(), name='get_clients'),


# payment
path('pending_payment/<int:bookingId>', PendingPayment.as_view(), name='pending_payment'),


# Team Member
path('get_team_member/<int:serviceId>', GetTeamMember.as_view(), name='get_team_member'),

# path('get_package_service_admin/<int:id>', GetPackageServicesAdmin.as_view(), name='get_package_service_admin'),

path('get_payment_list/<str:dateSelector>/<int:limit>/<int:page>', GetPaymentList.as_view(), name='get_payment_list'),
path('get_payment/<int:booking_id>', GetPayment.as_view(), name='get_payment'),
path('payment_submit/<int:id>', PaymentSubmit.as_view(), name='payment_submit'),

path('generate_invoice/<int:id>', GenerateInvoice.as_view(), name='generate_invoice'),


path('get_quotation_info/<int:bookingId>', getQuotationInfo.as_view(), name='get_quotation_info'),


path('generate_quotation/<int:id>/<int:discount>', GenerateQuotation.as_view(), name='generate_quotation'),
path('save_quotation/<int:id>', SaveQuotation.as_view(), name='save_quotation'),
path('email_quotation/<int:id>/<int:discount>', EmailQuotation.as_view(), name='email_quotation'),


path('console_dashboard', ConsoleDashboard.as_view(), name='console_dashboard'),


path('trash_camera_equipments_admin/<int:id>', TrashCameraEquipmentsAdmin.as_view(), name='trash_camera_equipments_admin'),
path('restore_camera_equipments_admin/<int:id>', RestoreCameraEquipmentsAdmin.as_view(), name='restore_camera_equipments_admin'),
path('get_camera_equipments_admin/<int:id>', GetCameraEquipmentsAdmin.as_view(), name='get_camera_equipments_admin'),
path('update_camera_equipments_admin/<int:id>', UpdateCameraEquipments.as_view(), name='update_camera_equipments_admin'),
path('add_camera_equipments_admin', AddCameraEquipmentsAdmin.as_view(), name='add_camera_equipments_admin'),



path('trash_production_process_admin/<int:id>', TrashProductionProcessAdmin.as_view(), name='trash_production_process_admin'),
path('restore_production_process_admin/<int:id>', RestoreProductionProcessAdmin.as_view(), name='restore_production_process_admin'),
path('get_production_process_admin/<int:id>', GetProductionProcessAdmin.as_view(), name='get_production_process_admin'),
path('update_production_process_admin/<int:id>', UpdateProductionProcess.as_view(), name='update_production_process_admin'),
path('add_production_process_admin', AddProductionProcessAdmin.as_view(), name='add_production_process_admin'),



path('trash_deliverables_admin/<int:id>', TrashDeliverablesAdmin.as_view(), name='trash_deliverables_admin'),
path('restore_deliverables_admin/<int:id>', RestoreDeliverablesAdmin.as_view(), name='restore_deliverables_admin'),
path('get_deliverables_admin/<int:id>', GetDeliverablesAdmin.as_view(), name='get_deliverables_admin'),
path('get_deliverables', GetDeliverables.as_view(), name='get_deliverables'),
path('update_deliverables_admin/<int:id>', UpdateDeliverables.as_view(), name='update_deliverables_admin'),
path('add_deliverables_admin', AddDeliverablesAdmin.as_view(), name='add_deliverables_admin'),



path('trash_terms_conditions_admin/<int:id>', TrashTermsConditionAdmin.as_view(), name='trash_terms_conditions_admin'),
path('restore_terms_conditions_admin/<int:id>', RestoreTermsConditionAdmin.as_view(), name='restore_terms_conditions_admin'),
path('get_terms_conditions_admin/<int:id>', GetTermsConditionAdmin.as_view(), name='get_terms_conditions_admin'),
path('update_terms_conditions_admin/<int:id>', UpdateTermsCondition.as_view(), name='update_terms_conditions_admin'),
path('add_terms_conditions_admin', AddTermsConditionAdmin.as_view(), name='add_terms_conditions_admin'),


path('create_reviews/<int:booking_id>', CreateReviews.as_view(), name='create_reviews'),
path('review_visibility/<int:review_id>', reviewVisibility.as_view(), name='review_visibility'),


# path('trash_shoot_category_admin/<int:id>', TrashShootCategoryAdmin.as_view(), name='trash_shoot_category_admin'),
# path('get_shoot_category_admin/<int:id>', GetShootCategoryAdmin.as_view(), name='get_shoot_category_admin'),
# path('update_shoot_category_admin/<int:id>', UpdateShootCategoryAdmin.as_view(), name='update_shoot_category_admin'),
# path('add_shoot_category_admin', AddShootCategoryAdmin.as_view(), name='add_shoot_category_admin'),



path('get_booking_ajax', GetBookingAjax.as_view(), name='get_booking_ajax'),
path('team_add_fund', teamAddFund.as_view(), name='team_add_fund'),
path('team_deposite', TeamDeposite.as_view(), name='team_deposite'),


path('create_walkin_client', CreateWalkinClient.as_view(), name='create_walkin_client'),
path('add_homepage_media', AddHomepageMedia.as_view(), name='add_homepage_media'),
path('image_gallery_upload', ImageGalleryUpload.as_view(), name='image_gallery_upload'),
path('get_homepage_media', GetHomepageMedia.as_view(), name='get_homepage_media'),

path('delete_homepage_media/<int:id>', DeleteHomepageMedia.as_view(), name='delete_homepage_media'),




# path('add_masterpiece_media', AddMasterpieceMedia.as_view(), name='add_masterpiece_media'),



path('get_shoot_date/<int:id>', getShootDate.as_view(), name='get_shoot_date'),
path('get_content_list/<str:title>/<int:limit>/<int:page>', GetContentList.as_view(), name='get_content_list'),
path('get_team_member_list', GetTeamMemberList.as_view(), name='get_team_member_list'),
path('get_team_member_payment_info/<int:user_id>', GetTeamMemberPaymentInfo.as_view(), name='get_team_member_payment_info'),
path('get_reviews_list/<str:dateSelector>/<int:limit>/<int:page>', GetReviewsList.as_view(), name='get_reviews_list'),




# path('vp', vp.as_view()),

# path('dashboard', api_login.as_view(), name='admin_login'),

]