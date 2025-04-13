from django.contrib import admin

from .models import *
admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Worker)
admin.site.register(Job)
admin.site.register(Review)
admin.site.register(Transaction)
admin.site.register(Offer)