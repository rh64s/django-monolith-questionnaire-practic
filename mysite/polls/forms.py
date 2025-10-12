from django.contrib.auth import password_validation;
from django.core.exceptions import ValidationError;
# from .models import user_registrated;
from django.contrib.auth import authenticate, login;
from django.forms import inlineformset_factory

from django.utils.translation import gettext_lazy;
from .models import PUser, Question, Choice;
from django import forms;

#FORMS

class FormChangeUserInfo(forms.ModelForm):
    email = forms.EmailField(required=True,
                             label='Адрес эл. почты');
    image = forms.ImageField(required=False, label="Аватар пользователя");
    class Meta:
        model = PUser;
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'image',
        );

class FormRegisterUser(forms.ModelForm):
    email = forms.EmailField(required = True,
                             label = "Адрес электронной почты");
    password1 = forms.CharField(label= 'Пароль',
                                widget=forms.PasswordInput,
                                help_text= password_validation.password_validators_help_text_html());
    password2 = forms.CharField(label='Подтвердить пароль',
                                widget=forms.PasswordInput,
                                help_text="Повторите пароль пожалуйста.");
    def clean_password(self):
        password1 = self.cleaned_data["password1"];
        if password1:
            password_validation.validate_password(password1);
        return password1;

    def clean(self):
        super().clean();
        password1 = self.cleaned_data["password1"];
        password2 = self.cleaned_data["password2"];
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError
            ('Введенные пароли не совпадают', code='password_mismatch')};
            raise ValidationError(errors);

    def save(self, commit=True):
        user = super().save(commit=False);
        user.set_password(self.cleaned_data["password1"]);
        if commit:
            user.save();
        # user_registrated.send(FormRegisterUser, instance=user);
        return user;

    class Meta:
        model = PUser;
        fields = ('username', 'email', 'first_name', 'last_name',
                'password1', 'password2');

class FormQuestion(forms.ModelForm):
    death_date = forms.DateTimeField(label='Время окончания опроса', widget=forms.SelectDateWidget, help_text='Выберите дату, когда опрос перестанет быть действительным')
    class Meta:
        model = Question;
        fields = ('author', 'question_header', 'question_text', 'image', 'death_date');
        widgets = {'author': forms.HiddenInput};

FormChoiceSet = inlineformset_factory(Question, Choice, fields=('choice_text',))
