import boto3
import os
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import create_key_pair

STATE_CHOICES = [
    ('Available', 'Available'),
    ('Pending', 'Pending'),
    ('Running', 'Running'),
    ('Stopping', 'Stopping'),
    ('Stopped', 'Stopped'),
    ('Shutting-down', 'Shutting-down'),
    ('Terminated', 'Terminated')
]

class User(AbstractUser):
    username = models.CharField(max_length= 255, null= True, blank= True, unique= True)
    email = models.EmailField(null= False, blank= False, unique= True)    

    def __str__(self):
        return self.email + str(self.id)
    
class Instance(models.Model):
    instance_id         = models.CharField(max_length= 255)
    image_id            = models.CharField(max_length= 255)
    public_ip           = models.CharField(max_length= 255)
    private_ip          = models.CharField(max_length= 255)
    security_group_id   = models.CharField(max_length= 255)
    key_pair_id         = models.CharField(max_length= 255)

    def __str__(self):
        return f"Instance {self.instance_id}"

class Application(models.Model):
    name                = models.CharField(max_length= 255)
    price               = models.DecimalField(max_digits= 8, decimal_places= 2)
    description         = models.TextField(blank= True, null= True)
    thumbnail           = models.ImageField(upload_to="uploads/", blank = True, null=True)
    ami                 = models.TextField(max_length= 255, blank= False, null= False)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user                = models.OneToOneField(User, on_delete=models.CASCADE)
    paid_amount         = models.DecimalField(max_digits=8, decimal_places= 2)

    def __str__(self):
        return f"Profile for {self.user.email}"

class Service(models.Model):
    application         = models.ForeignKey(Application, null= True,on_delete= models.SET_NULL)
    instance            = models.OneToOneField(Instance, null= True, on_delete= models.SET_NULL)
    profile             = models.ForeignKey(Profile, on_delete= models.CASCADE)
    start_time          = models.DateTimeField(auto_now_add= True)
    finish_time         = models.DateTimeField(null= True, blank= True)
    price_unit_per_hour = models.DecimalField(max_digits= 8, decimal_places= 2, blank= True, null= True)
    application_name    = models.CharField(max_length= 255, blank= True, null=True)
    state               = models.CharField(max_length= 255, choices= STATE_CHOICES)

    def save(self, *args, **kwargs):
        if(not(self.price_unit_per_hour)):
            self.price_unit_per_hour = self.application.price
        if(not((self.application_name))):
            self.application_name = self.application.name
        super(Service, self).save(*args, **kwargs)

    def __str__(self):
        if(not(self.finish_time)):
            return f"application {self.application.name} is in use by {self.profile.user.email}."
        return f"application {self.application.name} is terminated by {self.profile.user.email}."

    

@receiver(post_save, sender= settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, **kwargs):
    if(kwargs['created']):
        user = kwargs['instance']
        Profile.objects.create(user= user, paid_amount= 0)
        create_key_pair(region_name="us-east-1",key_name= str(user.email)+ str(user.id))
        s3_resource = boto3.resource('s3')
        bucket_name = 'platformy-keys-encrypted-bucket'
        file_path = os.path.join(os.path.dirname(__file__), '../keys/'+str(user.email)+str(user.id)+'.pem')
        key = str(user.email) +str(user.id) +'/' +str(user.email)+str(user.id)+ '.pem'
        s3_resource.Object(bucket_name, key).upload_file(file_path, ExtraArgs={'ContentType': '*/*'})