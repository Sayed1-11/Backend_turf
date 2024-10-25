from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from User.views import UserViewset,UserProfileUpdateViewset,AdminUserSignupViewSet
from rest_framework.authtoken.views import obtain_auth_token
from Turf.views import TurfViewSet,SportsViewSet,TimeSlotViewSet,PriceViewSet,SportFieldViewSet,FacilitiesViewSet,TimeSlotEligibilityViewSet,FieldTypeChoicesView,ReviewViewSet
from Slot.views import BadmintonSlotViewSet,TurfSlotViewSet,SwimmingSessionViewSet,SwimmingSlotViewSet,SlotHistoryViewSet
from Booking.views import TurfBookingViewSet, BadmintonBookingViewSet, SwimmingBookingViewSet,Booking_history
from Booking.views import aamarpay_callback, payment_success, payment_failure,MyBookingsViewSet

router = DefaultRouter()
router.register(r"user",UserViewset,basename="user")
router.register(r"user-update",UserProfileUpdateViewset,basename="update")
router.register(r"turfs", TurfViewSet, basename="turfs")
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r'sports', SportsViewSet)
router.register(r'facilities', FacilitiesViewSet)
router.register(r'My_bookings', MyBookingsViewSet,basename='MyBookings')
router.register(r'slot-history', SlotHistoryViewSet, basename='slot-history')
router.register(r'time-slots', TimeSlotViewSet)
router.register(r'booking-history', Booking_history, basename='booking-history')
router.register(r'Booking', TurfBookingViewSet)
router.register(r'admin_signup', AdminUserSignupViewSet, basename='admin-signup')
router.register(r'Badminton', BadmintonBookingViewSet)
router.register(r'Swimming_booking', SwimmingBookingViewSet)
router.register(r'prices', PriceViewSet)
router.register(r'sport-fields', SportFieldViewSet)
router.register(r'time_eligibilty', TimeSlotEligibilityViewSet)
router.register(r'TurfSlot', TurfSlotViewSet)
router.register(r'Swimming_sessions', SwimmingSessionViewSet)
router.register(r'Swimming', SwimmingSlotViewSet)
router.register(r'Badminton_slot', BadmintonSlotViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api-auth/",include("rest_framework.urls")),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('field-types/', FieldTypeChoicesView.as_view(), name='field-types'),
    path('payment/callback/', aamarpay_callback, name='aamarpay_callback'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/failure/', payment_failure, name='payment_failure'),
    
]

urlpatterns += router.urls
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
