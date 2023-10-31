from django.contrib import admin

from .models import Company


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    list_filter = ('owner',)
    search_fields = ('name', 'description')

admin.site.register(Company, CompanyAdmin)