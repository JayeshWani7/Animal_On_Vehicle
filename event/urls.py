from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'event'

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^add_event/$', views.add_event, name='add_event'),
    url(r'^(?P<pk>[0-9]+)/$', views.detail, name='detail'),
    url(r'update/(?P<pk>[0-9]+)/$', views.EventUpdate.as_view(), name='update_event'),
    url(r'profile/(?P<pk>[0-9]+)/$', views.get_user_profile, name='user_profile'),
    url(r'past_events/$', views.get_past_events, name='past_events'),
    url(r'add_money/(?P<pk>[0-9]+)/$', views.add_money, name='add_money'),
    url(r'withdraw_money/(?P<pk>[0-9]+)/$', views.withdraw_money, name='withdraw_money'),
    url(r'buy_ticket/(?P<pk>[0-9]+)/$', views.buy_ticket, name='buy_ticket'),
    url(r'invite_users/(?P<pk>[0-9]+)/$', views.invite_users, name='invite_users'),
    url(r'send_invites/(?P<pk>[0-9]+)/$', views.send_invites, name='send_invites'),
    url(r'event_name_validate/$', views.event_name_validate, name='event_name_validate'),
    url(r'event_date_validate/$', views.event_date_validate, name='event_date_validate')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)