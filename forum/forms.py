from django import forms
from .models import Forum, CommentForum
TYPE_CHOICES=[
    ('Activite','Activité et sport'),
    ('Loisir','Loisir'),
    ('Culture','Culture et patrimoine,...'),
    ('Salon','Marché, manifestation, salon,...'),
    ('technologie','Technologie et science'),
    ('autres','Divers'),

]   

class ForumForm(forms.ModelForm):
    description= forms.CharField(
        max_length=500,
        min_length=1,
        label='description',
        widget=forms.Textarea(attrs={
            'rows':'3',
            'placeholder':'Description...',
        })
    )
    category=forms.CharField(
        label='category:',
        widget = forms.Select(choices=TYPE_CHOICES)
    )
    class Meta:
        model = Forum
        fields=["description","category"]

class CommentForm(forms.ModelForm):
   
    comment= forms.CharField(
        max_length=500,
        min_length=1,
        label='',
        widget=forms.Textarea(attrs={
            'rows':'3',
            'placeholder':'commentaire...',
        })
    )      
    class Meta:
        model = CommentForum
        fields=["comment"]
