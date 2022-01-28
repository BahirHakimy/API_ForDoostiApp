from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete

CHAT_TYPES = [("PR", "Private"), ("PB", "Public")]


class Chat(models.Model):
    name = models.CharField(max_length=30, unique=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)
    chat_type = models.CharField(max_length=2, choices=CHAT_TYPES)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class MessageManager(models.Manager):
    def get_message_group(self, room):
        querset = super().get_queryset().filter(chat=room).order_by("timestamp")
        if len(querset) > 15:
            querset = querset[len(querset) - 15 : len(querset)]
        return querset

    def get_older_messages(self, room, lastmessage_id):
        message = Message.objects.get(id=lastmessage_id)
        querset = (
            super()
            .get_queryset()
            .filter(chat=room, timestamp__lt=message.timestamp)
            .order_by("timestamp")
        )
        if len(querset) > 15:
            querset = querset[len(querset) - 15 : len(querset)]
        return querset


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    attached_file = models.FileField(upload_to="files", null=True, blank=True)
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="viewed_users"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = MessageManager()

    def __str__(self):
        return self.content.split(" ")[0]


def delete_related_file(instance, *args, **kwargs):
    if instance.attached_file:
        instance.attached_file.delete(False)


post_delete.connect(delete_related_file, sender=Message)
