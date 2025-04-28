from django.contrib import admin
from .models import (
    Category, Question, Choice,
    GameMatch, Round, RoundSession, AnswerLog,
)

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ('text','category','approved')
    list_filter   = ('approved','category')
    inlines       = [ChoiceInline]

admin.site.register(Category)
admin.site.register(GameMatch)
admin.site.register(Round)
admin.site.register(RoundSession)
admin.site.register(AnswerLog)
