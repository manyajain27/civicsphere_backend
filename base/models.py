from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.

class User(AbstractUser):
    location = models.CharField(max_length=255)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions_set", blank=True)

class Customer(User):
    customer_id = models.AutoField(primary_key=True)

class Worker(User):
    worker_id = models.AutoField(primary_key=True)
    skills = models.TextField()
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, choices=[('available', 'Available'), ('busy', 'Busy')])

class Job(models.Model):
    job_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('open', 'Open'), ('assigned', 'Assigned'), ('completed', 'Completed')])
    image = models.ImageField(upload_to='job_images/', blank=True, null=True)

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
