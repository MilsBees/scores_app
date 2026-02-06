from django import forms
from django.db.models import Q
from django.forms import formset_factory, inlineformset_factory

from .models import SquashMatch, SquashSet, SquashPlayer, SquashSession


def get_or_create_player_case_insensitive(name: str) -> SquashPlayer:
    cleaned = (name or "").strip()
    if not cleaned:
        raise ValueError("Player name is required")

    existing = SquashPlayer.objects.filter(name__iexact=cleaned).first()
    if existing:
        return existing
    return SquashPlayer.objects.create(name=cleaned)

class SquashMatchForm(forms.ModelForm):
    player_1_name = forms.CharField(
        max_length=100,
        required=True,
        label="Player 1",
        error_messages={"required": "Player 1 name is required."},
    )
    player_2_name = forms.CharField(
        max_length=100,
        required=True,
        label="Player 2",
        error_messages={"required": "Player 2 name is required."},
    )

    class Meta:
        model = SquashMatch
        fields = ['date_played']
        widgets = {
            'date_played': forms.DateInput(attrs={'type': 'date'})
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = (cleaned_data.get('player_1_name') or '').strip()
        p2 = (cleaned_data.get('player_2_name') or '').strip()

        if not p1:
            self.add_error('player_1_name', 'Player 1 name is required.')
        if not p2:
            self.add_error('player_2_name', 'Player 2 name is required.')
        
        if p1 and p2 and p1.lower() == p2.lower():
            raise forms.ValidationError("Players must be different!")

        cleaned_data['player_1_name'] = p1
        cleaned_data['player_2_name'] = p2
        return cleaned_data

    def save(self, commit=True):
        p1_name = self.cleaned_data.get('player_1_name').strip()
        p2_name = self.cleaned_data.get('player_2_name').strip()

        player_1 = get_or_create_player_case_insensitive(p1_name)
        player_2 = get_or_create_player_case_insensitive(p2_name)
        
        match = super().save(commit=False)
        match.player_1 = player_1
        match.player_2 = player_2
        
        if commit:
            match.save()
        return match


class SquashSetForm(forms.ModelForm):
    player_1_points = forms.IntegerField(
        min_value=0,
        required=True,
        error_messages={
            "invalid": "Enter a whole number.",
            "required": "Player 1 points are required.",
            "min_value": "Points cannot be negative.",
        },
        widget=forms.NumberInput(attrs={"class": "score-input", "min": 0, "step": 1}),
    )
    player_2_points = forms.IntegerField(
        min_value=0,
        required=True,
        error_messages={
            "invalid": "Enter a whole number.",
            "required": "Player 2 points are required.",
            "min_value": "Points cannot be negative.",
        },
        widget=forms.NumberInput(attrs={"class": "score-input", "min": 0, "step": 1}),
    )

    class Meta:
        model = SquashSet
        fields = ['player_1_points', 'player_2_points']


SquashSetFormSet = inlineformset_factory(
    SquashMatch,
    SquashSet,
    form=SquashSetForm,
    extra=1,
    can_delete=True,
)


class SquashSessionForm(forms.ModelForm):
    class Meta:
        model = SquashSession
        fields = ["date_played"]
        widgets = {
            "date_played": forms.DateInput(attrs={"type": "date"}),
        }


class SquashSessionSetEntryForm(forms.Form):
    player_a_name = forms.CharField(
        max_length=100,
        required=True,
        label="Player A",
        error_messages={"required": "Player A name is required."},
    )
    player_b_name = forms.CharField(
        max_length=100,
        required=True,
        label="Player B",
        error_messages={"required": "Player B name is required."},
    )
    player_a_points = forms.IntegerField(
        min_value=0,
        required=True,
        label="Player A points",
        error_messages={"invalid": "Enter a whole number.", "min_value": "Points cannot be negative."},
    )
    player_b_points = forms.IntegerField(
        min_value=0,
        required=True,
        label="Player B points",
        error_messages={"invalid": "Enter a whole number.", "min_value": "Points cannot be negative."},
    )

    def clean(self):
        cleaned_data = super().clean()
        player_a_name = (cleaned_data.get("player_a_name") or "").strip()
        player_b_name = (cleaned_data.get("player_b_name") or "").strip()

        if not player_a_name:
            self.add_error("player_a_name", "Player A name is required.")
        if not player_b_name:
            self.add_error("player_b_name", "Player B name is required.")

        if player_a_name and player_b_name and player_a_name.lower() == player_b_name.lower():
            raise forms.ValidationError("Players must be different!")

        cleaned_data["player_a_name"] = player_a_name
        cleaned_data["player_b_name"] = player_b_name
        return cleaned_data


SquashSessionSetEntryFormSet = formset_factory(
    SquashSessionSetEntryForm,
    extra=1,
    can_delete=True,
)
