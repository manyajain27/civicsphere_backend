from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['Name', 'email', 'location', 'profile_pic']
        
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        # Automatically create a Worker or Customer profile
        if user.role == 'worker':
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

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

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