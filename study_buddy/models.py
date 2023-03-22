from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    Модель профиля пользователя с указанием роли (студент или преподаватель) и интересов.
    """

    ROLE_CHOICES = (
        ("student", "Студент"),
        ("teacher", "Преподаватель"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student", verbose_name="Роль")
    interests = models.TextField(blank=True, verbose_name="Интересы")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return self.user.username


class Course(models.Model):
    """
    Модель курса с информацией о преподавателе, начальной и конечной дате курса.
    """

    title = models.CharField(max_length=255, verbose_name="Название")
    teacher = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="courses_taught",
        verbose_name="Преподаватель",
    )
    students = models.ManyToManyField(UserProfile, related_name="courses_enrolled", verbose_name="Студенты")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """
    Модель занятия с информацией о курсе, к которому оно относится, и времени проведения.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    date_time = models.DateTimeField(verbose_name="Дата и время")

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
        ordering = ["-date_time"]

    def __str__(self):
        return self.title


class Assignment(models.Model):
    """
    Модель домашнего задания или проекта, связанного с определенным курсом.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Курс",
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    due_date = models.DateTimeField(verbose_name="Срок выполнения")
    students_completed = models.ManyToManyField(
        UserProfile,
        related_name="completed_assignments",
        blank=True,
        verbose_name="Студенты, выполнившие задание",
    )

    class Meta:
        verbose_name = "Домашнее задание или проект"
        verbose_name_plural = "Домашние задания и проекты"
        ordering = ["-due_date"]

    def __str__(self):
        return self.title


class Forum(models.Model):
    """
    Модель форума для обсуждения вопросов, связанных с определенным курсом.
    """

    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name="forum", verbose_name="Курс")
    title = models.CharField(max_length=255, verbose_name="Название")

    class Meta:
        verbose_name = "Форум"
        verbose_name_plural = "Форумы"

    def __str__(self):
        return self.title


class ForumPost(models.Model):
    """
    Модель сообщения на форуме.
    """

    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name="posts", verbose_name="Форум")
    author = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="forum_posts",
        verbose_name="Автор",
    )
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name = "Сообщение на форуме"
        verbose_name_plural = "Сообщения на форуме"

    def __str__(self):
        return self.title


class Notification(models.Model):
    """
    Модель уведомления для оповещения пользователей о различных событиях.
    """

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Пользователь",
    )
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    read = models.BooleanField(default=False, verbose_name="Прочитано")

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return self.title
