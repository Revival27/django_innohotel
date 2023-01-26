import json
import requests
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import Permission
from booking.decorators import unauthenticated_user
from .forms import LoginForm, RegisterForm, BookingForm, EditForm

from .models import Device, User, Booking, Room
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DeviceSerializer
from django.http import HttpResponse
from django.template import loader

from django.db.models import Q

class Openhab(APIView):
    def get(self, request, *args, **kwargs):
        return Response()

class Devices(APIView):

    def get(self, request, *args, **kwargs):
        try:
            email = request.query_params['email']
            print(email)
            if email != None:
                str_email=str(email)
                number_of_digits = len(str_email)
                print(number_of_digits)
                guest_id = 'inno-'+ str_email

            deviceuser=User.objects.get(id=email)
            print(deviceuser)
            device, created = Device.objects.get_or_create(email=deviceuser, address = guest_id)
            serializer = DeviceSerializer(device)
        except Device.DoesNotExist:
            print("Device does not exist. Listing All Devices")
            devices = Device.objects.all()
            serializer = DeviceSerializer(devices, many = True)
        return Response({'device': serializer.data})

    # def post(self, request, format=None):
    #     serializer = SnippetSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def home(request):
    return render(request, "index.html", {'name': "Innohotel Booking System"})
def success(request):
    return render(request, "success.html",)
def booking(request):
    #Logic here if user is loggedin !require email else redirect to register
    #if request.user.is_authenticated:
    #return "Please register before booking!"
    context = {}
    #if request.user.is_authenticated:
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            #booking = Booking.objects.get(id=id)
            return render(request, 'success.html')
            #Do something if booking sform was submitted else let form be bookingform and add bookingform to context
        # else:
        #     return render(request, 'response/error.html')
    else:
        form = BookingForm()
    context["booking_form"] = form
    return render(request, 'booking.html', context)

#@hotel_staff
def hotel_staff(request):
    hotel_staff_context = {}
    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_staff or request.user.is_superuser:
           bookings = Booking.objects.all()

           rooms = Room.objects.get(id=1)
           hotel_staff_context['bookings'] = bookings
           hotel_staff_context['room_ids'] = Room.objects.values_list('id', flat=True)
           #hotel_staff_context['users'] = User.objects.get(id=1)
        #    for bookingid in bookings_id:
        #     print(bookingid)

           hotel_staff_context['rooms'] = rooms
           #print(hotel_staff_context.get('rooms'))
           return render(request, "hotel_personnel.html", hotel_staff_context)
        else:
           return redirect("home")
    return redirect("home")

def edit(request, id):
    edit_context = {}
    booking = Booking.objects.get(id=id)
    room = Room.objects.get(id=id)
    edit_context['booking'] = booking
    form = EditForm(instance=booking)
    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_staff or request.user.is_superuser:
            if request.method == 'POST':
             form = EditForm(request.POST, instance=booking)
             if form.is_valid():
                form.save()
                return redirect('hotel_personnel')
             else:
                return print("form is not valid")
            else:
                edit_context['edit_form'] = EditForm()
                return render(request, "edit.html", edit_context)
    else:
        return redirect("home")

def devices(request):
    context = {}
    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_staff or request.user.is_superuser:
           devices = Device.objects.all()

           context['devices'] = devices
           return render(request, "hotel_personnel.html", context)
        else:
           return redirect("home")
    return redirect("home")

def rooms(request):
    context = {}
    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_staff or request.user.is_superuser:
           rooms = Room.objects.all()

           context['rooms'] = rooms
           return render(request, "hotel_personnel.html", context)
        else:
           return redirect("home")
    return redirect("home")

@unauthenticated_user
def register(request):
    context = {}
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')

            #Give sigend up user a group name
            #group = Permission.objects.get("name")
            #user.groups.add(group)

            user = authenticate(email = email, password = raw_password)
            login(request, user)
            return redirect('home')
        else:
            context['registration_form'] = form
    else:
        form = RegisterForm()
        context['registration_form'] = form
    return render(request, "register.html", context)

@unauthenticated_user
def signin(request):
    context = {}
    user = request.user

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            try:
                user = authenticate(email = email, password = password)
            #device = Device.objects.get_or_create(email, a)
            except:
               HttpResponse("Invalid credentials", status.HTTP_500_INTERNAL_SERVER_ERROR)
        if user:
            try:
                login(request, user)
                return redirect("home")
            except:
               HttpResponse("Invalid credentials", status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        form = LoginForm()
    context['login_form'] = form
    return render(request, "login.html", context)

def signout(request):
    logout(request)
    return redirect('home')

#Consume rest api in django application
def openhabItems(request):
    itemsBaseURL = 'http://127.0.0.1:8080/rest/items'
    # itemsBaseURL = 'https://home.myopenhab.org/rest/items'
    headersGetItem = {'Authorization': 'Bearer oh.innohotel.4TZyP70PQ1BKlu0gdRDafJfFtCmwKXx5WlFsWFZejceLe7X0SjrMYdBW4ng8m7pfS7UeqJ0ESYDRUGkrRfk4A'}
    headersPutState = {'Authorization': 'Bearer oh.innohotel.4TZyP70PQ1BKlu0gdRDafJfFtCmwKXx5WlFsWFZejceLe7X0SjrMYdBW4ng8m7pfS7UeqJ0ESYDRUGkrRfk4A',
                       'Content-Type':'text/plain'}
    headersPutJSON = {'Authorization': 'Bearer oh.innohotel.4TZyP70PQ1BKlu0gdRDafJfFtCmwKXx5WlFsWFZejceLe7X0SjrMYdBW4ng8m7pfS7UeqJ0ESYDRUGkrRfk4A',
                       'Content-Type':'application/json'}
    # headersGetItem = {'Cookie':'__utmz=211485577.1674555907.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=211485577.2060927058.1674555907.1674564450.1674720051.3; CloudServer=192.168.142.10%3A3001; X-OPENHAB-AUTH-HEADER=true; X-OPENHAB-SESSIONID=c2361afb-c1ee-494f-bb17-fb5cee3b706b',
    #                   'X-OPENHAB-TOKEN':'eyJraWQiOm51bGwsImFsZyI6IlJTMjU2In0.eyJpc3MiOiJvcGVuaGFiIiwiYXVkIjoib3BlbmhhYiIsImV4cCI6MTY3NDc0MDMzMCwianRpIjoicmtqVHkyZkpxdUdVdVV3Y2ZKTWxYUSIsImlhdCI6MTY3NDczNjczMCwibmJmIjoxNjc0NzM2NjEwLCJzdWIiOiJhZG1pbiIsImNsaWVudF9pZCI6Imh0dHBzOi8vaG9tZS5teW9wZW5oYWIub3JnIiwic2NvcGUiOiJhZG1pbiIsInJvbGUiOlsiYWRtaW5pc3RyYXRvciJdfQ.dYDbdriElswsi6xynPTdBWdGCPm60f4YsCSdPA26XQkvsqOHgp1N6sKZQ_ESfI9uX1Y3qyNZfSYYTCUHMwasGTmRN-DoIk8vfKAYXBjzgixTp6rdxxSmTS9rTNrBNOJTPiU283_6HGh1ej-Zs0SXveUQeDuGILMLDl0diCkDTLmlN-GpvXm5Yf-PF2l_qwI8WGse8Nt0pnqljODKT0t6rD0gcCVg4gI_oOEcmC6BzVX4N4lHdKtssMGP-gNWyy0Glr6GBwUT5bXCarIe1xIs78Xy16LYvBcgwZqW2I405Rk_kqKNmbT_fMNgM1NXI_eT22PDabAFShjFxxTJM-E03A',
    #  }
    # headersPutJSON = {'Cookie':'__utmz=211485577.1674555907.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=211485577.2060927058.1674555907.1674564450.1674720051.3; CloudServer=192.168.142.10%3A3001; X-OPENHAB-AUTH-HEADER=true; X-OPENHAB-SESSIONID=c2361afb-c1ee-494f-bb17-fb5cee3b706b',
    #                    'X-OPENHAB-TOKEN':'eyJraWQiOm51bGwsImFsZyI6IlJTMjU2In0.eyJpc3MiOiJvcGVuaGFiIiwiYXVkIjoib3BlbmhhYiIsImV4cCI6MTY3NDc0MDMzMCwianRpIjoicmtqVHkyZkpxdUdVdVV3Y2ZKTWxYUSIsImlhdCI6MTY3NDczNjczMCwibmJmIjoxNjc0NzM2NjEwLCJzdWIiOiJhZG1pbiIsImNsaWVudF9pZCI6Imh0dHBzOi8vaG9tZS5teW9wZW5oYWIub3JnIiwic2NvcGUiOiJhZG1pbiIsInJvbGUiOlsiYWRtaW5pc3RyYXRvciJdfQ.dYDbdriElswsi6xynPTdBWdGCPm60f4YsCSdPA26XQkvsqOHgp1N6sKZQ_ESfI9uX1Y3qyNZfSYYTCUHMwasGTmRN-DoIk8vfKAYXBjzgixTp6rdxxSmTS9rTNrBNOJTPiU283_6HGh1ej-Zs0SXveUQeDuGILMLDl0diCkDTLmlN-GpvXm5Yf-PF2l_qwI8WGse8Nt0pnqljODKT0t6rD0gcCVg4gI_oOEcmC6BzVX4N4lHdKtssMGP-gNWyy0Glr6GBwUT5bXCarIe1xIs78Xy16LYvBcgwZqW2I405Rk_kqKNmbT_fMNgM1NXI_eT22PDabAFShjFxxTJM-E03A',
    #                    'Content-Type':'application/json'}
    # headersPutState = {'Cookie':'__utmz=211485577.1674555907.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=211485577.2060927058.1674555907.1674564450.1674720051.3; CloudServer=192.168.142.10%3A3001; X-OPENHAB-AUTH-HEADER=true; X-OPENHAB-SESSIONID=c2361afb-c1ee-494f-bb17-fb5cee3b706b',
    #                    'X-OPENHAB-TOKEN':'eyJraWQiOm51bGwsImFsZyI6IlJTMjU2In0.eyJpc3MiOiJvcGVuaGFiIiwiYXVkIjoib3BlbmhhYiIsImV4cCI6MTY3NDc0MDMzMCwianRpIjoicmtqVHkyZkpxdUdVdVV3Y2ZKTWxYUSIsImlhdCI6MTY3NDczNjczMCwibmJmIjoxNjc0NzM2NjEwLCJzdWIiOiJhZG1pbiIsImNsaWVudF9pZCI6Imh0dHBzOi8vaG9tZS5teW9wZW5oYWIub3JnIiwic2NvcGUiOiJhZG1pbiIsInJvbGUiOlsiYWRtaW5pc3RyYXRvciJdfQ.dYDbdriElswsi6xynPTdBWdGCPm60f4YsCSdPA26XQkvsqOHgp1N6sKZQ_ESfI9uX1Y3qyNZfSYYTCUHMwasGTmRN-DoIk8vfKAYXBjzgixTp6rdxxSmTS9rTNrBNOJTPiU283_6HGh1ej-Zs0SXveUQeDuGILMLDl0diCkDTLmlN-GpvXm5Yf-PF2l_qwI8WGse8Nt0pnqljODKT0t6rD0gcCVg4gI_oOEcmC6BzVX4N4lHdKtssMGP-gNWyy0Glr6GBwUT5bXCarIe1xIs78Xy16LYvBcgwZqW2I405Rk_kqKNmbT_fMNgM1NXI_eT22PDabAFShjFxxTJM-E03A',
    #                    'Content-Type':'text/plain'}
    itemsResponse = requests.get(itemsBaseURL, headers=headersGetItem)
    openhab_items = itemsResponse.json()

    rooms = Room.list_of_rooms()
    bookings = Booking.list_of_bookings()
    #Create string array of existing room names from list of Rooms
    room_name_arr = Room.string_list_of_rooms()
    #room_status_arr = Room.room_statuses()

    
    #Create string list of openhab rooms   

    # Cleanup of openhab room items
    # Iterate through room objects to see how many rooms to create in openhab
    number_of_rooms_in_openhab = requests.get(itemsBaseURL, headers=headersGetItem)
    number_of_items_in_openhab = number_of_rooms_in_openhab.json()
    print(len(number_of_items_in_openhab))
    openhab_name_arr = []
    number_of_rooms = 0
    for item in openhab_items:
        for item_value in item:
            if "name" in item_value:
                if "Room" in item[item_value]:
                    print("NAMAEWA:   ",item[item_value])
                    openhab_name_arr.append(str(item[item_value]))

    #Here comes delete room in openhab if not exists in webserver                 
    for room in openhab_name_arr:
        if room in room_name_arr:
            print("Room exists in both arrays")      
        else:
            print("Room not exists")
            delete_room = requests.delete(itemsBaseURL + "/" + room, headers=headersGetItem)
            print(str(delete_room))
    

    roomsJSON = serializers.serialize('json', rooms)
    print(roomsJSON)

    
    bookingsJSON = serializers.serialize('json', bookings)
    countRooms=0
    countBookings=0
    for item in openhab_items:
        #print(item)
        for key in item:
           # print(key, '->', item[key])
            if key == "name":
                if "Room" in item[key]: 
                    countRooms += 1
                    print("FOUND ROOM, roomCount=", countRooms)
                if "CheckIn" in item[key]:
                    countBookings +=1
                    print("FOUND BOOKING WITH CHECKIN,CHEKOUT: countBookings=", countBookings)
    print("FOUND ROOMS: counter=",countRooms)

    openhabBookings = []
    openhabRooms = []
    roomWithBooking = []
    for room in rooms:
        booking_id = room.booking_id
        print("Room:",room.id ,"room.room_number", room.room_number, "booking.id:", room.booking_id)
        if(len(rooms) > 0):
            numberOfRooms = len(rooms)
        openhabRoom = {"type": "Group","name": "Room"+str(room.room_number),"label": "","category": "","tags": [""],"groupNames": [""],"groupType": "",
                        "function": {"name": "","params": [""]}}
        if room.booking_id != None:
            roomWithBooking.append({room.id:room.booking_id})
        print("Rooms with booking_ids:", roomWithBooking)
        # for room in roomWithBooking:
        #     for value in room:
        #         if value != 0:
        #             print("ROOM ID IN roomWithBooking:", key)
        openhabRooms.append(openhabRoom)
        
        print(openhabRooms)
        #openhabRoomsNames ="Room"+str(room.room_number)
    print("OPENHAB ROOM openhab_items        :", openhabRooms)
    booking_ids=[]
    for booking_id in roomWithBooking:
            for key in booking_id:
                # if key == "id":
                    #print("Room with Booking has this id:",booking.id)
                    print("TRUE,",booking_id[key])
                    booking_ids.append(booking_id[key])
    checkInDict= []
    checkOutDict= []
    ChekinItemName, ChekinItemDateTime, CheckinItemUrl = "", "", ""            
    ChekoutItemName, ChekoutItemDateTime, CheckoutItemUrl = "", "", ""  
    openhabBookings = []
    roomStatuses = []
    # openhabBookingCheckin = json()
    # openhabBookingCheckout = json()
    for booking in bookings:
        print('GUEST ID',booking.guest_id,'BOOKING CHECKIN',booking.checkin_date,'BOOKING CHECKOUT',booking.checkout_date, "Arrival", booking.arrival, "Booking leaving", booking.leaving)
        
        
        if(len(bookings) > 0 ):
            for theIdWithRoom in booking_ids:                 
              if theIdWithRoom == booking.id:
                print("FINALLY TH ID IDDDSS is",booking.id,"TO ",booking.checkin_date, "AND", booking.checkout_date)
                ChekinItemName = "CheckIn" + str(booking.id)
                ChekinItemDateTime = str(booking.checkin_date)+""+str(booking.arrival)
                CheckinItemUrl = "/" + ChekinItemName + "/"
                ChekoutItemName = "CheckOut" + str(booking.id)
                ChekoutItemDateTime = str(booking.checkout_date)+"T"+str(booking.leaving) 
                CheckoutItemUrl = "/" + ChekoutItemName + "/"
                StateItemName = "RoomStatus" + str(booking.id)
                StateItemUrl = "/" + StateItemName + "/"
                #stateItemList.a

                checkInDict.append({ChekinItemName:{ChekinItemDateTime, CheckinItemUrl}})
                checkOutDict.append({ChekoutItemName:{ChekoutItemDateTime, CheckoutItemUrl}})
                openhabBookingCheckin = {"type": "String","name": "CheckIn" + str(booking.id),"label": "","category": "","tags": [""],"groupNames": [""],
                             "groupType": "","function": {"name": "","params": [""]}}
            
                openhabBookingCheckout = {"type": "String","name": "CheckOut" + str(booking.id),"label": "","category": "","tags": [""],"groupNames": [""],
                             "groupType": "","function": {"name": "","params": [""]}}
                openhabReadyState = {"type": "String","name": "RoomStatus" + str(booking.id),"label": "READY","category": "","tags": [""],"groupNames": [""],
                             "groupType": "","function": {"name": "","params": [""]}}
            
                openhabBookings.append(openhabBookingCheckin)
                openhabBookings.append(openhabBookingCheckout)
                roomStatuses.append(openhabReadyState)
    #~ˇ~ˇ~ˇ~ˇ~ˇ~ˇ~ˇ~Send request to create item list of rooms to OpenHAB~ˇ~ˇ~ˇ~ˇ~ˇ~ˇ~ˇ~
    #if countRooms <= 0:
    roomsResponse = requests.put(itemsBaseURL, json = openhabRooms, headers = headersPutJSON)
    #Here comes send room status to openhab rooms
    roomStatusResponse = requests.put(itemsBaseURL, json =roomStatuses, headers = headersPutJSON)
    #~ˇ~ˇ~ˇ~ˇ~ˇ~ˇ~ˇ~Send request to create DateTiem item list of corresponding bookings to OpenHAB~ˇ~ˇ~ˇ~ˇ~ˇ~ˇ~ˇ~   
    
    bookingResponse = requests.put(itemsBaseURL, json = openhabBookings, headers = headersPutJSON)
    print("CHEKIN DICT", checkInDict)
    print("CHEKOUT DICT", checkOutDict)
    checkinURL = itemsBaseURL + CheckinItemUrl + "state"
    createCheckinResponseUrl = []
    createCheckinResponseDate = []
    createCheckoutResponseUrl = []
    createCheckoutResponseDate = []
    for checkin in checkInDict:
        for key in checkin:
            for value in checkin[key]:
                print(value)
                if "/" in value:
                    checkinResponseUrlStr = itemsBaseURL + value + "state/"
                    createCheckinResponseUrl.append(checkinResponseUrlStr)
                if "-" in value:
                    chekinResponseDate = value
                    createCheckinResponseDate.append(chekinResponseDate)
    for checkout in checkOutDict:
        for key in checkout:
            for value in checkout[key]:
                print(value)
                if "/" in value:
                    checkoutResponseUrlStr = itemsBaseURL + value + "state/"
                    createCheckoutResponseUrl.append(checkoutResponseUrlStr)
                if "-" in value:
                    checkoutResponseDate = value
                    createCheckoutResponseDate.append(checkoutResponseDate)
    numbersOfChekinResponsesToSend = len(createCheckinResponseUrl)
    print("Length of createCheckinResponseUrl: ", numbersOfChekinResponsesToSend)
    while numbersOfChekinResponsesToSend >= 0:
            print("Created checkin url: ",createCheckinResponseUrl)
            print("Created checkout url: ",createCheckoutResponseUrl)
            print("Counter to send requests: ",numbersOfChekinResponsesToSend)
            numbersOfChekinResponsesToSend = numbersOfChekinResponsesToSend-1
            print("round is ", numbersOfChekinResponsesToSend)
            requests.put(createCheckinResponseUrl[numbersOfChekinResponsesToSend], data = createCheckinResponseDate[numbersOfChekinResponsesToSend], headers = headersPutState)
            requests.put(createCheckoutResponseUrl[numbersOfChekinResponsesToSend], data = createCheckoutResponseDate[numbersOfChekinResponsesToSend], headers = headersPutState)
            requests.put()
            #print(checkinResponseUrlStr)
            #createCheckinResponse.append(checkinResponseUrlStr)
            #put()
    print(createCheckinResponseUrl)
    print(createCheckinResponseDate)
    chekinResponse = requests.put(itemsBaseURL + CheckinItemUrl + "state" , data = ChekinItemDateTime, headers = headersPutState)
    chekoutResponse = requests.put(itemsBaseURL + CheckoutItemUrl + "state", data = ChekoutItemDateTime, headers = headersPutState)
        #dateOfBookingResponse = requests.put(baseURL + "/CheckIn"+ str(),)
   
    #  /items/{itemName}/members/{memberItemName} 
    # Adds a new member to a group item.
    for room in roomWithBooking:
        print(roomWithBooking)
        for key in room:
            print(str(key))
            print(room[key])
            url = "/Room"+ str(key)+"/members/CheckIn"+str(room[key])+"/"
            print(url)
            addDateToRoomResponse = requests.put(itemsBaseURL + "/Room"+ str(key)+"/members/CheckIn"+str(room[key])+"/", headers = headersPutState)
            requests.put(itemsBaseURL + "/Room"+ str(key)+"/members/CheckOut"+str(room[key])+"/", headers = headersPutState)
            
            
            requests.put(itemsBaseURL + "/Room"+ str(key)+"/members/RoomStatus"+str(room[key])+"/", headers = headersPutState)
  
    # bookings = Booking.objects.filter(id__in=[Booking.id for booking in
    #     Booking.objects.all()()])[::1]
    #return HttpResponse(items)
    #return HttpResponse(roomsResponse)
    #return render(request, 'items.html',{'items':items})
    # print(ChekinItemName)
    # print(ChekinItemDateTime+"T00:00:00.000")
    # print(checkinURL)
    # print(ChekoutItemName)
    # print(ChekoutItemDateTime+"T00:00:00.000")
    # print(CheckoutItemUrl)
    #return render(request, 'items.html',{'items':items})
    return HttpResponse(str(bookingResponse))

