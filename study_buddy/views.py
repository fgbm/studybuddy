from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)

from .forms import AssignmentForm, UserLoginForm, UserProfileForm
from .models import Assignment, Course, Lesson, UserProfile


class UserLoginView(LoginView):
    """
    Представление для авторизации пользователя.
    """

    authentication_form = UserLoginForm
    template_name = "login.html"
    success_url = reverse_lazy("home")


def user_logout(request):
    """
    Метод выхода из системы.
    """
    logout(request)
    messages.success(request, "Вы успешно вышли из системы")
    return redirect("home")


class UserRegisterView(CreateView):
    """
    Представление для регистрации новых пользователей.
    """

    form_class = UserCreationForm
    template_name = "register.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        profile_form = UserProfileForm(self.request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = self.object
            profile.save()
        return response


class HomeView(LoginRequiredMixin, TemplateView):
    """
    Представление для главной страницы приложения.
    """

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем профиль пользователя
        user_profile = UserProfile.objects.filter(user=self.request.user).first()
        # Если профиль существует, добавляем список курсов в контекст
        if user_profile:
            if user_profile.role == "student":
                courses = user_profile.courses_enrolled.all()
            else:
                courses = user_profile.courses_taught.all()
            context["courses"] = courses
        else:
            context["courses"] = []

        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для отображения детальной информации о курсе.
    """

    model = Course
    template_name = "course_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_students"] = UserProfile.objects.filter(role="student").exclude(
            courses_enrolled=self.object.id
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        course = self.get_object()
        if user.userprofile.role == "student" and user.userprofile not in course.students.all():
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class CourseCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    """
    Представление для создания курса.
    """

    model = Course
    fields = ["title", "start_date", "end_date"]
    template_name = "course_form.html"

    def test_func(self):
        return self.request.user.userprofile.role == "teacher"

    def form_valid(self, form):
        form.instance.teacher = self.request.user.userprofile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("course_detail", args=[str(self.object.id)])


class CourseUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования курса.
    """

    model = Course
    fields = ["title", "start_date", "end_date"]
    template_name = "course_form.html"

    def test_func(self):
        return self.request.user.userprofile.role == "teacher"

    def get_success_url(self):
        return reverse_lazy("course_detail", args=[str(self.object.id)])


class CourseDeleteView(DeleteView):
    model = Course
    template_name = "course_confirm_delete.html"
    success_url = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.userprofile.role != "teacher":
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class AssignmentDetailView(DetailView):
    """
    Представление для детального просмотра домашнего задания.
    """

    model = Assignment
    template_name = "assignment_detail.html"
    context_object_name = "assignment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.userprofile.role == "student":
            obj.students_completed.add(request.user.userprofile)
            obj.save()
            return HttpResponseRedirect(reverse("assignment_detail", kwargs={"pk": obj.pk}))
        return HttpResponseRedirect(reverse("assignment_detail", kwargs={"pk": obj.pk}))


class AssignmentCreateView(CreateView):
    """
    Представление для создания домашнего задания.
    """

    model = Assignment
    form_class = AssignmentForm
    template_name = "assignment_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        return context

    def form_valid(self, form):
        form.instance.teacher = self.request.user.userprofile
        form.instance.course = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("course_detail", args=[str(self.object.course.id)])


class AssignmentUpdateView(UpdateView):
    """
    Представление для обновления домашнего задания.
    """

    model = Assignment
    form_class = AssignmentForm
    template_name = "assignment_form.html"

    def get_success_url(self):
        return reverse_lazy("course_detail", args=[str(self.object.course.id)])


class LessonCreateView(CreateView):
    """
    Представление для создания урока.
    """

    model = Lesson
    template_name = "lesson_form.html"
    fields = ["title", "description", "date_time"]

    def form_valid(self, form):
        course = Course.objects.get(pk=self.kwargs["course_pk"])
        form.instance.course = course
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = Course.objects.get(pk=self.kwargs["course_pk"])
        return context

    def get_success_url(self):
        return reverse_lazy("course_detail", kwargs={"pk": self.kwargs["course_pk"]})


class LessonUpdateView(UpdateView):
    """
    Представление для обновления урока.
    """

    model = Lesson
    template_name = "lesson_form.html"
    fields = ["title", "description", "date_time"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.object.course
        return context

    def get_success_url(self):
        return reverse_lazy("course_detail", kwargs={"pk": self.object.course.pk})


class AddStudentToCourseView(View):
    """
    Представление для добавления студента в курс.
    """

    def post(self, request, *args, **kwargs):
        course = Course.objects.get(pk=self.kwargs["course_pk"])
        student_pk = request.POST.get("student_pk")
        student = UserProfile.objects.get(pk=student_pk)
        course.students.add(student)
        return HttpResponseRedirect(reverse_lazy("course_detail", kwargs={"pk": self.kwargs["course_pk"]}))


class RemoveStudentFromCourseView(View):
    """
    Представление для исключения студента из курса.
    """

    def post(self, request, *args, **kwargs):
        course = Course.objects.get(pk=self.kwargs["course_pk"])
        student = UserProfile.objects.get(pk=self.kwargs["student_pk"])
        course.students.remove(student)
        return HttpResponseRedirect(reverse_lazy("course_detail", kwargs={"pk": self.kwargs["course_pk"]}))
