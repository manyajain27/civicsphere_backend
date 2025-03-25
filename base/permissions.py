from rest_framework import permissions

class IsWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        # Ensure user is authenticated and is a worker
        return request.user.is_authenticated and request.user.is_worker()
    

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        # Ensure user is authenticated and is a customer
        return request.user.is_authenticated and request.user.is_customer()