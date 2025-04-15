from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Course, Lesson, Student
from .forms import CourseForm, LessonForm, CourseEnrollmentForm, UserUpdateForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseSerializer

def about(request):
    return render(request, 'courses/about.html')

# Course List
# @login_required
# def course_list(request):
#     courses = Course.objects.all()
#     return render(request, 'courses/course_list.html', {'courses': courses})

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'



# Course Detail
# def course_detail(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     lessons = course.lessons.all()
#      # Initialize student and progress
#     student = None
#     progress = None

#     # Check if the user is a student
#     try:
#         student = Student.objects.get(user=request.user)
#         completed_lessons = student.completed_lessons.filter(course=course).count()
#         total_lessons = lessons.count()

#         if total_lessons > 0:
#             progress = (completed_lessons / total_lessons) * 100
#         else:
#             progress = 0
#     except Student.DoesNotExist:
#         pass

#     return render(request, 'courses/course_detail.html', {
#         'course': course,
#         'lessons': lessons,
#         'student': student,
#         'progress': progress
#     })

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        lessons = course.lessons.all()

        context['lessons'] = lessons
        context['student'] = None
        context['progress'] = None

        # Check if user is a student
        try:
            student = Student.objects.get(user=self.request.user)
            completed_lessons = student.completed_lessons.filter(course=course).count()
            total_lessons = lessons.count()

            context['student'] = student
            context['progress'] = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        except Student.DoesNotExist:
            pass

        return context

# Create Course
# def course_create(request):
#     if request.method == "POST":
#         form = CourseForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Course created successfully!")
#             return redirect('course_list')
#     else:
#         form = CourseForm()
#     return render(request, 'courses/course_form.html', {'form': form})

# Update Course
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form})

# Delete Course
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

# Create Lesson
def lesson_create(request):
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson created successfully!")
            return redirect('course_list')
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form})

# Update Lesson
def lesson_update(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect('course_list')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form})

# Delete Lesson
def lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})

@login_required
def enroll_student(request):
    if request.method == 'POST':
        form = CourseEnrollmentForm(request.POST)
        if form.is_valid():
            #student_name = form.cleaned_data['student_name']
            #student_email = form.cleaned_data['student_email']
            course = form.cleaned_data['course']

            # Check if student already exists
            #email=student_email, defaults={'name': student_name}
            student, created = Student.objects.get_or_create(user = request.user)

            # Check if the student is already enrolled in the course
            if course in student.enrolled_courses.all():
                return render(request, 'courses/enrollment_failed.html', {
                    'student': student,
                    'course': course,
                    'error': 'You are already enrolled in this course.'
                })

            # Enroll the student
            #student.name = student_name  # Update name if it was blank
            #student.save()
            student.enrolled_courses.add(course)

            return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
    else:
        form = CourseEnrollmentForm()

    return render(request, 'courses/enroll_student.html', {'form': form})


def enrolled_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.students.all()  # Fetch all students in this course
    return render(request, 'courses/enrolled_students.html', {'course': course, 'students': students})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'courses/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('/')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'courses/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('/login/')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'courses/profile.html', {'form': form})

class CourseCreateView(CreateView):
    model = Course
    fields = ['title', 'description', 'duration', 'thumbnail']
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')
    
class CourseListAPI(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)

class CourseDetailAPI(APIView):
    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
class EnrollStudentAPI(APIView):
    def post(self, request):
        # student_email = request.data.get('email')
        course_id = request.data.get('course_id')
        
        if not course_id:
            return Response({'error': 'course_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        student, created = Student.objects.get_or_create(user=request.user)
        
        if course in student.enrolled_courses.all():
            return Response({'error': 'You are already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST)
        
        student.enrolled_courses.add(course)

        return Response({'message': f'{student.email} has been enrolled in {course.title}'})