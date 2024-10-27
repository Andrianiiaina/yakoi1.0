from django.urls import path
from .views import FiltreVoyage,VoyageSearch,VoyageListView, EvenementCategoryView, FiltreSemantique, Explore,EventSearch,FiltreEvent,BigCalendarListView,CommentReplyView,EventNotification,EventListView,EventDetailView,EventEditView,EventDeleteView,CommentDeleteView, AddLike, FollowNotification,RemoveNotification

urlpatterns = [ 
    path('', EventListView.as_view(), name='event_list'),
    path('listes-des-évènements', BigCalendarListView.as_view(), name='evenements'),
    path('voyages', VoyageListView.as_view(), name='voyages'),
    
    path('évènement/<int:pk>/', EventDetailView.as_view(),  name='event_detail'),
    path('évènement/modification-évènement/<int:pk>', EventEditView.as_view(),  name='event_edit'),
    path('evenement/delete/<int:pk>', EventDeleteView.as_view(),  name='event_delete'),
    
    path('évènement/comment/<int:event_pk>/<int:comment_pk>/reply', CommentReplyView.as_view(), name="comment_reply"),
    path('évènement/comment/delete/<int:event_pk>/<int:pk>', CommentDeleteView.as_view(),  name='comment_delete'),
    
    path('notification/<int:notification_pk>/évènement/<int:evenement_pk>',EventNotification.as_view(),name="event_notification"),   
    path('notification/<int:notification_pk>/profile/<int:profile_pk>',FollowNotification.as_view(),name="follow_notification"),
    path('notification/delete/<int:notification_pk>',RemoveNotification.as_view(), name="remove_notification"),
    
    path('event/<int:pk>/like', AddLike.as_view(), name="like"),

    path('évènement-filtre/', FiltreEvent.as_view(), name="event_filtre"),
    path('recherche-d-évènement/', EventSearch.as_view(), name="event_search"),
    path('évènement/explorer/', Explore.as_view(), name='explore'),
    path('filtre-par-mot-cle', FiltreSemantique.as_view(), name='tri_event'),
    path('search_voyage/', VoyageSearch.as_view(), name="search_voyages"),
    path('voyage-filtre/', FiltreVoyage.as_view(), name="voyage_filtre"),
    
    path('category/<str:category>/', EvenementCategoryView.as_view(), name='event_category'),
    
    
   

  
  
]
   