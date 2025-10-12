from django.contrib import admin;
from .models import Question, Choice, PUser;


class ChoiceInLine(admin.TabularInline):
    model = Choice;
    extra = 2;


class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "pub_date");
    inlines = [ChoiceInLine];

class PUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'date_joined');
    search_fields = ('username', 'email', 'first_name', 'last_name');
    fields = (
        ('username', 'email'),
        ('first_name', 'last_name'),
        ('is_staff', 'is_superuser'),
        ('last_login', 'date_joined'),
        'image'
    );
    readonly_fields = ('date_joined', 'last_login');

admin.site.register(Question, QuestionAdmin);
admin.site.register(PUser, PUserAdmin);
