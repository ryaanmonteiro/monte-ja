def notificacoes(request):
    """Disponibiliza o total de notificações não lidas para a barra superior."""
    if request.user.is_authenticated:
        return {"nao_lidas": request.user.notificacoes.filter(lida=False).count()}
    return {"nao_lidas": 0}
