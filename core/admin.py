"""Django admin — Midnight Detailing (PT)."""

from django.contrib import admin

from .models import InclusaoPacote, Pacote, PedidoContacto, Testemunho


admin.site.site_header = 'Midnight Detailing — Gestão'
admin.site.site_title = 'Midnight Detailing'
admin.site.index_title = 'Gestão de conteúdo'


class InclusaoPacoteInline(admin.TabularInline):
    model = InclusaoPacote
    extra = 1
    fields = ('descricao', 'ordem')


@admin.register(Pacote)
class PacoteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tier', 'preco_desde', 'destaque', 'ordem', 'ativo')
    list_editable = ('destaque', 'ordem', 'ativo')
    list_filter = ('ativo', 'destaque', 'tier')
    search_fields = ('nome', 'descricao_curta')
    inlines = [InclusaoPacoteInline]
    fieldsets = (
        (None, {
            'fields': ('tier', 'nome', 'descricao_curta', 'preco_desde'),
        }),
        ('Apresentação', {
            'fields': ('destaque', 'ordem', 'ativo'),
        }),
    )


@admin.register(Testemunho)
class TestemunhoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'viatura', 'avaliacao', 'ativo', 'criado_em')
    list_editable = ('ativo',)
    list_filter = ('ativo', 'avaliacao')
    search_fields = ('nome', 'viatura', 'texto')
    readonly_fields = ('criado_em',)


@admin.register(PedidoContacto)
class PedidoContactoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'pacote_interesse', 'criado_em', 'contactado')
    list_editable = ('contactado',)
    list_filter = ('contactado', 'pacote_interesse', 'criado_em')
    search_fields = ('nome', 'email', 'telefone', 'viatura', 'mensagem')
    readonly_fields = ('nome', 'email', 'telefone', 'viatura', 'pacote_interesse', 'mensagem', 'criado_em')
    date_hierarchy = 'criado_em'
    list_per_page = 50
    ordering = ('-criado_em',)
    fieldsets = (
        ('Cliente', {
            'fields': ('nome', 'email', 'telefone', 'viatura'),
        }),
        ('Pedido', {
            'fields': ('pacote_interesse', 'mensagem', 'criado_em'),
        }),
        ('Gestão interna', {
            'fields': ('contactado',),
        }),
    )

    actions = ('marcar_contactado', 'marcar_por_contactar')

    @admin.action(description='Marcar como contactado')
    def marcar_contactado(self, request, queryset):
        n = queryset.update(contactado=True)
        self.message_user(request, f'{n} pedido(s) marcado(s) como contactado(s).')

    @admin.action(description='Marcar como por contactar')
    def marcar_por_contactar(self, request, queryset):
        n = queryset.update(contactado=False)
        self.message_user(request, f'{n} pedido(s) marcado(s) como por contactar.')
