import json
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required(login_url="login")
def groups(request):
    group=Group.objects.filter(members=request.user)
    if request.method=="POST":
      search=request.POST.get('search')
      group=Group.objects.filter(members=request.user,group_name__icontains=search).order_by("group_name")
    return render(request, 'groups.html', {"group": group})


def home(request):
    return render(request, "base.html")

@login_required(login_url="login")
def notification(request):
    return render(request,"notification.html")


@csrf_exempt
def create_group(request):
    if request.method == "POST":
        data = json.loads(request.body)
        groupname = data["groupname"]
        if Group.objects.filter(group_name=groupname).exists():
            return JsonResponse({"response": "This one is choosen.. Try different group name"}, safe=False)
        if not groupname.isalnum():
            return JsonResponse({"response": "groupname should be alphanumeric"}, safe=False)
        group_desc = data["groupdesc"]
        gpmembers = data["members"]
        gp_obj = Group(group_name=groupname,
                       creater=request.user, group_info=group_desc)
        gp_obj.save()
        gp_obj.members.add(request.user)
        for member in gpmembers:
            user_obj = User.objects.get(username=member)
            gp_obj.members.add(user_obj)
        messages.success(request, "group : created successfully....")
        return JsonResponse({"response": "successfully created group"}, safe=False)
    users = User.objects.all().exclude(username=request.user.username).order_by("username")
    return render(request, "create_group.html", {"users": users})

@login_required(login_url="login")
def contacts(request):
    contacts = User.objects.all().exclude(username=request.user.username).order_by("username")
    if request.method=="POST":
      search=request.POST.get('search')
      contacts=User.objects.filter(username__icontains=search).order_by("username")
    return render(request, 'contacts.html', {"contacts": contacts})

@login_required(login_url="login")
def socket(request, group_name):
    groupp= Group.objects.get(group_name=group_name, members=request.user)
    notifications=Notification.objects.filter(user_to=request.user,is_group=True,group=groupp)
    for notify in notifications:
        notify.is_seen=True
        notify.save()
    access = Group.objects.filter(group_name=group_name, members=request.user).exists()
        
    return render(request, 'socket.html', {"group_name": group_name, "group_access": access})

@login_required(login_url="login")
def personal(request, contact):
    user2=User.objects.get(username=contact)
    notifications=Notification.objects.filter(user_to=request.user,is_group=False, notify_by=user2)
    for notify in notifications:
        notify.is_seen=True
        notify.save()
    room_names = One_to_one_room.objects.filter(
        members__username=request.user) & One_to_one_room.objects.filter(members__username=contact)
    room_name=0
    for room in room_names:    
        room_name=room.group_name
        print(room_name)
    if not room_names.exists():
        room_names=One_to_one_room.objects.create(group_name=str(request.user.username + contact))
        room_names.save()
        room_names.members.add(request.user)
        
        room_names.members.add(user2)
        room_name=room_names.group_name
    return render(request, 'chat.html', {"group_name": room_name,"chat_with":contact})


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']
        if len(username) < 5:
            messages.error(
                request, " username mustbe greater than 10 characters")
            return render(request, 'signup.html')
        if not username.isalnum():
            messages.error(request, " username mustbe be alphanumeric")
            return render(request, 'signup.html')
        if pass1 != pass2:
            messages.error(request, " passwords not matching")
            return render(request, 'signup.html')

        elif len(username) >= 5 and username.isalnum() and pass1 == pass2:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.first_name = name
            myuser.save()
            messages.success(request, ' : user successfully created')
            return redirect('/login')
    return render(request, 'signup.html')


def handlelogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass3 = request.POST['password']
        # print(username,pass3)
        user = authenticate(username=username, password=pass3)
        if user is not None:
            login(request, user)
            messages.success(request, username+" successfully loged in ")
            return redirect("/")
        else:
            messages.error(request, "invalid credentials")
            return render(request, 'login.html')
    return render(request, 'login.html')


def handlelogout(request):
    logout(request)
    messages.success(request, " successfully loged out ")
    return redirect('/')

    # today i developed the login page signup page for poc and also implemented logic to handle the contacts and groups then while creating a new group I faced a chellenge that we cannot send multiple data through checkbox  for that i learned the ajax and implemented it harsh ask me to post the form data using javascript
