from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from blog.forms import CommentForm, PostForm
from blog.models import Category, Comment, Post, User


class RegistrationView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class EditCommentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_object(self):
        post_pk = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=post_pk)
        comment = get_object_or_404(Comment, pk=self.kwargs.get('comment_pk'))
        if comment.post_id != post.pk:
            raise Http404()
        return comment

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['edit_comment_mode'] = True
    #     context['delete_comment_mode'] = False
    #     return context


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'pk': self.object.post.pk})

    def get_object(self):
        post_pk = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=post_pk)
        comment = get_object_or_404(Comment, pk=self.kwargs.get('comment_pk'))
        if comment.post_id != post.pk:
            raise Http404()
        return comment

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['delete_comment_mode'] = True
    #     context['edit_comment_mode'] = False
    #     return context


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/add_comment.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))

        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = post
        comment.save()

        return redirect('blog:post_detail', pk=self.kwargs.get('pk'))


class UserProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = settings.PAGINATE_BY

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return user.posts.all().annotate(
            comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['profile'] = user
        context['username'] = user.username
        if self.request.user.is_authenticated and self.request.user == user:
            context['can_edit'] = True
            context['change_password_url'] = 'password_change'
        return context


class UserProfileUpdateView(LoginRequiredMixin,
                            UserPassesTestMixin,
                            UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username', 'email']
    slug_url_kwarg = 'username'
    slug_field = 'username'
    context_object_name = 'user'

    def test_func(self):
        return self.request.user == self.get_object()

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PasswordChangeView(LoginRequiredMixin, TemplateView):
    template_name = 'users/password_change.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['edit_post_mode'] = False
    #     context['delete_post_mode'] = False
    #     return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs.get('pk'))

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['edit_post_mode'] = True
    #     context['delete_post_mode'] = False
    #     return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        # context['delete_post_mode'] = True
        # context['edit_post_mode'] = False
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = settings.PAGINATE_BY

    def get_queryset(self):
        queryset = Post.published_objects.all().annotate(
            comment_count=Count('comments')).order_by('-pub_date')
        return queryset


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        # context['delete_post_mode'] = False
        # context['edit_post_mode'] = False
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.user == self.object.author:
            return super().get(request, *args, **kwargs)

        if (not self.object.is_published
           or not self.object.category.is_published):
            raise Http404()

        return super().get(request, *args, **kwargs)


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = settings.PAGINATE_BY

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category,
                                     slug=category_slug,
                                     is_published=True)
        return Post.published_objects.filter(category=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        context['category'] = get_object_or_404(Category,
                                                slug=category_slug,
                                                is_published=True)
        return context
