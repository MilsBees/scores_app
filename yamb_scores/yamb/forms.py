from django import forms
from django.forms import inlineformset_factory
from .models import Game, Score, Player, YambGame, YambScoresheet

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


# Yamb scoresheet forms
class YambGameForm(forms.ModelForm):
    class Meta:
        model = YambGame
        fields = []


class YambScoresheetForm(forms.ModelForm):
    player_name = forms.CharField(max_length=100, required=True, label="Player name")

    class Meta:
        model = YambScoresheet
        fields = [
            'row_1_down', 'row_1_up', 'row_1_l', 'row_1_s', 'row_1_total',
            'row_2_down', 'row_2_up', 'row_2_l', 'row_2_s', 'row_2_total',
            'row_3_down', 'row_3_up', 'row_3_l', 'row_3_s', 'row_3_total',
            'row_4_down', 'row_4_up', 'row_4_l', 'row_4_s', 'row_4_total',
            'row_5_down', 'row_5_up', 'row_5_l', 'row_5_s', 'row_5_total',
            'row_6_down', 'row_6_up', 'row_6_l', 'row_6_s', 'row_6_total',
            'row_h_down', 'row_h_up', 'row_h_l', 'row_h_s', 'row_h_total',
            'row_l_down', 'row_l_up', 'row_l_l', 'row_l_s', 'row_l_total',
            'row_fh_down', 'row_fh_up', 'row_fh_l', 'row_fh_s', 'row_fh_total',
            'row_c_down', 'row_c_up', 'row_c_l', 'row_c_s', 'row_c_total',
            'row_s_down', 'row_s_up', 'row_s_l', 'row_s_s', 'row_s_total',
            'row_p_down', 'row_p_up', 'row_p_l', 'row_p_s', 'row_p_total',
            'final_score',
        ]
        widgets = {f: forms.NumberInput(attrs={'class': 'score-input'}) for f in fields if f != 'player_name'}

    def clean_player_name(self):
        name = self.cleaned_data['player_name'].strip()
        if not name:
            raise forms.ValidationError("Player name required")
        return name

    def save(self, commit=True):
        player_name = self.cleaned_data.get('player_name')
        player, _ = Player.objects.get_or_create(name=player_name)
        scoresheet = super().save(commit=False)
        scoresheet.player = player
        if commit:
            scoresheet.save()
        return scoresheet


YambScoresheetFormSet = inlineformset_factory(
    YambGame,
    YambScoresheet,
    form=YambScoresheetForm,
    extra=1,
    can_delete=True,
)
