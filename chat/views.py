from django.contrib.auth.models import User
from rest_framework import generics,permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from .serializers import ThreadSerializer,MessageSerializer
from rest_framework.views import APIView
from .models import Thread,Message
from rest_framework import serializers

class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    permission_classes=[AllowAny]


    def post(self,request,*args,**kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()
        token,created=Token.objects.get_or_create(user=user)
        return Response({
            "user":serializer.data,
            "token":token.key       
        })
    
class LoginView(ObtainAuthToken):
    def post(self,request,*args,**kwargs):
        response=super().post(request,*args,**kwargs)
        token=Token.objects.get(key=response.data['token'])
        return Response({'token':token.key,'user_id':token.user_id,'username':token.user.username})
    


class ThreadView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def post(self,request,*args,**kwargs):
        user1=request.user
        user2_id=request.data.get("user2_id")
        try:
            user2=User.objects.get(id=user2_id)
        except User.DoesNotExist:
            return Response({"error":"User not found"},status=404)
        
        thread,created=Thread.objects.get_or_create(
            user1=min(user1,user2,key=lambda u:u.id),
            user2=max(user1,user2,key=lambda u:u.id)
        )
        return Response(ThreadSerializer(thread).data)
    
class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class=MessageSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        thread_id=self.kwargs['thread_id']
        return Message.objects.filter(thread_id=thread_id).order_by("timestamp")
    
    def perform_create(self,serializer):
        thread_id=self.kwargs['thread_id']
        try:
           thread=Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            raise serializers.ValidationError({"error":"Thread not found"})
        serializer.save(sender=self.request.user,thread=thread)