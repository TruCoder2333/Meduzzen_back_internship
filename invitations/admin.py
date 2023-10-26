from django.contrib import admin
from .models import CompanyInvitation

class CompanyInvitationAdmin(admin.ModelAdmin):
    list_display = ('company', 'invited_user', 'status')
    list_filter = ('company',)
    search_fields = ('company', 'invited_user')

admin.site.register(CompanyInvitation, CompanyInvitationAdmin)