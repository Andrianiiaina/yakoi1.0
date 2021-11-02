from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, verbose_name='user', related_name='profile', on_delete=models.CASCADE)
    bio=models.CharField(max_length=500, blank=True, null=True)
    localisation = models.CharField(max_length=100, default='Antananarivo', null=True)
    picture = models.ImageField(upload_to='uploads/profile_pictures', default='uploads/profile_pictures/profile.png', blank=True)
    fonction = models.BooleanField(blank=True, default=False)
    contact = models.IntegerField(blank=True, default='034')
    cin = models.CharField(blank=True,max_length=50, default='')
    activities= models.CharField(max_length=200, blank=True, null=True)
    nif = models.CharField(blank=True,max_length=50, default='')
    stat = models.CharField(blank=True,max_length=50, default='')
    lien = models.CharField(blank=True, max_length=450, default='')
    followers = models.ManyToManyField(User, blank=True, related_name='followers')
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
@receiver(post_save, sender=User)    

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()   



class UserprofileFollowers(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    userprofile=models.ForeignKey(UserProfile, on_delete=models.CASCADE)  
    
class Gallery(models.Model):
    user= models.ForeignKey(User,null=False, on_delete=models.CASCADE)
    titre=models.CharField("titre",max_length=450)
    image=models.ManyToManyField('Image', blank=True)

class Image(models.Model):
    image = models.ImageField(upload_to='uploads/gallery', blank=True, null=True)      