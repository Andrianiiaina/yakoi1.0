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
        label='bio',
        widget=forms.Textarea(attrs={
            'rows':'3',
            'placeholder':'Description...',
        })
    )
    localisation = forms.CharField(
        max_length=100,
        label='localisation',

    )
    contact = forms.CharField(
        max_length=10,
        min_length=10,
        label='contact',

    )
    class Meta:
        model = UserProfile
        fields=["picture","bio","contact","localisation","nif","stat","cin"]


class GalleryForm(forms.ModelForm):
    title = forms.CharField(
        max_length=100,
        label='title',

    )

    image= forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple':True
        })
    )
    class Meta:
        model = Gallery
        fields=["title","image"]

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