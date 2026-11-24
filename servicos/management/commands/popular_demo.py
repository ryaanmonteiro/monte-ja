from django.core.management.base import BaseCommand

from contas.models import Usuario
from servicos.models import Servico

SENHA = "demo12345"


class Command(BaseCommand):
    help = "Cria usuários e serviços de demonstração (somente para desenvolvimento)."

    def handle(self, *args, **options):
        cliente, _ = self._usuario("cliente@demo.com", "Cliente Demo", "52998224725", "11999990001", Usuario.CLIENTE)
        m1, _ = self._usuario(
            "ryan@demo.com", "Ryan Monteiro", "11144477735", "11999990002", Usuario.MONTADOR,
            sobre="Montador profissional, 6+ anos de experiência, pontual e cuidadoso.",
            area_atuacao="Zona Sul e Centro, São Paulo - SP", anos_experiencia=6, moedas=5,
        )
        m2, _ = self._usuario(
            "marcelo@demo.com", "Marcelo Souto", "39053344705", "11999990003", Usuario.MONTADOR,
            sobre="Especialista em cozinhas planejadas e guarda-roupas.",
            area_atuacao="Zona Leste e Centro, São Paulo - SP", anos_experiencia=4, moedas=5,
        )
        itens = [
            (m1, "Armário completo da marca X", "armario", 180),
            (m1, "Estante da marca Y", "estante", 90),
            (m1, "Cama da marca Y", "cama", 100),
            (m2, "Guarda-roupa da marca X", "guarda_roupa", 220),
            (m2, "Balcão da marca X", "balcao", 120),
            (m2, "Cozinha completa", "cozinha", 450),
            (m2, "Cama infantil da marca X", "cama", 110),
        ]
        for montador, titulo, categoria, preco in itens:
            Servico.objects.get_or_create(
                montador=montador, titulo=titulo,
                defaults={"categoria": categoria, "preco_base": preco, "regiao": "São Paulo",
                          "descricao": f"Montagem de {titulo.lower()}, com ferramentas próprias e limpeza ao final."},
            )
        self.stdout.write(self.style.SUCCESS(
            f"Dados de demonstração criados. Logins: cliente@demo.com, ryan@demo.com, marcelo@demo.com (senha: {SENHA})"
        ))

    def _usuario(self, email, nome, cpf, tel, tipo, **extra):
        existente = Usuario.objects.filter(email=email).first()
        if existente:
            return existente, False
        u = Usuario.objects.create_user(email=email, password=SENHA, nome_completo=nome, cpf=cpf, telefone=tel, tipo=tipo, **extra)
        return u, True
