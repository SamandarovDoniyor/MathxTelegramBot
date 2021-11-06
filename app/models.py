from django.db import models

# ManyToOne - ForeignKey
# ManyToMany - ManyToMany

class BotUser(models.Model):
    objects = models.Manager()
    chat_id = models.IntegerField(unique=True)
    full_name = models.CharField(max_length=255)
    record = models.IntegerField(default=0)


class Game(models.Model):
    user = models.ForeignKey(to=BotUser, on_delete=models.CASCADE)
    question_number = models.IntegerField(default=1)
    finished = models.BooleanField(default=False)


class Question(models.Model):
    class Difficulty(models.TextChoices):
        EASY = 'Easy'
        MEDIUM = 'Medium'
        HARD = 'Hard'
        VERY_HARD = 'Very hard'

    class Operator(models.TextChoices):
        PLUS = '+'
        MINUS = '-'
        MULTIPLE = '*'
        DIVIDE = '/'

    first_value = models.IntegerField()
    second_value = models.IntegerField()
    operator = models.CharField(max_length=1, choices=Operator.choices)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices)

    @property
    def result(self):
        text = str(self.first_value) 
        text += ' ' + self.operator
        text += str(self.second_value)
        return eval(text)
