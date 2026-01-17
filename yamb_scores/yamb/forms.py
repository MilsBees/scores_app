from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Game, Score, Player, YambGame, YambScoresheet


class PlayerNameMixin:
    """Mixin for forms that handle player names with normalization and case-insensitive lookup"""
    
    def clean_player_name(self):
        name = self.cleaned_data['player_name'].strip()
        if not name:
            raise forms.ValidationError("Player name required")
        # Normalize to title case (capitalize first letter of each word)
        return name.title()
    
    def get_or_create_player(self, player_name):
        """Get existing player using case-insensitive lookup or create new one"""
        try:
            player = Player.objects.get(name__iexact=player_name)
        except Player.DoesNotExist:
            player = Player.objects.create(name=player_name)
        return player


class FriendlyErrorMixin:
    """Mixin to provide user-friendly error messages for common validation errors"""
    
    def add_error(self, field, error):
        """Override to customize error messages"""
        if field and error:
            # Check if it's an integer validation error
            if isinstance(error, ValidationError):
                for message in error.messages:
                    if 'valid integer' in message.lower() or 'whole number' in message.lower():
                        error = ValidationError(
                            f'Please enter a valid whole number (e.g., 5 or -3, not 5.5 or "abc").'
                        )
                        break
        super().add_error(field, error)


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = []

class ScoreForm(FriendlyErrorMixin, PlayerNameMixin, forms.ModelForm):
    player_name = forms.CharField(max_length=100, required=False, label="Player name")

    class Meta:
        model = Score
        fields = ['score']
        widgets = {
            'score': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text'}),
        }

    def clean(self):
        """Validate only if form is not marked for deletion and has data"""
        cleaned_data = super().clean()
        
        # Skip all validation if marked for deletion
        if cleaned_data.get('DELETE'):
            return cleaned_data
        
        # Check if form has any data (not completely empty)
        player_name = cleaned_data.get('player_name', '').strip()
        score = cleaned_data.get('score')
        has_any_data = bool(player_name or score)
        
        # Only validate if the form has any data entered
        if has_any_data:
            if not player_name:
                self.add_error('player_name', 'Player name is required')
        
        return cleaned_data

    def save(self, commit=True):
        player_name = self.cleaned_data.get('player_name')
        player = self.get_or_create_player(player_name)
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
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


# Yamb scoresheet forms
class YambGameForm(forms.ModelForm):
    class Meta:
        model = YambGame
        fields = []


class YambScoresheetForm(FriendlyErrorMixin, PlayerNameMixin, forms.ModelForm):
    player_name = forms.CharField(max_length=100, required=False, label="Player name")

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
        # Make row totals readonly since they're calculated automatically
        widgets = {
            **{f: forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text'}) 
               for f in fields if f != 'player_name' and f not in ['row_1_total', 'row_2_total', 'row_3_total', 'row_4_total', 'row_5_total', 'row_6_total', 'row_h_total', 'row_l_total', 'row_fh_total', 'row_c_total', 'row_s_total', 'row_p_total', 'final_score']},
            'row_1_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_2_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_3_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_4_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_5_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_6_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_h_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_l_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_fh_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_c_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_s_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'row_p_total': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
            'final_score': forms.TextInput(attrs={'class': 'score-input', 'inputmode': 'text', 'readonly': 'readonly'}),
        }
    
    def calculate_row_1_total(self, row_1_down, row_1_up, row_1_l, row_1_s):
        """
        Calculate the total for Row 1 based on the sum of the four dice columns.
        
        Logic:
        - If sum = 12: total = 0
        - For each integer above 12: add 10 to total
        - For each integer below 12: subtract 10 from total
        
        Formula: (sum - 12) * 10
        """
        if row_1_down is None or row_1_up is None or row_1_l is None or row_1_s is None:
            return None
        
        total_sum = row_1_down + row_1_up + row_1_l + row_1_s
        return (total_sum - 12) * 10
    
    def calculate_row_2_total(self, row_2_down, row_2_up, row_2_l, row_2_s):
        """
        Calculate the total for Row 2 based on the sum of the four dice columns.
        
        Logic:
        - If sum = 12: total = 0
        - For each integer above 12: add 20 to total
        - For each integer below 12: subtract 20 from total
        
        Formula: (sum - 12) * 20
        """
        if row_2_down is None or row_2_up is None or row_2_l is None or row_2_s is None:
            return None
        
        total_sum = row_2_down + row_2_up + row_2_l + row_2_s
        return (total_sum - 12) * 20
    
    def calculate_row_3_total(self, row_3_down, row_3_up, row_3_l, row_3_s):
        """Calculate Row 3 total: (sum - 12) * 30"""
        if row_3_down is None or row_3_up is None or row_3_l is None or row_3_s is None:
            return None
        total_sum = row_3_down + row_3_up + row_3_l + row_3_s
        return (total_sum - 12) * 30
    
    def calculate_row_4_total(self, row_4_down, row_4_up, row_4_l, row_4_s):
        """Calculate Row 4 total: (sum - 12) * 40"""
        if row_4_down is None or row_4_up is None or row_4_l is None or row_4_s is None:
            return None
        total_sum = row_4_down + row_4_up + row_4_l + row_4_s
        return (total_sum - 12) * 40
    
    def calculate_row_5_total(self, row_5_down, row_5_up, row_5_l, row_5_s):
        """Calculate Row 5 total: (sum - 12) * 50"""
        if row_5_down is None or row_5_up is None or row_5_l is None or row_5_s is None:
            return None
        total_sum = row_5_down + row_5_up + row_5_l + row_5_s
        return (total_sum - 12) * 50
    
    def calculate_row_6_total(self, row_6_down, row_6_up, row_6_l, row_6_s):
        """Calculate Row 6 total: (sum - 12) * 60"""
        if row_6_down is None or row_6_up is None or row_6_l is None or row_6_s is None:
            return None
        total_sum = row_6_down + row_6_up + row_6_l + row_6_s
        return (total_sum - 12) * 60
    
    def calculate_row_h_total(self, row_h_down, row_h_up, row_h_l, row_h_s, row_l_down, row_l_up, row_l_l, row_l_s):
        """Calculate Row H total: sum of 4 H cells + bonuses (30 per column where H+L >= 50)"""
        # Only calculate when ALL 8 cells (both H and L rows) are filled
        if (row_h_down is None or row_h_up is None or row_h_l is None or row_h_s is None or
            row_l_down is None or row_l_up is None or row_l_l is None or row_l_s is None):
            return None
        
        # Calculate bonuses: 30 for each column where H + L >= 50
        bonuses = 0
        if row_h_down + row_l_down >= 50:
            bonuses += 30
        if row_h_up + row_l_up >= 50:
            bonuses += 30
        if row_h_l + row_l_l >= 50:
            bonuses += 30
        if row_h_s + row_l_s >= 50:
            bonuses += 30
        
        return row_h_down + row_h_up + row_h_l + row_h_s + bonuses
    
    def calculate_row_l_total(self, row_l_down, row_l_up, row_l_l, row_l_s, row_h_down, row_h_up, row_h_l, row_h_s):
        """Calculate Row L total: simple sum of 4 L cells (only when both H and L complete)"""
        # Only calculate when ALL 8 cells (both H and L rows) are filled
        if (row_l_down is None or row_l_up is None or row_l_l is None or row_l_s is None or
            row_h_down is None or row_h_up is None or row_h_l is None or row_h_s is None):
            return None
        
        return row_l_down + row_l_up + row_l_l + row_l_s
    
    def calculate_row_fh_total(self, row_fh_down, row_fh_up, row_fh_l, row_fh_s):
        """Calculate Row FH total: simple sum of 4 cells"""
        if row_fh_down is None or row_fh_up is None or row_fh_l is None or row_fh_s is None:
            return None
        return row_fh_down + row_fh_up + row_fh_l + row_fh_s
    
    def calculate_row_c_total(self, row_c_down, row_c_up, row_c_l, row_c_s):
        """Calculate Row C total: simple sum of 4 cells"""
        if row_c_down is None or row_c_up is None or row_c_l is None or row_c_s is None:
            return None
        return row_c_down + row_c_up + row_c_l + row_c_s
    
    def calculate_row_s_total(self, row_s_down, row_s_up, row_s_l, row_s_s):
        """Calculate Row S total: simple sum of 4 cells"""
        if row_s_down is None or row_s_up is None or row_s_l is None or row_s_s is None:
            return None
        return row_s_down + row_s_up + row_s_l + row_s_s
    
    def calculate_row_p_total(self, row_p_down, row_p_up, row_p_l, row_p_s):
        """Calculate Row P total: simple sum of 4 cells"""
        if row_p_down is None or row_p_up is None or row_p_l is None or row_p_s is None:
            return None
        return row_p_down + row_p_up + row_p_l + row_p_s
    
    def calculate_final_score(self, row_1_total, row_2_total, row_3_total, row_4_total,
                              row_5_total, row_6_total, row_h_total, row_l_total,
                              row_fh_total, row_c_total, row_s_total, row_p_total):
        """Calculate final score: sum of all row totals"""
        totals = [row_1_total, row_2_total, row_3_total, row_4_total, row_5_total, row_6_total,
                 row_h_total, row_l_total, row_fh_total, row_c_total, row_s_total, row_p_total]
        # Only calculate if all totals are present
        if any(t is None for t in totals):
            return None
        return sum(totals)
    
    def validate_row_1_field(self, field_name, value):
        """Validate that Row 1 field values are between 0-5 inclusive"""
        if value is not None and (value < 0 or value > 5):
            self.add_error(field_name, f'Row 1 values must be between 0 and 5 (you entered {value})')
    
    def validate_row_2_field(self, field_name, value):
        """Validate that Row 2 field values are between 0-5 inclusive"""
        if value is not None and (value < 0 or value > 5):
            self.add_error(field_name, f'Row 2 values must be between 0 and 5 (you entered {value})')
    
    def validate_row_3_field(self, field_name, value):
        """Validate that Row 3 field values are between 0-5 inclusive"""
        if value is not None and (value < 0 or value > 5):
            self.add_error(field_name, f'Row 3 values must be between 0 and 5 (you entered {value})')
    
    def validate_row_4_field(self, field_name, value):
        """Validate that Row 4 field values are between 0-5 inclusive"""
        if value is not None and (value < 0 or value > 5):
            self.add_error(field_name, f'Row 4 values must be between 0 and 5 (you entered {value})')
    
    def validate_row_5_field(self, field_name, value):
        """Validate that Row 5 field values are between 0-5 inclusive"""
        if value is not None and (value < 0 or value > 5):
            self.add_error(field_name, f'Row 5 values must be between 0 and 5 (you entered {value})')
    
    def validate_row_6_field(self, field_name, value):
        """Validate that Row 6 field values are between 0-5 inclusive"""
        if value is not None and (value < 0 or value > 5):
            self.add_error(field_name, f'Row 6 values must be between 0 and 5 (you entered {value})')
    
    def validate_row_h_field(self, field_name, value):
        """Validate that Row H field values are between 0-30 inclusive"""
        if value is not None and (value < 0 or value > 30):
            self.add_error(field_name, f'Row H values must be between 0 and 30 (you entered {value})')
    
    def validate_row_l_field(self, field_name, value):
        """Validate that Row L field values are between 0-30 inclusive"""
        if value is not None and (value < 0 or value > 30):
            self.add_error(field_name, f'Row L values must be between 0 and 30 (you entered {value})')
    
    def validate_h_greater_than_l(self, h_value, l_value, column_name):
        """Validate that H value is greater than L value for a given column (exception: both can be 0)"""
        if h_value is not None and l_value is not None:
            # H must be greater than L, unless both are 0
            if h_value <= l_value and not (h_value == 0 and l_value == 0):
                self.add_error(f'row_h_{column_name}', f'Row H {column_name.upper()} ({h_value}) must be greater than Row L {column_name.upper()} ({l_value})')
    
    def validate_row_fh_field(self, field_name, value):
        """Validate that Row FH field values are either 40 or 0"""
        if value is not None and value != 0 and value != 40:
            self.add_error(field_name, f'Row FH values must be either 0 or 40 (you entered {value})')
    
    def validate_row_c_field(self, field_name, value):
        """Validate that Row C field values are either 60 or 0"""
        if value is not None and value != 0 and value != 60:
            self.add_error(field_name, f'Row C values must be either 0 or 60 (you entered {value})')
    
    def validate_row_s_field(self, field_name, value):
        """Validate that Row S field values are either 80 or 0"""
        if value is not None and value != 0 and value != 80:
            self.add_error(field_name, f'Row S values must be either 0 or 80 (you entered {value})')
    
    def validate_row_p_field(self, field_name, value):
        """Validate that Row P field values are either 100 or 0"""
        if value is not None and value != 0 and value != 100:
            self.add_error(field_name, f'Row P values must be either 0 or 100 (you entered {value})')

    def clean(self):
        """Validate only if form is not marked for deletion and has data"""
        cleaned_data = super().clean()
        
        # Skip all validation if marked for deletion
        if cleaned_data.get('DELETE'):
            return cleaned_data
        
        # Validate Row 1 fields are in range 0-5
        row_1_down = cleaned_data.get('row_1_down')
        row_1_up = cleaned_data.get('row_1_up')
        row_1_l = cleaned_data.get('row_1_l')
        row_1_s = cleaned_data.get('row_1_s')
        
        self.validate_row_1_field('row_1_down', row_1_down)
        self.validate_row_1_field('row_1_up', row_1_up)
        self.validate_row_1_field('row_1_l', row_1_l)
        self.validate_row_1_field('row_1_s', row_1_s)
        
        # Calculate Row 1 total if all four columns are filled in
        calculated_total = self.calculate_row_1_total(row_1_down, row_1_up, row_1_l, row_1_s)
        if calculated_total is not None:
            cleaned_data['row_1_total'] = calculated_total
        
        # Validate Row 2 fields are in range 0-5
        row_2_down = cleaned_data.get('row_2_down')
        row_2_up = cleaned_data.get('row_2_up')
        row_2_l = cleaned_data.get('row_2_l')
        row_2_s = cleaned_data.get('row_2_s')
        
        self.validate_row_2_field('row_2_down', row_2_down)
        self.validate_row_2_field('row_2_up', row_2_up)
        self.validate_row_2_field('row_2_l', row_2_l)
        self.validate_row_2_field('row_2_s', row_2_s)
        
        # Calculate Row 2 total if all four columns are filled in
        calculated_total_2 = self.calculate_row_2_total(row_2_down, row_2_up, row_2_l, row_2_s)
        if calculated_total_2 is not None:
            cleaned_data['row_2_total'] = calculated_total_2
        
        # Validate and calculate Row 3
        row_3_down = cleaned_data.get('row_3_down')
        row_3_up = cleaned_data.get('row_3_up')
        row_3_l = cleaned_data.get('row_3_l')
        row_3_s = cleaned_data.get('row_3_s')
        self.validate_row_3_field('row_3_down', row_3_down)
        self.validate_row_3_field('row_3_up', row_3_up)
        self.validate_row_3_field('row_3_l', row_3_l)
        self.validate_row_3_field('row_3_s', row_3_s)
        calculated_total_3 = self.calculate_row_3_total(row_3_down, row_3_up, row_3_l, row_3_s)
        if calculated_total_3 is not None:
            cleaned_data['row_3_total'] = calculated_total_3
        
        # Validate and calculate Row 4
        row_4_down = cleaned_data.get('row_4_down')
        row_4_up = cleaned_data.get('row_4_up')
        row_4_l = cleaned_data.get('row_4_l')
        row_4_s = cleaned_data.get('row_4_s')
        self.validate_row_4_field('row_4_down', row_4_down)
        self.validate_row_4_field('row_4_up', row_4_up)
        self.validate_row_4_field('row_4_l', row_4_l)
        self.validate_row_4_field('row_4_s', row_4_s)
        calculated_total_4 = self.calculate_row_4_total(row_4_down, row_4_up, row_4_l, row_4_s)
        if calculated_total_4 is not None:
            cleaned_data['row_4_total'] = calculated_total_4
        
        # Validate and calculate Row 5
        row_5_down = cleaned_data.get('row_5_down')
        row_5_up = cleaned_data.get('row_5_up')
        row_5_l = cleaned_data.get('row_5_l')
        row_5_s = cleaned_data.get('row_5_s')
        self.validate_row_5_field('row_5_down', row_5_down)
        self.validate_row_5_field('row_5_up', row_5_up)
        self.validate_row_5_field('row_5_l', row_5_l)
        self.validate_row_5_field('row_5_s', row_5_s)
        calculated_total_5 = self.calculate_row_5_total(row_5_down, row_5_up, row_5_l, row_5_s)
        if calculated_total_5 is not None:
            cleaned_data['row_5_total'] = calculated_total_5
        
        # Validate and calculate Row 6
        row_6_down = cleaned_data.get('row_6_down')
        row_6_up = cleaned_data.get('row_6_up')
        row_6_l = cleaned_data.get('row_6_l')
        row_6_s = cleaned_data.get('row_6_s')
        self.validate_row_6_field('row_6_down', row_6_down)
        self.validate_row_6_field('row_6_up', row_6_up)
        self.validate_row_6_field('row_6_l', row_6_l)
        self.validate_row_6_field('row_6_s', row_6_s)
        calculated_total_6 = self.calculate_row_6_total(row_6_down, row_6_up, row_6_l, row_6_s)
        if calculated_total_6 is not None:
            cleaned_data['row_6_total'] = calculated_total_6
        
        # Validate and calculate Row H and L (together since they depend on each other)
        row_h_down = cleaned_data.get('row_h_down')
        row_h_up = cleaned_data.get('row_h_up')
        row_h_l = cleaned_data.get('row_h_l')
        row_h_s = cleaned_data.get('row_h_s')
        row_l_down = cleaned_data.get('row_l_down')
        row_l_up = cleaned_data.get('row_l_up')
        row_l_l = cleaned_data.get('row_l_l')
        row_l_s = cleaned_data.get('row_l_s')
        
        # Validate ranges
        self.validate_row_h_field('row_h_down', row_h_down)
        self.validate_row_h_field('row_h_up', row_h_up)
        self.validate_row_h_field('row_h_l', row_h_l)
        self.validate_row_h_field('row_h_s', row_h_s)
        self.validate_row_l_field('row_l_down', row_l_down)
        self.validate_row_l_field('row_l_up', row_l_up)
        self.validate_row_l_field('row_l_l', row_l_l)
        self.validate_row_l_field('row_l_s', row_l_s)
        
        # Validate that H > L for each column
        self.validate_h_greater_than_l(row_h_down, row_l_down, 'down')
        self.validate_h_greater_than_l(row_h_up, row_l_up, 'up')
        self.validate_h_greater_than_l(row_h_l, row_l_l, 'l')
        self.validate_h_greater_than_l(row_h_s, row_l_s, 's')
        
        # Calculate totals (only when all 8 cells are filled)
        calculated_total_h = self.calculate_row_h_total(row_h_down, row_h_up, row_h_l, row_h_s,
                                                         row_l_down, row_l_up, row_l_l, row_l_s)
        if calculated_total_h is not None:
            cleaned_data['row_h_total'] = calculated_total_h
        
        calculated_total_l = self.calculate_row_l_total(row_l_down, row_l_up, row_l_l, row_l_s,
                                                         row_h_down, row_h_up, row_h_l, row_h_s)
        if calculated_total_l is not None:
            cleaned_data['row_l_total'] = calculated_total_l
        
        # Validate and calculate Row FH
        for field_name in ['row_fh_down', 'row_fh_up', 'row_fh_l', 'row_fh_s']:
            self.validate_row_fh_field(field_name, cleaned_data.get(field_name))
        
        row_fh_total = self.calculate_row_fh_total(
            cleaned_data.get('row_fh_down'),
            cleaned_data.get('row_fh_up'),
            cleaned_data.get('row_fh_l'),
            cleaned_data.get('row_fh_s')
        )
        if row_fh_total is not None:
            cleaned_data['row_fh_total'] = row_fh_total
        
        # Validate and calculate Row C
        for field_name in ['row_c_down', 'row_c_up', 'row_c_l', 'row_c_s']:
            self.validate_row_c_field(field_name, cleaned_data.get(field_name))
        
        row_c_total = self.calculate_row_c_total(
            cleaned_data.get('row_c_down'),
            cleaned_data.get('row_c_up'),
            cleaned_data.get('row_c_l'),
            cleaned_data.get('row_c_s')
        )
        if row_c_total is not None:
            cleaned_data['row_c_total'] = row_c_total
        
        # Validate and calculate Row S
        for field_name in ['row_s_down', 'row_s_up', 'row_s_l', 'row_s_s']:
            self.validate_row_s_field(field_name, cleaned_data.get(field_name))
        
        row_s_total = self.calculate_row_s_total(
            cleaned_data.get('row_s_down'),
            cleaned_data.get('row_s_up'),
            cleaned_data.get('row_s_l'),
            cleaned_data.get('row_s_s')
        )
        if row_s_total is not None:
            cleaned_data['row_s_total'] = row_s_total
        
        # Validate and calculate Row P
        for field_name in ['row_p_down', 'row_p_up', 'row_p_l', 'row_p_s']:
            self.validate_row_p_field(field_name, cleaned_data.get(field_name))
        
        row_p_total = self.calculate_row_p_total(
            cleaned_data.get('row_p_down'),
            cleaned_data.get('row_p_up'),
            cleaned_data.get('row_p_l'),
            cleaned_data.get('row_p_s')
        )
        if row_p_total is not None:
            cleaned_data['row_p_total'] = row_p_total
        
        # Calculate final score (sum of all row totals)
        final_score = self.calculate_final_score(
            cleaned_data.get('row_1_total'),
            cleaned_data.get('row_2_total'),
            cleaned_data.get('row_3_total'),
            cleaned_data.get('row_4_total'),
            cleaned_data.get('row_5_total'),
            cleaned_data.get('row_6_total'),
            cleaned_data.get('row_h_total'),
            cleaned_data.get('row_l_total'),
            cleaned_data.get('row_fh_total'),
            cleaned_data.get('row_c_total'),
            cleaned_data.get('row_s_total'),
            cleaned_data.get('row_p_total')
        )
        if final_score is not None:
            cleaned_data['final_score'] = final_score
        

        # Check if form has any data (not completely empty)
        player_name = cleaned_data.get('player_name', '').strip()
        # Check if any scoresheet field has data
        has_scoresheet_data = any(
            cleaned_data.get(field) is not None and cleaned_data.get(field) != ''
            for field in self.fields if field != 'player_name'
        )
        has_any_data = bool(player_name or has_scoresheet_data)
        
        # Only validate if the form has any data entered
        if has_any_data:
            if not player_name:
                self.add_error('player_name', 'Player name is required')
        
        return cleaned_data

    def save(self, commit=True):
        player_name = self.cleaned_data.get('player_name')
        player = self.get_or_create_player(player_name)
        scoresheet = super().save(commit=False)
        scoresheet.player = player
        if commit:
            scoresheet.save()
        return scoresheet


YambScoresheetFormSet = inlineformset_factory(
    YambGame,
    YambScoresheet,
    form=YambScoresheetForm,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
