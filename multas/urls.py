from django.urls import path, re_path
from . import views
from .views import List, Listb, Detail, Delete, Delete1

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #path('api/multar/', views.api_multar, name='api_multar'),
    path('listc/', Listb.as_view(), name='list_c'),
    path('listb/', views.list_v, name='list_v'),
    path('logout_confirm/', views.logout_confirm, name='logout_confirm'),
    path('list/', List.as_view(), name='list'),
    path('list/<int:pk>/', Detail.as_view(), name='lista'),
    path('get/', views.get_view, name='get'),
    path('multar1/<int:pk>/', views.multar1, name='multar1'),  
    path('multar/<int:pk>/', views.multar, name='multar'),
    path('confirm/<int:pk>/', views.confirm, name='confirm'),
    path('confirm1/<int:pk>/', views.confirm1, name='confirm1'),
    path('delete/<int:pk>/', Delete.as_view(), name='apagar_multa'), 
    path('delete1/<int:pk>/', Delete1.as_view(), name='delete1'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('confirmar_multa/<int:pk>/', views.confirmar_multa, name="confirmar_multa"),    
    path('confirmar_multa1/<int:pk>/', views.confirmar_multa1, name='confirmar_multa1'),
    re_path(r'^.*$/', views.pagina_404),

    #path('api/multar/', api_multar, name='api_multar'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



#Josemar Neves

































#Josemar Neves
