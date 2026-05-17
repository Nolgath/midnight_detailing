"""Email helpers."""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


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
