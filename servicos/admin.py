from django.contrib import admin

from .models import Avaliacao, Desbloqueio, Mensagem, Notificacao, Servico, Solicitacao

admin.site.register(Servico)
admin.site.register(Solicitacao)
admin.site.register(Desbloqueio)
admin.site.register(Avaliacao)
admin.site.register(Mensagem)
admin.site.register(Notificacao)
