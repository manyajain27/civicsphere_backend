from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_('You must provide a valid email address'))

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('User must have an email address'))
        
        email = self.normalize_email(email)
        self.email_validator(email)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('worker', 'Worker'),
    )
    
    username=None  
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions_set", blank=True)
        
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email

    def is_worker(self):
        return self.role == "worker"

    def is_customer(self):
        return self.role == "customer"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="worker_profile")
    skills = models.TextField()
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, choices=[('available', 'Available'), ('busy', 'Busy')])
    average_rating = models.FloatField(default=0.0)  # ✅ New field
    total_reviews = models.PositiveIntegerField(default=0)  # ✅ Optional helper
    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

class Job(models.Model):
    job_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='jobs')
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('open', 'Open'), ('assigned', 'Assigned'), ('completed', 'Completed')], default='open')
    image = models.ImageField(upload_to='job_images/', blank=True, null=True)
    time_preference = models.CharField(max_length=20, choices=[('Now', 'Now'), ('Later', 'Later')], default='Now')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
    
# models.py
class Offer(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='offers')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    proposed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer by {self.worker.user.first_name} for {self.job.title}"



class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_chats')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chats')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews_given')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='reviews_received')
    ratings = models.IntegerField()
    comments = models.TextField()
    image = models.ImageField(upload_to='review_images/', blank=True, null=True)

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions_made')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='transactions_received')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pay_mode = models.CharField(max_length=50, choices=[('card', 'Card'), ('cash', 'Cash'), ('online', 'Online')])
    time = models.DateTimeField(auto_now_add=True)

