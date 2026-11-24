from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

Usuario = settings.AUTH_USER_MODEL


class Servico(models.Model):
    """Serviço de montagem divulgado por um montador."""

    CATEGORIAS = [
        ("armario", "Armários"),
        ("cama", "Camas"),
        ("guarda_roupa", "Guarda-roupas"),
        ("estante", "Estantes"),
        ("balcao", "Balcões"),
        ("cozinha", "Cozinhas completas"),
        ("outros", "Outros"),
    ]
    ICONES = {"armario": "🗄️", "cama": "🛏️", "guarda_roupa": "🚪", "estante": "📚", "balcao": "🍽️", "cozinha": "🍳", "outros": "🔧"}

    montador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="servicos", limit_choices_to={"tipo": "montador"})
    titulo = models.CharField("Título", max_length=120)
    categoria = models.CharField("Categoria", max_length=20, choices=CATEGORIAS, default="outros")
    descricao = models.TextField("Descrição")
    preco_base = models.DecimalField("Preço a partir de (R$)", max_digits=8, decimal_places=2)
    regiao = models.CharField("Região de atendimento", max_length=80, default="São Paulo")
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return self.titulo

    @property
    def icone(self):
        return self.ICONES.get(self.categoria, "🔧")


class Solicitacao(models.Model):
    """Pedido de montagem feito por um cliente.

    - Com montador escolhido ("Contratar agora"): nasce PENDENTE e aguarda o aceite.
    - Sem montador: nasce ABERTA e fica visível para os montadores.
    """

    ABERTA, PENDENTE, ACEITA, CONCLUIDA, CANCELADA, RECUSADA = "aberta", "pendente", "aceita", "concluida", "cancelada", "recusada"
    STATUS = [
        (ABERTA, "Aberta"),
        (PENDENTE, "Aguardando aceite"),
        (ACEITA, "Aceita"),
        (CONCLUIDA, "Concluída"),
        (CANCELADA, "Cancelada"),
        (RECUSADA, "Recusada"),
    ]

    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="solicitacoes")
    montador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="trabalhos")
    servico = models.ForeignKey(Servico, on_delete=models.SET_NULL, null=True, blank=True, related_name="solicitacoes")
    tipo_movel = models.CharField("Tipo de móvel", max_length=120)
    endereco = models.CharField("Endereço completo", max_length=255)
    cidade = models.CharField("Cidade/região", max_length=80, default="São Paulo")
    data = models.DateField("Data")
    horario = models.TimeField("Horário")
    observacoes = models.TextField("Observações", blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default=ABERTA)
    criado_em = models.DateTimeField(auto_now_add=True)
    concluida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "solicitação"
        verbose_name_plural = "solicitações"

    def __str__(self):
        return f"#{self.pk} {self.tipo_movel} – {self.get_status_display()}"

    @property
    def pode_cancelar(self):
        return self.status in (self.ABERTA, self.PENDENTE, self.ACEITA)


class Desbloqueio(models.Model):
    """Montador que gastou moedas para ver o contato do cliente de uma solicitação aberta."""

    montador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="desbloqueios")
    solicitacao = models.ForeignKey(Solicitacao, on_delete=models.CASCADE, related_name="desbloqueios")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("montador", "solicitacao")


class Avaliacao(models.Model):
    """Avaliação do montador feita pelo cliente após a conclusão do serviço."""

    solicitacao = models.OneToOneField(Solicitacao, on_delete=models.CASCADE, related_name="avaliacao")
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="avaliacoes_feitas")
    montador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="avaliacoes_recebidas")
    nota = models.PositiveSmallIntegerField("Nota", validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField("Comentário", blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "avaliação"
        verbose_name_plural = "avaliações"


class Mensagem(models.Model):
    """Mensagem do chat entre dois usuários."""

    remetente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="mensagens_enviadas")
    destinatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="mensagens_recebidas")
    texto = models.TextField()
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["criado_em"]


class Notificacao(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="notificacoes")
    texto = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "notificação"
        verbose_name_plural = "notificações"


def notificar(usuario, texto, url=""):
    Notificacao.objects.create(usuario=usuario, texto=texto[:255], url=url)
