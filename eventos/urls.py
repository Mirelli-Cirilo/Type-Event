from django.urls import path

from . import views

urlpatterns = [
    path('novo_evento/', views.novo_evento, name='novo_evento'),
    path('gerenciar_evento/', views.gerenciar_evento, name='gerenciar_evento'),
    path('inscrever_evento/<int:pk>/', views.inscrever_evento, name='inscrever_evento'),
    path('listar_participantes/<int:pk>/', views.listar_participantes, name='listar_participantes'),
    path('gerar_csv/<int:pk>/', views.gerar_csv, name='gerar_csv'),
    path('certificado_evento/<int:pk>/', views.certificado_evento, name='certificado_evento'),
    path('gerar_certificado/<int:pk>/', views.gerar_certificado, name='gerar_certificado'),
    path('procurar_certificado/<int:pk>/', views.procurar_certificado, name="procurar_certificado")
]