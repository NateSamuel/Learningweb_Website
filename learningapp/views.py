from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *

import logging
import requests

logger = logging.getLogger(__name__)
from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    """Renders the homepage of the application."""
    return render(request, 'learningapp/index.html')

@login_required
def user_logout(request):
    """Logs out the user and redirects to the app's home page."""
    logout(request)
    logger.warning("User has logged out")
    logger.debug("User has logged out")
    logger.info("User has logged out")
    logger.error("User has logged out")
    logger.critical("User has logged out")
    return HttpResponseRedirect('../app/')

from django.shortcuts import render, get_object_or_404, redirect
from .models import UserProfile, Course, Status
from .forms import StatusForm
from rest_framework.decorators import api_view
from rest_framework.response import Response

@login_required
def profile(request, username=None):
    """Displays the user's profile, including their statuses, courses, and role-based options."""
    if username:
        user = get_object_or_404(User, username=username)
        user_profile = get_object_or_404(UserProfile, user=user)
        is_own_profile = user == request.user
    else:
        user = request.user
        user_profile = user.userprofile
        is_own_profile = True

    statuses = Status.objects.filter(user=user).order_by('-created_at')
    courses = user_profile.courses_enrolled.all()
    not_enrolled_courses = Course.objects.exclude(id__in=courses.values('id'))
    teacher_courses = None
    if user_profile.role == "Teacher":
        teacher_courses = Course.objects.filter(teacher=user)

    form = StatusForm(request.POST or None)
    if is_own_profile and request.method == 'POST':
        if form.is_valid():
            status = form.save(commit=False)
            status.user = user
            status.save()
            return redirect('profile', username=user.username)

    return render(request, 'learningapp/profile.html', {
        'user_profile': user_profile,
        'statuses': statuses,
        'form': form,
        'is_own_profile': is_own_profile,
        'courses': courses,
        'not_enrolled_courses': not_enrolled_courses,
        'teacher_courses': teacher_courses,
    })

@login_required
def user_list(request):
    """Displays a list of all users except the currently logged-in user."""
    users = User.objects.all().exclude(username=request.user.username)
    return render(request, 'learningapp/user_list.html', {'users': users})

def user_login(request):
    """Handles user login and redirects to the profile page if successful."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/profile/')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            logger.warning('Invalid login: ' + username)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'learningapp/login.html')

def register(request):
    """Handles user registration and creates both user and user profile."""
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.role = profile_form.cleaned_data['role']
            profile.save()

            registered = True
            return redirect('account_created')
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'learningapp/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def account_created(request):
    """Displays a page confirming that the user's account was created."""
    return render(request, 'learningapp/accountCreated.html')

def course_detail_view(request, course_id):
    """Fetches and displays the details of a specific course using an external API."""
    api_url = f"http://127.0.0.1:8000/api/courses/details/{course_id}/"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        course_data = response.json()
    else:
        course_data = None

    return render(request, 'learningapp/course_detail.html', {'course': course_data})

@login_required
def enrolled_students_view(request, course_id):
    """Displays the list of students enrolled in a specific course."""
    api_url = f"http://127.0.0.1:8000/api/courses/{course_id}/students/"
    response = requests.get(api_url, cookies=request.COOKIES)
    
    if response.status_code == 200:
        students_data = response.json().get('students', [])
    else:
        students_data = []

    return render(request, 'learningapp/enrolled_students.html', {'students': students_data, 'course_id': course_id})

@login_required
def remove_student_from_course(request, course_id, student_id):
    """Removes a student from a course, only accessible by teachers."""
    if request.user.userprofile.role != 'Teacher':
        return redirect('course_detail', course_id=course_id)

    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(UserProfile, id=student_id)

    course_student = CourseStudents.objects.filter(course=course, student=student).first()

    if course_student:
        course_student.delete()

    return redirect('course_detail', course_id=course.id)

@login_required
def create_course_page(request):
    """Allows teachers to create a new course."""
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'Teacher':
            return redirect('/profile/')
    except UserProfile.DoesNotExist:
        return redirect('/profile/')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm()

    return render(request, 'learningapp/create_course.html', {'form': form})

@login_required
def edit_course_page(request, course_id):
    """Allows a teacher to edit an existing course's details."""
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == 'POST':
        course_form = CourseEditForm(request.POST, request.FILES, instance=course)

        if course_form.is_valid():
            course_form.save()
            return redirect('profile', username=request.user.username)
    else:
        course_form = CourseEditForm(instance=course)

    return render(request, 'learningapp/edit_course.html', {
        'course_form': course_form,
        'course': course
    })

@login_required
def add_week_page(request, course_id):
    """Allows a teacher to add a new week to a specific course."""
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    if request.method == 'POST':
        form = CourseWeekForm(request.POST)
        if form.is_valid():
            week = form.save(commit=False)
            week.course = course
            week.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseWeekForm()

    return render(request, 'learningapp/add_week.html', {'form': form, 'course': course})

@login_required
def add_week_content(request, course_id, week_id):
    """Allows a teacher to add content to a specific week of a course."""
    course = get_object_or_404(Course, id=course_id)
    week = get_object_or_404(CourseWeek, id=week_id, course=course)

    if request.method == 'POST':
        form = CourseWeekContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.course_week = week
            content.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseWeekContentForm()

    return render(request, 'learningapp/add_week_content.html', {
        'course': course,
        'week': week,
        'form': form
    })
