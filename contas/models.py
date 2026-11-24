from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Avg
from django.utils import timezone

from .validators import validar_cpf


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _criar(self, email, password, **extra):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        usuario = self.model(email=self.normalize_email(email), **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._criar(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra["is_staff"] = True
        extra["is_superuser"] = True
        return self._criar(email, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Usuário da plataforma: cliente ou montador (o login é feito pelo e-mail)."""

    CLIENTE = "cliente"
    MONTADOR = "montador"
    TIPOS = [(CLIENTE, "Cliente"), (MONTADOR, "Montador")]

    nome_completo = models.CharField("Nome completo", max_length=150)
    email = models.EmailField("E-mail", unique=True)
    cpf = models.CharField("CPF", max_length=14, unique=True, validators=[validar_cpf])
    telefone = models.CharField("Telefone", max_length=20)
    tipo = models.CharField("Tipo de conta", max_length=10, choices=TIPOS, default=CLIENTE)
    cidade = models.CharField("Cidade/região", max_length=80, default="São Paulo")

    # Dados do perfil do montador
    sobre = models.TextField("Sobre", blank=True)
    area_atuacao = models.CharField("Área de atuação", max_length=200, blank=True)
    anos_experiencia = models.PositiveSmallIntegerField("Anos de experiência", default=0)

    # Sistema de moedas (usado pelo montador para ver o contato de clientes)
    moedas = models.PositiveIntegerField("Moedas", default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(default=timezone.now)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome_completo", "cpf", "telefone"]

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    def __str__(self):
        return f"{self.nome_completo} ({self.get_tipo_display()})"

    @property
    def eh_montador(self):
        return self.tipo == self.MONTADOR

    @property
    def nota_media(self):
        media = self.avaliacoes_recebidas.aggregate(m=Avg("nota"))["m"]
        return round(media, 1) if media else 0

    @property
    def nota_arredondada(self):
        return int(round(self.nota_media))

    @property
    def total_avaliacoes(self):
        return self.avaliacoes_recebidas.count()
