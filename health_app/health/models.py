from django.db import models

class UserProfile(models.Model):
    age = models.IntegerField()
    height = models.FloatField()
    weight = models.FloatField()
    gender = models.CharField(max_length=10, choices=[('男性', '男性'), ('女性', '女性')])
    activity_level = models.CharField(max_length=10, choices=[('軽度', '軽度'), ('中程度', '中程度'), ('高度', '高度')])
    goal = models.CharField(max_length=10, choices=[('減量', '減量'), ('維持', '維持'), ('増量', '増量')])

class MealRecord(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=10, choices=[('朝食', '朝食'), ('昼食', '昼食'), ('夕食', '夕食'), ('間食', '間食')])
    food_items = models.TextField()
    calories = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    date = models.DateField(auto_now_add=True)
