"""Popula a base de dados com pacotes e testemunhos iniciais.

Uso:
    python manage.py seed_data           # idempotente: cria/actualiza
    python manage.py seed_data --reset   # apaga tudo e recria do zero
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import InclusaoPacote, Pacote, Testemunho


PACOTES = [
    {
        'tier': 'essential',
        'nome': 'Essential',
        'descricao_curta': 'A base do detailing de qualidade — para quem quer o carro impecável no dia-a-dia.',
        'preco_desde': 'desde 80€',
        'destaque': False,
        'ordem': 1,
        'inclusoes': [
            'Lavagem manual exterior detalhada',
            'Descontaminação química',
            'Aspiração e limpeza interior completa',
            'Limpeza e tratamento de vidros',
            'Dressing de plásticos exteriores',
        ],
    },
    {
        'tier': 'signature',
        'nome': 'Signature',
        'descricao_curta': 'O equilíbrio perfeito entre proteção e brilho — o nosso pacote mais procurado.',
        'preco_desde': 'desde 180€',
        'destaque': True,
        'ordem': 2,
        'inclusoes': [
            'Tudo o que inclui Essential',
            'Descontaminação física com clay bar',
            'Polimento de manutenção',
            'Selante de cera de longa duração',
            'Higienização profunda de interior',
            'Tratamento de couro / estofos',
        ],
    },
    {
        'tier': 'midnight',
        'nome': 'Midnight',
        'descricao_curta': 'A experiência flagship — correção de pintura, proteção cerâmica e atenção total ao detalhe.',
        'preco_desde': 'Sob consulta',
        'destaque': False,
        'ordem': 3,
        'inclusoes': [
            'Tudo o que inclui Signature',
            'Correção de pintura em 1 a 3 fases',
            'Proteção cerâmica certificada',
            'Higienização com ozono',
            'Restauro de faróis',
            'Avaliação personalizada antes de cada serviço',
        ],
    },
]

TESTEMUNHOS = [
    {
        'nome': 'Carlos M.',
        'viatura': 'Porsche 911',
        'texto': 'Um nível de detalhe que não encontrei em mais nenhum sítio em Lisboa.',
        'avaliacao': 5,
    },
    {
        'nome': 'Sofia R.',
        'viatura': 'BMW M3 Competition',
        'texto': 'Recebi o carro como se tivesse acabado de sair do stand. Profissionalismo absoluto.',
        'avaliacao': 5,
    },
    {
        'nome': 'André P.',
        'viatura': 'Mercedes-AMG GT',
        'texto': 'Atenção ao pormenor incomparável. Já fidelizado.',
        'avaliacao': 5,
    },
]


class Command(BaseCommand):
    help = 'Popula pacotes e testemunhos iniciais.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Apaga pacotes/inclusões/testemunhos antes de criar.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            InclusaoPacote.objects.all().delete()
            Pacote.objects.all().delete()
            Testemunho.objects.all().delete()
            self.stdout.write(self.style.WARNING('Dados anteriores removidos.'))

        for spec in PACOTES:
            defaults = {k: v for k, v in spec.items() if k not in ('tier', 'inclusoes')}
            inclusoes = spec['inclusoes']
            pacote, created = Pacote.objects.update_or_create(
                tier=spec['tier'],
                defaults=defaults,
            )
            pacote.inclusoes.all().delete()
            for ordem, descricao in enumerate(inclusoes, start=1):
                InclusaoPacote.objects.create(
                    pacote=pacote, descricao=descricao, ordem=ordem,
                )
            verb = 'criado' if created else 'actualizado'
            self.stdout.write(self.style.SUCCESS(
                f'Pacote {pacote.nome} {verb} ({len(inclusoes)} inclusões).'
            ))

        for spec in TESTEMUNHOS:
            t, created = Testemunho.objects.update_or_create(
                nome=spec['nome'], viatura=spec['viatura'],
                defaults={
                    'texto': spec['texto'],
                    'avaliacao': spec['avaliacao'],
                    'ativo': True,
                },
            )
            verb = 'criado' if created else 'actualizado'
            self.stdout.write(self.style.SUCCESS(
                f'Testemunho de {t.nome} {verb}.'
            ))

        self.stdout.write(self.style.SUCCESS('Seed concluído.'))
