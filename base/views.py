from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.views import APIView
from .permissions import *
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import *
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=201)


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response(description="Login successful"),
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
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user_type': user.role,
                'user': UserSerializer(user).data,
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


class CustomerJobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        user = self.request.user
        return Job.objects.filter(customer=user.customer_profile)


# Get list of all jobs with categorical search
# all jobs visible to all users
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


# worker proposes an offer and customer can see offers
class JobOfferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Only workers can post offers
        if not hasattr(request.user, 'worker_profile'):
            return Response({'detail': 'Only workers can make offers.'}, status=403)

        job = get_object_or_404(Job, pk=pk)
        worker = request.user.worker_profile

        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(job=job, worker=worker)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request, pk):
        # Only the customer who owns the job can view offers
        job = get_object_or_404(Job, pk=pk)
        if job.customer.user != request.user:
            return Response({'detail': 'Not authorized to view offers.'}, status=403)

        offers = job.offers.all()
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data)



#Accepting job offer by customer
class AcceptJobView(generics.UpdateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def update(self, request, *args, **kwargs):
        job = self.get_object()

        # Check if the job is open
        if job.status != 'open':
            return Response({'detail': 'Job is not available for acceptance.'}, status=status.HTTP_400_BAD_REQUEST)

        worker_id = request.data.get('worker_id')  # Accept from frontend
        try:
            worker = Worker.objects.get(id=worker_id)
        except Worker.DoesNotExist:
            return Response({'detail': 'Worker not found.'}, status=status.HTTP_404_NOT_FOUND)

        job.status = 'assigned'
        job.worker = worker
        job.save()

        serializer = self.get_serializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)


#Worker checking all accepted/completed jobs
class WorkerAssignedJobsView(generics.ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsWorker]

    def get_queryset(self):
        worker = self.request.user.worker_profile

        status_filter = self.request.query_params.get('status', None)
        queryset = Job.objects.filter(worker=worker)

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

