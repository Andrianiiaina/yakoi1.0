from django.contrib import admin
from .models import Evenement,Notification,Comment,Tag
# Register your models here.
admin.site.register(Evenement)
admin.site.register(Notification)
admin.site.register(Comment)
admin.site.register(Tag)

