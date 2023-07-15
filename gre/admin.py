from django.contrib import admin
from .models import Word, Category, Quiz
# Register your models here.

admin.site.register(Word)
admin.site.register(Category)
admin.site.register(Quiz)