from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg, Max, Count, Min
from django.urls import reverse
from .models import Game, Player, Score, YambGame, YambScoresheet
from .forms import GameForm, ScoreFormSet, YambGameForm, YambScoresheetFormSet, YambScoresheetForm

def game_list(request):
    games = Game.objects.prefetch_related('scores__player').order_by('-played_at')[:50]
    return render(request, 'scores/game_list.html', {'games': games})

def new_game(request):
    # Check if we're coming from yamb_form with pre-populated data
    yamb_game_id = request.GET.get('yamb_game_id')
    initial_players = []
    
    if yamb_game_id:
        try:
            yamb_game = YambGame.objects.get(id=yamb_game_id)
            initial_players = [
                {'player_name': s.player.name, 'score': s.final_score}
                for s in yamb_game.yamb_scoresheets.all()
                if s.final_score is not None
            ]
        except YambGame.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = GameForm(request.POST)
        game = Game()
        formset = ScoreFormSet(request.POST, instance=game)
        if form.is_valid() and formset.is_valid():
            game = form.save()
            formset.instance = game
            formset.save()
            return redirect(reverse('scores:game_list'))
    else:
        form = GameForm()
        formset = ScoreFormSet(instance=Game())
        
        # Pre-populate formset if coming from yamb
        if initial_players:
            for i, player_data in enumerate(initial_players):
                if i < len(formset.forms):
                    formset.forms[i].initial = player_data
    
    return render(request, 'scores/game_form.html', {'form': form, 'formset': formset})

def leaderboard(request):
    # Get sort parameter from query string (default to 'avg')
    sort_by = request.GET.get('sort', 'avg')
    
    # Annotate players with stats
    players = Player.objects.annotate(
        avg_score=Avg('scores__score'),
        best_score=Max('scores__score'),
        games_played=Count('scores__game', distinct=True),
    )
    
    # Sort based on query parameter
    if sort_by == 'best':
        players = players.order_by('-best_score')
    elif sort_by == 'games':
        players = players.order_by('-games_played')
    else:  # default to avg
        players = players.order_by('-avg_score')
    
    # Get top 10 highest individual scores
    top_scores = Score.objects.select_related('player').order_by('-score')[:10]
    
    # Get bottom 10 lowest individual scores
    low_scores = Score.objects.select_related('player').order_by('score')[:10]
    
    context = {
        'players': players,
        'top_scores': top_scores,
        'low_scores': low_scores,
        'sort_by': sort_by,
    }
    return render(request, 'scores/leaderboard.html', context)


def yamb_list(request):
    """List all Yamb games"""
    yamb_games = YambGame.objects.prefetch_related('yamb_scoresheets__player').order_by('-created_at')[:50]
    return render(request, 'scores/yamb_list.html', {'yamb_games': yamb_games})


def new_yamb(request):
    """Create a new Yamb game with scoresheets for multiple players"""
    if request.method == 'POST':
        form = YambGameForm(request.POST)
        game = YambGame()
        formset = YambScoresheetFormSet(request.POST, instance=game)
        if form.is_valid() and formset.is_valid():
            game = form.save()
            formset.instance = game
            formset.save()
            # Redirect to new_game with yamb_game_id to pre-populate
            return redirect(f"{reverse('scores:new_game')}?yamb_game_id={game.id}")
    else:
        form = YambGameForm()
        formset = YambScoresheetFormSet(instance=YambGame())
    return render(request, 'scores/yamb_form.html', {'form': form, 'formset': formset})


def yamb_detail(request, pk):
    """View a Yamb game"""
    yamb_game = get_object_or_404(YambGame, pk=pk)
    scoresheets = yamb_game.yamb_scoresheets.all()
    return render(request, 'scores/yamb_detail.html', {
        'yamb_game': yamb_game,
        'scoresheets': scoresheets
    })


def edit_yamb_scoresheet(request, game_pk, scoresheet_pk):
    """Edit a single scoresheet in a Yamb game"""
    yamb_game = get_object_or_404(YambGame, pk=game_pk)
    scoresheet = get_object_or_404(YambScoresheet, pk=scoresheet_pk, game=yamb_game)
    
    if request.method == 'POST':
        form = YambScoresheetForm(request.POST, instance=scoresheet)
        if form.is_valid():
            form.save()
            # Redirect to new_game with yamb_game_id to pre-populate
            return redirect(f"{reverse('scores:new_game')}?yamb_game_id={yamb_game.id}")
    else:
        form = YambScoresheetForm(instance=scoresheet)
        # Pre-fill the player_name field
        form.initial['player_name'] = scoresheet.player.name
    
    return render(request, 'scores/edit_yamb_scoresheet.html', {
        'yamb_game': yamb_game,
        'scoresheet': scoresheet,
        'form': form
    })


def delete_yamb_scoresheet(request, game_pk, scoresheet_pk):
    """Delete a scoresheet from a Yamb game"""
    yamb_game = get_object_or_404(YambGame, pk=game_pk)
    scoresheet = get_object_or_404(YambScoresheet, pk=scoresheet_pk, game=yamb_game)
    
    if request.method == 'POST':
        scoresheet.delete()
        
        # If the game has no more scoresheets, delete the game too
        if not yamb_game.yamb_scoresheets.exists():
            yamb_game.delete()
            return redirect(reverse('scores:yamb_list'))
        else:
            return redirect(reverse('scores:yamb_detail', args=[yamb_game.id]))
    
    return render(request, 'scores/confirm_delete_scoresheet.html', {
        'yamb_game': yamb_game,
        'scoresheet': scoresheet
    })
