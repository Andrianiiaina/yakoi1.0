from django.shortcuts import render
from .models import Evenement, Comment, Tag, Ville
from django.core.paginator import Paginator
from django.db.models import Count
import datetime
#le grand calendrier
def get_calendar(request):
        evenements_ = Evenement.objects.exclude(date__lte=datetime.date.today()+datetime.timedelta(days=-1)).order_by('date')
        context= {
            'villes':Ville.objects.all().order_by(),
            'evenements':Paginator(evenements_, 10).get_page(request.GET.get('page')),
            'tags':Tag.objects.all(),
            'famous_events':Evenement.objects.annotate(num_like=Count('likes')).order_by('-num_like')[:8],
        }
        return render(request, 'evenements/big_calendar.html', context)


def filter_event(request):
        today_date=datetime.date.today()
        categories=request.GET.getlist('activities[]')
        location=request.GET.get('region')
        order=request.GET.get('order')
        category_type=request.GET.get('type')
        evenements=Evenement.objects.all()
        
        if category_type != 'all'and category_type is not None:
            evenements=Evenement.objects.filter(category=category_type)
        if categories:   
            evenements=Evenement.objects.filter(category='')
            for i in categories:
                if i != " ":
                    evenements =evenements | Evenement.objects.filter(category=i)
                 
        if order == 'asc':
            evenements=evenements & Evenement.objects.all()
        elif order == 'desc':
            evenements=evenements & Evenement.objects.all().order_by('-date')
        if location != 'all':
            evenements = evenements & Evenement.objects.filter(location =location) 
        
        tariff_max=request.GET.get('tariff')
        evenements = evenements & Evenement.objects.filter(tariff__lte = tariff_max)
        return render(request, 'evenements/event_search.html',{'publications': evenements})   
