import datetime
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.expressions import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Application, Instance, Profile, Service
from .utils import create_instance, stop_instance, connect_instance

def home(request):
    try:
        if(request.user.is_anonymous or not(request.COOKIES.get('jwt', None))):
            return render(request, 'login.html')
    except:
        return render(request,'login.html')
    user = request.user
    services = Service.objects.select_related('profile').select_related('profile__user').filter(profile__user= user).filter(Q(state="Running")|Q(state="Pending"))
    list_used_applications = []
    for service in services:
        list_used_applications.append(service.application.id)
    used_applications = Application.objects.filter(id__in= list_used_applications)
    available_applications = Application.objects.filter(~Q(id__in= list_used_applications))
    context = {
        'used_applications': used_applications,
        'available_applications': available_applications,
        'email': user.email,
        'services': services
    }
    return render(request, 'home.html', context= context)

def signup(request):
    return render(request, 'signup.html')

def login(request):
    return render(request, 'login.html')

@api_view(["POST"])
def start_application(request):
    try:
        application_id = request.data.get("application_id",None)
        if(application_id):
            # Fetch start app endpoint
            service = Service.objects.select_related('profile').select_related('profile__user').filter(profile__user= request.user).filter(application__id= application_id).filter(Q(state="Running")|Q(state="Pending")|Q(finish_time__isnull= True))
            if(service.exists()):
                return Response({
                    "error": "You aleady have an instance running."
                }, status=status.HTTP_400_BAD_REQUEST)
            application = Application.objects.filter(id= application_id).first()
            profile = Profile.objects.filter(user= request.user).first()
            ami = application.ami
            key_name = str(profile.user.email) + str(profile.user.id)
            instance_object = create_instance(ImageId= ami, KeyName= key_name)
            # Todo: Adding real values instead of dummy ones.
            instance = Instance.objects.create(
                instance_id= instance_object["InstanceId"],
                image_id= application.ami,
                public_ip= "dummy for now",
                private_ip= "dummy for now",
                security_group_id= "dummy for now",
                key_pair_id= "dummy for now"
            )
            service = Service.objects.create(
                application= application,
                instance= instance,
                profile= profile,
                state= "Running"
            )
            return Response({
                "message": "Your instance id is : " + instance_object["InstanceId"]
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "You must specify the application id."
            }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
            "error": "Something went wrong!!!"
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def stop_application(request):
    try:
        application_id = request.data.get("application_id",None)
        if(application_id):
            print("xxxx")
            service = Service.objects.select_related('profile').select_related('profile__user').filter(profile__user= request.user).filter(application__id= application_id).filter(Q(state="Running")|Q(state="Pending")|Q(finish_time__isnull= True))
            print("yyyy")
            if(not(service.exists())):
                return Response({
                    "error": "You don't have an instance running."
                }, status=status.HTTP_400_BAD_REQUEST)
            # Fetch stop app endpoint
            instance_id = service.first().instance.instance_id
            print(" instance  id : ", instance_id)
            stop_instance(instance_id)
            service = service.first()
            service.finish_time = datetime.datetime.now()
            service.state = "Terminated"
            service.save()
            return Response({
                "message": "Your instance is terminated."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "You must specify the application id."
            }, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
            "error": "Something went wrong!!!"
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def connect_application(request):
    try:
        application_id = request.data.get("application_id",None)
        if(application_id):
            service = Service.objects.select_related('profile').select_related('profile__user').filter(profile__user= request.user).filter(application__id= application_id).filter(Q(state="Running")|Q(state="Pending")|Q(finish_time__isnull= True))
            if(not(service.exists())):
                return Response({
                    "error": "You don't have an instance running."
                }, status=status.HTTP_400_BAD_REQUEST)
            # Fetch stop app endpoint
            instance_id = service.first().instance.instance_id
            user_id = request.user.id
            user_email = request.user.email
            private_key_file = f"{user_email}{user_id}/{user_email}{user_id}.pem"
            output = connect_instance(instance_id,  region_name='us-east-1', private_key_file=private_key_file)
            plain_password = output['plain_password']
            rdp_file_path = output['rdp_file']
            if(os.path.exists(rdp_file_path)):
                with open(rdp_file_path,'rb') as reader:
                    response = HttpResponse(reader.read(), content_type="application/rdp;charset=UTF-8")
                    response['Content-Disposition'] = 'attachment; filename=Application.rdp'
                    response['password'] = plain_password
                    response['instance_id'] = instance_id
                    return response
    except:
        return Response({
            "error": "Something went wrong!!!"
        }, status=status.HTTP_400_BAD_REQUEST)