from django.contrib import admin
from app.models import *


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'full_name', 'record']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['user', 'question_number', 'finished']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['first_value', 'second_value', 'difficulty', 'operator']

