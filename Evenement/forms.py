from django import forms
from .models import Evenement, Comment
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class EventForm(forms.ModelForm):
    titre = forms.CharField(
        max_length=50,
        min_length=4,
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    image= forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple':True
        })
    )
    tarif = forms.IntegerField(
       max_value=1000000, 
       min_value=0
    )
    
    description= forms.CharField(
        max_length=500,
        min_length=3,
        widget=forms.Textarea(attrs={
            'rows':'3',
            'placeholder':'Description...',
            'class':'form-control',
        })
    )

    lieu = forms.CharField(
        max_length=100,
        min_length=3,
        widget=forms.TextInput(attrs={'class':'form-control'})
       
    )
    class Meta:
        model = Evenement
        fields=["titre","description","lieu","tarif"]

def validate_tarif(date1,date2):
        if date1 >= date2:
            raise ValidationError(
                _('le date de debut doit etre inferieur a la date de fin de voyage'),
                params={'value': value},
        )
class VoyageForm(forms.ModelForm):
    titre = forms.CharField(
        max_length=50,
        min_length=4,
        widget=forms.TextInput(attrs={'class':'form-control'})
    )
    image= forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple':True
        })
    )
    description= forms.CharField(
        max_length=500,
        min_length=3,
        widget=forms.Textarea(attrs={
            'rows':'3',
            'placeholder':'Description...',
            'class':'form-control',
        })
    )

    lieu = forms.CharField(
        max_length=100,
        min_length=3,
        widget=forms.TextInput(attrs={'class':'form-control'})
       
    )

    tarif = forms.IntegerField(
       #validators=[validate_tarif]
       max_value=1000000, 
       min_value=0
    )
    
    class Meta:
        model = Evenement
        fields=["titre","description","lieu","tarif","image"]



class CommentForm(forms.ModelForm):
   
    comment= forms.CharField(
        max_length=500,
        min_length=2,
        label='',
        widget=forms.Textarea(attrs={
            'rows':'3',
            'placeholder':'commentaire...',
        })
    )      
    class Meta:
        model = Comment
        fields=["comment"]
