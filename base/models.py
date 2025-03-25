from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('worker', 'Worker'),
    )
       
    location = models.CharField(max_length=255)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions_set", blank=True)
    
    def is_worker(self):
        return self.role == "worker"

    def is_customer(self):
        return self.role == "customer"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile")

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="worker_profile")
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
