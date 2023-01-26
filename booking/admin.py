from django.contrib import admin
from .models import User, Device, Booking, Room, RoomStatus, Building
from django.utils.translation import gettext_lazy as _

admin.site.register(User)
admin.site.register(Device)
admin.site.register(Booking)
admin.site.register(Room)
admin.site.register(RoomStatus)
admin.site.register(Building)
# Register your models here.


