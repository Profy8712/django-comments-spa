from rest_framework import serializers
from .models import Comment, Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']


class CommentSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'user_name',
            'email',
            'homepage',
            'text',
            'parent',
            'created_at',
            'attachments',
            'children'
        ]

    def get_children(self, obj):
        return CommentSerializer(obj.children.all(), many=True).data
