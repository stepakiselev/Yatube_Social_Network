from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page': page,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    number_posts = author.posts.count()
    is_following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author).exists()
    user = get_object_or_404(User, username=username)
    following = user.follower.count()
    followers = user.following.count()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts': posts,
        'page': page,
        'number_posts': number_posts,
        'is_following': is_following,
        'following': following,
        'followers': followers
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    author = post.author
    number_posts = author.posts.count()
    user = get_object_or_404(User, username=username)
    following = user.follower.count()
    followers = user.following.count()
    context = {
        'author': author,
        'post': post,
        'form': form,
        'comments': comments,
        'number_posts': number_posts,
        'following': following,
        'followers': followers
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post
                    )
    if post.author != request.user:
        return redirect('post', username=username, post_id=post.id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post.id)
    return render(
        request, 'new.html',
        {'post': post, 'form': form}
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post', username, post_id)
    return render(
        request, 'include/comments.html', {'form': form, 'post': post}
    )


@login_required
def follow_index(request):
    current_user = request.user
    posts = Post.objects.filter(
        author__following__user=request.user
    ).all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'follow.html',
        {'page': page, 'paginator': paginator, 'user': current_user}
    )


@login_required
def profile_follow(request, username):
    profile = get_object_or_404(User, username=username)
    if request.user != profile:
        Follow.objects.get_or_create(
            user=request.user,
            author=profile
        )

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    unfollow_user = get_object_or_404(User, username=username)
    get_object_or_404(
        Follow,
        user=request.user,
        author=unfollow_user
    ).delete()
    return redirect('profile', username=username)
