from django.db import models
from uuid import uuid4


class Token(models.Model):
    token = models.UUIDField(verbose_name='token', default=uuid4)
    user = models.ForeignKey('auth.User', related_name='registration_tokens', verbose_name='user', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.token)