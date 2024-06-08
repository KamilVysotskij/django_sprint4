from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView, TemplateView
)
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.db.models import Count
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from blog.models import Post, Category, Comment, User
from blog.forms import PostForm, CommentForm


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
        post_pk = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_pk)
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_pk'])
        if comment.post_id != post.pk:
            raise Http404()
        return comment


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.post.pk})

    def get_object(self):
        post_pk = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_pk)
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_pk'])
        if comment.post_id != post.pk:
            raise Http404()
        return comment


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/add_comment.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])

        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = post
        comment.save()

        return redirect('blog:post_detail', pk=self.kwargs['pk'])


class UserProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = "username"
    slug_field = "username"
    context_object_name = 'user'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.object.posts.all().annotate(comment_count=Count('comments')).order_by('-pub_date')
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context['page_obj'] = page_obj
        context['profile'] = self.object
        if self.request.user.is_authenticated and self.request.user == self.object:
            context['can_edit'] = True
            context['change_password_url'] = 'password_change'  # URL для изменения пароля
        return context


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username', 'email']
    slug_url_kwarg = "username"
    slug_field = "username"
    context_object_name = 'user'

    def test_func(self):
        return self.request.user == self.get_object()

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


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
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


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
        return redirect('blog:post_detail', pk=self.kwargs['pk'])

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
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = Post.published_objects.all().annotate(comment_count=Count('comments')).order_by('-pub_date')
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
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if request.user == self.object.author:
            return super().get(request, *args, **kwargs)

        if not self.object.is_published or not self.object.category.is_published:
            raise Http404()

        return super().get(request, *args, **kwargs)

class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']  # Извлечение slug категории из URL
        category = get_object_or_404(Category, slug=category_slug, is_published=True)
        return Post.published_objects.filter(category=category)  # Выборка опубликованных постов из данной категории

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']  # Извлечение slug категории из URL
        context['category'] = get_object_or_404(Category, slug=category_slug, is_published=True)  # Добавление объекта категории в контекст
        return context



# def index(request):
#     template = 'blog/index.html'
#     post_list = Post.published_objects.all()[:5]
#     context = {'post_list': post_list}
#     return render(request, template, context)


# def post_detail(request, pk):
#     template = 'blog/detail.html'
#     post = get_object_or_404(
#         Post.published_objects.all(),
#         pk=pk)
#     context = {
#         'post': post
#     }
#     return render(request, template, context)


# def category_posts(request, category_slug):
#     template = 'blog/category.html'
#     category = get_object_or_404(
#         Category,
#         slug=category_slug,
#         is_published=True)
#     post_list = Post.published_objects.all().filter(
#         category=category)
#     context = {
#         'category': category,
#         'post_list': post_list
#     }
#     return render(request, template, context)