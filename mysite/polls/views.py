from django.shortcuts import render, get_object_or_404, redirect;
from django.http import HttpResponse, HttpResponseRedirect;
from .models import Question, Choice, PUser;
from django.template import loader;
from django.urls import reverse, reverse_lazy;
from django.views import generic;
from django.views.generic import UpdateView, CreateView, DeleteView;

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth import logout, authenticate, login;
from django.contrib.auth.decorators import login_required;
from django.contrib.auth.mixins import LoginRequiredMixin;
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin;

from .forms import FormChangeUserInfo, FormRegisterUser, FormQuestion, FormChoiceSet;
from .models import PUser, UserChoice;

# QUESTIONS

class IndexView(generic.ListView):
    template_name = 'polls/question/index.html';
    context_object_name = 'latest_question_list';

    # return all questions sorted by date
    def get_queryset(self):
        return Question.objects.order_by('-pub_date');


class DetailView(generic.DetailView):
    model = Question;
    template_name = 'polls/question/detail.html';


class ResultsView(generic.DetailView):
    model = Question;
    template_name = 'polls/question/results.html';


@login_required(login_url="polls:login")
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id);
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice']);
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/question/detail.html', {
            'question': question,
            'error_message': 'вы не сделали выбор'
        });
    try:
        user_choice = UserChoice.objects.get(question=question_id, user=request.user.pk);
        choices = [user_choice.choice.pk, selected_choice.pk]
        user_choice.choice = selected_choice; 
        user_choice.save();
        
        choice = Choice.objects.get(pk=choices[0]);
        choice.votes -= 1
        choice.save();
        
        choice = Choice.objects.get(pk=choices[1]);
        choice.votes += 1
        choice.save();
    # if get more than one answer (debug)
    except ObjectDoesNotExist:
        UserChoice(user=request.user, choice=selected_choice, question=Question.objects.get(pk=question_id)).save();
        user_choice = UserChoice.objects.get(user=request.user, choice=selected_choice, question=Question.objects.get(pk=question_id))
        choice = Choice.objects.get(pk=user_choice.choice.pk);
        choice.votes += 1;
        choice.save();
    # UserChoice.objects.all().delete();
    for choices in Choice.objects.filter(question_id=question_id):
        choices.votes = UserChoice.objects.filter(choice=choices).count();
        choices.save();
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)));

@login_required(login_url="polls:login")
def question_create(request):
    if request.method == 'POST':
        form = FormQuestion(request.POST, request.FILES);
        if form.is_valid():
            question = form.save();
            formset = FormChoiceSet(request.POST, instance=question);
            if formset.is_valid():
                formset.save();
                messages.add_message(request, messages.SUCCESS, 'Опрос добавлен');
                return redirect('polls:profile');
    else:
        form = FormQuestion(initial={'author': request.user.pk});
        formset = FormChoiceSet();
    context = {'form': form, 'formset':formset};
    return render(request, 'polls/question/create.html',context);

# USER VIEWS

class PLoginView(LoginView):
    template_name = 'polls/user/login.html';
    next_page = 'polls:profile';

@login_required(login_url="polls:login")
def p_profile(request):
    questions = Question.objects.filter(author=request.user.pk);
    context = {"questions": questions};
    return render(request, "polls/user/profile.html", context);

@login_required(login_url="polls:login")
def p_profile_change(request):
    pass;

@login_required(login_url="polls:login")
def p_logout(request):
    logout(request);
    return redirect('/');

class PChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = PUser;
    template_name = 'polls/user/profile_change.html';
    form_class = FormChangeUserInfo;
    success_url = reverse_lazy('polls:profile');
    success_message = 'Личные данные полльзователя изменены';
    login_url = reverse_lazy('polls:login')


    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk;
        return super().dispatch(request, *args, **kwargs);
    
    def get_object(self, queryset = None):
        if not queryset:
            queryset = self.get_queryset();
        return get_object_or_404(queryset, pk=self.user_id);

class PPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'polls/user/password_change.html';
    success_url = reverse_lazy('polls:profile');
    success_message = 'Пароль изменен';
    login_url = reverse_lazy('polls:login')


class PRegisterDoneView(generic.base.TemplateView, LoginRequiredMixin):
    template_name = 'polls/user/register_user_success.html';
    login_url = reverse_lazy('polls:login')


class PRegisterUserView(CreateView):
    model = PUser;
    template_name = 'polls/user/register_user.html';
    form_class = FormRegisterUser;
    success_url = reverse_lazy('polls:register_done');
    
    # перепись сценария при регистрации пользователя
    
    def form_valid(self, form):
        # вызываем метод для сохранения пользователя с данными из формы
        user = form.save();
        """
        вызов родительского метода (сразу после сохранения), чтобы
        CreateView отработал.
        """
        response = super().form_valid(form);
        user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password1"]);
        # чтобы избежать ошибки в случае, если не удастся войти
        if user is not None:
            login(self.request, user);
        return response;
    
class PDeleteUserView(LoginRequiredMixin, DeleteView):
    model = PUser;
    template_name = 'polls/user/profile_delete.html'
    success_url = reverse_lazy('polls:index')
    login_url = reverse_lazy('polls:login')
    
    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, "Пользователь удален")
        return super().post(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)
