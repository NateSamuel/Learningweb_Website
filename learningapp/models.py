from django.db import models
from django.contrib.auth.models import User

def course_image_upload_path(instance, filename):
    """Generate file path for course images based on the course name."""
    course_name = instance.name.replace(" ", "_")
    return f"course_images/{course_name}/{filename}"

class Course(models.Model):
    """Represents a course with a name, description, date, deadline, teacher, and optional image."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses_taught")
    image = models.ImageField(upload_to=course_image_upload_path, blank=True, null=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """Represents a user profile, including the role (Teacher/Student) and courses the user is enrolled in."""
    TEACHER = 'Teacher'
    STUDENT = 'Student'
    ROLE_CHOICES = [
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=STUDENT)
    courses_enrolled = models.ManyToManyField("Course", through='CourseStudents', related_name="user_profiles", blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Status(models.Model):
    """Represents a status update made by a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}"

class CourseWeek(models.Model):
    """Represents a week within a course, with a start date and end date."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="weeks")
    week_number = models.PositiveIntegerField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('course', 'week_number')

    def __str__(self):
        return f"{self.course.name} - Week {self.week_number}"

def course_pdf_upload_path(instance, filename):
    """Dynamically generate file path for course PDFs based on the course and week."""
    course_name = instance.course_week.course.name.replace(" ", "_")
    return f"course_pdfs/{course_name}/Week_{instance.course_week.week_number}.pdf"

class CourseWeekContent(models.Model):
    """Represents content (PDF) associated with a specific week in a course."""
    course_week = models.ForeignKey(CourseWeek, on_delete=models.CASCADE, related_name="content")
    title = models.CharField(max_length=255)
    pdf = models.FileField(upload_to=course_pdf_upload_path)

    def __str__(self):
        return f"{self.course_week.course.name} - {self.title}"

class Feedback(models.Model):
    """Represents feedback given by a student for a specific course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="feedback")
    student = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="feedback_given")
    feedback_text = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.course.name} by {self.student.user.username}"

class CourseStudents(models.Model):
    """Represents the enrollment of a student in a specific course."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrolled_students")
    student = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="course_students")

    class Meta:
        unique_together = ('course', 'student')

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.course.name}"
