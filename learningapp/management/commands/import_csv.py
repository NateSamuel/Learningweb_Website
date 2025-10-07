import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from django.conf import settings
from learningapp.models import UserProfile, Status, Course, CourseWeek, CourseWeekContent, Feedback, CourseStudents
from datetime import datetime
from django.utils import timezone

MEDIA_ROOT = settings.MEDIA_ROOT  # Ensure MEDIA_ROOT is properly set

class Command(BaseCommand):
    help = 'Import data from CSV files into the database'

    def handle(self, *args, **kwargs):

        try:
            # Import Users
            with open('data/users.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    user, created = User.objects.get_or_create(username=row['username'], email=row['email'])
                    if created:
                        user.set_password(row['password'])
                        user.save()

                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.role = row.get('role', 'Student')  # Default to 'Student' if missing
                    profile.save()
        except Exception as e:
            print(f"Error importing users: {e}")

        try:
            # Import Courses
            with open('data/courses.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    teacher = User.objects.get(username=row['teacher_username'])
                    course, created = Course.objects.get_or_create(
                        name=row['course_name'],
                        teacher=teacher
                    )
                    course.date_created = datetime.strptime(row['date_created'].strip(), "%Y-%m-%d %H:%M:%S")
                    course.date_created = timezone.make_aware(course.date_created)  # Make it aware
                    course.deadline = datetime.strptime(row['deadline'].strip(), "%Y-%m-%d %H:%M:%S")
                    course.deadline = timezone.make_aware(course.deadline)  # Make it aware
                    course.save()
        except Exception as e:
            print(f"Error importing courses: {e}")

        try:
            # Import Course Weeks
            with open('data/course_weeks.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Try to get the course by name
                    try:
                        course = Course.objects.get(name=row['course_name'])
                    except Course.DoesNotExist:
                        print(f"Course '{row['course_name']}' not found. Skipping...")
                        continue  # Skip to the next row if course doesn't exist

                    # Now, create or update the course week
                    try:
                        week, created = CourseWeek.objects.get_or_create(
                            course=course,
                            week_number=row['week_number'],
                            start_date=datetime.strptime(row['start_date'], "%Y-%m-%d").date(),
                            end_date=datetime.strptime(row['end_date'], "%Y-%m-%d").date()
                        )
                        week.save()
                    except Exception as e:
                        print(f"Error creating course week: {e}")
        except Exception as e:
            print(f"Error importing course weeks: {e}")

        # Import Course Week Content
        try:
            with open('data/course_week_content.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    course_name = row['course_name'].strip()
                    week_number = int(row['week_number'])
                    pdf_path = row['pdf'].strip()

                    # Find the corresponding CourseWeek instance
                    try:
                        course = Course.objects.get(name=course_name)
                        course_week = CourseWeek.objects.get(course=course, week_number=week_number)
                    except Course.DoesNotExist:
                        print(f"Course '{course_name}' not found. Skipping...")
                        continue
                    except CourseWeek.DoesNotExist:
                        print(f"CourseWeek '{course_name} - Week {week_number}' not found. Skipping...")
                        continue

                    # Create CourseWeekContent instance
                    course_week_content, created = CourseWeekContent.objects.get_or_create(
                        course_week=course_week,
                        title=f"Week {week_number} Content"
                    )

                    # Instead of saving a new file, just store the file path
                    course_week_content.pdf.name = pdf_path  # Assign the relative path
                    course_week_content.save()

        except Exception as e:
            print(f"Error importing course week content: {e}")

        try:
            # Import Course Enrollment
            with open('data/course_enrollment.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    student_profile = UserProfile.objects.get(user__username=row['student_username'])
                    course = Course.objects.get(name=row['course_name'])
                    enrollment, created = CourseStudents.objects.get_or_create(student=student_profile, course=course)
                    enrollment.save()
        except Exception as e:
            print(f"Error importing course enrollments: {e}")

        try:
            # Import Feedback
            with open('data/feedback.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    student_profile = UserProfile.objects.get(user__username=row['student_username'])
                    course = Course.objects.get(name=row['course_name'])

                    # Parse the date from CSV
                    date_submitted = datetime.strptime(row['date_given'], "%Y-%m-%d %H:%M:%S")

                    # Ensure the datetime is timezone-aware
                    if timezone.is_naive(date_submitted):
                        date_submitted = timezone.make_aware(date_submitted)
                    
                    feedback, created = Feedback.objects.get_or_create(
                        student=student_profile,
                        course=course,
                        feedback_text=row['feedback_text'],
                        date_submitted=date_submitted
                    )
        except Exception as e:
            print(f"Error importing feedback: {e}")

        # Import Status
        try:
            with open('data/status.csv', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    username = row['username'].strip()
                    text = row['text'].strip()

                    # Assuming the 'created_at' field in CSV is in the format 'YYYY-MM-DD HH:MM:SS'
                    created_at = datetime.strptime(row['created_at'].strip(), "%Y-%m-%d %H:%M:%S")
                    created_at = timezone.make_aware(created_at)

                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        print(f"User '{username}' not found. Skipping...")
                        continue

                    # Create and save Status object
                    status, created = Status.objects.get_or_create(
                        user=user,
                        text=text,
                        created_at=created_at
                    )

        except Exception as e:
            print(f"Error importing status updates: {e}")

        

