import json
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import UserProfile, Course, CourseStudents, Status
from datetime import datetime
import pytz
from django.urls import reverse
from django.test import Client
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile

class UserCoursesApiTests(APITestCase):
    
    def test_get_user_courses_empty(self):
        """Test that the endpoint returns an empty list if the user has no enrolled courses"""

        self.user_3 = User.objects.create_user(username='no_courses_user', password='testpassword')
        self.user_profile_3 = UserProfile.objects.create(user=self.user_3)

        url = '/api/courses/no_courses_user/'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json(), [])

    def test_get_user_courses_invalid_user(self):
        """Test that the endpoint returns a 404 if the user does not exist"""

        url = '/api/courses/non_existent_user/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class UserLoginTests(APITestCase):
    def setUp(self):
        """Create a user with valid credentials"""
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

        self.user_profile = UserProfile.objects.create(user=self.user)

    def test_user_login_success(self):
        """Use the client to simulate a POST request with valid credentials"""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })

        self.assertRedirects(response, '/profile/')
    
    def test_user_login_invalid_credentials(self):
        """Test invalid username or password"""
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })

        self.assertContains(response, "Invalid login details supplied.")

    def test_user_login_get(self):
        response = self.client.get(reverse('login'))
        """Ensure that the status code is 200 (OK) and the login form is present"""
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form', count=1)

    def test_user_login_success_authenticated(self):
        """Make a POST request to log in"""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })

        self.assertTrue(response.wsgi_request.user.is_authenticated)

class ProfileViewTests(TestCase):

    def setUp(self):

        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_profile = UserProfile.objects.create(user=self.user)
        
        self.client.login(username='testuser', password='testpassword')

    def test_view_own_profile(self):
        response = self.client.get(reverse('profile', kwargs={'username': 'testuser'}))
        
        """Ensure that the profile page loads correctly for the logged-in user"""
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learningapp/profile.html')
        self.assertContains(response, 'testuser')
        self.assertTrue(response.context['is_own_profile'])
    
    def test_view_other_user_profile(self):
        """Create another user to view"""
        other_user = User.objects.create_user(username='otheruser', password='testpassword')
        UserProfile.objects.create(user=other_user)

        response = self.client.get(reverse('profile', kwargs={'username': 'otheruser'}))
        

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'otheruser')
        self.assertFalse(response.context['is_own_profile'])
    
    def test_profile_with_statuses(self):
        """Check statuses"""
        Status.objects.create(user=self.user, text="This is my first status.")
        Status.objects.create(user=self.user, text="This is my second status.")

        response = self.client.get(reverse('profile', kwargs={'username': self.username}))
        
        self.assertEqual(len(response.context['statuses']), 2)
        self.assertContains(response, "This is my first status.")
        self.assertContains(response, "This is my second status.")

class RegisterViewTests(TestCase):

    def test_successful_registration(self):
        data = {
            'username': 'newuser',
            'password': 'testpassword',
            'email': 'newuser@example.com',
            'role': 'Student',  # Or whatever the options are
        }
        
        response = self.client.post(reverse('register'), data)
        
        self.assertRedirects(response, reverse('account_created'))
        

        user = User.objects.get(username='newuser')
        self.assertTrue(user.check_password('testpassword'))
        
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, 'Student')

class RegisterViewTests(TestCase):

    def test_successful_registration(self):
        data = {
            'username': 'newuser',
            'password': 'testpassword',
            'email': 'newuser@example.com',
            'role': 'Student',  # Or whatever the options are
        }
        

        response = self.client.post(reverse('register'), data)
        
        self.assertRedirects(response, reverse('account_created'))
        
        user = User.objects.get(username='newuser')
        self.assertTrue(user.check_password('testpassword'))  # Check that the password is hashed
        
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, 'Student')

    def test_password_is_hashed(self):
        data = {
            'username': 'newuser',
            'password': 'testpassword',
            'email': 'newuser@example.com',
            'role': 'Student',
        }

        self.client.post(reverse('register'), data)
        
        user = User.objects.get(username='newuser')
        
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
    

class UserCourseDetailsAPITests(APITestCase):
    
    def setUp(self):
        self.teacher = User.objects.create_user(username='testteacher', password='testpassword')
        self.course = Course.objects.create(name='Test Course', description='A test course', teacher=self.teacher)
    
    def test_user_course_details_api_success(self):

        response = self.client.get(reverse('user_course_details_api', kwargs={'course_id': self.course.id}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], 'Test Course')
    
    def test_user_course_details_api_empty_data(self):

        response = self.client.get(reverse('user_course_details_api', kwargs={'course_id': self.course.id}))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertIn('weeks', response.data)
        self.assertEqual(len(response.data['weeks']), 0)
        
        self.assertIn('feedback', response.data)
        self.assertEqual(len(response.data['feedback']), 0)
    def test_user_course_details_api_not_found(self):

        response = self.client.get(reverse('user_course_details_api', kwargs={'course_id': 9999}))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
class EnrolledStudentsViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.course = Course.objects.create(name="Test Course", description="Test course description", teacher=self.user)
        self.url = reverse('enrolled_students', kwargs={'course_id': self.course.id})
        
    @patch('requests.get')
    def test_enrolled_students_view_success(self, mock_get):

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'students': [{'id': 1, 'username': 'student1'}, {'id': 2, 'username': 'student2'}]}
        

        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(self.url)
        

        self.assertEqual(response.status_code, 200)
        
        self.assertIn('students', response.context)
        self.assertEqual(len(response.context['students']), 2)  # There should be 2 students
        

        self.assertContains(response, 'student1')
        self.assertContains(response, 'student2')
    
    def test_enrolled_students_view_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    @patch('requests.get')
    def test_enrolled_students_view_no_students(self, mock_get):

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'students': []}
        

        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get(self.url)
        

        self.assertEqual(response.status_code, 200)
        

        self.assertIn('students', response.context)
        self.assertEqual(len(response.context['students']), 0)  # No students returned
class RemoveStudentFromCourseTests(TestCase):
    
    def setUp(self):

        self.teacher_user = User.objects.create_user(username='teacheruser', password='teacherpassword')
        self.student_user = User.objects.create_user(username='studentuser', password='studentpassword')


        self.teacher_profile = UserProfile.objects.create(user=self.teacher_user, role='Teacher')
        self.student_profile = UserProfile.objects.create(user=self.student_user, role='Student')

        self.course = Course.objects.create(
            name="Test Course",
            description="A test course",
            teacher=self.teacher_user  # Assign the teacher to the course
        )

        self.course_student = CourseStudents.objects.create(course=self.course, student=self.student_profile)

    def test_remove_student_unauthenticated(self):
        """Since the user is not authenticated, they should be redirected to login"""
        url = reverse('remove_student_from_course', kwargs={'course_id': self.course.id, 'student_id': self.student_profile.id})
        response = self.client.get(url)
        
        self.assertRedirects(response, f'/accounts/login/?next={url}')

class CreateCoursePageTests(TestCase):
    def setUp(self):

        self.teacher_user = User.objects.create_user(username='teacher', password='password')
        self.student_user = User.objects.create_user(username='student', password='password')

        UserProfile.objects.create(user=self.teacher_user, role='Teacher')
        UserProfile.objects.create(user=self.student_user, role='Student')

        self.create_course_url = reverse('create_course_page')

    def test_redirect_if_not_teacher(self):
        """Test that users who are not teachers are redirected to the profile page."""
        self.client.login(username='student', password='password')
        response = self.client.get(self.create_course_url)
        self.assertRedirects(response, '/profile/')
    
    def test_get_create_course_page_for_teacher(self):
        """Test that a teacher can access the create course page and see the form."""
        self.client.login(username='teacher', password='password')
        response = self.client.get(self.create_course_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

class EditCoursePageTests(TestCase):
    def setUp(self):
        
        self.teacher_user = User.objects.create_user(username='teacher', password='password')
        self.student_user = User.objects.create_user(username='student', password='password')

        
        UserProfile.objects.create(user=self.teacher_user, role='Teacher')
        UserProfile.objects.create(user=self.student_user, role='Student')

        
        self.course = Course.objects.create(
            name='Test Course',
            description='Test Course Description',
            teacher=self.teacher_user
        )

        
        self.edit_course_url = reverse('edit_course_page', kwargs={'course_id': self.course.id})

    def test_teacher_can_access_edit_course_page(self):
        """Test that a teacher can access the course edit page."""
        self.client.login(username='teacher', password='password')
        response = self.client.get(self.edit_course_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Course')
    def test_non_teacher_cannot_access_edit_course_page(self):
        """Test that a non-teacher (student) cannot access the course edit page."""
        self.client.login(username='student', password='password')
        response = self.client.get(self.edit_course_url)
        self.assertEqual(response.status_code, 404)
    