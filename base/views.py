from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from .permissions import *
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class LoginView(generics.GenericAPIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response(description="Login successful", schema=UserSerializer),
            400: "Invalid credentials",
        },
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })

        return Response({'error': 'Invalid credentials'}, status=400)


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

#Accepting job by worker
class AcceptJobView(generics.UpdateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsWorker]

    def update(self, request, *args, **kwargs):
        job = self.get_object()
        
        # Check if the job is open
        if job.status != 'open':
            return Response({'detail': 'Job is not available for acceptance.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        worker = request.user.worker_profile
        # Ensure the authenticated user is a worker
        # try:
        #     worker = request.user.worker_profile
        # except Worker.DoesNotExist:
        #     return Response({'detail': 'Only workers can accept jobs.'},
        #                     status=status.HTTP_403_FORBIDDEN)

        # Update the job status and assign the worker
        job.status = 'assigned'
        job.assigned_worker = worker
        job.save()

        serializer = self.get_serializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Worker checking all accepted/completed jobs
class WorkerAssignedJobsView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsWorker]

    def get_queryset(self):
        
        worker = self.request.user.worker_profile
        # Ensure the user is a worker
        # try:
        #     worker = self.request.user.worker_profile
        # except Worker.DoesNotExist:
        #     return Job.objects.none()  # Return an empty queryset if not a worker
        
        # Get the status filter from query parameters (default to None)
        status_filter = self.request.query_params.get('status', None)
        
        # Filter jobs based on the assigned worker and optionally filter by status
        queryset = Job.objects.filter(assigned_worker=worker)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

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

