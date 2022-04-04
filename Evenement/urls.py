from django.urls import path
from .views import EvenementCategoryView,FiltreSemantique,Explore,FiltreVoyage, CommentReplyView, EventListView, EventDetailView, EventEditView, EventDeleteView,CommentDeleteView, CommentReplyView, AddLike, EvenementListView,VoyageListView,EventNotification, FollowNotification, RemoveNotification,EventSearch,FiltreEvent

urlpatterns = [ 
    path('', EventListView.as_view(), name='event_list'),
    path('évènement/<str:username>/<str:url>', EventDetailView.as_view(),  name='event_detail'),
    path('évènement/modification-évènement/<str:username>/<int:pk>', EventEditView.as_view(),  name='event_edit'),
    path('evenement/delete/<int:pk>', EventDeleteView.as_view(),  name='event_delete'),
    #commentairees
    path('évènement/<str:username>/<int:event_pk>/comment/delete/<int:pk>', CommentDeleteView.as_view(),  name='comment_delete'),
    path('évènement/<int:évènement_pk>/comment/<int:pk>/reply', CommentReplyView.as_view(), name="comment_reply"),
    path('évènement/<int:évènement_pk>/comment/<int:pk>/reply', CommentReplyView.as_view(), name="comment_reply"),
    #likes
    path('<str:url>/like', AddLike.as_view(), name="like"),
    #listes de touts les evenements
    path('le_grand_calendrier', EvenementListView.as_view(), name="calendar"),
    #voyage organisé
    path('voyages_organisés', VoyageListView.as_view(), name="voyage_list"),

    #notifications
    path('notification/<int:notification_pk>/évènement/<int:evenement_pk>',EventNotification.as_view(),name="event_notification"),   
    path('notification/<int:notification_pk>/profile/<int:profile_pk>',FollowNotification.as_view(),name="follow_notification"),
    path('notification/delete/<int:notification_pk>',RemoveNotification.as_view(), name="remove_notification"),
    #recherche et trie
    
    path('recherche-d-évènement', EventSearch.as_view(), name="event_search"),
    path('évènement-filtre/', FiltreEvent.as_view(), name="event_filtre"),
    path('voyage-filtre/', FiltreVoyage.as_view(), name="voyage_filtre"),
    path('évènement/category/<str:category>/', EvenementCategoryView.as_view(), name='event_category'),
    
    #tag
    path('évènement/explorer/', Explore.as_view(), name='explore'),
    path('filtre-par-mot-cle', FiltreSemantique.as_view(), name='semantic_filter'),
    


]
   