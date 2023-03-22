from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Assignment, Course, ForumPost, UserProfile


class UserLoginForm(AuthenticationForm):
    """
    Форма для аутентификации пользователей.
    """

    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class UserRegistrationForm(UserCreationForm):
    """
    Форма для регистрации нового пользователя.
    """

    username = forms.CharField(label="Имя пользователя")
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "due_date", "course"]


class ForumPostForm(forms.ModelForm):
    """
    Форма для создания нового сообщения на форуме.
    """

    class Meta:
        model = ForumPost
        fields = ["title", "content"]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["role", "interests"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["interests"].widget.attrs.update({"rows": 5})


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "teacher", "start_date", "end_date", "students"]
