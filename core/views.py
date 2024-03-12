from django.shortcuts import render ,redirect
from django.contrib.auth.models import User 
from django.contrib import auth
from django.contrib import messages
from django.http import HttpResponse 
from .models import Profile
from django.contrib.auth.decorators import login_required


@login_required(login_url = 'signin/')
def index(request):
    return render(request , 'index.html')

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