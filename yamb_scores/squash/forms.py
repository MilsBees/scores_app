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


class SquashPlayerForm(forms.ModelForm):
    """Form for creating and editing players"""
    class Meta:
        model = SquashPlayer
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Player name'})
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Player name is required.")
        
        # Check for case-insensitive duplicates (excluding the current instance if editing)
        existing = SquashPlayer.objects.filter(name__iexact=name)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError(f"A player with the name '{name}' already exists.")
        
        return name.title()


class SquashMatchForm(forms.ModelForm):
    player_1 = forms.ModelChoiceField(
        queryset=SquashPlayer.objects.all().order_by('name'),
        required=True,
        label="Player 1",
        error_messages={"required": "Player 1 is required."},
    )
    player_2 = forms.ModelChoiceField(
        queryset=SquashPlayer.objects.all().order_by('name'),
        required=True,
        label="Player 2",
        error_messages={"required": "Player 2 is required."},
    )

    class Meta:
        model = SquashMatch
        fields = ['player_1', 'player_2', 'date_played']
        widgets = {
            'date_played': forms.DateInput(attrs={'type': 'date'})
        }

    def clean(self):
        cleaned_data = super().clean()
        player_1 = cleaned_data.get('player_1')
        player_2 = cleaned_data.get('player_2')

        if player_1 and player_2 and player_1 == player_2:
            raise forms.ValidationError("Players must be different!")

        return cleaned_data


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
    player_a = forms.ModelChoiceField(
        queryset=SquashPlayer.objects.all().order_by('name'),
        required=True,
        label="Player A",
        error_messages={"required": "Player A is required."},
    )
    player_b = forms.ModelChoiceField(
        queryset=SquashPlayer.objects.all().order_by('name'),
        required=True,
        label="Player B",
        error_messages={"required": "Player B is required."},
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
        player_a = cleaned_data.get("player_a")
        player_b = cleaned_data.get("player_b")

        if player_a and player_b and player_a == player_b:
            raise forms.ValidationError("Players must be different!")

        return cleaned_data


SquashSessionSetEntryFormSet = formset_factory(
    SquashSessionSetEntryForm,
    extra=1,
    can_delete=True,
)
