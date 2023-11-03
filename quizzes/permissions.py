from rest_framework import permissions


class IsCompanyOwnerOrAdministrator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the company or an administrator
        company = obj.company
        user = request.user
        return company.owner == user or user in company.administrators.all()
