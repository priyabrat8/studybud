from django.shortcuts import render,redirect
from .models import Room,Topic,Message,User
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import RoomForm,UserForm,MyUserCreationForm
# Create your views here.

# rooms =[
#     {'id':1,'name':"Let's learn python"},
#     {'id':2,'name':"Hi Django"},
#     {'id':3,'name':"React Developer"}
# ]

def home(request):
    q= request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    topics = Topic.objects.all()
    room_count = rooms.count()
    
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms':rooms,'topics':topics[:4],'room_count':room_count,'room_messages':room_messages}
    return render(request,'base/home.html',context)

@login_required(login_url='login')
def room(request,pk):
    room = Room.objects.filter(room_id=pk).first()
    messages = room.message_set.all().order_by('created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(user= request.user ,room=room ,body=request.POST.get('body'))
        room.participants.add(request.user)
        return redirect('room',pk=room.room_id)
    context = {'room':room,'room_messages':messages,'participants':participants}
    return render(request,'base/room.html',context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic , created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host= request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        return redirect('home')
        
    context = {'form':form,'sit':'Create','topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room = Room.objects.filter(room_id=pk).first()
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return redirect('home')
        
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic , created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form':form,'sit':'Update','topics':topics,'room':room}
    return render(request, 'base/room_form.html',context=context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.filter(room_id=pk).first()

    if request.user != room.host:
        return redirect('home')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request,'User does not exist')
        
        user = authenticate(request,email=email,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'Invalid Credential')        
    context = {'page':page}
    return render(request,'base/login_register.html',context)

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    page = 'register'
    if request.user.is_authenticated:
        return redirect('home')
    
    form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error accourd during registration')
    context = {'page':page,'form':form}
    return render(request,'base/login_register.html',context)

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.filter(msg_id=pk).first()

    if request.user != message.user:
        return redirect('home')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':message})

login_required(login_url='login')
def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context={'user':user,'rooms':rooms,'room_messages':room_message,'topics':topics}
    return render(request, 'base/profile.html',context)

login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES,instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile',pk=user.id)
    context = {"form":form}
    return render(request,'base/update-user.html',context)

def topicsPage(request):
    q= request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics':topics}
    return render(request,'base/topics.html',context)

def activityPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages':room_messages}
    return render(request,'base/activity.html',context)
