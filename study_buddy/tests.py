from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Assignment, Course, Lesson, UserProfile


# Создаём тестовые данные, которые можно использовать в разных тестовых случаях
def create_test_data():
    user_teacher = User.objects.create_user(username="testuser_teacher", password="testpassword_teacher")
    user_student = User.objects.create_user(username="testuser_student", password="testpassword_student")
    teacher = UserProfile.objects.create(user=user_teacher, role="teacher")
    student = UserProfile.objects.create(user=user_student, role="student")
    course = Course.objects.create(
        title="Test Course", start_date="2023-01-01", end_date="2023-12-31", teacher=teacher
    )
    lesson = Lesson.objects.create(
        title="Test Lesson",
        date_time="2023-01-10 14:00:00",
        description="Test lesson description",
        course=course,
    )
    assignment = Assignment.objects.create(
        title="Test Assignment",
        description="Test assignment description",
        due_date="2023-01-20 23:59:59",
        course=course,
    )
    return user_teacher, user_student, teacher, student, course, lesson, assignment


class ModelTests(TestCase):
    def test_course_creation(self):
        _, _, _, _, course, _, _ = create_test_data()
        self.assertEqual(course.title, "Test Course")

    def test_lesson_creation(self):
        _, _, _, _, _, lesson, _ = create_test_data()
        self.assertEqual(lesson.title, "Test Lesson")

    def test_assignment_creation(self):
        _, _, _, _, _, _, assignment = create_test_data()
        self.assertEqual(assignment.title, "Test Assignment")


class LessonViewTests(TestCase):
    def test_lesson_create_view(self):
        user_teacher, _, _, _, course, _, _ = create_test_data()
        self.client.login(username="testuser_teacher", password="testpassword_teacher")
        response = self.client.get(reverse("lesson_create", args=[course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Создание нового урока")

    def test_lesson_update_view(self):
        user_teacher, _, _, _, course, lesson, _ = create_test_data()
        self.client.login(username="testuser_teacher", password="testpassword_teacher")
        response = self.client.get(reverse("lesson_update", args=[lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Редактирование урока")


class AssignmentViewTests(TestCase):
    def test_assignment_create_view(self):
        user_teacher, _, _, _, course, _, _ = create_test_data()
        self.client.login(username="testuser_teacher", password="testpassword_teacher")
        response = self.client.get(reverse("assignment_create", args=[course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Создание нового задания")

    def test_assignment_update_view(self):
        user_teacher, _, _, _, course, _, assignment = create_test_data()
        self.client.login(username="testuser_teacher", password="testpassword_teacher")
        response = self.client.get(reverse("assignment_update", args=[assignment.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Редактирование задания")


class StudentManagementTests(TestCase):
    def test_add_student_to_course(self):
        user_teacher, user_student, _, student, course, _, _ = create_test_data()
        self.client.login(username="testuser_teacher", password="testpassword_teacher")
        response = self.client.post(
            reverse("add_student_to_course", args=[course.pk]), data={"student_pk": student.pk}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        course.refresh_from_db()
        self.assertTrue(student in course.students.all())

    def test_remove_student_from_course(self):
        user_teacher, user_student, _, student, course, _, _ = create_test_data()
        course.students.add(student)
        course.save()
        self.client.login(username="testuser_teacher", password="testpassword_teacher")
        response = self.client.post(reverse("remove_student_from_course", args=[course.pk, student.pk]))
        self.assertEqual(response.status_code, 302)
        course.refresh_from_db()
        self.assertFalse(student in course.students.all())


class CourseManagementTests(TestCase):
    def test_course_create(self):
        user_teacher, _, _, _, _, _, _ = create_test_data()
        self.client.login(username="testuser_teacher", password="testpassword_teacher")

        response = self.client.post(
            reverse("course_create"),
            data={
                "title": "New Test Course",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "teacher": user_teacher.userprofile.pk,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Course.objects.filter(title="New Test Course").exists())

    def test_course_update(self):
        user_teacher, _, _, _, course, _, _ = create_test_data()
        self.client.login(username="testuser_teacher", password="testpassword_teacher")

        response = self.client.post(
            reverse("course_update", args=[course.pk]),
            data={
                "title": "Updated Test Course",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "teacher": user_teacher.userprofile.pk,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        course.refresh_from_db()
        self.assertEqual(course.title, "Updated Test Course")

    def test_course_delete(self):
        user_teacher, _, _, _, course, _, _ = create_test_data()
        self.client.login(username="testuser_teacher", password="testpassword_teacher")

        response = self.client.post(reverse("course_delete", args=[course.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Course.objects.filter(pk=course.pk).exists())

    def test_student_cannot_update_course(self):
        _, user_student, _, _, course, _, _ = create_test_data()
        self.client.login(username="testuser_student", password="testpassword_student")

        response = self.client.post(
            reverse("course_update", args=[course.pk]),
            data={
                "title": "Updated Test Course",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "teacher": course.teacher.pk,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 403)  # Ожидаемый статус-код "Forbidden"
        course.refresh_from_db()
        self.assertNotEqual(course.title, "Updated Test Course")

    def test_student_cannot_delete_course(self):
        _, user_student, _, _, course, _, _ = create_test_data()
        self.client.login(username="testuser_student", password="testpassword_student")

        response = self.client.post(reverse("course_delete", args=[course.pk]), follow=True)
        self.assertEqual(response.status_code, 403)  # Ожидаемый статус-код "Forbidden"
        self.assertTrue(Course.objects.filter(pk=course.pk).exists())

    def test_student_can_view_assigned_course(self):
        _, user_student, _, student, course, _, _ = create_test_data()
        course.students.add(student)  # Назначаем студента на курс
        self.client.login(username="testuser_student", password="testpassword_student")

        response = self.client.get(reverse("course_detail", args=[course.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Course")

    def test_student_cannot_view_unassigned_course(self):
        _, user_student, _, _, course, _, _ = create_test_data()
        self.client.login(username="testuser_student", password="testpassword_student")

        response = self.client.get(reverse("course_detail", args=[course.pk]))
        self.assertEqual(response.status_code, 403)  # Ожидаемый статус-код "Forbidden"
