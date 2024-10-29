from django.urls import path
from . import views


urlpatterns = [ 
    path('', views.index, name='index'),
    path('configurar/', views.configurar, name='configurar'),
    path('visualizarXML/', views.visualizarXML, name='visualizarXML'),
    path('subirXML/', views.subirXML, name='subirXML'),
    path('generarResultados/', views.generarResultados, name='generarResultados'),


    path('configurar2/', views.configurar2, name='configurar2'),
    path('visualizarXML2/', views.visualizarXML2, name='visualizarXML2'),
    path('subirXML2/', views.subirXML2, name='subirXML2'),
    path('generarResultados2/', views.generarResultados2, name='generarResultados2'),
]