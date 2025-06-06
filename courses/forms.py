from django import forms
from django.contrib.auth.models import User
from .models import Student, Course, Lesson
from django.contrib.auth.forms import UserCreationForm

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'duration', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'content']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class CourseEnrollmentForm(forms.Form):
    #student_name = forms.CharField(
    #    label="Full Name", 
    #    max_length=100, 
    #    widget=forms.TextInput(attrs={'class': 'form-control'})
    #)
    #student_email = forms.EmailField(
    #    label="Student Email", 
    #    widget=forms.EmailInput(attrs={'class': 'form-control'})
    #)
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), 
        label="Select Course", 
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")