from django.urls import path
from .views import Explore,EventListView,EventDetailView,EventEditView,EventDeleteView
from .notification_views import EventNotification, FollowNotification,RemoveNotification
from . import big_calendar_views  
from .interaction_views import CommentDeleteView
from . import interaction_views
from . import views 
urlpatterns = [ 
    path('', EventListView.as_view(), name='event_list'),
    path('listes-des-évènements', big_calendar_views.get_calendar, name='evenements'),
    
    path('évènement/<int:pk>/', EventDetailView.as_view(),  name='event_detail'),
    path('évènement/comment/<int:pk>/', interaction_views.comment_post,  name='comment_event'),
    path('évènement/modification-évènement/<int:pk>', EventEditView.as_view(),  name='event_edit'),
    path('evenement/delete/<int:pk>', EventDeleteView.as_view(),  name='event_delete'),
    
    path('évènement/comment/<int:event_pk>/<int:comment_pk>/reply', interaction_views.replay_comment_post, name="comment_reply"),
    path('évènement/comment/delete/<int:event_pk>/<int:pk>', CommentDeleteView.as_view(),  name='comment_delete'),
    
    path('notification/<int:notification_pk>/évènement/<int:evenement_pk>',EventNotification.as_view(),name="event_notification"),   
    path('notification/<int:notification_pk>/profile/<int:profile_pk>',FollowNotification.as_view(),name="follow_notification"),
    path('notification/delete/<int:notification_pk>',RemoveNotification.as_view(), name="remove_notification"),
    
    path('event/<int:pk>/like', interaction_views.like_event, name="like"),

    path('évènement-filtre/', big_calendar_views.filter_event, name="event_filtre"),
    path('evenement/search', interaction_views.search_event, name="event_search"),
    path('évènement/explorer/', Explore.as_view(), name='explore'),
    
    
    
   

  
  
]
   