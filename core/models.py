from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)   
    bio = models.TextField(blank = True )
    profile_img = models.ImageField(upload_to = 'profile_images' ,  default = 'blank_profile_picture.png')
    location =  models.CharField(max_length = 100 , blank = True)

    def __str__(self):
        return self.user.username
    
class Post(models.Model):
    id = models.UUIDField(primary_key=True , default = uuid.uuid4)
    user = models.CharField(max_length = 100)
    image = models.ImageField(upload_to = 'post_images') 
    caption = models.TextField()
    created_at = models.DateTimeField(default = datetime.now)
    no_of_likes = models.IntegerField(default = 0)

    def __str__(self):
        return self.user

class LikePost(models.Model):
    post_id = models.CharField(max_length = 100)
    username = models.CharField(max_length = 100)

    def __str__(self):
        return self.username
    
class FollowersCount(models.Model):
    follower = models.CharField(max_length = 100)
    user = models.CharField(max_length = 100)

    def __str__(self):
        return self.user
    
class Notification(models.Model):
    sender = models.CharField(max_length=100) 
    sender_profile = models.ForeignKey(Profile, on_delete=models.CASCADE,null=True, default=None)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True) 
    date_time = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.sender} -> {self.recipient.username}"
