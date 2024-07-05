from django import forms
from .models import UserProfile, MealRecord

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['age', 'height', 'weight', 'gender', 'activity_level', 'goal']

class MealRecordForm(forms.ModelForm):
    class Meta:
        model = MealRecord
        fields = ['meal_type', 'food_items']
