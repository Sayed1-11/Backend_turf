"""
URL configuration for Backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from User.views import UserViewset,UserProfileUpdateViewset
from rest_framework.authtoken.views import obtain_auth_token
from Turf.views import TurfViewSet,SportsViewSet,TimeSlotViewSet,PriceViewSet,SportFieldViewSet,FacilitiesViewSet,TimeSlotEligibilityViewSet,FieldTypeChoicesView
from Slot.views import BadmintonSlotViewSet,TurfSlotViewSet,SwimmingSessionViewSet,SwimmingSlotViewSet
from Booking.views import TurfBookingViewSet, BadmintonBookingViewSet, SwimmingBookingViewSet

router = DefaultRouter()
router.register(r"user",UserViewset,basename="user")
router.register(r"update",UserProfileUpdateViewset,basename="update")
router.register(r"turfs", TurfViewSet, basename="turfs")
router.register(r'sports', SportsViewSet)
router.register(r'facilities', FacilitiesViewSet)
router.register(r'time-slots', TimeSlotViewSet)
router.register(r'Booking', TurfBookingViewSet)
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
]

urlpatterns += router.urls
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)