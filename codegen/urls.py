

from django.contrib import admin
from django.urls import path, include
from generator import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('projects/',views.projects, name='projects'),
    path('accounts/', include('accounts.urls')),
    path('generator/',include('generator.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
