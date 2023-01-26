from django.urls import path, include
from . import views
from booking.views import Devices

urlpatterns = [
    path('', views.home, name='home'),
    path('registration/', views.register, name = 'registration'),
    path('login/', views.signin, name = 'login'),
    path('logout/', views.signout, name = 'logout'),
    path('booking/', views.booking, name = 'booking'),

    path('get_bookings/', views.hotel_staff, name = 'hotel_personnel'),
    path('get_devices/', views.devices, name = 'devices'),
    path('get_rooms/', views.rooms, name = 'rooms'),
    path('edit/<int:id>/', views.edit, name='edit'),
    
    path('success/', views.success, name = 'success'),

    path('device/', Devices.as_view(), name = 'device'),
    path('api/accounts/', include('authemail.urls')),

    #consume iprestapi
    path('openhab/', views.openhabItems, name = 'openhab_items')
] 