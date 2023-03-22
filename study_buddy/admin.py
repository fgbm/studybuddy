from django.contrib import admin

from .models import (
    Assignment,
    Course,
    Forum,
    ForumPost,
    Lesson,
    Notification,
    UserProfile,
)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "interests")


class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "start_date", "end_date")
    search_fields = ("title", "teacher__user__username")


class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "date_time")
    search_fields = ("title", "course__title")


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "due_date")
    search_fields = ("title", "course__title")


class ForumAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    search_fields = ("title", "course__title")


class ForumPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "forum", "created_at", "updated_at")
    search_fields = ("title", "author__user__username", "forum__title")


class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at", "read")
    search_fields = ("title", "user__user__username")


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(ForumPost, ForumPostAdmin)
admin.site.register(Notification, NotificationAdmin)
