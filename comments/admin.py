from django.contrib import admin

from .models import Comment, Attachment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user_name", "email", "created_at", "parent")
    list_filter = ("created_at",)
    search_fields = ("user_name", "email", "text")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "comment", "file", "uploaded_at")
    list_filter = ("uploaded_at",)



