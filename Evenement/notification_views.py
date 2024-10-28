from django.shortcuts import redirect
from django.views import View
from django.http import HttpResponse
from .models import Evenement, Comment, Notification, Image, Tag, Ville, Like
import datetime
class EventNotification(View):
    def get(self, request, notification_pk, evenement_pk, *args,**kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        evenement =Evenement.objects.get(pk=evenement_pk)
        notification.user_has_seen = True
        notification.save()

        return redirect('event_detail' ,pk=evenement_pk)
        
class FollowNotification(View):        
    def get(self, request, notification_pk, profile_pk, *args,**kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        user=User.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile', username=user.username)

class RemoveNotification(View):
    def delete(self, request, notification_pk, *args,**kwargs):
        notification = Notification.objects.get(pk=notification_pk)        
        notification.user_has_seen = True
        notification.save()
        return HttpResponse('Success', context_type='text/plain')
