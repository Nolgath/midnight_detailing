"""Views públicas — Midnight Detailing."""

import logging

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from .emails import send_pedido_contacto_notification
from .forms import PedidoContactoForm
from .models import Pacote, Testemunho


logger = logging.getLogger(__name__)


def _pacotes_ativos():
    return (
        Pacote.objects
        .filter(ativo=True)
        .order_by('ordem')
        .prefetch_related('inclusoes')
    )


def _testemunhos_ativos(limit=6):
    return Testemunho.objects.filter(ativo=True)[:limit]


def home(request):
    return render(request, 'core/home.html', {
        'page_title': 'Início',
        'pacotes': _pacotes_ativos(),
        'testemunhos': _testemunhos_ativos(),
        'form': PedidoContactoForm(),
    })


def services(request):
    return render(request, 'core/services.html', {
        'page_title': 'Serviços',
        'pacotes': _pacotes_ativos(),
    })


@require_http_methods(['GET', 'POST'])
def contact(request):
    if request.method == 'POST':
        form = PedidoContactoForm(request.POST)
        if form.is_valid():
            if not form.is_spam():
                pedido = form.save()
                try:
                    send_pedido_contacto_notification(pedido)
                except Exception:
                    logger.exception(
                        'Falha ao enviar email do pedido #%s', pedido.pk,
                    )
                    messages.warning(
                        request,
                        'Recebemos a sua mensagem mas houve um problema a '
                        'notificar a equipa. Vamos verificar manualmente.',
                    )
            return redirect(reverse('core:contact_thanks'))
    else:
        form = PedidoContactoForm()

    return render(request, 'core/contact.html', {
        'page_title': 'Contacto',
        'form': form,
    })


def contact_thanks(request):
    return render(request, 'core/contact_thanks.html', {'page_title': 'Obrigado'})


@require_POST
def pedido_contacto(request):
    """AJAX endpoint — recebe o form e devolve JSON.

    O frontend pode submeter via ``fetch`` em vez de fazer redirect full-page.
    Devolve ``{ok: true}`` em sucesso e ``{ok: false, errors: {...}}`` se
    houver erros de validação.
    """

    form = PedidoContactoForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'ok': False, 'errors': form.errors}, status=400)

    if form.is_spam():
        return JsonResponse({'ok': True})

    pedido = form.save()
    try:
        send_pedido_contacto_notification(pedido)
    except Exception:
        logger.exception('Falha ao enviar email do pedido #%s', pedido.pk)
        return JsonResponse({'ok': True, 'email_warning': True})

    return JsonResponse({'ok': True})
