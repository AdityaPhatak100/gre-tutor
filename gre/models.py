from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    category_name = models.CharField(
        verbose_name="category name", max_length=50, null=False, unique=False)
    learner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    
    def __str__(self) -> str:
        return self.category_name


class Word(models.Model):
    word_name = models.CharField(
        verbose_name="word name", max_length=50, null=False, unique=True, blank=False)
    meaning = models.CharField(
        verbose_name="word meaning", max_length=300, null=False, unique=True, blank=False)
    example = models.CharField(verbose_name="word example", max_length=300, null=True, blank=False)
    learner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.word_name

class Quiz(models.Model):
    data = models.JSONField()
    score = models.IntegerField()
    no_of_ques = models.IntegerField()
