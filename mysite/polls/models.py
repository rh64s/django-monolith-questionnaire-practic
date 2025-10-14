import datetime;

from django.db import models;
from django.utils import timezone;
from django.contrib.auth.models import AbstractUser;
from datetime import date

from .utilities import get_timestamp_path


class PUser(AbstractUser):
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Аватар', default='default_avatar.jpg');
    
    def delete(self, *args, **kwargs):
        for qu in self.question_set.all():
            qu.delete()
        super().delete(*args, **kwargs)
    
    class Meta(AbstractUser.Meta):
        pass;

class Question(models.Model):
    question_header = models.CharField(max_length=100, verbose_name='Заголовок');
    question_text = models.CharField(max_length=200, verbose_name='Вопрос');
    pub_date = models.DateTimeField('date published', default=date.today);
    death_date = models.DateField('date death');
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='Изображение');
    author = models.ForeignKey(PUser, on_delete=models.CASCADE, verbose_name='Автор вопроса');
    
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1);

    def __str__(self):
        return self.question_text;

    def delete(self, *args, **kwargs):
        for ch in self.choice_set.all():
            ch.delete()
        super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = 'Опросы'
        verbose_name = 'Опрос'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE);
    choice_text = models.CharField(max_length=200);
    votes = models.IntegerField(default=0);

    def __str__(self):
        return self.choice_text;

class UserChoice(models.Model):
    user = models.ForeignKey(PUser, on_delete=models.CASCADE);
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE);
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    def delete(self, *args, **kwargs):
        ch = UserChoice.objects.get(choice=self.choice).count();
        ch.votes -= 1;
        ch.save();
        super().delete(*args, **kwargs)
