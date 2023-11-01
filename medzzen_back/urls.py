"""
URL configuration for medzzen_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from djoser import views as djoser_views
from rest_framework.routers import DefaultRouter

from accounts.views import UserViewSet
from companies.views import CompanyViewSet
from quizzes.views import QuizViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'company', CompanyViewSet)
router.register(r'quizzes', QuizViewSet)



urlpatterns = [
    path('auth/token/create/', djoser_views.TokenCreateView.as_view(), name='token-create'),
    path('auth/token/destroy/', djoser_views.TokenDestroyView.as_view(), name='token-destroy'),
    path('', include('health_check.urls')),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('auth/register/', UserViewSet.as_view({'post': 'create'}), name='user-create'),
    path('auth/password/reset/', UserViewSet.as_view({'post': 'password_reset'}), name='password-reset'),
    path('auth/password/reset/confirm/<str:uidb64>/<str:token>/', 
        UserViewSet.as_view({'post': 'password_reset_confirm'}), name='password-reset-confirm'),
]   
