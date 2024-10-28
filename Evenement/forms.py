from django import forms
from .models import Evenement, Comment

class EventForm(forms.ModelForm):
    TYPE_CHOICES=[
        ('concert','Concert, Cinéma,...'),
        ('activite','Activité et sport'),
        ('culture','Culture et patrimoine,...'),
        ('salon','Marché, manifestation, salon,...'),
        ('technologie','Technologie et science'),
        ('sensation forte','Saut en parachute, Course,Karting,...'),
        ('excursion','Excursion, Sortie,...'),
        ('voyage','voyage organisé'),
        ('autres','Divers'),

    ]  
    title = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    image= forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple':True
        })
    )
    
    tariff = forms.IntegerField()
    category=forms.CharField(
        label='category:',
        widget = forms.Select(choices=TYPE_CHOICES)
    )
    description= forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows':'3',
            'placeholder':'Description...',
            'class':'form-control',
        })
    )

    location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control'})
       
    )
    class Meta:
        model = Evenement
        fields=["title","description","location","tariff","location","tariff","image"]

class CommentForm(forms.ModelForm):
   
    comment= forms.CharField(
        max_length=500,
        label='',
        widget=forms.Textarea(attrs={
            'rows':'3',
            'placeholder':'commentaire...',
        })
    )      
    class Meta:
        model = Comment
        fields=["comment"]
