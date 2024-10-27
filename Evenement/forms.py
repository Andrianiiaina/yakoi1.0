from django import forms
from .models import Evenement, Comment

class EventForm(forms.ModelForm):
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
        fields=["title","description","location","tariff","date","end_date","location","tariff","image"]

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
