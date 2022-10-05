from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from django.http import HttpResponse
from datetime import date

import datetime
import json

from .models import Event, Profile, Ticket
from .forms import EventForm, UserForm, ProfileForm, AddMoneyForm, WithdrawMoneyForm, BuyTicketForm

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'event/login.html')
    else:
        events = Event.objects.all()
        query = request.GET.get("query")
        if query:
            events = events.filter(
                Q(name__icontains=query) |
                Q(manager__first_name__icontains=query) |
                Q(manager__last_name__icontains=query)
            ).distinct()
            return render(request, './event/home.html', {
                'user': request.user,
                'events': events,
                'query': query,
            })
        else:
            return render(request, './event/home.html', {
                'user': request.user,
                'events': events,
                'query': query,
            })


def register(request):
    register_form = UserForm(request.POST or None, prefix="register")
    profile_form = ProfileForm(request.POST or None, request.FILES or None, prefix="profile")
    if register_form.is_valid() and profile_form.is_valid():
        user = register_form.save(commit=False)
        username = register_form.cleaned_data['username']
        password = register_form.cleaned_data['password']
        user.set_password(password)
        user.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.wallet_balance = 0
        profile.image = profile_form.cleaned_data['image']
        file_type = profile.image.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in IMAGE_FILE_TYPES:
            context = {
                'register_form': register_form,
                'profile_form': profile_form,
                'error_message': 'Image file must be PNG, JPG, or JPEG',
            }
            return render(request, 'event/register.html', context)
        profile.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                events = Event.objects.all()
                return render(request, 'event/home.html', {'events': events, 'user': user})
    context = {
        "register_form": register_form,
        "profile_form": profile_form,
    }
    return render(request, 'event/register.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                events = Event.objects.all()
                return render(request, 'event/home.html', {'events': events, 'user': user})
            else:
                return render(request, 'event/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'event/login.html', {'error_message': 'Invalid login'})
    return render(request, 'event/login.html')


def logout_user(request):
    logout(request)
    return render(request, 'event/login.html')


def add_event(request):
    if not request.user.is_authenticated:
        return render(request, 'event/login.html')
    else:
        form = EventForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            event = form.save(commit=False)
            event.manager = request.user
            event.image = form.cleaned_data['image']
            file_type = event.image.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'event': event,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'event/add_event.html', context)
            event.save()
            return render(request, 'event/detail.html', {'event': event})
        context = {
            "form": form,
        }
        return render(request, 'event/add_event.html', context)


def detail(request, pk):
    if not request.user.is_authenticated:
        return render(request, 'event/login.html')
    else:
        user = request.user
        event = get_object_or_404(Event, pk=pk)
        tickets = Ticket.objects.filter(event=event)
        return render(request, 'event/detail.html', {'event': event, 'user': user, 'tickets': tickets})


class EventUpdate(UpdateView):
    model = Event
    fields = ['name', 'location', 'date', 'time', 'image']

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(EventUpdate, self).get(request, *args, **kwargs)


def get_user_profile(request, pk):
    user = User.objects.get(pk=pk)
    profile = Profile.objects.get(user_id=pk)
    tickets = Ticket.objects.filter(attendee=user)
    return render(request, 'event/user_profile.html', {'user': user, 'profile': profile, 'tickets': tickets})


def get_past_events(request):
    events = Event.objects.filter(date__lt=date.today())
    return render(request, 'event/get_past_events.html', {'events': events})


def add_money(request, pk):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = AddMoneyForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if int(data['pin']) == profile.wallet_pin:
                profile.wallet_balance = profile.wallet_balance + data['amount']
                profile.save()
                tickets = Ticket.objects.filter(attendee=request.user)
                return render(request, 'event/user_profile.html', {'user': request.user, 'profile': profile, 'tickets': tickets})
            else:
                err = 'Invalid Pin!'
                context = {'profile': profile, 'form': form, 'error_message': err}
                return render(request, 'event/add_money.html', context)
    else:
        form = AddMoneyForm()
    return render(request, 'event/add_money.html', {'profile': profile, 'form': form})


def withdraw_money(request, pk):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = WithdrawMoneyForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if int(data['pin']) == profile.wallet_pin:
                if data['amount'] > profile.wallet_balance:
                    context = {'profile': profile, 'form': form, 'error_message': 'Amount to withdraw cannot be more than '
                                                                                  'available balance'}
                    return render(request, 'event/withdraw_money.html', context)
                profile.wallet_balance = profile.wallet_balance - data['amount']
                profile.save()
                tickets = Ticket.objects.filter(attendee=request.user)
                return render(request, 'event/user_profile.html', {'user': request.user, 'profile': profile, 'tickets': tickets})
            else:
                err = 'Invalid Pin!'
                context = {'profile': profile, 'form': form, 'error_message': err}
                return render(request, 'event/withdraw_money.html', context)
    else:
        form = WithdrawMoneyForm()
    return render(request, 'event/withdraw_money.html', {'profile': profile, 'form': form})


def buy_ticket(request, pk):
    user = request.user
    event = Event.objects.get(id=pk)
    profile = Profile.objects.get(user=user)
    if request.method == 'POST':
        form = BuyTicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if int(data['pin']) == profile.wallet_pin:
                if event.fare > profile.wallet_balance:
                    error_balance = 'Insufficient balance to buy ticket'
                    return render(request, 'event/buy_ticket.html', {'profile': profile, 'form': form, 'event': event,
                                                                     'error_balance': error_balance})
                else:
                    Ticket.objects.create(attendee=user, event=event, flag=1)
                    profile.wallet_balance = profile.wallet_balance - event.fare
                    owner = event.manager
                    owner_profile = Profile.objects.get(user=owner)
                    owner_profile.wallet_balance = owner_profile.wallet_balance + event.fare
                    profile.save()
                    tickets = Ticket.objects.filter(attendee=request.user)
                    return render(request, 'event/user_profile.html', {'user': user, 'profile': profile, 'tickets': tickets})
            else:
                err = 'Invalid Pin!'
                context = {'profile': profile, 'form': form, 'event': event, 'error_message': err}
                return render(request, 'event/buy_ticket.html', context)
    else:
        form = BuyTicketForm()
    return render(request, 'event/buy_ticket.html', {'profile': profile, 'form': form, 'event': event})


def invite_users(request, pk):
    all_users = User.objects.filter(is_superuser=False)
    event = Event.objects.get(id=pk)
    attendees = []
    for ticket in Ticket.objects.all():
        if ticket.event == event:
            attendees.append(ticket.attendee)
    attendees.append(request.user)
    users = list(set(all_users) ^ set(attendees))
    context = {'users': users, 'event': event}
    return render(request, 'event/invite_users.html', context)


def send_invites(request, pk):
    all_users = User.objects.filter(is_superuser=False)
    event = Event.objects.get(id=pk)
    attendees = []
    for ticket in Ticket.objects.all():
        if ticket.event == event:
            attendees.append(ticket.attendee)
    attendees.append(request.user)
    users = list(set(all_users) ^ set(attendees))
    if request.method == 'POST':
        for user in users:
            if request.POST[user.username] == 'yes':
                Ticket.objects.create(attendee=user, event=event, flag=0)
    events = Event.objects.all()
    return render(request, 'event/home.html', {'events': events})


def event_name_validate(request):
    user = request.user
    name = request.GET.get('name')
    all_events = Event.objects.all()
    event_names = []
    for event in all_events:
        if event.manager == user:
            event_names.append(event.name)
    if name in event_names:
        return HttpResponse(json.dumps({'valid': 'false'}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'valid': 'true'}), content_type="application/json")


def event_date_validate(request):
    inp_date = request.GET.get('date')
    if inp_date:
        inp_date = datetime.datetime.strptime(inp_date, "%m/%d/%Y").date()
        if inp_date < date.today():
            return HttpResponse(json.dumps({'valid': 'false'}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'valid': 'true'}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'valid': 'true'}), content_type="application/json")
