#from django.shortcuts import render
from lib2to3.pgen2 import token
from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from .serializers import *
from todo.models import *

from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate;

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            user = User.objects.create_user(data['username'], password=data['password'])
            user.save()
            token = Token.objects.create(user=user)
            return JsonResponse({'token':str(token)} , status=201)
        except IntegrityError:
            return JsonResponse({'error':'That username has already been taken. Please choose a new username'} , status=400)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        user = authenticate(request, username=data['username'], password=data['password'])
        if user is None:
            return JsonResponse({'error':'Could not login. Please check username and password and try again.'} , status=400)
        else:    
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token.objects.create(user=user)    
            return JsonResponse({'token':str(token)} , status=200)


class TodoCompletedList(generics.ListAPIView):
     serializer_class = TodoSerializer
     permission_classes = [permissions.IsAuthenticated]

     def get_queryset(self):
          user = self.request.user
          return Todo.objects.filter(user=user, datecompleted__isnull=False).order_by('-datecompleted')


class TodoListCreate(generics.ListCreateAPIView):
     serializer_class = TodoSerializer
     permission_classes = [permissions.IsAuthenticated]

     def get_queryset(self):
          user = self.request.user
          return Todo.objects.filter(user=user, datecompleted__isnull=True)

     def perform_create(self, serializer):
          serializer.save(user=self.request.user)

class TodoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
     serializer_class = TodoSerializer
     permission_classes = [permissions.IsAuthenticated]

     def get_queryset(self):
          user = self.request.user
          return Todo.objects.filter(user=user)

class TodoComplete(generics.UpdateAPIView):
     serializer_class = TodoCompleteSerializer
     permission_classes = [permissions.IsAuthenticated]

     def get_queryset(self):
          user = self.request.user
          return Todo.objects.filter(user=user)

     def perform_update(self, serializer):
          serializer.instance.datecompleted = timezone.now()
          serializer.save()

