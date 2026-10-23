from django.db import models


class BoardColumn(models.Model):
    name = models.CharField(max_length=80, unique=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position', 'pk']

    def __str__(self):
        return self.name


class Card(models.Model):
    class Owner(models.TextChoices):
        MILAN = 'M', 'Milan'
        EMMA = 'E', 'Emma'
        TOGETHER = 'S', 'Samen'

    title = models.CharField(max_length=200)
    owner = models.CharField(max_length=1, choices=Owner.choices)
    notes = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    column = models.ForeignKey(BoardColumn, related_name='cards', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'pk']

    def __str__(self):
        return self.title


class Subtask(models.Model):
    card = models.ForeignKey(Card, related_name='subtasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    is_done = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position', 'pk']

    def __str__(self):
        return self.title
