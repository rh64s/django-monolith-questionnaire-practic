from django.urls import path;

from . import views;


app_name = 'polls';
urlpatterns = [
    # main page (all questions)
    path('', views.IndexView.as_view(), name='index'),
    
    # user
    path('account/login/', views.PLoginView.as_view(), name='login'),
    path('accout/profile/delete/', views.PDeleteUserView.as_view(), name="profile_delete"),
    path('account/profile/change_password/', views.PPasswordChangeView.as_view(), name='password_change'),
    path('account/profile/change/', views.PChangeUserInfoView.as_view(), name='profile_change'),
    path('account/profile/', views.p_profile, name='profile'),
    path('account/register/', views.PRegisterUserView.as_view(), name='register'),
    path('account/register/done/', views.PRegisterDoneView.as_view(), name='register_done'),
    path('account/logout/', views.p_logout, name='logout'),
    
    
    # question
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('question_create/', views.question_create, name='question_create'),
];