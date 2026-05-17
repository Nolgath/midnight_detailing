"""Testes para o site público."""

import json

from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import InclusaoPacote, Pacote, PedidoContacto, Testemunho


VALID_PAYLOAD = {
    'nome': 'João Teste',
    'email': 'joao@example.com',
    'telefone': '912 345 678',
    'viatura': 'BMW M3 2020',
    'pacote_interesse': 'signature',
    'mensagem': 'Olá, queria detalhe completo do meu carro.',
}


class HomeContextTests(TestCase):
    def test_home_passes_pacotes_e_testemunhos(self):
        p_ativo = Pacote.objects.create(
            tier='signature', nome='Signature',
            descricao_curta='X', preco_desde='desde 180€', ordem=1, ativo=True,
        )
        Pacote.objects.create(
            tier='essential', nome='Essential',
            descricao_curta='Y', preco_desde='desde 80€', ordem=99, ativo=False,
        )
        Testemunho.objects.create(nome='A', viatura='Porsche 911', texto='top', ativo=True)
        Testemunho.objects.create(nome='B', viatura='Bugatti', texto='nope', ativo=False)

        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

        pacotes = list(response.context['pacotes'])
        self.assertEqual(pacotes, [p_ativo])

        testemunhos = list(response.context['testemunhos'])
        self.assertEqual({t.nome for t in testemunhos}, {'A'})

        self.assertIn('form', response.context)


class ContactFormFlowTests(TestCase):
    def test_get_contact_page_renders_form(self):
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        fields = response.context['form'].fields
        for name in ('nome', 'email', 'telefone', 'viatura',
                     'pacote_interesse', 'mensagem', 'website'):
            self.assertIn(name, fields, name)

    def test_valid_submission_saves_and_sends_email(self):
        response = self.client.post(reverse('core:contact'), VALID_PAYLOAD)
        self.assertRedirects(response, reverse('core:contact_thanks'))

        self.assertEqual(PedidoContacto.objects.count(), 1)
        pedido = PedidoContacto.objects.get()
        self.assertEqual(pedido.nome, 'João Teste')
        self.assertEqual(pedido.email, 'joao@example.com')
        self.assertEqual(pedido.telefone, '912345678')
        self.assertEqual(pedido.viatura, 'BMW M3 2020')
        self.assertEqual(pedido.pacote_interesse, 'signature')
        self.assertFalse(pedido.contactado)

        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertIn('Midnight Detailing', msg.subject)
        self.assertIn('João Teste', msg.body)
        self.assertIn('BMW M3 2020', msg.body)
        self.assertIn('Signature', msg.body)
        self.assertEqual(msg.reply_to, ['joao@example.com'])

    def test_telefone_pt_aceita_varios_formatos(self):
        for raw, expected in [
            ('912345678', '912345678'),
            ('912 345 678', '912345678'),
            ('+351 912 345 678', '912345678'),
            ('00351 912345678', '912345678'),
            ('218 765 432', '218765432'),
        ]:
            with self.subTest(raw=raw):
                PedidoContacto.objects.all().delete()
                response = self.client.post(reverse('core:contact'), {
                    **VALID_PAYLOAD, 'telefone': raw,
                })
                self.assertRedirects(response, reverse('core:contact_thanks'))
                self.assertEqual(
                    PedidoContacto.objects.get().telefone, expected,
                )

    def test_telefone_invalido_e_rejeitado(self):
        for bad in ['123456789', '812345678', '91234567', 'abc', '']:
            with self.subTest(bad=bad):
                response = self.client.post(reverse('core:contact'), {
                    **VALID_PAYLOAD, 'telefone': bad,
                })
                self.assertEqual(response.status_code, 200)
                self.assertIn('telefone', response.context['form'].errors)

    def test_email_invalido_e_rejeitado(self):
        response = self.client.post(reverse('core:contact'), {
            **VALID_PAYLOAD, 'email': 'nao-e-email',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)

    def test_honeypot_descarta_silenciosamente(self):
        response = self.client.post(reverse('core:contact'), {
            **VALID_PAYLOAD, 'website': 'http://spam.com',
        })
        self.assertRedirects(response, reverse('core:contact_thanks'))
        self.assertEqual(PedidoContacto.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)


class PedidoContactoAjaxTests(TestCase):
    url = '/api/pedido-contacto/'

    def test_ajax_success_returns_json_ok(self):
        response = self.client.post(self.url, VALID_PAYLOAD)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'ok': True})
        self.assertEqual(PedidoContacto.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_ajax_validation_error_returns_json_with_errors(self):
        response = self.client.post(self.url, {
            **VALID_PAYLOAD, 'email': 'nao-e-email', 'telefone': 'abc',
        })
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['ok'])
        self.assertIn('email', data['errors'])
        self.assertIn('telefone', data['errors'])

    def test_ajax_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_ajax_honeypot_returns_ok_without_saving(self):
        response = self.client.post(self.url, {
            **VALID_PAYLOAD, 'website': 'http://spam.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'ok': True})
        self.assertEqual(PedidoContacto.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)


class SeedDataCommandTests(TestCase):
    def test_seed_data_creates_expected_records(self):
        call_command('seed_data')

        self.assertEqual(Pacote.objects.count(), 3)
        tiers = set(Pacote.objects.values_list('tier', flat=True))
        self.assertEqual(tiers, {'essential', 'signature', 'midnight'})
        self.assertEqual(Pacote.objects.filter(destaque=True).count(), 1)
        self.assertEqual(
            Pacote.objects.get(tier='signature').destaque, True,
        )
        self.assertEqual(InclusaoPacote.objects.count(), 5 + 6 + 6)
        self.assertEqual(Testemunho.objects.count(), 3)

    def test_seed_data_is_idempotent(self):
        call_command('seed_data')
        call_command('seed_data')
        self.assertEqual(Pacote.objects.count(), 3)
        self.assertEqual(InclusaoPacote.objects.count(), 5 + 6 + 6)
        self.assertEqual(Testemunho.objects.count(), 3)
