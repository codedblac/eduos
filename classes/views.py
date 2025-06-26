from django.shortcuts import render

# Create your views here.
# classes/views.py
from rest_framework import generics, permissions
from .models import ClassLevel, Stream
from .serializers import ClassLevelSerializer, StreamSerializer
from .permissions import IsSuperAdmin, CanManageClasses

# ClassLevel Views

class ClassLevelListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassLevelSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageClasses]

    def get_queryset(self):
        # Filter by user's institution
        if self.request.user.role == 'superadmin':
            return ClassLevel.objects.all()
        return ClassLevel.objects.filter(institution=self.request.user.institution)

    def perform_create(self, serializer):
        # Automatically assign institution if user is admin/schooladmin
        if self.request.user.role != 'superadmin':
            serializer.save(institution=self.request.user.institution)
        else:
            serializer.save()


class ClassLevelRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassLevelSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageClasses]
    queryset = ClassLevel.objects.all()
    lookup_field = 'pk'


# Stream Views

class StreamListCreateView(generics.ListCreateAPIView):
    serializer_class = StreamSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageClasses]

    def get_queryset(self):
        # Filter streams by user's institution via class_level
        if self.request.user.role == 'superadmin':
            return Stream.objects.all()
        return Stream.objects.filter(class_level__institution=self.request.user.institution)

    def perform_create(self, serializer):
        # Prevent users from creating streams outside their institution
        class_level = serializer.validated_data['class_level']
        if self.request.user.role != 'superadmin':
            if class_level.institution != self.request.user.institution:
                raise PermissionError("You cannot create streams for other institutions.")
        serializer.save()


class StreamRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StreamSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageClasses]
    queryset = Stream.objects.all()
    lookup_field = 'pk'
