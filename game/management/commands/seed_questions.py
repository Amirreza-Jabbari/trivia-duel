# game/management/commands/seed_questions.py
from django.core.management.base import BaseCommand
from game.models import Category, Question, Choice

class Command(BaseCommand):
    help = 'Seed 6 categories and 5 dummy questions each'

    def handle(self, *args, **options):
        names = ['Technology','Science','History','Sports','Entertainment','Geography']
        for name in names:
            cat, _ = Category.objects.get_or_create(name=name, slug=name.lower())
            Question.objects.filter(category=cat).delete()
            for i in range(1,6):
                q = Question.objects.create(
                    category=cat,
                    text=f"Sample {i} in {name}?"
                )
                Choice.objects.create(question=q,text="Correct Answer",is_correct=True)
                for j in range(1,4):
                    Choice.objects.create(question=q,text=f"Wrong {j}",is_correct=False)
        self.stdout.write(self.style.SUCCESS("✅ Seeded categories & questions."))
