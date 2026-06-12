"""Email helpers."""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_marcacao_client_confirmation(ctx):
    """Envia ao cliente a confirmação de receção da marcação (HTML + texto)."""

    linhas = '\n'.join(
        '  • {} — {}€'.format(i.get('nome', '—'), i.get('preco', '?'))
        for i in ctx['itens']
        if isinstance(i, dict)
    )
    text_body = (
        f'Olá {ctx["nome"]},\n\n'
        'Recebemos a tua marcação. Vamos entrar em contacto para '
        'confirmar os detalhes.\n\n'
        f'Data: {ctx["dia_txt"]}\n'
        f'Período: {ctx["periodo"] or "—"}\n'
        f'Zona: {ctx["zona"]}\n'
        f'Recolha ao domicílio: {"Sim" if ctx["recolha"] else "Não"}\n\n'
        f'Serviços:\n{linhas}\n\n'
        f'TOTAL: {ctx["total"]}€\n\n'
        'Esta marcação só fica confirmada após o nosso contacto.\n'
        '— Midnight Detailing\n'
    )
    html_body = render_to_string('core/emails/marcacao_cliente.html', ctx)

    message = EmailMultiAlternatives(
        subject='Marcação recebida · Midnight Detailing',
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[ctx['email']],
        reply_to=[settings.BOOKING_EMAIL],
    )
    message.attach_alternative(html_body, 'text/html')
    message.send(fail_silently=False)


def send_pedido_contacto_notification(pedido):
    tier_label = dict(pedido._meta.get_field('pacote_interesse').choices).get(
        pedido.pacote_interesse, '—',
    )

    subject = f'[Midnight Detailing] Novo pedido de {pedido.nome}'

    body = (
        'Recebeu um novo pedido pelo site:\n\n'
        f'Nome: {pedido.nome}\n'
        f'Email: {pedido.email}\n'
        f'Telefone: {pedido.telefone}\n'
        f'Viatura: {pedido.viatura or "—"}\n'
        f'Pacote de interesse: {tier_label if pedido.pacote_interesse else "—"}\n\n'
        f'Mensagem:\n{pedido.mensagem or "(sem mensagem)"}\n\n'
        f'— Recebido a {pedido.criado_em:%Y-%m-%d %H:%M}\n'
    )

    message = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_EMAIL],
        reply_to=[pedido.email],
    )
    message.send(fail_silently=False)
