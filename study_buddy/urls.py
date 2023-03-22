from django.contrib import admin
from django.urls import path

from .views import (
    AddStudentToCourseView,
    AssignmentCreateView,
    AssignmentDetailView,
    AssignmentUpdateView,
    CourseCreateView,
    CourseDeleteView,
    CourseDetailView,
    CourseUpdateView,
    HomeView,
    LessonCreateView,
    LessonUpdateView,
    RemoveStudentFromCourseView,
    UserLoginView,
    UserRegisterView,
    user_logout,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("accounts/login/", UserLoginView.as_view(), name="login"),
    path("logout/", user_logout, name="logout"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("course/<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
    path("course/<int:pk>/delete/", CourseDeleteView.as_view(), name="course_delete"),
    path("course/add/", CourseCreateView.as_view(), name="course_create"),
    path("course/<int:pk>/edit/", CourseUpdateView.as_view(), name="course_update"),
    path("course/<int:course_pk>/assignment/add/", AssignmentCreateView.as_view(), name="assignment_create"),
    path("course/<int:course_pk>/lesson/add/", LessonCreateView.as_view(), name="lesson_create"),
    path(
        "course/<int:course_pk>/student/add/",
        AddStudentToCourseView.as_view(),
        name="add_student_to_course",
    ),
    path(
        "course/<int:course_pk>/student/<int:student_pk>/remove/",
        RemoveStudentFromCourseView.as_view(),
        name="remove_student_from_course",
    ),
    path("assignment/<int:pk>/", AssignmentDetailView.as_view(), name="assignment_detail"),
    path("assignment/<int:pk>/edit/", AssignmentUpdateView.as_view(), name="assignment_update"),
    path("lessons/<int:pk>/edit/", LessonUpdateView.as_view(), name="lesson_update"),
]
