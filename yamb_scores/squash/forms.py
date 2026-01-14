from django import forms
from django.forms import inlineformset_factory
from .models import SquashMatch, SquashSet, SquashPlayer

class SquashMatchForm(forms.ModelForm):
    player_1_name = forms.CharField(max_length=100, required=True, label="Player 1")
    player_2_name = forms.CharField(max_length=100, required=True, label="Player 2")

    class Meta:
        model = SquashMatch
        fields = ['date_played']
        widgets = {
            'date_played': forms.DateInput(attrs={'type': 'date'})
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('player_1_name')
        p2 = cleaned_data.get('player_2_name')
        
        if p1 and p2 and p1.strip().lower() == p2.strip().lower():
            raise forms.ValidationError("Players must be different!")
        return cleaned_data

    def save(self, commit=True):
        p1_name = self.cleaned_data.get('player_1_name').strip()
        p2_name = self.cleaned_data.get('player_2_name').strip()
        
        player_1, _ = SquashPlayer.objects.get_or_create(name=p1_name)
        player_2, _ = SquashPlayer.objects.get_or_create(name=p2_name)
        
        match = super().save(commit=False)
        match.player_1 = player_1
        match.player_2 = player_2
        
        if commit:
            match.save()
        return match


class SquashSetForm(forms.ModelForm):
    class Meta:
        model = SquashSet
        fields = ['player_1_points', 'player_2_points']
        widgets = {
            'player_1_points': forms.NumberInput(attrs={'class': 'score-input'}),
            'player_2_points': forms.NumberInput(attrs={'class': 'score-input'}),
        }


SquashSetFormSet = inlineformset_factory(
    SquashMatch,
    SquashSet,
    form=SquashSetForm,
    extra=1,
    can_delete=True,
)
