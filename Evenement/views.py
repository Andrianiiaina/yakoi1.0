from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from .models import Evenement, Comment, Notification, Image, Tag, Ville, Like
from Profile.models import UserProfile
from .forms import EventForm, CommentForm, EventForm
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.paginator import Paginator
from socialnetwork.cryptage import cryptage_url, decryptage_url
from django.contrib import messages
from django.db.models import Count
import datetime

class EventListView(View):
    def get(self, request, *args,**kwargs):
        evenements=Evenement.objects.all().exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).filter(end_date__isnull=True).order_by('-create_on')[:10]
        
        filtered_event=Evenement.objects.filter(title="")

        if request.user.is_authenticated:
            profile=UserProfile.objects.get(pk=request.user.pk)
            #si l'utilisateur n'as pas encore de lien profile
            if  profile.lien == '':
                return redirect('profile_edit', request.user.pk) 
            #personnalisation des evenents selon les activites de l'utilisateur
            if profile.activities:
                for i in profile.activities.split(','):
                    filtered_event= filtered_event | Evenement.objects.filter(category=i)            
                evenements=filtered_event.exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).filter(end_date__isnull=True)

        tags=Tag.objects.all().order_by('name')
        #recuperation des evenements chaque semaine
        today_date=datetime.date.today()
        start_week = today_date - datetime.timedelta(today_date.weekday())
        end_week=start_week + datetime.timedelta(7)
        events_week=Evenement.objects.filter(date__range=[start_week, end_week]).exclude(date__lte=today_date+datetime.timedelta(days=-1))
        
        villes=Ville.objects.all().order_by('name')
       
       
        context= {
            'events_week':events_week,
            'evenements':evenements,
            'tags':tags,
            'villes':villes,
        }
        return render(request, 'evenement/event_list.html', context)

    def post(self, request, *args,**kwargs):
        form = EventForm(request.POST)
        files = request.FILES.getlist('image')
        if form.is_valid():
            title = form.cleaned_data['title']
            new_event = form.save(commit=False)
            new_event.user = request.user
            new_event.category = request.POST.get('category')
            new_event.date=request.POST.get('datet') 
 
            new_event.save()
            messages.success(request, "l'événement  a bien été ajouté!")
            
            new_event.url=cryptage_url(new_event.pk)
            new_event.create_tags()      
            villes=Ville.objects.filter(name=new_event.location).first()
            if villes is None:
                Ville.objects.create(name=new_event.location)
                
            for f in files:
                img=Image(image=f)
                img.save()
                new_event.image.add(img)
            new_event.save()  

            profile= UserProfile.objects.get(pk=new_event.user)
            followers = profile.followers.all()   

            for follower in followers:    
                notification=Notification.objects.create(notification_type=4, from_user=new_event.user, to_user=follower, evenement=new_event)
            context = {
                'form':form,
            }
            return redirect('event_detail',username=new_event.user.username,url=new_event.url)   
        else: 
            messages.error(request, "la creation d'evenement a echouée, veuillez verifier vos données")
            return redirect('profile', username=request.user.username)   


class EventDetailView(View):
    def get(self,request,pk, *args,**kwargs):
        evenement= Evenement.objects.get(pk=pk)
        
        form = CommentForm()
        comments=Comment.objects.filter(event=evenement).order_by('-create_on') 
        #recuperation des evenements connexes
        evenements=Evenement.objects.exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).filter(category = evenement.category)[:6]
        context = {

            'evenements':evenements,
            'evenement':evenement,
            'comments':comments,
            'form':form,
        }

        return render(request, 'evenement/event_detail.html', context)
    #create_comments
    def post(self,request,pk, *args,**kwargs):  
        evenement=Evenement.objects.get(pk=pk)    
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.user=request.user
            new_comment.event=evenement
            new_comment.save()
        comments=Comment.objects.filter(event=evenement).order_by('create_on')
        notification=Notification.objects.create(notification_type=2, from_user=request.user, to_user=evenement.user, evenement=evenement)
        context = {
            'comments':comments,
            'form':form,
        }    
        return redirect('event_detail',pk=pk)       

class EventDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Evenement
    template_name='delete.html'    
    success_url=reverse_lazy('event_list')   
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user 

class EventEditView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model= Evenement
    fields=["title","description","location","date"]
    template_name = 'edit.html'
   
    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('event_detail',kwargs={'pk':pk})
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user  

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Comment
    template_name='delete.html' 

    def get_success_url(self):
        event_pk=self.kwargs['event_pk']
        pk=self.kwargs['pk']
        return reverse_lazy('event_detail', kwargs={'pk':event_pk})
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user

class AddLike(LoginRequiredMixin, View):
    def post(self, request,pk,*args,**kwargs):
        evenement=Evenement.objects.get(pk=pk)
        like, created= Like.objects.get_or_create(user_id=request.user.pk, event_id=pk)
        if created: 
            notification=Notification.objects.create(notification_type=1, from_user=request.user, to_user=evenement.user,evenement=evenement)
        else:
            like.delete() 
        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)   

class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request,evenement_pk,pk, *args,**kwargs):
        evenement=Evenement.objects.get(pk=evenement_pk)
        parent_comment=Comment.objects.get(pk=pk)
        form=CommentForm(request.POST)
        if form.is_valid():
            new_comment=form.save(commit=False)
            new_comment.user=request.user
            new_comment.event=evenement
            new_comment.parent = parent_comment
            new_comment.save()
            if(new_comment.user != parent_comment.user):
                notification=Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.user, comment=new_comment)
           
        return redirect('event_detail',username=evenement.user.username,url=cryptage_url(evenement_pk))    

class EventNotification(View):
    def get(self, request, notification_pk, evenement_pk, *args,**kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        evenement =Evenement.objects.get(pk=evenement_pk)
        notification.user_has_seen = True
        notification.save()

        return redirect('event_detail' ,username=evenement.user.username,url=cryptage_url(evenement_pk))
class FollowNotification(View):        
    def get(self, request, notification_pk, profile_pk, *args,**kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        user=User.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile', username=user.username)

class RemoveNotification(View):
    def delete(self, request, notification_pk, *args,**kwargs):
        notification = Notification.objects.get(pk=notification_pk)        
        notification.user_has_seen = True
        notification.save()
        return HttpResponse('Success', context_type='text/plain')

#le grand calendrier
class BigCalendarListView(View):
    def get(self, request, *args,**kwargs):

        evenements_ = Evenement.objects.exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).order_by('date')
        
        famous_events=Evenement.objects.annotate(num_like=Count('likes')).order_by('-num_like')[:8]  

        paginator = Paginator(evenements_, 10)
        page_number = request.GET.get('page')
        evenements = paginator.get_page(page_number)
        tags=Tag.objects.all()
        villes=Ville.objects.all().order_by()

        context= {
            'villes':villes,
            'evenements':evenements,
            'tags':tags,
            'famous_events':famous_events,
        }
        return render(request, 'evenement/big_calendar.html', context)

class FiltreEvent(View):
    def get(self, request, *args, **kwargs):
        today_date=datetime.date.today()
        categories=self.request.GET.getlist('activities[]')
        location=self.request.GET.get('region')
        jour=self.request.GET.get('jour')
        category_type=self.request.GET.get('type')
        x=Evenement.objects.all()
        
        if category_type != 'all'and category_type is not None:
            x=Evenement.objects.filter(category=category_type)
            
        if categories:   
            x=Evenement.objects.filter(category='')
            for i in categories:
                if i != " ":
                    x =x | Evenement.objects.filter(category=i)
                 
        if jour == 'asc':
            x=x & Evenement.objects.all()
        elif jour == 'desc':
            x=x & Evenement.objects.all().order_by('-date')
        tariff_max=self.request.GET.get('tariff')
        x = x & Evenement.objects.filter(tariff__lte = tariff_max)
        
            
        if location != 'all':
            x = x & Evenement.objects.filter(location =location) 

        context = {
        'publications': x,
        }
        return render(request, 'evenement/event_search.html',context)   

class EventSearch(View):
    def get(self, request, *args, **kwargs):
        query=self.request.GET.get('query')
        publications=Evenement.objects.filter(Q(description__icontains=query)) 
        context = {
            'publications':publications,
        }
        return render(request, 'evenement/event_search.html', context)
#tag
class Explore(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        tag = Tag.objects.filter(name=query).first()
        if tag:
            posts = Evenement.objects.filter(tags__in=[tag])
        else:
            posts = Evenement.objects.all()
        context = {
        'publications': posts,
        }
        return render(request, 'evenement/event_search.html', context)


class FiltreSemantique(View):
    def post(self, request, *args,**kwargs):
        evenements1=Evenement.objects.filter(category="all")
        evenements2=Evenement.objects.filter(category="all")
        liste_tags=request.POST.getlist('rc[]')
        mere=['autres','technologie','concert','excursion','culture','sport','fete']
        for i in mere:
            for j in liste_tags:
                if j==i :
                    evenements1 = evenements1 | Evenement.objects.filter(category=j)  
        for k in liste_tags:
            evenements2 = evenements2 | Evenement.objects.filter(Q(description__icontains=k))
        if evenements1 is None:
            evenements1=Evenement.objects.all()
        intersection_evenements = evenements1 & evenements2
        union_evenements =  evenements1 | evenements2 
        context = {
            'connexes' : union_evenements,
            'publications' : intersection_evenements,
        }  
        return render(request, 'evenement/event_search.html', context)  

class EvenementCategoryView(View):
    def get(self, request,category, *args, **kwargs):
        evenements=Evenement.objects.filter(category=category)
        if evenements is None:
            evenements=Evenement.objects.all()
            
        context={
            'publications':evenements,
        }       
        return render(request,'evenement/event_search.html',context)


class VoyageListView(View):
    def get(self, request, *args,**kwargs):
        form_voyage=EventForm()
        evenements=Evenement.objects.filter(end_date__isnull = False)
        context= {
            'evenements':evenements,
            'formv':form_voyage,
        }
        return render(request, 'voyage.html', context)

    def post(self, request, *args,**kwargs):
        form = EventForm(request.POST)
        files = request.FILES.getlist('image')
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.user = request.user
             #seulement si le date de debut est < date fin
            if new_event.date <= new_event.end_date:          
                new_event.save()
                messages.success(request, "l'événement  a bien été ajouté!")
                new_event.url=cryptage_url(new_event.pk)
                new_event.create_tags()
                for f in files:
                    img=Image(image=f)
                    img.save()
                    new_event.image.add(img)
                new_event.save()  

                profile= UserProfile.objects.get(pk=new_event.user)
                followers = profile.followers.all()  
            
                for follower in followers:    
                    notification=Notification.objects.create(notification_type=4, from_user=new_event.user, to_user=follower, evenement=new_event)
                
                context = {
                    'form':form,
                }
                return redirect('event_detail',username=new_event.user.username,url=new_event.url) 
            else:
                messages.error(request,"le date du debut de voyage doit etre inferieur au date du fin de voyage")
                return redirect('profile',username=request.user.username) 

class VoyageSearch(View):
    def get(self, request, *args, **kwargs):
        query=self.request.GET.get('query')
        publications=Evenement.objects.filter(Q(description__icontains=query)).filter(end_date__isnull=False).exclude(date__lte=datetime.date.today())
        context = {
            'publications':publications,
        }
        return render(request, 'evenement/event_search.html', context)

class FiltreVoyage(View):
    def get(self, request, *args, **kwargs):
        location=self.request.GET.get('location')
        x=Evenement.objects.filter(end_date__isnull=False).exclude(date__lte=datetime.date.today())
        if request.GET.get('date'):
            try:
                date=self.request.GET.get('date')    
                if request.GET.get('end_date'):
                    x= x & Evenement.objects.filter(date__lte=end_date).filter(date__gte=date)                
                else:                
                    x= x & Evenement.objects.filter(date__lte=date)  
            except:
                pass 
        else:
            try:
                end_date=self.request.GET.get('end_date')            
                x= x & Evenement.objects.filter(date__lte=end_date)  
            except:
                pass   

        try:
            tariff_max=int(self.request.GET.get('tariff'))
            x = x & Evenement.objects.filter(tariff__lte = tariff_max)
        except:
            pass        
        
        if location is not None:
            x = x & Evenement.objects.filter(location =location)  

        y=Evenement.objects.filter(location =location)
        context = {
        'publications': x,
        'connexes': y,
        }
        return render(request, 'evenement/event_search.html',context)  
