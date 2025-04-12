from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name', required=True)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'password','confirm_password', 'role']  # Explicitly defining fields
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        name = validated_data['first_name']
        email = validated_data['email']
        password = validated_data['password']
        role = validated_data.get('role', 'customer')  # default to customer

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=name,
            role=role,
        )

        if role == 'worker':
            Worker.objects.create(user=user)
        else:
            Customer.objects.create(user=user)

        return user


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        extra_kwargs = {
            'customer': {'required': False}
        }

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

# token serializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Get the default token
        token = super().get_token(user)
        
        # Add more detailed claims
        token['email'] = user.email
        token['user_type'] = user.__class__.__name__  # 'Customer', 'Worker', or 'User'
        
        # Optional: Add more user-specific information
        if hasattr(user, 'customer_id'):
            token['customer_id'] = user.customer_id
        elif hasattr(user, 'worker_id'):
            token['worker_id'] = user.worker_id
        
        return token

from rest_framework.response import Response
from rest_framework import status

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        # Try getting the user first to avoid the DoesNotExist error
        email = request.data.get('username')  # JWT uses 'username' for email
        
        # Check if user exists before attempting authentication
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "No active account found with the given credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # If user exists, proceed with token generation
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Add user info to response
                user_data = UserSerializer(user).data
                
                response.data['user'] = user_data
                response.data['user_role'] = user.role
                
                # Add profile info if needed
                if user.role == 'customer':
                    try:
                        customer_profile = user.customer_profile
                        response.data['profile'] = CustomerSerializer(customer_profile).data
                    except Customer.DoesNotExist:
                        pass
                elif user.role == 'worker':
                    try:
                        worker_profile = user.worker_profile
                        response.data['profile'] = WorkerSerializer(worker_profile).data
                    except Worker.DoesNotExist:
                        pass
                    
            return response
            
        except Exception as e:
            return Response(
                {"detail": "Invalid credentials or error during authentication"},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Get user info
            email = request.data.get('username')  # JWT is using 'username' for the email field
            user = User.objects.get(email=email)
            
            # Serialize user info
            user_data = UserSerializer(user).data
            
            # Add user info to response
            response.data['user'] = user_data
            response.data['user_role'] = user.role
            
            # Add profile info if needed
            if user.role == 'customer':
                try:
                    customer_profile = user.customer_profile
                    response.data['profile'] = CustomerSerializer(customer_profile).data
                except Customer.DoesNotExist:
                    pass
            elif user.role == 'worker':
                try:
                    worker_profile = user.worker_profile
                    response.data['profile'] = WorkerSerializer(worker_profile).data
                except Worker.DoesNotExist:
                    pass
                
        return response

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        # Get the default validation result
        data = super().validate(attrs)
        
        # Decode the refresh token to access its claims
        refresh = RefreshToken(attrs['refresh'])
        
        # Preserve additional claims in the new access token
        preserved_claims = ['email', 'user_type', 'customer_id', 'worker_id']
        for claim in preserved_claims:
            if claim in refresh:
                data[claim] = refresh[claim]
        
        return data

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer