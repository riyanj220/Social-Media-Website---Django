from django.shortcuts import render ,redirect
from django.contrib.auth.models import User 
from django.contrib import auth
from django.contrib import messages
from django.http import HttpResponse 
from .models import Profile

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

                # log user in and direct to settings page

                #create a profile object for the new user

                user_model = User.objects.get(username=user.username)
                new_profile = Profile.objects.create(user=user_model , id_user = user_model.id)
                new_profile.save()
                return redirect('signup')
        else:
            messages.info(request , "Password Not Matching")
            return redirect('signup')
        
    return render(request , 'signup.html')