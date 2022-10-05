from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.dispatch import receiver


class Event(models.Model):
    name = models.CharField(max_length=50, null=False)
    image = models.ImageField(default='settings.MEDIA_ROOT/default_event.jpg')
    location = models.TextField(max_length=500, null=False)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    fare = models.PositiveIntegerField(null=True)

    def get_absolute_url(self):
        return reverse('event:detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name + ', ' + self.manager.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='settings.MEDIA_ROOT/default_user.jpg')
    bio = models.TextField(max_length=500, blank=True, null=True)
    location = models.TextField(max_length=500, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    wallet_pin = models.PositiveIntegerField(null=True)
    wallet_balance = models.PositiveIntegerField(default=0, null=True)

    def __str__(self):
        return self.user.username


class Ticket(models.Model):
    attendee = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    flag = models.BooleanField(null=False)

    def __str__(self):
        return self.attendee.username
