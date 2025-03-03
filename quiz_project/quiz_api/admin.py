# quiz_api/admin.py
from django.contrib import admin
from .models import Category, Question, Choice

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('text', 'category')
    list_filter = ('category',)
    search_fields = ('text',)

admin.site.register(Category)
admin.site.register(Question, QuestionAdmin)
