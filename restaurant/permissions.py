from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Delivery crew').exists()

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return not request.user.groups.exists()

class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated and (
                request.user.is_staff or
                request.user.groups.filter(name='Manager').exists()
            )
        )
