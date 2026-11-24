from django.urls import path

from . import views

app_name = "servicos"

urlpatterns = [
    path("servico/novo/", views.servico_novo, name="servico_novo"),
    path("servico/<int:pk>/", views.servico_detalhe, name="servico_detalhe"),
    path("solicitar/", views.solicitar, name="solicitar"),
    path("contratar/<int:montador_id>/", views.solicitar, name="contratar"),
    path("pedidos/", views.minhas_solicitacoes, name="minhas_solicitacoes"),
    path("disponiveis/", views.disponiveis, name="disponiveis"),
    path("solicitacao/<int:pk>/desbloquear/", views.desbloquear, name="desbloquear"),
    path("solicitacao/<int:pk>/aceitar/", views.aceitar, name="aceitar"),
    path("solicitacao/<int:pk>/recusar/", views.recusar, name="recusar"),
    path("solicitacao/<int:pk>/concluir/", views.concluir, name="concluir"),
    path("solicitacao/<int:pk>/cancelar/", views.cancelar, name="cancelar"),
    path("avaliacoes/<int:montador_id>/", views.avaliacoes, name="avaliacoes"),
    path("avaliar/<int:solicitacao_id>/", views.avaliar, name="avaliar"),
    path("chat/", views.conversas, name="conversas"),
    path("chat/<int:usuario_id>/", views.conversa, name="conversa"),
    path("notificacoes/", views.notificacoes, name="notificacoes"),
]
