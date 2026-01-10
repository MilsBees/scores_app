from django.shortcuts import render, redirect
from django.db.models import Sum, Avg, Max, Count
from django.urls import reverse
from .models import Game, Player, Score
from .forms import GameForm, ScoreFormSet

def game_list(request):
    games = Game.objects.prefetch_related('scores__player').order_by('-played_at')[:50]
    return render(request, 'scores/game_list.html', {'games': games})

def new_game(request):
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
    return render(request, 'scores/game_form.html', {'form': form, 'formset': formset})

def leaderboard(request):
    # Get sort parameter from query string
    sort_by = request.GET.get('sort', 'best')
    
    # Annotate players with stats
    players = Player.objects.annotate(
        avg_score=Avg('scores__score'),
        best_score=Max('scores__score'),
        games_played=Count('scores__game', distinct=True),
    )
    
    # Sort based on query parameter
    if sort_by == 'avg':
        players = players.order_by('-avg_score')
    elif sort_by == 'games':
        players = players.order_by('-games_played')
    else:  # default to best
        players = players.order_by('-best_score')
    
    # Get top 10 individual scores
    top_scores = Score.objects.select_related('player').order_by('-score')[:10]
    
    context = {
        'players': players,
        'top_scores': top_scores,
        'sort_by': sort_by,
    }
    return render(request, 'scores/leaderboard.html', context)
