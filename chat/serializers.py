from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Thread,Message
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email','password']
        extra_kwargs={'password':{'write_only':True}}

    def create(self,validated_data):
        user=User(
            username=validated_data['username'],
            email=validated_data.get('email','')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class ThreadSerializer(serializers.ModelSerializer):
    user1=UserSerializer(read_only=True)
    user2=UserSerializer(read_only=True)

    class Meta:
        model=Thread
        fields=['id','user1','user2','created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender=UserSerializer(read_only=True)

    class Meta:
        model=Message
        fields=['id','thraed','sender','message','timestamp']