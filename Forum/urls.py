
from django.urls import path
from Forum.views import ForumListView,ForumDeleteView,ForumDetailView,CommentDeleteView,CommentReplyView

urlpatterns = [
    path('forum', ForumListView.as_view(), name="forum_list"),
    path('forum/<str:url>', ForumDetailView.as_view(), name="forum_detail"),
    
    path('forum/supprimer/<int:pk>', ForumDeleteView.as_view(), name="forum_delete"),
    path('forum/<int:forum_pk>/suppression-commentaires/<int:pk>', CommentDeleteView.as_view(),  name='forum_comment_delete'),
    path('forum/<int:forum_pk>/reponse-a-un-commentaire/<int:pk>', CommentReplyView.as_view(), name="forum_comment_reply"),

]