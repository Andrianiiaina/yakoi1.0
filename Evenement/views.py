from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from .models import Evenement, Comment, Notification, Image, Tag, Ville
from Profile.models import UserProfile
from .forms import EventForm, CommentForm, VoyageForm
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.core.paginator import Paginator
from socialnetwork.cryptage import cryptage_url, decryptage_url
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.views.generic.dates import WeekArchiveView
from django.db.models import Count
import datetime

#test si l'urn decrypter est de type int
def test_user(url):
    try:
        pk=int(decryptage_url(url))
    except pk.DoesNotExist:
        raise Http404("cet evenement n'existe pas")  
    return pk

class EventListView(View):
    def get(self, request, *args,**kwargs):
        evenements=Evenement.objects.all().exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).filter(datefin__isnull=True).order_by('-create_on')[:10]
        
        a=Evenement.objects.filter(titre="")

        if request.user.is_authenticated:
            profile=UserProfile.objects.get(pk=request.user.pk)
            #si l'utilisateur n'as pas encore de lien profile
            if  profile.lien == '':
                return redirect('profile_edit', request.user.pk) 
            #personnalisation des evenents selon les activites de l'utilisateur
            if profile.activities:
                for i in profile.activities.split(','):
                    a= a | Evenement.objects.filter(category=i)            
                evenements=a.exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).filter(datefin__isnull=True)

        tags=Tag.objects.all().order_by('name')
        #recuperation des evenements chaque semaine
        date_du_jour=datetime.date.today()
        start_week = date_du_jour - datetime.timedelta(date_du_jour.weekday())
        end_week=start_week + datetime.timedelta(7)
        events_week=Evenement.objects.filter(date__range=[start_week, end_week]).exclude(date__lte=date_du_jour+datetime.timedelta(days=-1))
        
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
            titre = form.cleaned_data['titre']
            new_event = form.save(commit=False)
            new_event.user = request.user
            new_event.category = request.POST.get('category')
            new_event.date=request.POST.get('datet') 
 
            new_event.save()
            messages.success(request, "l'événement  a bien été ajouté!")
            
            new_event.url=cryptage_url(new_event.pk)
            new_event.create_tags()      
            villes=Ville.objects.filter(name=new_event.lieu).first()
            if villes is None:
                Ville.objects.create(name=new_event.lieu)
                
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
    def get(self,request,url, *args,**kwargs):
        pk=int(decryptage_url(url))
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
    def post(self,request,url, *args,**kwargs):  
        pk=test_user(url)
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
        return redirect('event_detail',username=evenement.user.username,url=url)       

class EventDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Evenement
    template_name='delete.html'    
    success_url=reverse_lazy('event_list')   
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user 

class EventEditView(LoginRequiredMixin,UserPassesTestMixin, UpdateView):
    model= Evenement
    fields=["titre","description","lieu","date"]
    template_name = 'edit.html'
   
    def get_success_url(self):
        pk=self.kwargs['pk']
        username=self.kwargs['username']
        return reverse_lazy('event_detail', kwargs={'username':username, 'url':cryptage_url(pk)})
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user  

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Comment
    template_name='delete.html' 

    def get_success_url(self):
        pk=self.kwargs['event_pk']
        username=self.kwargs['username']
        return reverse_lazy('event_detail', kwargs={'username':username,'url':cryptage_url(pk)})
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user

class AddLike(LoginRequiredMixin, View):
    def post(self, request,url,*args,**kwargs):
        pk=test_user(url)
        evenement= Evenement.objects.get(pk=pk)
        is_like = False
        for like in evenement.likes.all():
            if like == request.user:
                is_like = True
                break
        if not is_like:  
            evenement.likes.add(request.user)
            notification=Notification.objects.create(notification_type=1, from_user=request.user, to_user=evenement.user,evenement=evenement)
        if is_like:
            evenement.likes.remove(request.user) 
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
class EvenementListView(View):
    def get(self, request, *args,**kwargs):

        evenements = Evenement.objects.all().exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).order_by('date')
        #les evenemnts qui a le plus de like
        celebrate_evenements=Evenement.objects.all().annotate(like=Count('likes')).order_by('-like')[:8]  

        paginator = Paginator(evenements, 10)
        page_number = request.GET.get('page')
        evenements_obj = paginator.get_page(page_number)

        form =EventForm()
        tags=Tag.objects.all()
        villes=Ville.objects.all().order_by()

        context= {
            'villes':villes,
            'form':form,
            'evenements_obj':evenements_obj,
            'tags':tags,
            'c_evenements':celebrate_evenements,
        }
        return render(request, 'evenement/evenements_list.html', context)

class FiltreEvent(View):
    def get(self, request, *args, **kwargs):
        date_du_jour=datetime.date.today()
        categories=self.request.GET.getlist('activities[]')
        lieu=self.request.GET.get('region')
        jour=self.request.GET.get('jour')
        category=self.request.GET.get('type')
        x=Evenement.objects.all()
        
        if category != 'all'and category is not None:
            x=Evenement.objects.filter(category=category)
            

        if categories:   
            x=Evenement.objects.filter(category='')
            for i in categories:
                if i != " ":
                    x =x | Evenement.objects.filter(category=i)
                 

            
        if jour == 0:
            x=x & Evenement.objects.all().order_by('-date')
        elif jour == '1':
            x=x & Evenement.objects.filter(date=date_du_jour)
        elif jour == '2':
            dt=date_du_jour+datetime.timedelta(days=1)
            x=x & Evenement.objects.filter(date=dt)           
        elif jour == '3':
            start_week = date_du_jour - datetime.timedelta(date_du_jour.weekday())
            end_week=start_week + datetime.timedelta(7)
            x=x & Evenement.objects.filter(date__range=[start_week, end_week]) 
        elif jour == '4':
            dt=date_du_jour+datetime.timedelta(date_du_jour.weekday())
            x=x & Evenement.objects.filter(date__range=[date_du_jour,dt])     
         
        try:
            tarif_max=int(self.request.GET.get('tarif'))
            x = x & Evenement.objects.filter(tarif__lte = tarif_max)
        except:
            pass
            
        if lieu != 'all':
            x = x & Evenement.objects.filter(lieu =lieu) 

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
        form_voyage=VoyageForm()
        evenements=Evenement.objects.filter(datefin__isnull = False)
        context= {
            'evenements':evenements,
            'formv':form_voyage,
        }
        return render(request, 'voyage.html', context)

    def post(self, request, *args,**kwargs):
        form = VoyageForm(request.POST)
        files = request.FILES.getlist('image')
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.user = request.user
             #seulement si le date de debut est < date fin
            if new_event.date <= new_event.datefin:          
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
        publications=Evenement.objects.filter(Q(description__icontains=query)).filter(datefin__isnull=False).exclude(date__lte=datetime.date.today())
        context = {
            'publications':publications,
        }
        return render(request, 'evenement/event_search.html', context)

class FiltreVoyage(View):
    def get(self, request, *args, **kwargs):
        lieu=self.request.GET.get('lieu')
        x=Evenement.objects.filter(datefin__isnull=False).exclude(date__lte=datetime.date.today())
        if request.GET.get('date'):
            try:
                date=self.request.GET.get('date')    
                if request.GET.get('datefin'):
                    x= x & Evenement.objects.filter(date__lte=datefin).filter(date__gte=date)                
                else:                
                    x= x & Evenement.objects.filter(date__lte=date)  
            except:
                pass 
        else:
            try:
                datefin=self.request.GET.get('datefin')            
                x= x & Evenement.objects.filter(date__lte=datefin)  
            except:
                pass   

        try:
            tarif_max=int(self.request.GET.get('tarif'))
            x = x & Evenement.objects.filter(tarif__lte = tarif_max)
        except:
            pass        
        
        if lieu is not None:
            x = x & Evenement.objects.filter(lieu =lieu)  

        y=Evenement.objects.filter(lieu =lieu)
        context = {
        'publications': x,
        'connexes': y,
        }
        return render(request, 'evenement/event_search.html',context)  
