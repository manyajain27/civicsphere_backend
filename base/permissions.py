from rest_framework import permissions

class IsWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        # Ensure user is authenticated and is a worker
        return request.user.is_authenticated and request.user.is_worker()
    

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        # Ensure user is authenticated and is a customer
        return request.user.is_authenticated and request.user.is_customer()
    
class IsJobOwner(permissions.BasePermission):
    """
    Permission to allow only the job creator (customer) to update it.
    """

    def has_object_permission(self, request, view, obj):
        # Ensure the user is authenticated and is the owner of the job
        return obj.customer.user == request.user