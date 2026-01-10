from django import forms
from django.forms import inlineformset_factory
from .models import Game, Score, Player

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = []

class ScoreForm(forms.ModelForm):
    player_name = forms.CharField(max_length=100, required=True, label="Player name")

    class Meta:
        model = Score
        fields = ['score']

    def clean_player_name(self):
        name = self.cleaned_data['player_name'].strip()
        if not name:
            raise forms.ValidationError("Player name required")
        return name

    def save(self, commit=True):
        player_name = self.cleaned_data.get('player_name')
        player, _ = Player.objects.get_or_create(name=player_name)
        score = super().save(commit=False)
        score.player = player
        if commit:
            score.save()
        return score

ScoreFormSet = inlineformset_factory(
    Game,
    Score,
    form=ScoreForm,
    fields=('score',),
    extra=3,
    can_delete=True,
)
