"""Forms públicos."""

import re

from django import forms

from .models import PedidoContacto


PHONE_PT_DIGITS = re.compile(r'^[29]\d{8}$')


def _normalize_phone(raw):
    """Strip spaces/dashes/parens/dots and an optional +351 / 00351 prefix."""

    if not raw:
        return ''
    cleaned = re.sub(r'[\s().\-]', '', raw)
    if cleaned.startswith('+351'):
        cleaned = cleaned[4:]
    elif cleaned.startswith('00351'):
        cleaned = cleaned[5:]
    return cleaned


class PedidoContactoForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'autocomplete': 'off', 'tabindex': '-1'}),
    )

    class Meta:
        model = PedidoContacto
        fields = (
            'nome', 'email', 'telefone', 'viatura',
            'pacote_interesse', 'mensagem',
        )
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'md-input',
                'autocomplete': 'name',
                'placeholder': 'O seu nome',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'md-input',
                'autocomplete': 'email',
                'placeholder': 'email@exemplo.com',
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'md-input',
                'autocomplete': 'tel',
                'inputmode': 'tel',
                'placeholder': '912 345 678',
            }),
            'viatura': forms.TextInput(attrs={
                'class': 'md-input',
                'placeholder': 'Marca, modelo, ano',
            }),
            'pacote_interesse': forms.Select(attrs={
                'class': 'md-input md-select',
            }),
            'mensagem': forms.Textarea(attrs={
                'class': 'md-input md-textarea',
                'rows': 5,
                'placeholder': 'Conte-nos sobre o seu carro e o que procura.',
            }),
        }
        labels = {
            'nome': 'Nome',
            'email': 'Email',
            'telefone': 'Telefone',
            'viatura': 'Viatura',
            'pacote_interesse': 'Pacote de interesse',
            'mensagem': 'Mensagem',
        }

    def clean_telefone(self):
        raw = self.cleaned_data.get('telefone', '')
        digits = _normalize_phone(raw)
        if not PHONE_PT_DIGITS.match(digits):
            raise forms.ValidationError(
                'Indique um número de telefone português válido '
                '(9 dígitos começando por 2 ou 9).',
            )
        return digits

    def is_spam(self):
        return bool(self.cleaned_data.get('website'))
