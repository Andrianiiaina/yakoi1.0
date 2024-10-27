from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Forum(models.Model):
    user= models.ForeignKey(User,null=False, on_delete=models.CASCADE,default=1)
    description=models.TextField()
    category=models.CharField("category", max_length=500, default="autres")
    create_on=models.DateField(default=timezone.now)
    def __str__(self):
        return self.description
    
class CommentForum(models.Model): 
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    forum=models.ForeignKey(Forum, on_delete=models.CASCADE)  
    parent = models.ForeignKey('self',on_delete=models.CASCADE, blank=True,null=True,related_name='+')
    @property
    def children(self):
        return CommentForum.objects.filter(parent=self).all()
    @property
    def is_parent(self):
        if self.parent is None:
            return True