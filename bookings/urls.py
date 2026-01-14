from rest_framework.routers import DefaultRouter

from bookings.views import BookingViewSet, RoomViewSet

router = DefaultRouter()
router.register("rooms", RoomViewSet, basename="room")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = router.urls
