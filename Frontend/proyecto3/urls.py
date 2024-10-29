from django.urls import path
from . import views


urlpatterns = [ 
    path('', views.index, name='index'),
    path('configurar/', views.configurar, name='configurar'),
    path('visualizarXML/', views.visualizarXML, name='visualizarXML'),
    path('subirXML/', views.subirXML, name='subirXML'),
    path('generarResultados/', views.generarResultados, name='generarResultados'),
]