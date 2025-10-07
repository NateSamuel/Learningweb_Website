from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from django.shortcuts import get_object_or_404, redirect

from .models import Course, CourseStudents, UserProfile, CourseWeek, CourseWeekContent, Feedback
from .serializers import CourseSerializer, CourseStudentsSerializer, UserProfileSerializer, CourseWeekSerializer, CourseWeekContentSerializer, FeedbackSerializer,CourseCreateSerializer, CourseEditSerializer, EnrolledStudentSerializer
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
from rest_framework import status

@api_view(['GET'])
def user_courses_api(request, username=None):
    """Fetches the courses a user is enrolled in based on their username or the logged-in user."""
    if username:
        user = get_object_or_404(UserProfile, user__username=username)
    else:
        user = request.user.userprofile

    enrolled_courses = CourseStudents.objects.filter(student=user).select_related('course')
    serializer = CourseStudentsSerializer(enrolled_courses, many=True)
    
    return Response(serializer.data)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_enrolled_students_api(request, course_id):
    """Fetches the list of students enrolled in a course, ensuring the user is authenticated and a teacher."""
    if not request.user.is_authenticated or request.user.userprofile.role != UserProfile.TEACHER:
        return Response({"detail": "You do not have permission to view enrolled students."}, status=403)

    course = get_object_or_404(Course, id=course_id)
    enrolled_students = UserProfile.objects.filter(courses_enrolled__id=course.id)
    student_serializer = EnrolledStudentSerializer(enrolled_students, many=True)

    return Response({"students": student_serializer.data})

@api_view(['GET'])
def user_course_details_api(request, course_id):
    """Fetches the details of a course, including its weeks and feedback."""
    course = get_object_or_404(Course, id=course_id)

    course_weeks = CourseWeek.objects.filter(course=course).prefetch_related('content')
    feedback = Feedback.objects.filter(course=course)

    course_serializer = CourseSerializer(course)
    course_week_serializer = CourseWeekSerializer(course_weeks, many=True)
    feedback_serializer = FeedbackSerializer(feedback, many=True)

    response_data = course_serializer.data
    response_data['weeks'] = course_week_serializer.data
    response_data['feedback'] = feedback_serializer.data

    return Response(response_data)

@api_view(['GET'])
def courses_not_enrolled_api(request, username=None):
    """Fetches the courses that a user is not enrolled in, based on their username or the logged-in user."""
    if username:
        user = get_object_or_404(UserProfile, user__username=username)
    else:
        user = request.user.userprofile
    
    enrolled_courses = user.courses_enrolled.all()
    all_courses = Course.objects.exclude(id__in=[course.id for course in enrolled_courses])

    serializer = CourseSerializer(all_courses, many=True)
    
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enroll_student_api(request, course_id):
    """Enrolls the logged-in student into a course, ensuring the student is not already enrolled."""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    course = get_object_or_404(Course, id=course_id)

    if CourseStudents.objects.filter(course=course, student=user_profile).exists():
        return Response({"error": "You are already enrolled in this course."}, status=status.HTTP_400_BAD_REQUEST)

    CourseStudents.objects.create(course=course, student=user_profile)

    course_url = reverse('course_detail', args=[course.id])
    return redirect(course_url)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback_api(request, course_id):
    """Submits feedback for a course by the authenticated student."""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_authenticated:
        student_profile = request.user.userprofile

        data = request.data.copy()
        data['course'] = course.id
        data['student'] = student_profile.id

        serializer = FeedbackSerializer(data=data)
        if serializer.is_valid():
            feedback = serializer.save(student=student_profile)
            return redirect('course_detail', course_id=course.id)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    """Creates a new course by the authenticated teacher."""
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'Teacher':
            return Response({"detail": "You must be a teacher to create a course."}, status=status.HTTP_403_FORBIDDEN)
    except UserProfile.DoesNotExist:
        return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CourseCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(teacher=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_courses_api(request):
    """Fetches the list of courses taught by the authenticated teacher."""
    try:
        user_profile = request.user.userprofile
        if user_profile.role != 'Teacher':
            return Response({"detail": "You are not authorized to view this."}, status=403)

        courses = Course.objects.filter(teacher=request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=200)

    except UserProfile.DoesNotExist:
        return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def edit_course_api(request, course_id):
    """Allows a teacher to update a course's details like name, description, deadline, and image."""
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    serializer = CourseEditSerializer(course, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_week_api(request, course_id):
    """Allows a teacher to add a new week to a course."""
    course = get_object_or_404(Course, id=course_id, teacher=request.user)

    week_number = request.data.get('week_number')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')

    if CourseWeek.objects.filter(course=course, week_number=week_number).exists():
        return Response({'error': 'A week with this number already exists in the course.'}, status=status.HTTP_400_BAD_REQUEST)

    week = CourseWeek.objects.create(course=course, week_number=week_number, start_date=start_date, end_date=end_date)

    return Response(CourseWeekSerializer(week).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_week_content_api(request, course_id, week_id):
    """Allows a teacher to add content (title and PDF) to a specific week in a course."""
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    week = get_object_or_404(CourseWeek, id=week_id, course=course)

    title = request.data.get('title')
    pdf = request.FILES.get('pdf')

    if not title or not pdf:
        return Response({"error": "Both title and PDF are required."}, status=400)

    content = CourseWeekContent.objects.create(
        course_week=week,
        title=title,
        pdf=pdf
    )

    content_serializer = CourseWeekContentSerializer(content)
    return Response(content_serializer.data, status=201)