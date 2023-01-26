from ast import Dict
import datetime
from email.policy import default
from tabnanny import verbose
from typing import Any
from xml.dom import ValidationErr
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django_innohotel import settings

class CustomUserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, email, password = None, **extra_fields):
        now = timezone.now()
        
        if not email:
            raise ValueError('Please enter an email address')
        if not password:
            raise ValueError('Please enter a password')

        user = self.model(

            email = self.normalize_email(email),
           
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self, email, password = None, **extra_fields):
        user = self.create_user(
            email = self.normalize_email(email),
            password = password
        )
        user.set_password(password)
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        return user  
    
class User(AbstractBaseUser, PermissionsMixin):
    username = None
     
    email = models.EmailField(_("email address"), unique=True, max_length=255)
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default = False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    last_login = models.DateTimeField(_("last login"), default = timezone.now)

    is_verified = models.BooleanField(
        _('verified'), default=True,
        help_text=_('Designates whether this user has completed the email '
                    'verification process to allow login.'))

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class BookingStatusManager(models.Manager):
    def create_bookingstatus(self, booking_status):
        return BookingStatus(booking_status=booking_status)

class BookingStatus(models.Model):
    booking_status = models.CharField(_('Booking status'), max_length=255)
    class Meta:
        verbose_name = 'BookingStatuse'
        verbose_name_plural = 'BookingStatuses'

class RoomStatusManager(models.Manager):
    def create_roomstatus(self, room_status):
        return RoomStatus(room_status=room_status)

class RoomStatus(models.Model):
    OOO = 'OOO'
    READY = 'READY'
    CHECKED_IN = 'CHECKED-IN'
    OCCUPIED = 'OCCUPIED'
    ROOM_STATUS_CHOICES = [
        (OOO, 'OOO'),
        (READY, 'Ready'),
        (CHECKED_IN, 'Checked-in'),
        (OCCUPIED, 'Occupied'),
    ]
    room_status = models.CharField(_('Room status'), choices = ROOM_STATUS_CHOICES, default = OOO, max_length=10,)
    objects = RoomStatusManager()
    class Meta:
        verbose_name = 'RoomStatus'
        verbose_name_plural = 'RoomStatuses'
    def __str__(self):
        return self.room_status

# class HVACTypeManager(models.Manager):
#     def create_HVACType(self, HVAC_type):
#         return HVACType(HVAC_type=HVAC_type)

# class HVACType(models.Model):
#     HVAC_type = models.CharField(_('HVAC type'), max_length=255, unique=True)
#     objects = HVACTypeManager()
#     class Meta:
#         verbose_name = 'HVACType'
#         verbose_name_plural = 'HVACTypes'
#     def __str__(self):
#         return self.HVAC_type

# class RoomTypeManager(models.Manager):
#     def create_roomtype(self, room_type):
#         return RoomType(room_type=room_type)

# class RoomType(models.Model):
#     room_type = models.CharField(_('Room type'), max_length=255, unique=True)
#     objects = RoomTypeManager()
#     class Meta:
#         verbose_name = 'RoomType'
#         verbose_name_plural = 'RoomTypes'
#     def __str__(self):
#         return self.room_type

class BuildingManager(models.Manager):
    def create_building(self, building_name):
        return Building(building_name=building_name)

class Building(models.Model):
    building_name = models.CharField(_('Building name'), max_length=255, unique=True, default='Kecskemét_Pécsvárad_u')
    objects = BuildingManager()
    def __str__(self):
        return self.building_name
    class Meta:
        verbose_name = 'Building'
        verbose_name_plural = 'Buildings'
class BookingManager(models.Manager):
    def get_bookings(self):
        return Booking.objects.all()

    def create_booking(self, guest, checkin_date, checkout_date,arrival,leaving,first_name, last_name, booking_status, room_status):# room_number
       return Booking(guest=guest,
                      first_name=first_name,
                      last_name=last_name,
                      checkin_date=checkin_date,
                      checkout_date=checkout_date,
                      arrival=arrival,
                      leaving=leaving,
                      booking_status = booking_status,)
     
class Booking(models.Model):
    def Date_validation(value):
        if value < datetime.date.today():
            raise ValidationErr("The date cannot be in the past")

    CREATED = 'CREATED'
    CONFIRMED = 'CONFIRMED'
    CHECKED_IN = 'CHECKED-IN'
    CHECKED_OUT = 'CHECKED-OUT'
    BOOKING_STATUS_CHOICES = [
        (CREATED, 'Created'),
        (CONFIRMED, 'Confirmed'),
        (CHECKED_IN, 'Checked-in'),
        (CHECKED_OUT, 'Checked-out'),
    ]
    guest = models.ForeignKey('User', on_delete = models.CASCADE,) #'User'
    #booking = 
    first_name = models.CharField(_("first_name"), max_length=255)
    last_name = models.CharField(_("last_name"), max_length=255)
    checkin_date = models.DateField(_("checkin date"),default=datetime.date.today, validators=[Date_validation])
    checkout_date = models.DateField(_("checkout date"),default=datetime.date.today, validators=[Date_validation])
    arrival = models.TimeField(_("arrival"),)
    leaving = models.TimeField(_("leaving"),)
    booking_status = models.CharField(_("booking status"), choices=BOOKING_STATUS_CHOICES, default=CREATED, max_length=11)
    room_type = models.CharField(_('Room type'), max_length=255 )
    
    
    #room_status = models.ForeignKey(Room, on_delete= models.CASCADE, unique=True)
     #to_field='room_type'
    #room_number = models.ForeignKey(Room,on_delete = models.CASCADE, verbose_name=_('Room number'),)
    #room = models.ForeignKey(Room, on_delete = models.CASCADE, verbose_name=_('Room'), related_name='rooms', default="room-1")
    objects = BookingManager()
    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = 'Bookings'
    # def __str__(self):
    #         return self.guest
    def __str__(self):
       return str(self.guest)
    def list_of_bookings():
        bookings = list(Booking.objects.all())
        return bookings
    
class RoomManager(models.Manager):
    def create_room(self, room_number, booking , building, room_type, room_lights, room_tv,  HVAC, HVAC_type, TEMP, room_status):
        return Room(room_number=room_number, booking = booking, building=building, room_type = room_type, room_lights = room_lights, room_tv = room_tv,HVAC=HVAC, HVAC_type=HVAC_type, TEMP=TEMP, room_status=room_status)

class Room(models.Model):
    room_number = models.IntegerField(_('Room number'), unique=True,)
    booking = models.ForeignKey(
        'Booking',
        on_delete = models.CASCADE,
        default='guest@example.com',
        blank=True,#01-18 NEW
        null=True, #01-18 NEW
        related_name="bookings" #01-18 NEW Also deleted and remigrated rooms table
    )
    building = models.ForeignKey(Building, on_delete=models.CASCADE,)
    SINGLE = 'SINGLE'
    DOUBLE = 'DOUBLE'
    ROOM_TYPE_CHOICES = [
        (SINGLE, 'Single'),
        (DOUBLE, 'Double')
    ]
    room_type = models.CharField(_('Room type'), max_length=6, choices=ROOM_TYPE_CHOICES, default=SINGLE,)
    WELCOME ='WELCOME'
    OFF = 'OFF'
    USER = 'USER'
    ROOM_LIGHTS_CHOICES = [
        (WELCOME, 'Welcome'),
        (OFF, 'off'),
        (USER, 'user'),
    ]
    room_lights = models.CharField(_('Room lights'), max_length=7, choices=ROOM_LIGHTS_CHOICES, default=OFF)
    HELP = 'HELP'
    TV = 'TV'
    MUSIC = 'MUSIC'
    ROOM_TV_CHOICES = [
        (WELCOME, 'Welcome'),
        (HELP, 'help'),
        (TV, 'TV'),
        (MUSIC, 'music'),
    ] 
    room_tv = models.CharField(_('Room tv'), max_length=7, choices=ROOM_TV_CHOICES, default=WELCOME) 
   
    HVAC = models.IntegerField(_('HVAC'))
    COMFORT = 'COMFORT'
    FAST = 'FAST'
    HVAC_TYPE_CHOICES = [
        (COMFORT, 'Comfort'),
        (FAST, 'Fast')
    ]
    HVAC_type = models.CharField(max_length=7, choices=HVAC_TYPE_CHOICES, default=COMFORT)
    TEMP = models.IntegerField(_('Measured TEMP'))
    room_status = models.ForeignKey('RoomStatus',
                                     on_delete=models.CASCADE,
                                     default='OOO',
                                     blank=True,#01-18 NEW
                                     null=True, #01-18 NEW
                                     related_name="roomstatuses",)
    objects = RoomManager()
    # def __str__(self):S
    #     return self.room_number
    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'

    def __str__(self):
        room_number = str(self.room_number)
        return room_number
    def list_of_rooms():
        rooms = list(Room.objects.all())
        return rooms
    def string_list_of_rooms():
        string_list_of_rooms = []
        for room in Room.list_of_rooms():
            string_list_of_rooms.append("Room" + str(room.room_number))
        return string_list_of_rooms
    def room_statuses():
        #room_status = []
        list_of_room_statuses = []
        for room in Room.list_of_rooms:
            list_of_room_statuses.append(str(room.room_status))
        return list_of_room_statuses

class DeviceManager(models.Manager):
    def create_device(self, email, address):
        return Device(email, address)

class Device(models.Model):
    email = models.ForeignKey(User, on_delete = models.CASCADE)
    address = models.CharField(_("device_address"), unique=True, max_length=255)
    objects = DeviceManager()
    class Meta:
        verbose_name = "Device"
        verbose_name_plural = 'Devices'
    def get_address_by_email(email):
        address = User.objects.filter(email=email).first()
        return address



