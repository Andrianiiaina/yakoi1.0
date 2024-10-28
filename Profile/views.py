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
from Evenement.forms import EventForm, EventForm
from socialnetwork.cryptage import cryptage, decryptage,cryptage_url,decryptage_url
from Evenement.models import Evenement
from django.views.generic.edit import UpdateView,DeleteView
from django.core.paginator import Paginator


class ProfileView(View):
    def get(self, request, username, *args,**kwargs):
        user=User.objects.get(username=username)
        evenements= Evenement.objects.all().filter(user=user).order_by('-create_on')  
        context = {
            'form_evenement':EventForm(),
            'formgallery':GalleryForm(),
            'evenements':Paginator(evenements, 10).get_page(request.GET.get('page')),
            'is_following':request.user.followers.filter(user_id=user.id).exists(),
            'galleries':Gallery.objects.filter(user=user),
            'user':user,
        }
        return render(request, 'profile/profile.html', context)
class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model= UserProfile
    fields=["bio","localisation","activities","contact","picture"]
    template_name = 'profile/profile_edit.html'
    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username':self.request.user.username})
    def test_func(self):
        profile=self.get_object()
        activities=self.request.POST.getlist('activities[]')
        profile.activities=','.join(map(str,activities))
        profile.save()

        return self.request.user == profile.user 
class ProfileRespoCreateView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        return render(request, 'profile/profile_respo_create.html',{'form':ProfileForm()})
    def post(self, request, *args,**kwargs):
        
        bio=request.POST.get('bio')
        nif=cryptage(str(request.POST.get('nif')))
        stat=cryptage(str(request.POST.get('stat')))
        cin=cryptage(str(request.POST.get('cin')))
        
        localisation=request.POST.get('localisation')
        contact=request.POST.get('contact')
        activities=request.POST.getlist('activities[]')
        activities=','.join(map(str,activities))

        user=UserProfile(user=request.user, activities=activities, bio=bio,localisation=localisation,nif=nif,stat=stat,cin=cin,contact=contact,fonction=True)
        user.save() 
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
        return render(request, 'profile/search.html', {'profile_list':profile_list})

class ListFollowers(View):
    def get(self,request,pk,*args,**kwargs):
        context = {
            'profile':UserProfile.objects.get(pk=pk),
            'followers': profile.followers.all(),
        }
        return render(request,'profile/list_followers.html',context)



class GalleryView(LoginRequiredMixin, View):
    def post(self, request, *args,**kwargs):
        form=GalleryForm(request.POST)
        files = request.FILES.getlist('image')
        if form.is_valid():
            title = form.cleaned_data['title']
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


class AddNotification(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        evenement = Evenement.objects.get(pk=pk)   
        notification=Notification.objects.create(notification_type=5, to_user=request.user, evenement=evenement)
        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)          
