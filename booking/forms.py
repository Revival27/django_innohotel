from datetime import date
import datetime
from .models import User,Booking,Room
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput, DateTimePickerInput

class EditForm(forms.ModelForm):
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
    room_status = forms.ChoiceField(label = _("Room Status"), choices=ROOM_STATUS_CHOICES,)
    booking_status = forms.ChoiceField(label = _("Booking Status"), choices=BOOKING_STATUS_CHOICES,)
    class Meta:
        model = Booking
        fields = ('room_status', 'booking_status')

class DateInput(forms.DateInput):
    input_type = 'date'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.attrs.setdefault('min', '2020-01-01')
    # def get_context(self, name, value, attrs):
    #     print('date checkin attributes:' + attrs)
    #     attrs.setdefault('min', now().strftime('%Y-%m-%d'))
    #     return super().get_context(name, value, attrs)
    
class TimeInput(forms.TimeInput):
    input_type = 'time'
    # def get_context(self, name, value, attrs):
    #     attrs.setdefault('min', now().strftime('%Y-%m-%d'))
    #     return super().get_context(name, value, attrs)
    

class BookingForm(forms.ModelForm):
    guest = User #help_text = 'Required. Add a valid email address'
    first_name = forms.CharField(label = _("First Name"))
    last_name = forms.CharField(label = _("Last Name"))
    SINGLE = 'S'
    DOUBLE = 'D'
    ROOM_TYPE_CHOICES = [
        (SINGLE, 'Single'),
        (DOUBLE, 'Double')
    ]
    room_type = forms.ChoiceField(label = _("Room Type"), choices=ROOM_TYPE_CHOICES)
    class Meta:
        model = Booking
        fields = ('guest', 'first_name', 'last_name', 'checkin_date', 'checkout_date','arrival', 'leaving', 'room_type')
        widgets = {
            'checkin_date': DateInput(attrs={'type':'date', 'min': now().strftime('%Y-%m-%d'), }),
            'checkout_date': DateInput(attrs={'type': 'date', 'min' : now().strftime('%Y-%m-%d'), }),
            'arrival': TimeInput(),
            'leaving': TimeInput(),
        }
        
    def clean(self):

        checkin = self.cleaned_data['checkin_date']
        checkout = self.cleaned_data['checkout_date']
        if checkout <= checkin:
            raise forms.ValidationError("The selected checkout date must be after your check-in!")
        
 

class LoginForm(forms.ModelForm):
    password = forms.CharField(label = 'Password', widget = forms.PasswordInput)
        
    class Meta:
        model = User
        fields = ('email', 'password')
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if not authenticate(email = email, password = password):
            raise forms.ValidationError("Invalid login")
            
    # User = get_user_model()
    # User.get_username = forms.EmailField(label='Email')
    
class RegisterForm(UserCreationForm):
    email = forms.EmailField(label = _("Email"), help_text = 'Required. Add a valid email address')
    # def clean_email(self):
    #     """
    #     Clean form email.
    #     :return str email: cleaned email
    #     :raise ValidationError: Email is duplicated
    #     """
    #     # Since EmailUser.email is unique, this check is redundant,
    #     # but it sets a nicer error message than the ORM. See #13147.
    #     email = self.cleaned_data["email"]
    #     try:
    #         User._default_manager.get(email=email)
    #     except get_user_model().DoesNotExist:
    #         return email
    #         raise ValidationError(
    #         self.error_messages["duplicate_email"],
    #         code="duplicate_email",
    #      )
    
    class Meta:
        model = User
        fields = ('email','password1','password2')