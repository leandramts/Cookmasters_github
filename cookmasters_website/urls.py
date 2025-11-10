
from django.contrib import admin
from django.urls import path, include
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name = 'home'),
    path('usuarios/', include('usuarios.urls')),
    path('receitas/', include('receitas.urls'))
    

]
