from rest_framework import serializers
from .models import Course, CourseStudents, UserProfile, CourseWeek, CourseWeekContent, Feedback

class CourseSerializer(serializers.ModelSerializer):
    """Serializes the Course model for displaying course details."""
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image', 'date_created', 'deadline', 'teacher']

class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializes the Course model for creating a new course."""
    class Meta:
        model = Course
        fields = ['name', 'deadline', 'teacher']

class CourseStudentsSerializer(serializers.ModelSerializer):
    """Serializes the CourseStudents model with related course details."""
    course = CourseSerializer()

    class Meta:
        model = CourseStudents
        fields = ['course', 'student']

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes the UserProfile model, including the courses a user is enrolled in."""
    courses = CourseSerializer(many=True, read_only=True, source='courses_enrolled')

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role', 'courses']

class CourseWeekContentSerializer(serializers.ModelSerializer):
    """Serializes the CourseWeekContent model, representing content for each week in a course."""
    class Meta:
        model = CourseWeekContent
        fields = ['course_week', 'title', 'pdf']

class FeedbackSerializer(serializers.ModelSerializer):
    """Serializes the Feedback model, including student username for feedback submission."""
    student_username = serializers.CharField(source='student.user.username', read_only=True)

    class Meta:
        model = Feedback
        fields = ['student_username', 'feedback_text', 'date_submitted', 'course', 'student']
        read_only_fields = ['id', 'student_username', 'date_submitted', 'student']

class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """Serializes the CourseStudents model for handling course enrollment and validation."""
    class Meta:
        model = CourseStudents
        fields = ['course', 'student']

    def validate(self, data):
        """Ensure the student is not already enrolled in the course."""
        student = data['student']
        course = data['course']

        if CourseStudents.objects.filter(course=course, student=student).exists():
            raise serializers.ValidationError("Student is already enrolled in this course.")

        return data

    def create(self, validated_data):
        """Create a new enrollment record."""
        return CourseStudents.objects.create(**validated_data)

class CourseWeekSerializer(serializers.ModelSerializer):
    """Serializes the CourseWeek model, including related CourseWeekContent."""
    content = CourseWeekContentSerializer(many=True)

    class Meta:
        model = CourseWeek
        fields = ['id', 'week_number', 'start_date', 'end_date', 'content']

class CourseEditSerializer(serializers.ModelSerializer):
    """Serializes the Course model for editing course details."""
    class Meta:
        model = Course
        fields = ['name', 'description', 'deadline', 'image']

class EnrolledStudentSerializer(serializers.ModelSerializer):
    """Serializes the UserProfile model for enrolled students, displaying their username and email."""
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    id = serializers.IntegerField(source='user.id')

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email']
