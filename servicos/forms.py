import datetime

from django import forms

from .models import Avaliacao, Servico, Solicitacao


class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ["titulo", "categoria", "descricao", "preco_base", "regiao"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 4})}

    def clean_preco_base(self):
        preco = self.cleaned_data["preco_base"]
        if preco <= 0:
            raise forms.ValidationError("Informe um preço maior que zero.")
        return preco


class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = ["tipo_movel", "endereco", "cidade", "data", "horario", "observacoes"]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "horario": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_data(self):
        data = self.cleaned_data["data"]
        if data < datetime.date.today():
            raise forms.ValidationError("A data não pode estar no passado.")
        return data


class AvaliacaoForm(forms.ModelForm):
    nota = forms.TypedChoiceField(
        label="Nota",
        choices=[(i, "★" * i) for i in range(5, 0, -1)],
        coerce=int,
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Avaliacao
        fields = ["nota", "comentario"]
        widgets = {"comentario": forms.Textarea(attrs={"rows": 4, "placeholder": "Conte como foi o serviço (opcional)"})}
