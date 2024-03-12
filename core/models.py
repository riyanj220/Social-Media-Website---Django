from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    bio = models.TextField(blank = True )
    profile_img = models.ImageField(upload_to = 'profile_images' ,  default = 'blank_profile_picture.png')
    location =  models.CharField(max_length = 100 , blank = True)

    def __str__(self):
        return self.user.username
