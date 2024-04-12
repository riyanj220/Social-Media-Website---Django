from django.shortcuts import render ,redirect
from django.contrib.auth.models import User 
from django.contrib import auth
from django.contrib import messages
from .models import Profile ,Post ,LikePost ,FollowersCount ,Notification
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from itertools import chain
from random import shuffle
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden,HttpResponseNotAllowed

@login_required(login_url = 'signin/')
def index(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile = Profile.objects.get(user = user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower = request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user = usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # for suggestions

    active_user_following = FollowersCount.objects.filter(follower=request.user.username).exclude(user=request.user.username).values_list('user', flat=True)
    active_user_following = list(active_user_following) 
    active_user_following.append(request.user.username)  

    suggested_profiles = Profile.objects.exclude(user__username__in=active_user_following)

    suggested_profiles = list(suggested_profiles)
    shuffle(suggested_profiles)
    suggested_profiles = suggested_profiles[:4]

    return render(request , 'index.html' , {'user_profile': user_profile , 'post' : feed_list,'suggested_profiles': suggested_profiles})

@login_required(login_url = 'signin/')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST.get('caption')

        new_post = Post.objects.create(user = user , image = image, caption = caption)
        new_post.save()
        return redirect('/')
    
def delete_post(request,post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('/')

    
@login_required(login_url = 'signin/')
def search(request):
    user_object = User.objects.get(username = request.user.username)
    user_profile_pic = Profile.objects.get(user = user_object)

    user_profile = None
    if request.method == 'POST':
        username = request.POST.get('username') 
        users = Profile.objects.filter(user__username__icontains=username)

    return render(request, 'search.html', {'users': users, 'user_profile': user_profile, 'user_profile_pic': user_profile_pic})


@login_required(login_url = 'signin/')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    
    post = Post.objects.get(id = post_id)

    if isinstance(post.user, str):
        post_owner_username = post.user
    else:
        post_owner_username = post.user.username

    if username != post_owner_username:
        like_filter = LikePost.objects.filter(post_id=post.id, username=username).first()

        if like_filter is None:
            new_like = LikePost.objects.create(post_id=post.id, username=username)
            new_like.save()
            post.no_of_likes += 1
            post.save()
            
            recipient_user = User.objects.get(username=post.user)
            sender_profile = Profile.objects.get(user=request.user)
            Notification.objects.create(sender=username,sender_profile=sender_profile, recipient=recipient_user, post=post)
            
            return redirect('/')
        else:
            like_filter.delete()
            post.no_of_likes -= 1
            post.save()

            recipient_user = User.objects.get(username=post.user)
            
            Notification.objects.filter(sender=username, recipient=recipient_user, post=post).delete()
    else:
        like_filter = LikePost.objects.filter(post_id=post.id, username=username).first()

        if like_filter is None:
            new_like = LikePost.objects.create(post_id=post.id, username=username)
            new_like.save()
            post.no_of_likes += 1
            post.save()
        else:
            like_filter.delete()
            post.no_of_likes -= 1
            post.save()
    
    return redirect('/')

def notifications(request):
    user_notifications = Notification.objects.filter(recipient=request.user).order_by('-date_time')[:4]
    notifications_data = []
    
    for notification in user_notifications:
        sender_profile = notification.sender_profile
        sender_username = notification.sender
        
        if sender_profile:
            profile_picture = sender_profile.profile_img.url if sender_profile.profile_img else None
        else:
            profile_picture = None

        formatted_date_time = notification.date_time.strftime('%B %d, %Y, %I:%M %p')
        
        notifications_data.append({
            'sender': sender_username,
            'profile_picture': profile_picture,
            'date_time': formatted_date_time
        })
        
    return JsonResponse({'notifications': notifications_data})

@login_required(login_url = 'signin/')
def profile(request , pk):
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user = pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower , user=user).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"

    user_followers = len(FollowersCount.objects.filter(user = pk))
    user_following = len(FollowersCount.objects.filter(follower = pk))

    context = {
        'user_object': user_object,
        'user_profile' : user_profile,
        'user_posts' : user_posts,
        'user_post_length' : user_post_length,
        'button_text' : button_text,
        'followers_count' : user_followers,
        'user_following' : user_following
    }
    return render(request, 'profile.html' , context)


@login_required(login_url = 'signin/')
def follow(request):
    if request.method == 'POST':
        follower = request.POST.get('follower')
        user = request.POST.get('user')

        if FollowersCount.objects.filter(follower = follower , user = user).first():
            delete_follower = FollowersCount.objects.get(follower = follower , user = user )
            delete_follower.delete()
            return redirect('/profile/'+user)
        
        else:
            new_follower = FollowersCount.objects.create(follower = follower, user = user)
            new_follower.save()
            return redirect('/profile/'+user)
    
    elif request.method == 'GET':
        follower = request.GET.get('follower')
        user = request.GET.get('user')

        FollowersCount.objects.create(follower=follower, user=user)
        return redirect('/')
    else:
        return redirect('/')
    
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email  = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:
            if User.objects.filter(email = email).exists():
                messages.info(request , "Email already exists")
                return redirect('signup')
            
            elif User.objects.filter(username = username).exists():
                messages.info(request , "Username is already taken")
                return redirect('signup')
            
            else:
                user = User.objects.create_user(
                    username = username, 
                    email = email ,
                    password = password
                )
                user.save()

                user_login = auth.authenticate(username = username , password = password)
                auth.login(request , user_login)

                user_model = User.objects.get(username=user.username)
                new_profile = Profile.objects.create(user=user_model )
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request , "Password Not Matching")
            return redirect('signup')
        
    return render(request , 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')  
        password = request.POST.get('password') 
        
        user = auth.authenticate(username = username , password = password)

        if user is not None:
            auth.login(request , user)
            return redirect('/')
        else:
            messages.info(request , "Invalid Credentials")
            return redirect('signin')
        
    else:
        return render(request , 'signin.html')

@login_required(login_url = 'signin/')
def logout(request):
    auth.logout(request)
    return redirect('signin')


@login_required(login_url = 'signin/')
def settings(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        image = request.FILES.get('image', user_profile.profile_img)
        bio = request.POST.get('bio', user_profile.bio)
        location = request.POST.get('location', user_profile.location)

        user_profile.profile_img = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()
        
        return redirect('/')
    
    return render(request, 'setting.html', {'user_profile': user_profile})
