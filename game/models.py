import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .constants import TOTAL_ROUNDS

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    text        = models.TextField()
    approved    = models.BooleanField(default=True)  # only approved appear
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

class Choice(models.Model):
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text       = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class GameMatch(models.Model):
    STATUS_CHOICES = [
        ('WAITING',    'Waiting for opponent'),
        ('IN_ROUND',   'Round in progress'),
        ('COMPLETED',  'Match completed'),
    ]
    player1       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_p1')
    player2       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_p2', null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    started_at    = models.DateTimeField(null=True, blank=True)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='WAITING')
    current_round = models.IntegerField(default=1)

    def __str__(self):
        return f"Match {self.id} ({self.player1} vs {self.player2 or '…'})"

class Round(models.Model):
    match        = models.ForeignKey(GameMatch, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField()
    chooser      = models.ForeignKey(User, on_delete=models.CASCADE)
    category     = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('match','round_number')

    def __str__(self):
        return f"Match {self.match.id} – Round {self.round_number}"

class RoundSession(models.Model):
    round        = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='sessions')
    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at   = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score        = models.IntegerField(default=0)

    class Meta:
        unique_together = ('round','user')

    def __str__(self):
        return f"{self.user} in {self.round}"

class AnswerLog(models.Model):
    session        = models.ForeignKey(RoundSession, on_delete=models.CASCADE, related_name='answers')
    question       = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice= models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    is_correct     = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.session.user} – Q{self.question.id}: {self.is_correct}"
