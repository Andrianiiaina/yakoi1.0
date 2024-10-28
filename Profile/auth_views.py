from django.shortcuts import render,redirect
from django.contrib import auth,messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import NewUserForm
from socialnetwork.cryptage import cryptage, decryptage

def register_request(request):
    if request.user.is_authenticated:
        return redirect('event_list')
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("event_list")
        else:    
            messages.error(request, "information invalide.")

    form = NewUserForm()
    return render (request=request, template_name="signup.html", context={"register_form":form})

def login_request(request):
    if request.user.is_authenticated:
        return redirect('event_list')
    if request.method == "POST":


        if User.objects.filter(username = request.POST['username']):
            user=User.objects.get(username = request.POST['username'])
            pas=decryptage(user.password)
            if pas == request.POST['password']:
                auth.login(request,user)
                return redirect('event_list')
            else:
                 messages.error(request, "Mot de passe incorrecte.")  
        else:
             messages.error(request, "Identifiant incorrecte, veuilez verifier votre identifiant s'il vous plait.")

    return render(request=request, template_name="login.html")	
