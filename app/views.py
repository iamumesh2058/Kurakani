from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Room, Topic, Message, User
from .form import RoomForm, UserForm, MyUserCreationForm
from django.http import HttpResponse


# Create your views here.
def userLogin(request):
    page = 'login'
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
        except:
            messages.error(request, 'This user doesnot exist')
            return redirect('login')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email and password not matched.')
            return redirect('login')

    context = {'page':page}
    return render(request, 'login.html', context)


def userLogout(request):
    request.user.is_active = False
    request.user.save()
    logout(request)
    return redirect('home')


def userRegister(request):
    form = MyUserCreationForm()
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.usernmae = user.username.lower()
            user.save()
            return redirect('login')
        else:
            messages.error(request, 'Error during registration.')
            return redirect('register')

    context = {'form':form}
    return render(request, 'signup.html', context)


def profile(request, pk):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    user = User.objects.get(id=pk)
    rooms = user.room_set.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(description__icontains = q) 
    )
    topics = Topic.objects.all()
    room_messages = user.message_set.all()
    context = {'user': user, 'rooms':rooms, 'topics':topics, 'room_messages':room_messages}
    return render(request, 'profile.html', context)


@login_required(login_url='login')
def updateUser(request, pk):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form' : form}

    return render(request, 'update-user.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    room_count = Room.objects.all().count()
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(description__icontains = q) 
    )
    topics = Topic.objects.all()[0:5]
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))
    context = {'page':'home', 'rooms':rooms, 'topics':topics, 'room_messages':room_messages, 'room_count': room_count}
    return render(request, 'index.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    
    participants = room.participants.all()
    if request.method == "POST":
        room_message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('room_message')
        )

        room.participants.add(request.user)
        return redirect('room', pk = room.id)
    context = {'room':room, "room_messages":room_messages, "participants":participants}
    return render(request, 'room.html', context)


@login_required(login_url='login')
def createRoom(request):
    page = 'create-room'
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
    
        return redirect('home')

    context = {'form':form, 'topics':topics, 'page': page}
    return render(request, 'create-room.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse("You are not allowed here.")
    

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        
    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'create-room.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed here.")
    
    if request.method == "POST":
        room.delete()
        return redirect('home')
        
    context = {'obj':room}
    return render(request, 'delete.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("You are not allowed here.")
    
    if request.method == "POST":
        message.delete()
        return redirect('room', pk=message.room.id)
    context = {'obj':message}
    return render(request, 'delete.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(
        Q(name__icontains = q)
    )
    context = {'topics':topics}
    return render(request, 'topics.html', context)


def activityPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages':room_messages}
    return render(request, 'activity.html', context)