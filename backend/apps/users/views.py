from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from .serializers import UserSerializer


class SignupView(CreateAPIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer