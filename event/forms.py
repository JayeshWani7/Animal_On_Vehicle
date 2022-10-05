from django import forms
from django.contrib.auth.models import User

from .models import Event, Profile


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'location', 'date', 'time', 'fare', 'image']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    wallet_pin = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'age', 'wallet_pin', 'image']


class AddMoneyForm(forms.Form):
    amount = forms.IntegerField(label='Amount to Add', min_value=0)
    pin = forms.CharField(label='Enter PIN', widget=forms.PasswordInput)


class WithdrawMoneyForm(forms.Form):
    amount = forms.IntegerField(label='Amount to Withdraw', min_value=0)
    pin = forms.CharField(label='Enter PIN', widget=forms.PasswordInput)


class BuyTicketForm(forms.Form):
    pin = forms.CharField(label='Enter PIN', widget=forms.PasswordInput)
