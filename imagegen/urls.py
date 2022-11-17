"""imagegen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from imgen import views as imgen_views
from users import views as user_views


urlpatterns = [
    path('', imgen_views.home, name='home'),
    path('contact/', imgen_views.contact, name='contact'),
    path('imgen/', imgen_views.imgen, name='imgen'),
    path('imgen/download/', imgen_views.download_dataset, name='download'),
    path('library/', imgen_views.library, name='library'),

    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    # path('', include('datagen.urls')),

    path('profile/', user_views.profile, name='profile'),
    path('profile/<int:pk>/', user_views.delete_dataset, name='delete_dataset'),
    path('profile/download/<int:pk>/', user_views.download_dataset, name='download_dataset'),

    path('dataset/<int:pk>/', user_views.dataset, name='dataset'),
    path('dataset/create/', user_views.dataset_create, name='dataset-create'),
    path('dataset/generate-images/<int:pk>', user_views.generate_images, name='generate-images'),
    path('dataset/remove_obj/<int:pk>/<int:obj_pk>', user_views.remove_obj, name='remove_obj'),

    # path('test/', user_views.test, name='test'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
