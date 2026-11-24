# Monte Já – Plataforma web de conexão entre clientes e montadores de móveis

Projeto Integrador II – Fatec Zona Sul "Dom Paulo Evaristo Arns" – Análise e Desenvolvimento de Sistemas (2º semestre de 2026).

**Integrantes:** Marcelo Gabriel Barbosa Souto · Ryan dos Santos Monteiro · Vitória Cauchioli

## O que é
Plataforma que conecta clientes que precisam montar móveis a montadores autônomos: busca de serviços, perfil do profissional, contratação, chat, notificações, avaliações e um sistema de moedas para o montador liberar o contato de novos clientes.

## Tecnologias
Python 3 · Django 5 · HTML/CSS (templates Django) · SQLite (padrão) ou PostgreSQL/MySQL · Git/GitHub

## Como rodar
```bash
python -m venv venv
# Windows: venv\Scripts\activate      Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations contas servicos
python manage.py migrate
python manage.py popular_demo        # (opcional) cria dados de demonstração
python manage.py runserver
```
Acesse http://127.0.0.1:8000/ — administração em `/admin/` (crie com `python manage.py createsuperuser`; informe o CPF só com números).

Contas de demonstração (após `popular_demo`, senha `demo12345`): `cliente@demo.com`, `ryan@demo.com`, `marcelo@demo.com`.

### Usar PostgreSQL ou MySQL
Defina as variáveis de ambiente `DB_ENGINE` (`postgres` ou `mysql`), `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, instale o driver (`psycopg2-binary` ou `mysqlclient`) e rode `migrate` novamente. Nunca grave senhas no código.

## Telas
| # | Tela | URL |
|---|------|-----|
| 1 | Página Inicial | `/` |
| 2 | Login | `/contas/login/` |
| 3 | Cadastro | `/contas/cadastro/` |
| 4 | Perfil do Montador | `/contas/montador/<id>/` |
| 5 | Avaliação | `/avaliacoes/<id>/` e `/avaliar/<pedido>/` |

Telas de apoio: detalhe do serviço, divulgar serviço, pedir/contratar montagem, meus pedidos, solicitações disponíveis (montador), chat, notificações e editar perfil.

## Estrutura
- `montaja/` – configurações e rotas do projeto
- `contas/` – usuário (cliente/montador), cadastro, login, perfil, moedas
- `servicos/` – serviços, solicitações, avaliações, chat, notificações
- `templates/` e `static/` – HTML e CSS

## Sistema de moedas
Montadores novos recebem moedas de boas-vindas. Para ver o contato/endereço de uma solicitação aberta é preciso gastar moedas; depois disso é possível aceitar o serviço. Pedidos enviados diretamente a um montador ("Contratar agora") não gastam moedas. A compra de moedas é **simulada** (sem pagamento real).
