from .models import UserProfile, Gallery
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from socialnetwork.cryptage import cryptage

class ProfileForm(forms.ModelForm):
  
    picture= forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple':True
        })
    )
    bio= forms.CharField(
        max_length=500,
        min_length=5,
        label='bio',
        widget=forms.Textarea(attrs={
            'rows':'3',
            'placeholder':'Description...',
        })
    )
    localisation = forms.CharField(
        max_length=100,
        min_length=5,
        label='localisation',

    )
    contact = forms.CharField(
        max_length=10,
        min_length=10,
        label='contact',

    )
   
    class Meta:
        model = UserProfile
        fields=["bio","localisation","picture","contact","nif","stat","cin"]

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True,label="E-mail")
	username=forms.CharField(required=True,label="Identifiant")
	password1=forms.CharField(label="Mot de passe",widget=forms.PasswordInput,required=True, min_length=6,max_length=20)
	password2=forms.CharField(label="Confirmation",widget=forms.PasswordInput,required=True, min_length=6,max_length=20)
	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.password=cryptage(self.cleaned_data.get('password1'))
		if commit:
			user.save()
		return user

class GalleryForm(forms.ModelForm):
    titre = forms.CharField(
        max_length=100,
        min_length=5,
        label='titre',

    )

    image= forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple':True
        })
    )
    class Meta:
        model = Gallery
        fields=["titre","image"]