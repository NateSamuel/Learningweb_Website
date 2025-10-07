from django.contrib import admin
from .models import UserProfile, Status, Course, CourseWeek, CourseWeekContent, Feedback, CourseStudents

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Status)
admin.site.register(Course)
admin.site.register(CourseWeek)
admin.site.register(CourseWeekContent)
admin.site.register(Feedback)
admin.site.register(CourseStudents)