from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Comment


@registry.register_document
class CommentDocument(Document):
    id = fields.IntegerField(attr="id")

    class Index:
        name = "comments"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = Comment
        fields = [
            "user_name",
            "email",
            "text",
            "created_at",
        ]
