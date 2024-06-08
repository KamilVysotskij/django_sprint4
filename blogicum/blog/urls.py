from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:pk>/comment/', views.AddCommentView.as_view(), name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_pk>/', views.EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_pk>/', views.CommentDeleteView.as_view(), name='delete_comment'),
    path('profile/<slug:username>/', views.UserProfileView.as_view(), name='profile'),
    path('profile/<slug:username>/edit/', views.UserProfileUpdateView.as_view(), name='edit_profile'),
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
]