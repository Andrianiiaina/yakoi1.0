from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib import auth,messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from .models import UserProfile,Image,Gallery
from .forms import ProfileForm,  GalleryForm, NewUserForm
from Evenement.models import Notification
from Evenement.forms import EventForm, VoyageForm
from socialnetwork.cryptage import cryptage, decryptage,cryptage_url,decryptage_url
from Evenement.models import Evenement
from django.views.generic.edit import UpdateView,DeleteView
from django.core.paginator import Paginator
# Create your views here.


class ProfileView(View):
    def get(self, request, username, *args,**kwargs):
        user=User.objects.get(username=username)
        profile = UserProfile.objects.get(pk=user.pk)

        evenements= Evenement.objects.all().filter(user=user).order_by('-create_on')    
        paginator = Paginator(evenements, 10)
        page_number = request.GET.get('page')
        evenements_obj = paginator.get_page(page_number)

        galleryForm=GalleryForm()
        followers = profile.followers.all()
        form_evenement=EventForm()
        form_voyage=VoyageForm()

        act=[]
        activities=profile.activities
        if activities:
            for i in activities.split(','):
                act.append(i)
            
        if len(followers)==0:
            is_following=False
        for follower in followers:
            if follower == request.user:
                is_following=True
            else:
                is_following = False    
        number_of_followers = len(followers)

        galleries=Gallery.objects.filter(user=user)
        
    
        context = {
            'form_voyage':form_voyage,
            'form_evenement':form_evenement,
            'formgallery':galleryForm,
            'profile':profile,
            'evenements':evenements_obj,
            'number_of_followers':number_of_followers,
            'is_following':is_following,
            'activities':act,
            'galleries':galleries,
            'user':user,

        }
        return render(request, 'profile/profile.html', context)
class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model= UserProfile
    fields=["bio","localisation","contact","picture"]
    template_name = 'profile/profile_edit.html'
    def get_success_url(self):
        pk=self.kwargs['pk']
        username=User.objects.get(pk=pk)
        return reverse_lazy('profile', kwargs={'username':username})

    def test_func(self):
        profile=self.get_object()
        activities=self.request.POST.getlist('activities[]')
        s=''
        for i in activities:
            s=s+i+','
        profile.activities=s
        profile.lien=cryptage(profile.pk)
        profile.save()

        return self.request.user == profile.user 
class ProfileRespoCreateView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        form=ProfileForm()
        context= {
            'form':form,
        }
        return render(request, 'profile/profile_respo_create.html',context)
    def post(self, request, *args,**kwargs):
        

        bio=request.POST.get('bio')
        nif=cryptage(str(request.POST.get('nif')))
        stat=cryptage(str(request.POST.get('stat')))
        cin=cryptage(str(request.POST.get('cin')))
        
        localisation=request.POST.get('localisation')
        contact=request.POST.get('contact')
        lien=cryptage(request.user.pk)
        activities=request.POST.getlist('activities[]')
        s=''
        for i in activities:
            s=s+i+','
        fonction=True
        profile = UserProfile.objects.get(pk=request.user)

        user=UserProfile(user=request.user, lien=lien,activities=s, bio=bio,localisation=localisation,nif=nif,stat=stat,cin=cin,contact=contact,fonction=fonction)
        user.save() 
        form=ProfileForm()
        return redirect('event_list')     


class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)       
        profile.followers.add(request.user)    
        notification=Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)
       
        return redirect('profile', username=request.user.username)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)       
        profile.followers.remove(request.user)    
        return redirect('profile', username=profile.user.username) 

class UserSearch(View):
    def get(self, request, *args, **kwargs):
        query=self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(Q(user__username__icontains=query))
        context = {
            'profile_list':profile_list,
        }
        return render(request, 'profile/search.html', context)

class ListFollowers(View):
    def get(self,request,pk,*args,**kwargs):
        profile= UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()

        context = {
            'profile':profile,
            'followers': followers,
        }
        return render(request,'profile/list_followers.html',context)



class GalleryView(LoginRequiredMixin, View):
    def post(self, request, *args,**kwargs):

        form=GalleryForm(request.POST)
        files = request.FILES.getlist('image')
       
        
        if form.is_valid():
            titre = form.cleaned_data['titre']
            new_gallery = form.save(commit=False)
            new_gallery.user = request.user
            new_gallery.save()
            for f in files:
                img=Image(image=f)
                img.save()
                new_gallery.image.add(img)
            new_gallery.save()
        return redirect('profile',username=new_gallery.user.username)   
class GalleryDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Gallery
    template_name='delete.html'    

    success_url=reverse_lazy('event_list')   
    def test_func(self):
        gallery=self.get_object()
        return self.request.user == gallery.user 

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

class AddNotification(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        evenement = Evenement.objects.get(pk=pk)   
        notification=Notification.objects.create(notification_type=5, to_user=request.user, evenement=evenement)
        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)          
