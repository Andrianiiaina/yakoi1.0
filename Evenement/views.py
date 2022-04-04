from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, Http404
from .models import Evenement, Comment, Image, Ville, Notification, Tag
from .forms import EventForm, CommentForm, VoyageForm
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import datetime
from django.core.paginator import Paginator
from socialnetwork.cryptage import cryptage_url, decryptage_url
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.views.generic.dates import WeekArchiveView
from django.db.models import Count, Q
import datetime
from Profile.models import UserProfile 
#test si l'evenement crypter sur l'url existe
def test_user(url):
    try:
        pk=int(decryptage_url(url))
    except pk.DoesNotExist:
        raise Http404("cet evenement n'existe pas")  
    return pk

activites=['jeu video','foot','basket','informatique','multimedia']

class EventListView(View):
    def get(self, request, *args,**kwargs):
        evenements=Evenement.objects.all().exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).filter(datefin__isnull=True).order_by('-create_on')[:10]   
        date_du_jour=datetime.date.today()
        start_week = date_du_jour - datetime.timedelta(date_du_jour.weekday())
        end_week=start_week + datetime.timedelta(7)

        events_week=Evenement.objects.filter(date__range=[start_week, end_week]).exclude(date__lte=date_du_jour+datetime.timedelta(days=-1))
        
        villes=Ville.objects.all().order_by('name')
        activities=activites
        form_evenement=EventForm()
        tags = Tag.objects.all()
        context= {
            'form_evenement':form_evenement,
            'events_week':events_week,
            'evenements':evenements,
            'villes':villes,
            'activites':activites,
            'tags':tags,
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
            new_event.date=request.POST.get('date_debut') 
            #on srock le date_fin si c'est un voyage
            if request.POST.get('date_fin'):
                if new_event.date > request.POST.get('date_fin'):
                    messages.error(request,"le date du debut de voyage doit etre inferieur au date du fin de voyage")                  
                    return redirect('profile', username=request.user.username)
                else: 
                    new_event.datefin = request.POST.get('date_fin')
            new_event.save()
            messages.success(request, "l'événement  a bien été ajouté!")
            new_event.url=cryptage_url(new_event.pk)


            villes=Ville.objects.filter(name=new_event.lieu).first()

            #si une nouvelle ville => on le stock
            if villes is None:
                Ville.objects.create(name=new_event.lieu)

            #on recupere les images    
            for f in files:
                img=Image(image=f)
                img.save()
                new_event.image.add(img)

            new_event.create_tags()   

            new_event.save()  
            profile= UserProfile.objects.get(pk=new_event.user)

            for follower in profile.followers.all():    
                notification=Notification.objects.create(notification_type=4, from_user=new_event.user, to_user=follower, evenement=new_event)
           
            context = {
                'form':form,
            }
            return redirect('event_detail',url=new_event.url,username=new_event.user.username)   
        else: 
            messages.error(request, "la creation d'evenement a echouée, veuillez verifier vos données")
            return redirect('profile', username=request.user.username)   

class VoyageListView(View):
    def get(self, request, *args,**kwargs):

        voyages=Evenement.objects.filter(datefin__isnull = False)
        context= {
            'voyages':voyages,
        }
        return render(request, 'evenement/voyage.html', context)

class EventDetailView(View):
    def get(self,request,url, *args,**kwargs):
        pk=test_user(url)      
        evenement= Evenement.objects.get(pk=pk)
        form = CommentForm()
        comments=Comment.objects.filter(event=evenement).order_by('-create_on') 

        #on recupere les evenements du meme category
        #evenements=Evenement.objects.exclude(date__lte=datetime.date.today()).filter(category = evenement.category)[:8]
        evenements=Evenement.objects.filter(category = evenement.category)[:8]
       
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
            if evenement.user != request.user:
                notification=Notification.objects.create(notification_type=2, from_user=request.user, to_user=evenement.user, evenement=evenement)
      
        comments=Comment.objects.filter(event=evenement).order_by('create_on')
        context = {
            'comments':comments,
            'form':form,
        }    
        return redirect('event_detail',url=url, username=evenement.user.username)       

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
        event.create_tags() 
        return self.request.user == event.user  

class CommentDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Comment
    template_name='delete.html' 

    def get_success_url(self):
        pk=self.kwargs['event_pk']
        username=self.kwargs['username']

        
        return reverse_lazy('event_detail', kwargs={'username':username,'url':cryptage_url(pk),})
    def test_func(self):
        event=self.get_object()
        return self.request.user == event.user

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
           
            
        return redirect('event_detail',url=cryptage_url(evenement_pk),username=evenement.user.username)    

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
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=evenement.user,evenement=evenement)
       
        if is_like:
            evenement.likes.remove(request.user)
        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)   

class EvenementListView(View):
    def get(self, request, *args,**kwargs):
        evenements = Evenement.objects.all().exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).order_by('date')
        c_evenements=Evenement.objects.all().annotate(like=Count('likes')).order_by('-like')[:8]  
        paginator = Paginator(evenements, 10)
        page_number = request.GET.get('page')
        evenements_obj = paginator.get_page(page_number)
        form =EventForm()
        villes=Ville.objects.all().order_by()
        context= {
            'villes':villes,
            'form':form,
            'evenements_obj':evenements_obj,
            'c_evenements':c_evenements,
        }
        return render(request, 'evenement/evenements_list.html', context)

class EventNotification(View):
    def get(self, request, notification_pk, evenement_pk, *args,**kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        evenement =Evenement.objects.get(pk=evenement_pk)
        notification.user_has_seen = True
        notification.save()

        return redirect('event_detail', url=cryptage_url(evenement_pk),username=evenement.user.username)

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

class EventSearch(View):
    def get(self, request, *args, **kwargs):
        query=self.request.GET.get('query')
        publications=Evenement.objects.filter(Q(description__icontains=query)) 
        context = {
            'publications':publications,
        }
        return render(request, 'evenement/event_search.html', context)

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
            
        
        if self.request.GET.getlist('activities[]'):   
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
        else:
            pass  
        
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

class FiltreVoyage(View):

    def get(self, request, *args, **kwargs):
        lieu=self.request.GET.get('region')

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
        
        if lieu != 'all':
            x = x & Evenement.objects.filter(lieu =lieu) 
        
        y=Evenement.objects.filter(lieu =lieu)
        context = {
        'publications': x,
        'explore_form': y,
        }
        return render(request, 'evenement/event_search.html',context)

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
        mere=['autres','technologie','plein air','salon','culture','sport','fete']
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
        context={
            'publications':evenements,
        }
        return render(request,'evenement/event_search.html',context)

