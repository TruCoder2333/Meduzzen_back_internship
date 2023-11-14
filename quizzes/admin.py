from django.contrib import admin

from .models import Quiz


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'created_at', 'updated_at')
    list_filter = ('company',)
    search_fields = ('title', 'description')

admin.site.register(Quiz, QuizAdmin)
