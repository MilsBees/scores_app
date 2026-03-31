from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg, Max, Count, Min
from django.urls import reverse
from .models import Game, Player, Score, YambGame, YambScoresheet
from .forms import GameForm, ScoreFormSet, YambGameForm, YambScoresheetFormSet, YambScoresheetForm, PlayerForm

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
                {'player': s.player, 'score': s.final_score}
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
    direction = request.GET.get('dir', 'desc')
    show_all = request.GET.get('show_all', 'false') == 'true'
    
    if sort_by not in {'best', 'avg', 'games'}:
        sort_by = 'avg'
    if direction not in {'asc', 'desc'}:
        direction = 'desc'
    
    # Annotate players with stats
    players = Player.objects.annotate(
        avg_score=Avg('scores__score'),
        best_score=Max('scores__score'),
        games_played=Count('scores__game', distinct=True),
    )
    
    # Filter out players with fewer than 5 games unless show_all is True
    if not show_all:
        players = players.filter(games_played__gte=5)
    
    prefix = '-' if direction == 'desc' else ''

    # Sort based on query parameter
    if sort_by == 'best':
        players = players.order_by(f'{prefix}best_score')
    elif sort_by == 'games':
        players = players.order_by(f'{prefix}games_played')
    else:  # default to avg
        players = players.order_by(f'{prefix}avg_score')
    
    # Get top 10 highest individual scores
    top_scores = Score.objects.select_related('player').order_by('-score')[:10]
    
    # Get bottom 10 lowest individual scores
    low_scores = Score.objects.select_related('player').order_by('score')[:10]
    
    # Build sort links with show_all parameter preserved
    show_all_param = '&show_all=true' if show_all else ''
    
    context = {
        'players': players,
        'top_scores': top_scores,
        'low_scores': low_scores,
        'sort_by': sort_by,
        'dir': direction,
        'show_all': show_all,
        'sort_links': {
            'best': f"sort=best&dir={'asc' if (sort_by == 'best' and direction == 'desc') else 'desc'}{show_all_param}",
            'avg': f"sort=avg&dir={'asc' if (sort_by == 'avg' and direction == 'desc') else 'desc'}{show_all_param}",
            'games': f"sort=games&dir={'asc' if (sort_by == 'games' and direction == 'desc') else 'desc'}{show_all_param}",
        },
        'toggle_link': f"?sort={sort_by}&dir={direction}&show_all={'false' if show_all else 'true'}",
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
    
    # Get all players for the JavaScript form builder
    players = Player.objects.all().order_by('name').values('id', 'name')
    import json
    players_json = json.dumps(list(players))
    
    return render(request, 'scores/yamb_form.html', {
        'form': form, 
        'formset': formset,
        'players_json': players_json,
    })


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


def player_stats(request):
    """Landing + detail page for player statistics based on Game/Score (same source as leaderboard)."""
    players = (
        Player.objects.annotate(games_played=Count("scores__game", distinct=True)).order_by("name")
    )

    selected_player = None
    stats = None
    recent_scores = []
    top_scores = []
    low_scores = []
    last_score = None

    player_id = request.GET.get("player")
    if player_id:
        selected_player = get_object_or_404(Player, pk=player_id)

        scores_qs = (
            Score.objects.filter(player=selected_player)
            .select_related("game")
        )

        stats = scores_qs.aggregate(
            avg_score=Avg("score"),
            best_score=Max("score"),
            worst_score=Min("score"),
            games_played=Count("game", distinct=True),
        )

        last_score = scores_qs.order_by("-game__played_at").first()
        recent_scores = list(scores_qs.order_by("-game__played_at")[:10])
        top_scores = list(scores_qs.order_by("-score", "-game__played_at")[:5])
        low_scores = list(scores_qs.order_by("score", "-game__played_at")[:5])

    return render(
        request,
        "scores/player_stats.html",
        {
            "players": players,
            "selected_player": selected_player,
            "stats": stats,
            "last_score": last_score,
            "recent_scores": recent_scores,
            "top_scores": top_scores,
            "low_scores": low_scores,
        },
    )


def player_list(request):
    """List all players"""
    players = Player.objects.all().order_by('name')
    return render(request, 'scores/player_list.html', {'players': players})


def new_player(request):
    """Create a new player"""
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('scores:player_list'))
    else:
        form = PlayerForm()
    
    return render(request, 'scores/new_player.html', {'form': form})


def edit_player(request, pk):
    """Edit an existing player"""
    player = get_object_or_404(Player, pk=pk)
    
    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect(reverse('scores:player_list'))
    else:
        form = PlayerForm(instance=player)
    
    return render(request, 'scores/edit_player.html', {'form': form, 'player': player})


def delete_player(request, pk):
    """Delete a player"""
    player = get_object_or_404(Player, pk=pk)
    
    if request.method == 'POST':
        player.delete()
        return redirect(reverse('scores:player_list'))
    
    return render(request, 'scores/confirm_delete_player.html', {'player': player})
