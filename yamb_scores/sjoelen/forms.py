from django import forms
from django.forms import inlineformset_factory
from .models import SjoelenGame, SjoelenScore, SjoelenPlayer


class SjoelenPlayerForm(forms.ModelForm):
    """Form for creating and editing players"""
    class Meta:
        model = SjoelenPlayer
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Player name'})
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Player name is required.")
        
        # Check for case-insensitive duplicates (excluding the current instance if editing)
        existing = SjoelenPlayer.objects.filter(name__iexact=name)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError(f"A player with the name '{name}' already exists.")
        
        return name.title()


class SjoelenGameForm(forms.ModelForm):
    """Form for creating a Sjoelen game"""
    class Meta:
        model = SjoelenGame
        fields = []


class SjoelenScoreForm(forms.ModelForm):
    """Form for entering scores for a player in a game"""
    player = forms.ModelChoiceField(
        queryset=SjoelenPlayer.objects.all().order_by('name'),
        required=False,
        label="Player",
    )

    class Meta:
        model = SjoelenScore
        fields = ['round_1', 'round_2', 'round_3']
        widgets = {
            'round_1': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'numeric', 'placeholder': '0', 'style': 'width: 100%; padding: 0.25rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;'}),
            'round_2': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'numeric', 'placeholder': '0', 'style': 'width: 100%; padding: 0.25rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;'}),
            'round_3': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'numeric', 'placeholder': '0', 'style': 'width: 100%; padding: 0.25rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem;'}),
        }

    def clean(self):
        """Validate only if form has data and is not marked for deletion"""
        cleaned_data = super().clean()
        
        # Skip validation if marked for deletion
        if cleaned_data.get('DELETE'):
            return cleaned_data
        
        # Check if form has any data
        player = cleaned_data.get('player')
        has_any_score = any([
            cleaned_data.get('round_1'),
            cleaned_data.get('round_2'),
            cleaned_data.get('round_3'),
        ])
        
        # Only validate if the form has data
        if has_any_score or player:
            if not player:
                self.add_error('player', 'Player is required')
        
        return cleaned_data

    def save(self, commit=True):
        score = super().save(commit=False)
        score.player = self.cleaned_data.get('player')
        if commit:
            score.save()
        return score


SjoelenScoreFormSet = inlineformset_factory(
    SjoelenGame,
    SjoelenScore,
    form=SjoelenScoreForm,
    fields=('round_1', 'round_2', 'round_3'),
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
