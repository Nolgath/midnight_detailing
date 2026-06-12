"""Views públicas — Midnight Detailing."""

import json
import logging
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from .emails import (
    send_marcacao_client_confirmation,
    send_pedido_contacto_notification,
)
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
    return render(request, 'core/home.html')


def services(request):
    return render(request, 'core/services.html')


GALLERY_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.avif'}


def sobre(request):
    """Página Sobre — descrição, galeria de trabalhos e redes sociais.

    A galeria lista as imagens em ``static/img/trabalho/``: para adicionar
    fotos basta colocar os ficheiros nessa pasta.
    """

    gallery_dir = settings.STATICFILES_DIRS[0] / 'img' / 'trabalho'
    fotos = []
    if gallery_dir.is_dir():
        fotos = sorted(
            f.name for f in gallery_dir.iterdir()
            if f.suffix.lower() in GALLERY_EXTENSIONS
        )
    return render(request, 'core/sobre.html', {'fotos': fotos})


def robots_txt(request):
    content = (
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /admin/\n'
        '\n'
        f'Sitemap: {settings.SITE_URL}/sitemap.xml\n'
    )
    return HttpResponse(content, content_type='text/plain')


def sitemap_xml(request):
    base = settings.SITE_URL
    pages = [
        ('/', '1.0', 'weekly'),
        ('/servicos/', '0.9', 'weekly'),
        ('/sobre/', '0.9', 'monthly'),
        ('/contacto/', '0.7', 'monthly'),
    ]
    urls = ''.join(
        f'<url><loc>{base}{path}</loc>'
        f'<changefreq>{freq}</changefreq><priority>{prio}</priority></url>'
        for path, prio, freq in pages
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'{urls}</urlset>'
    )
    return HttpResponse(xml, content_type='application/xml')


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
def agendar(request):
    """Recebe uma marcação (carrinho + data + contacto) e envia email à equipa."""

    try:
        data = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'error': 'Pedido inválido.'}, status=400)

    nome = (data.get('nome') or '').strip()
    telefone = (data.get('telefone') or '').strip()
    email = (data.get('email') or '').strip()
    zona = (data.get('zona') or '').strip()
    data_marcacao = (data.get('data') or '').strip()
    dia_semana = (data.get('dia_semana') or '').strip()
    periodo = (data.get('periodo') or '').strip()
    modo = (data.get('modo') or '').strip()
    segmento = (data.get('segmento') or '').strip()
    recolha = bool(data.get('recolha'))
    itens = data.get('itens') or []
    total = data.get('total')

    errors = {}
    if not nome:
        errors['nome'] = 'Indica o teu nome.'
    if not email:
        errors['email'] = 'Indica o teu email.'
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = 'Email inválido.'
    if not zona:
        errors['zona'] = 'Indica a tua zona.'
    if not data_marcacao:
        errors['data'] = 'Escolhe uma data.'
    if not isinstance(itens, list) or not itens:
        errors['itens'] = 'Seleciona pelo menos um serviço.'
    if errors:
        return JsonResponse({'ok': False, 'errors': errors}, status=400)

    data_fmt = data_marcacao
    try:
        data_fmt = datetime.strptime(data_marcacao, '%Y-%m-%d').strftime('%d/%m/%Y')
    except ValueError:
        pass
    dia_txt = f'{dia_semana} {data_fmt}'.strip()

    linhas = '\n'.join(
        '  • {} — {}€'.format(i.get('nome', '—'), i.get('preco', '?'))
        for i in itens
        if isinstance(i, dict)
    )

    body = (
        'Nova marcação pelo site:\n\n'
        f'Cliente: {nome}\n'
        f'Telemóvel: {telefone or "—"}\n'
        f'Email: {email}\n'
        f'Zona: {zona}\n'
        f'Recolha ao domicílio: {"Sim" if recolha else "Não"}\n\n'
        f'Data: {dia_txt}\n'
        f'Período: {periodo or "—"}\n'
        f'Modo: {modo or "—"}\n'
        f'Segmento: {segmento or "—"}\n\n'
        f'Serviços:\n{linhas}\n\n'
        f'TOTAL: {total}€\n'
    )

    # Assunto: apenas nome do cliente e o dia.
    subject = f'Marcação · {nome} · {dia_txt}'

    message = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.BOOKING_EMAIL],
        reply_to=[email],
    )
    try:
        message.send(fail_silently=False)
    except Exception:
        logger.exception('Falha ao enviar email de marcação')
        return JsonResponse(
            {'ok': False, 'error': 'Não foi possível enviar a marcação.'},
            status=500,
        )

    # Confirmação para o cliente — se falhar, a marcação continua válida
    # (a equipa já foi notificada), por isso não devolvemos erro.
    try:
        send_marcacao_client_confirmation({
            'nome': nome,
            'email': email,
            'zona': zona,
            'recolha': recolha,
            'dia_txt': dia_txt,
            'periodo': periodo,
            'itens': itens,
            'total': total,
        })
    except Exception:
        logger.exception('Falha ao enviar confirmação ao cliente (%s)', email)

    return JsonResponse({'ok': True})


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
