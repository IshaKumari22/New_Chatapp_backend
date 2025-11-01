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
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .serializers import RegisterSerializer


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
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,       # ✅ this is the token frontend needs
            'username': user.username # optional, useful to store username
        })
class ThreadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user2_id = request.data.get("user2")
        if not user2_id:
            return Response({"error": "user2 id required"}, status=status.HTTP_400_BAD_REQUEST)

        user1 = request.user
        user2 = User.objects.get(id=user2_id)

        # check if thread exists
        thread = Thread.objects.filter(users=user1).filter(users=user2).first()
        if not thread:
            thread = Thread.objects.create()
            thread.users.add(user1, user2)
            thread.save()

        return Response({"thread_id": thread.id})
# class ThreadListCreateView(generics.ListCreateAPIView):
#     serializer_class = ThreadSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         # Fetch threads where logged-in user is either user1 or user2
#         user = self.request.user
#         return Thread.objects.filter(user1=user) | Thread.objects.filter(user2=user)

#     def perform_create(self, serializer):
#         user1 = self.request.user
#         user2_id = self.request.data.get('user2')
#         user2 = User.objects.get(id=user2_id)
        
#         # Check if thread already exists
#         thread = Thread.objects.filter(user1=user1, user2=user2).first() or \
#                  Thread.objects.filter(user1=user2, user2=user1).first()
#         if thread:
#             serializer.instance = thread  # return existing thread
#         else:
#             serializer.save(user1=user1, user2=user2)
class ThreadListCreateView(generics.ListCreateAPIView):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(users=self.request.user)

    def perform_create(self, serializer):
        user1 = self.request.user
        user2_id = self.request.data.get('user2')
        user2 = User.objects.get(id=user2_id)

        thread = Thread.objects.filter(users=user1).filter(users=user2).first()
        if thread:
            serializer.instance = thread
        else:
            thread = serializer.save()
            thread.users.add(user1, user2)
            thread.save()

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        return Message.objects.filter(thread_id=thread_id).order_by("timestamp")

    def perform_create(self, serializer):
        thread_id = self.kwargs['thread_id']
        try:
            thread = Thread.objects.get(id=thread_id)
        except Thread.DoesNotExist:
            raise serializers.ValidationError({"error": "Thread not found"})

        sender = self.request.user
        print("Sender:", sender)  # ✅ Debug

        # ✅ Determine the receiver
        if thread.user1 == sender:
            receiver = thread.user2
        elif thread.user2 == sender:
            receiver = thread.user1
        else:
            raise serializers.ValidationError({"error": "Sender not part of this thread"})

        print("Receiver:", receiver)  # ✅ Debug

        serializer.save(sender=sender, receiver=receiver, thread=thread)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def user_list(request):
    # Exclude the currently logged-in user
    current_user=request.user
    users = User.objects.exclude(id=current_user.id)
    serializer=UserSerializer(users,many=True)
    return Response(serializer.data)
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def start_thread(request,user_id):
    current_user=request.user
    try:
        other_user=User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error":"User not found ."},status=status.HTTP_404_NOT_FOUND)
    thread=Thread.objects.filter(
        user1=current_user,user2=other_user
    ).first() or Thread.objects.filter(
        user1=other_user,user2=current_user
    ).first()

    if not thread:
        thread=Thread.objects.create(user1=current_user,user2=other_user)
    
    serializer=ThreadSerializer(thread)
    return Response(serializer.data)