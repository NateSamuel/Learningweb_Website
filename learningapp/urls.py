from django.urls import include, path
from . import views
from .api import user_courses_api, user_course_details_api, courses_not_enrolled_api, enroll_student_api, submit_feedback_api, create_course, edit_course_api, add_week_api, get_enrolled_students_api
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('account_created/', views.account_created, name='account_created'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('accounts/login/', views.user_login, name='login'),
    path('app/', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('api/courses/<str:username>/', user_courses_api, name='user_courses_api'),
    path('api/courses/details/<int:course_id>/', user_course_details_api, name='user_course_details_api'),
    path('course/details/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('api/courses/not-enrolled/<str:username>/', courses_not_enrolled_api, name='courses_not_enrolled_api'),
    path('api/enroll/<int:course_id>/', enroll_student_api, name='enroll-student'),
    path('api/submit-feedback/<int:course_id>/', submit_feedback_api, name='submit_feedback_api'),
    path('create-course/', views.create_course_page, name='create_course_page'),
    path('api/create-course/', create_course, name='create_course_api'),
    path('api/course/<int:course_id>/edit/', edit_course_api, name='edit_course_api'),
    path('course/<int:course_id>/edit/', views.edit_course_page, name='edit_course_page'),
    path('api/courses/<int:course_id>/add_week/', add_week_api, name='add_week_api'),
    path('course/<int:course_id>/add_week/', views.add_week_page, name='add_week_page'),
    path('course/<int:course_id>/week/<int:week_id>/add_content/', views.add_week_content, name='add_week_content'),
    path('api/courses/<int:course_id>/students/', get_enrolled_students_api, name='get_enrolled_students_api'),
    path('course/<int:course_id>/students/', views.enrolled_students_view, name='enrolled_students'),
    path('course/<int:course_id>/students/remove/<int:student_id>/', views.remove_student_from_course, name='remove_student_from_course'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)