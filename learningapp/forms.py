from django import forms
from django.forms import ModelForm
from .models import *

from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.RadioSelect,  # Ensure role is displayed as radio buttons
        required=True
    )

    class Meta:
        model = UserProfile
        fields = ('role',)

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['text']

class CourseWeekContentForm(forms.ModelForm):
    class Meta:
        model = CourseWeekContent
        fields = ['title', 'pdf']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'deadline']

class CourseWeekForm(forms.ModelForm):
    class Meta:
        model = CourseWeek
        fields = ['week_number', 'start_date', 'end_date']

class CourseEditForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'deadline', 'image']
