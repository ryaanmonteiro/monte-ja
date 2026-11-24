from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AvaliacaoForm, ServicoForm, SolicitacaoForm
from .models import Avaliacao, Desbloqueio, Mensagem, Servico, Solicitacao, notificar

Usuario = get_user_model()
REGIAO_PADRAO = "São Paulo"


def montador_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.eh_montador:
            messages.error(request, "Área exclusiva para montadores.")
            return redirect("home")
        return view(request, *args, **kwargs)

    return login_required(wrapper)


def cliente_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.user.eh_montador:
            messages.error(request, "Esta ação é exclusiva para clientes.")
            return redirect("home")
        return view(request, *args, **kwargs)

    return login_required(wrapper)


# ---------------------------------------------------------------- Tela 1: Página Inicial
def home(request):
    q = request.GET.get("q", "").strip()
    if request.GET.get("regiao"):
        regiao = request.GET["regiao"].strip()
    elif request.user.is_authenticated:
        regiao = request.user.cidade
    else:
        regiao = REGIAO_PADRAO

    base = Servico.objects.filter(ativo=True).select_related("montador")
    if q:
        base = base.filter(
            Q(titulo__icontains=q)
            | Q(descricao__icontains=q)
            | Q(montador__nome_completo__icontains=q)
            | Q(categoria__in=[c for c, nome in Servico.CATEGORIAS if q.lower() in nome.lower()])
        )

    categorias = []
    for codigo, nome in Servico.CATEGORIAS:
        itens = list(base.filter(categoria=codigo)[:9])
        if itens:
            categorias.append((nome, itens))

    context = {
        "q": q,
        "regiao": regiao,
        "ultimos": base[:9],
        "da_regiao": base.filter(regiao__icontains=regiao)[:9],
        "categorias": categorias,
    }
    return render(request, "servicos/home.html", context)


def servico_detalhe(request, pk):
    servico = get_object_or_404(Servico.objects.select_related("montador"), pk=pk, ativo=True)
    return render(request, "servicos/servico_detalhe.html", {"servico": servico, "montador": servico.montador})


@montador_required
def servico_novo(request):
    form = ServicoForm(request.POST or None, initial={"regiao": request.user.cidade})
    if request.method == "POST" and form.is_valid():
        servico = form.save(commit=False)
        servico.montador = request.user
        servico.save()
        messages.success(request, "Serviço divulgado com sucesso!")
        return redirect("servicos:servico_detalhe", pk=servico.pk)
    return render(request, "servicos/servico_form.html", {"form": form})


# ---------------------------------------------------------------- Contratação
@cliente_required
def solicitar(request, montador_id=None):
    montador = get_object_or_404(Usuario, pk=montador_id, tipo=Usuario.MONTADOR) if montador_id else None
    servico = None
    if montador and request.GET.get("servico"):
        servico = Servico.objects.filter(pk=request.GET["servico"], montador=montador).first()

    initial = {"cidade": request.user.cidade}
    if servico:
        initial["tipo_movel"] = servico.titulo
    form = SolicitacaoForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        solicitacao = form.save(commit=False)
        solicitacao.cliente = request.user
        solicitacao.montador = montador
        solicitacao.servico = servico
        solicitacao.status = Solicitacao.PENDENTE if montador else Solicitacao.ABERTA
        solicitacao.save()
        if montador:
            notificar(
                montador,
                f"Novo pedido de {request.user.nome_completo}: {solicitacao.tipo_movel}",
                reverse("servicos:minhas_solicitacoes"),
            )
            messages.success(request, "Pedido enviado! Aguarde o aceite do montador.")
        else:
            messages.success(request, "Solicitação publicada! Os montadores já podem vê-la.")
        return redirect("servicos:minhas_solicitacoes")
    return render(request, "servicos/solicitar.html", {"form": form, "montador": montador})


@login_required
def minhas_solicitacoes(request):
    if request.user.eh_montador:
        lista = request.user.trabalhos.select_related("cliente")
    else:
        lista = request.user.solicitacoes.select_related("montador")
    pendentes_avaliacao = set()
    if not request.user.eh_montador:
        pendentes_avaliacao = set(
            lista.filter(status=Solicitacao.CONCLUIDA, avaliacao__isnull=True).values_list("pk", flat=True)
        )
    return render(request, "servicos/minhas_solicitacoes.html", {"solicitacoes": lista, "pendentes_avaliacao": pendentes_avaliacao})


@montador_required
def disponiveis(request):
    """Solicitações abertas. O contato do cliente só é liberado gastando moedas."""
    abertas = Solicitacao.objects.filter(status=Solicitacao.ABERTA).select_related("cliente")
    if not request.GET.get("todas"):
        abertas = abertas.filter(cidade__icontains=request.user.cidade)
    liberadas = set(request.user.desbloqueios.values_list("solicitacao_id", flat=True))
    context = {
        "solicitacoes": abertas,
        "liberadas": liberadas,
        "custo": settings.CUSTO_DESBLOQUEIO_CONTATO,
        "todas": bool(request.GET.get("todas")),
    }
    return render(request, "servicos/disponiveis.html", context)


@montador_required
@require_POST
def desbloquear(request, pk):
    solicitacao = get_object_or_404(Solicitacao, pk=pk, status=Solicitacao.ABERTA)
    custo = settings.CUSTO_DESBLOQUEIO_CONTATO
    try:
        with transaction.atomic():
            if Desbloqueio.objects.filter(montador=request.user, solicitacao=solicitacao).exists():
                messages.info(request, "Você já liberou este contato.")
                return redirect("servicos:disponiveis")
            gastou = Usuario.objects.filter(pk=request.user.pk, moedas__gte=custo).update(moedas=F("moedas") - custo)
            if not gastou:
                messages.error(request, "Moedas insuficientes. Adicione moedas para ver o contato do cliente.")
                return redirect("servicos:disponiveis")
            Desbloqueio.objects.create(montador=request.user, solicitacao=solicitacao)
    except IntegrityError:
        messages.info(request, "Você já liberou este contato.")
        return redirect("servicos:disponiveis")
    messages.success(request, f"Contato liberado! {custo} moeda(s) utilizada(s).")
    return redirect("servicos:disponiveis")


@montador_required
@require_POST
def aceitar(request, pk):
    solicitacao = get_object_or_404(Solicitacao, pk=pk)
    if solicitacao.status == Solicitacao.PENDENTE and solicitacao.montador_id == request.user.pk:
        atualizadas = Solicitacao.objects.filter(pk=pk, status=Solicitacao.PENDENTE, montador=request.user).update(status=Solicitacao.ACEITA)
    elif solicitacao.status == Solicitacao.ABERTA:
        if not Desbloqueio.objects.filter(montador=request.user, solicitacao=solicitacao).exists():
            messages.error(request, "Libere o contato do cliente (com moedas) antes de aceitar.")
            return redirect("servicos:disponiveis")
        atualizadas = Solicitacao.objects.filter(pk=pk, status=Solicitacao.ABERTA).update(status=Solicitacao.ACEITA, montador=request.user)
    else:
        atualizadas = 0
    if atualizadas:
        notificar(solicitacao.cliente, f"{request.user.nome_completo} aceitou seu pedido: {solicitacao.tipo_movel}", reverse("servicos:minhas_solicitacoes"))
        messages.success(request, "Serviço aceito! Combine os detalhes com o cliente pelo chat.")
    else:
        messages.error(request, "Não foi possível aceitar: o pedido não está mais disponível.")
    return redirect("servicos:minhas_solicitacoes")


@montador_required
@require_POST
def recusar(request, pk):
    atualizadas = Solicitacao.objects.filter(pk=pk, status=Solicitacao.PENDENTE, montador=request.user).update(status=Solicitacao.RECUSADA)
    if atualizadas:
        solicitacao = Solicitacao.objects.get(pk=pk)
        notificar(solicitacao.cliente, f"{request.user.nome_completo} recusou seu pedido: {solicitacao.tipo_movel}", reverse("servicos:minhas_solicitacoes"))
        messages.info(request, "Pedido recusado.")
    else:
        messages.error(request, "Não foi possível recusar este pedido.")
    return redirect("servicos:minhas_solicitacoes")


@montador_required
@require_POST
def concluir(request, pk):
    atualizadas = Solicitacao.objects.filter(pk=pk, status=Solicitacao.ACEITA, montador=request.user).update(
        status=Solicitacao.CONCLUIDA, concluida_em=timezone.now()
    )
    if atualizadas:
        solicitacao = Solicitacao.objects.get(pk=pk)
        notificar(solicitacao.cliente, "Serviço concluído! Avalie o profissional.", reverse("servicos:avaliar", args=[pk]))
        messages.success(request, "Serviço marcado como concluído.")
    else:
        messages.error(request, "Não foi possível concluir este serviço.")
    return redirect("servicos:minhas_solicitacoes")


@login_required
@require_POST
def cancelar(request, pk):
    solicitacao = get_object_or_404(Solicitacao, pk=pk)
    if request.user.pk not in (solicitacao.cliente_id, solicitacao.montador_id):
        messages.error(request, "Você não pode cancelar este pedido.")
        return redirect("servicos:minhas_solicitacoes")
    if not solicitacao.pode_cancelar:
        messages.error(request, "Este pedido não pode mais ser cancelado.")
        return redirect("servicos:minhas_solicitacoes")
    solicitacao.status = Solicitacao.CANCELADA
    solicitacao.save(update_fields=["status"])
    outro = solicitacao.montador if request.user.pk == solicitacao.cliente_id else solicitacao.cliente
    if outro:
        notificar(outro, f"{request.user.nome_completo} cancelou o pedido: {solicitacao.tipo_movel}", reverse("servicos:minhas_solicitacoes"))
    messages.info(request, "Pedido cancelado.")
    return redirect("servicos:minhas_solicitacoes")


# ---------------------------------------------------------------- Tela 5: Avaliação
def avaliacoes(request, montador_id):
    montador = get_object_or_404(Usuario, pk=montador_id, tipo=Usuario.MONTADOR)
    pendente = None
    if request.user.is_authenticated and not request.user.eh_montador:
        pendente = Solicitacao.objects.filter(
            cliente=request.user, montador=montador, status=Solicitacao.CONCLUIDA, avaliacao__isnull=True
        ).first()
    context = {
        "montador": montador,
        "lista": montador.avaliacoes_recebidas.select_related("cliente"),
        "pendente": pendente,
    }
    return render(request, "servicos/avaliacoes.html", context)


@cliente_required
def avaliar(request, solicitacao_id):
    solicitacao = get_object_or_404(Solicitacao, pk=solicitacao_id, cliente=request.user, status=Solicitacao.CONCLUIDA)
    if hasattr(solicitacao, "avaliacao"):
        messages.info(request, "Este serviço já foi avaliado.")
        return redirect("servicos:avaliacoes", montador_id=solicitacao.montador_id)
    form = AvaliacaoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        avaliacao = form.save(commit=False)
        avaliacao.solicitacao = solicitacao
        avaliacao.cliente = request.user
        avaliacao.montador = solicitacao.montador
        avaliacao.save()
        notificar(solicitacao.montador, f"{request.user.nome_completo} avaliou seu serviço com {avaliacao.nota} estrela(s).", reverse("servicos:avaliacoes", args=[solicitacao.montador_id]))
        messages.success(request, "Obrigado pela sua avaliação!")
        return redirect("servicos:avaliacoes", montador_id=solicitacao.montador_id)
    return render(request, "servicos/avaliar.html", {"form": form, "solicitacao": solicitacao, "montador": solicitacao.montador})


# ---------------------------------------------------------------- Chat e notificações
@login_required
def conversas(request):
    u = request.user
    ids = set(Mensagem.objects.filter(remetente=u).values_list("destinatario_id", flat=True))
    ids |= set(Mensagem.objects.filter(destinatario=u).values_list("remetente_id", flat=True))
    return render(request, "servicos/conversas.html", {"contatos": Usuario.objects.filter(pk__in=ids)})


@login_required
def conversa(request, usuario_id):
    outro = get_object_or_404(Usuario, pk=usuario_id)
    if outro.pk == request.user.pk:
        return redirect("servicos:conversas")
    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        if texto:
            Mensagem.objects.create(remetente=request.user, destinatario=outro, texto=texto)
            notificar(outro, f"Nova mensagem de {request.user.nome_completo}", reverse("servicos:conversa", args=[request.user.pk]))
        return redirect("servicos:conversa", usuario_id=outro.pk)
    Mensagem.objects.filter(remetente=outro, destinatario=request.user, lida=False).update(lida=True)
    mensagens = Mensagem.objects.filter(
        Q(remetente=request.user, destinatario=outro) | Q(remetente=outro, destinatario=request.user)
    )
    return render(request, "servicos/conversa.html", {"outro": outro, "mensagens": mensagens})


@login_required
def notificacoes(request):
    lista = list(request.user.notificacoes.all()[:50])
    request.user.notificacoes.filter(lida=False).update(lida=True)
    return render(request, "servicos/notificacoes.html", {"lista": lista})
