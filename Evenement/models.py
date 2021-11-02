from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
from forum.models import Forum
class Evenement(models.Model):
    user= models.ForeignKey(User,null=False, on_delete=models.CASCADE)
    titre=models.CharField("titre",max_length=50)
    description=models.TextField()
    image=models.ManyToManyField('Image', blank=True)
    date=models.DateField("date")
    datefin=models.DateField(blank=True, null=True)
    lieu=models.CharField("lieu",max_length=250)
    tarif=models.CharField("tarif",default='0',max_length=250)
    category=models.CharField("category", max_length=100,default="autres")
    create_on=models.DateField(default=timezone.now)
    url=models.CharField(max_length=50,default="a")
    likes = models.ManyToManyField(User, blank=True, related_name='Likes')
    tags = models.ManyToManyField('Tag',blank=True)


    def create_tags(self):
        for word in self.description.split():
            if(word[0] == "#"):
                tag=Tag.objects.filter(name=word[1:]).first()
                if tag:
                    self.tags.add(tag.pk)
                else:
                    tag = Tag(name=word[1:])
                    tag.save()    
                    self.tags.add(tag.pk)
                self.save() 

    def __str__(self):
        return self.titre

class Comment(models.Model): 
    comment = models.TextField()
    create_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event=models.ForeignKey(Evenement, on_delete=models.CASCADE)  
    parent = models.ForeignKey('self',on_delete=models.CASCADE, blank=True,null=True,related_name='+')
    @property
    def children(self):
        return Comment.objects.filter(parent=self).order_by('create_on').all()
    @property
    def is_parent(self):
        if self.parent is None:
            return True
     
class Notification(models.Model):
        #like/comment/follow
        notification_type = models.IntegerField()
        to_user = models.ForeignKey(User, related_name='notification_to',on_delete=models.CASCADE, null=True)
        from_user = models.ForeignKey(User, related_name='notification_from',on_delete=models.CASCADE, null=True)
        evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
        comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
        date = models.DateField(default=timezone.now)
        user_has_seen = models.BooleanField(default=False)
        
class Image(models.Model):
    image = models.ImageField(upload_to='uploads/post_photos', blank=True, null=True)        
class Tag(models.Model):
    name=models.CharField(max_length=255)  

class Ville(models.Model):
    name=models.CharField(max_length=255)  



   
      
   