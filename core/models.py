"""Models de domínio — Midnight Detailing."""

from django.db import models


class Pacote(models.Model):
    """Pacotes de serviço em tiers: Essential, Signature, Midnight."""

    TIER_CHOICES = [
        ('essential', 'Essential'),
        ('signature', 'Signature'),
        ('midnight', 'Midnight'),
    ]

    tier = models.CharField('tier', max_length=20, choices=TIER_CHOICES, unique=True)
    nome = models.CharField('nome', max_length=100)
    descricao_curta = models.CharField('descrição curta', max_length=200)
    preco_desde = models.CharField(
        'preço desde', max_length=50,
        help_text="ex.: 'desde 80€' ou 'Sob consulta'",
    )
    destaque = models.BooleanField(
        'destaque', default=False,
        help_text="Marca como 'Mais popular' / flagship.",
    )
    ordem = models.PositiveIntegerField('ordem', default=0)
    ativo = models.BooleanField('activo', default=True)

    class Meta:
        verbose_name = 'pacote'
        verbose_name_plural = 'pacotes'
        ordering = ('ordem', 'tier')

    def __str__(self):
        return self.nome


class InclusaoPacote(models.Model):
    """Itens incluídos em cada pacote."""

    pacote = models.ForeignKey(
        Pacote, related_name='inclusoes', on_delete=models.CASCADE,
        verbose_name='pacote',
    )
    descricao = models.CharField('descrição', max_length=200)
    ordem = models.PositiveIntegerField('ordem', default=0)

    class Meta:
        verbose_name = 'inclusão'
        verbose_name_plural = 'inclusões'
        ordering = ('ordem', 'id')

    def __str__(self):
        return self.descricao


class Testemunho(models.Model):
    nome = models.CharField('nome', max_length=100)
    viatura = models.CharField(
        'viatura', max_length=100, blank=True,
        help_text="ex.: 'Porsche 911'",
    )
    texto = models.TextField('testemunho')
    avaliacao = models.PositiveSmallIntegerField(
        'avaliação', default=5,
        choices=[(i, f'{i} / 5') for i in range(1, 6)],
    )
    ativo = models.BooleanField('activo', default=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'testemunho'
        verbose_name_plural = 'testemunhos'
        ordering = ('-criado_em',)

    def __str__(self):
        return f'{self.nome} ({self.avaliacao}/5)'


class PedidoContacto(models.Model):
    nome = models.CharField('nome', max_length=100)
    email = models.EmailField('email')
    telefone = models.CharField('telefone', max_length=20)
    viatura = models.CharField('viatura', max_length=100, blank=True)
    pacote_interesse = models.CharField(
        'pacote de interesse', max_length=20,
        choices=Pacote.TIER_CHOICES, blank=True,
    )
    mensagem = models.TextField('mensagem', blank=True)
    criado_em = models.DateTimeField('recebido em', auto_now_add=True)
    contactado = models.BooleanField('contactado', default=False)

    class Meta:
        verbose_name = 'pedido de contacto'
        verbose_name_plural = 'pedidos de contacto'
        ordering = ('-criado_em',)

    def __str__(self):
        return f'{self.nome} — {self.criado_em:%Y-%m-%d %H:%M}'
