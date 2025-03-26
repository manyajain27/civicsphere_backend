from django.shortcuts import render
from rest_framework import viewsets
from .permissions import *
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        # Use the default create method from the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens for the newly created user
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=201)

class LoginView(generics.GenericAPIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=email, password=password)
        
        if user:
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })
        
        return Response({'error': 'Invalid credentials'}, status=400)

# Job Posting
class JobCreateView(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def perform_create(self, serializer):
        # Get the customer profile for the authenticated user
        customer = Customer.objects.get(user=self.request.user)
        # Save the job with the customer
        serializer.save(customer=customer)

# Fetch Jobs
# class JobListView(generics.ListAPIView):
#     serializer_class = JobSerializer
#     permission_classes = [permissions.AllowAny]

#     def get_queryset(self):
#         queryset = Job.objects.all()
#         category = self.request.query_params.get('category', None)
        
#         if category:
#             queryset = queryset.filter(category__iexact=category)  # Case-insensitive match
        
#         return queryset
# Get list of all jobs with categorical search
class JobListView(generics.ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def get_queryset(self):
        queryset = super().get_queryset()
        categories = self.request.query_params.getlist('category')  # Get multiple categories
        
        if categories:
            queryset = queryset.filter(category__in=categories)  # Filter by multiple categories
            
        return queryset

# Update Job
class JobUpdateView(generics.UpdateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]

#Delete Job
class JobDeleteView(generics.DestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]

# Workers List
class WorkerListView(generics.ListAPIView):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

# Submit Ratings
class CustomerReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsWorker]
    
class WorkerReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

#User can see their own profile
class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        user_data = UserSerializer(user).data  # Serialize user data

        # Check if the user is a customer or a worker and fetch additional details
        if user.role == 'customer':
            customer_profile = getattr(user, 'customer_profile', None)
            user_data['profile'] = CustomerSerializer(customer_profile).data if customer_profile else None
        elif user.role == 'worker':
            worker_profile = getattr(user, 'worker_profile', None)
            user_data['profile'] = WorkerSerializer(worker_profile).data if worker_profile else None
        
        return Response(user_data)


# Secure Messaging
# class ChatCreateView(generics.CreateAPIView):
#     queryset = Chat.objects.all()
#     serializer_class = ChatSerializer
#     permission_classes = [permissions.IsAuthenticated]

