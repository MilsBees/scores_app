from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg, Max, Count, Min, Q
from django.db import models
from django.urls import reverse
from django.forms import inlineformset_factory
from datetime import date, timedelta
from statistics import median
from .models import Game, Player, Score, YambGame, YambScoresheet
from .forms import GameForm, ScoreFormSet, YambGameForm, YambScoresheetFormSet, YambScoresheetForm, PlayerForm, ScoreForm

def index(request):
    return render(request, 'scores/index.html')

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
    
    # Calculate how many extra forms we need
    # If coming from yamb: extra = len(players) - 1 (since there's a base form)
    # If normal new game: extra = 0 (just show the default single form)
    extra_forms = len(initial_players) - 1 if initial_players else 0
    
    # Create formset class with the correct number of extra forms
    DynamicScoreFormSet = inlineformset_factory(
        Game,
        Score,
        form=ScoreForm,
        fields=('score',),
        extra=extra_forms,
        can_delete=True,
        min_num=1,
        validate_min=True,
    )
    
    if request.method == 'POST':
        form = GameForm(request.POST)
        game = Game()
        formset = DynamicScoreFormSet(request.POST, instance=game)
        if form.is_valid() and formset.is_valid():
            game = form.save()
            formset.instance = game
            formset.save()
            return redirect(reverse('scores:game_list'))
    else:
        form = GameForm()
        formset = DynamicScoreFormSet(instance=Game())
        
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
    
    if sort_by not in {'best', 'avg', 'games', 'median'}:
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
    
    # Calculate median for each player and add to the queryset
    player_list = []
    for player in players:
        scores = list(player.scores.values_list('score', flat=True))
        if scores:
            player.median_score = median(scores)
        else:
            player.median_score = None
        player_list.append(player)
    
    # Sort based on query parameter
    if sort_by == 'best':
        player_list.sort(key=lambda p: p.best_score if p.best_score else 0, reverse=(direction == 'desc'))
    elif sort_by == 'games':
        player_list.sort(key=lambda p: p.games_played, reverse=(direction == 'desc'))
    elif sort_by == 'median':
        player_list.sort(key=lambda p: p.median_score if p.median_score else 0, reverse=(direction == 'desc'))
    else:  # default to avg
        player_list.sort(key=lambda p: p.avg_score if p.avg_score else 0, reverse=(direction == 'desc'))
    
    # Get top 10 highest individual scores
    top_scores = Score.objects.select_related('player').order_by('-score')[:10]
    
    # Get bottom 10 lowest individual scores
    low_scores = Score.objects.select_related('player').order_by('score')[:10]
    
    # Build sort links with show_all parameter preserved
    show_all_param = '&show_all=true' if show_all else ''
    
    context = {
        'players': player_list,
        'top_scores': top_scores,
        'low_scores': low_scores,
        'sort_by': sort_by,
        'dir': direction,
        'show_all': show_all,
        'sort_links': {
            'best': f"sort=best&dir={'asc' if (sort_by == 'best' and direction == 'desc') else 'desc'}{show_all_param}",
            'avg': f"sort=avg&dir={'asc' if (sort_by == 'avg' and direction == 'desc') else 'desc'}{show_all_param}",
            'median': f"sort=median&dir={'asc' if (sort_by == 'median' and direction == 'desc') else 'desc'}{show_all_param}",
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


def yamb_statistics(request):
    """Option 1: Dedicated statistics page with detailed charts and visualizations"""
    import json
    from collections import Counter
    from statistics import stdev
    
    # Get all scores from squash games
    all_scores_qs = Score.objects.all()
    all_scores = [s.score for s in all_scores_qs]
    total_games = all_scores_qs.count()  # Each Score = 1 game (player participation)
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    high_score = max(all_scores) if all_scores else None
    low_score = min(all_scores) if all_scores else None
    
    # Score distribution data for histogram - fixed buckets from min to max score
    score_bins = {}
    bucket_size = 10
    min_bucket = (min(all_scores) // bucket_size) * bucket_size if all_scores else 0
    max_bucket = (max(all_scores) // bucket_size) * bucket_size + bucket_size if all_scores else bucket_size
    
    # Initialize all buckets
    for bucket_start in range(min_bucket, max_bucket, bucket_size):
        bucket_label = f"{bucket_start}-{bucket_start + bucket_size}"
        score_bins[bucket_label] = 0
    
    # Assign scores to buckets
    for score in all_scores:
        bucket_start = (score // bucket_size) * bucket_size
        bucket_label = f"{bucket_start}-{bucket_start + bucket_size}"
        if bucket_label in score_bins:
            score_bins[bucket_label] += 1
    
    # Player stats with standard deviation
    players = Player.objects.annotate(
        avg_score=Avg('scores__score'),
        games_played=Count('scores'),
    ).filter(games_played__gt=0).order_by('-avg_score')
    
    # Count unique players
    unique_players_count = players.count()
    
    # Calculate std dev and box plot data for each player
    player_stats = []
    player_box_data = {}
    for player in players:
        player_scores = list(player.scores.values_list('score', flat=True))
        if player_scores and len(player_scores) > 1:
            try:
                std_dev = stdev(player_scores)
            except:
                std_dev = 0
        else:
            std_dev = 0
        
        player_stats.append({
            'player': player,
            'avg_score': player.avg_score,
            'std_dev': std_dev,
            'min': min(player_scores) if player_scores else None,
            'max': max(player_scores) if player_scores else None,
            'count': player.games_played,
        })
        
        # Store scores for box plot
        player_box_data[player.name] = sorted(player_scores)
    
    # Games over time - count scores by date for the entire year 2026
    scores_all = Score.objects.all().select_related('game')
    games_by_date_dict = {}
    for score in scores_all:
        date_key = score.game.played_at.strftime('%Y-%m-%d')
        games_by_date_dict[date_key] = games_by_date_dict.get(date_key, 0) + 1
    
    # Generate full year 2026 with all dates (including zeros)
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    current_date = start_date
    games_by_date = {}
    
    while current_date <= end_date:
        date_key = current_date.strftime('%Y-%m-%d')
        games_by_date[date_key] = games_by_date_dict.get(date_key, 0)
        current_date += timedelta(days=1)
    
    # Row extremes - based on Yamb scoresheets (highest/lowest per row)
    scoresheets_yamb = YambScoresheet.objects.filter(final_score__isnull=False)
    row_fields = ['row_1_total', 'row_2_total', 'row_3_total', 'row_4_total', 'row_5_total', 'row_6_total',
                  'row_h_total', 'row_l_total', 'row_fh_total', 'row_c_total', 'row_s_total', 'row_p_total']
    
    row_extremes = []
    for row_field in row_fields:
        # Get high extremes
        high_sheets = list(scoresheets_yamb.filter(**{f'{row_field}__isnull': False}).order_by(f'-{row_field}'))
        high_value = None
        high_display = None
        high_tooltip = None
        high_scoresheet_id = None
        high_game_id = None
        if high_sheets:
            high_value = getattr(high_sheets[0], row_field)
            # Get all sheets with this value
            sheets_with_high = [s for s in high_sheets if getattr(s, row_field) == high_value]
            if len(sheets_with_high) == 1:
                high_display = f"{sheets_with_high[0].player.name} ({high_value})"
                high_scoresheet_id = sheets_with_high[0].id
                high_game_id = sheets_with_high[0].game_id
            elif len(sheets_with_high) == 2:
                high_display = f"{sheets_with_high[0].player.name}, {sheets_with_high[1].player.name} ({high_value})"
                high_scoresheet_id = sheets_with_high[0].id
                high_game_id = sheets_with_high[0].game_id
            else:
                high_display = f"Multiple players ({high_value})"
                high_tooltip = ", ".join([s.player.name for s in sheets_with_high])
                high_scoresheet_id = sheets_with_high[0].id
                high_game_id = sheets_with_high[0].game_id
        
        # Get low extremes
        low_sheets = list(scoresheets_yamb.filter(**{f'{row_field}__isnull': False}).order_by(f'{row_field}'))
        low_value = None
        low_display = None
        low_tooltip = None
        low_scoresheet_id = None
        low_game_id = None
        if low_sheets:
            low_value = getattr(low_sheets[0], row_field)
            # Get all sheets with this value
            sheets_with_low = [s for s in low_sheets if getattr(s, row_field) == low_value]
            if len(sheets_with_low) == 1:
                low_display = f"{sheets_with_low[0].player.name} ({low_value})"
                low_scoresheet_id = sheets_with_low[0].id
                low_game_id = sheets_with_low[0].game_id
            elif len(sheets_with_low) == 2:
                low_display = f"{sheets_with_low[0].player.name}, {sheets_with_low[1].player.name} ({low_value})"
                low_scoresheet_id = sheets_with_low[0].id
                low_game_id = sheets_with_low[0].game_id
            else:
                low_display = f"Multiple players ({low_value})"
                low_tooltip = ", ".join([s.player.name for s in sheets_with_low])
                low_scoresheet_id = sheets_with_low[0].id
                low_game_id = sheets_with_low[0].game_id
        
        row_name = row_field.replace('row_', '').replace('_total', '').upper()
        row_extremes.append({
            'row': row_name,
            'highest': high_display,
            'highest_tooltip': high_tooltip,
            'highest_scoresheet_id': high_scoresheet_id,
            'highest_game_id': high_game_id,
            'lowest': low_display,
            'lowest_tooltip': low_tooltip,
            'lowest_scoresheet_id': low_scoresheet_id,
            'lowest_game_id': low_game_id,
        })
    
    context = {
        'total_games': total_games,
        'avg_score': f"{avg_score:.1f}",
        'high_score': high_score,
        'low_score': low_score,
        'unique_players_count': unique_players_count,
        'score_bins': json.dumps(score_bins),
        'player_stats': player_stats,
        'player_box_data': json.dumps(player_box_data),
        'games_by_date': json.dumps(games_by_date),
        'row_extremes': row_extremes,
    }
    
    return render(request, 'scores/yamb_statistics.html', context)


def yamb_dashboard(request):
    """Option 3: Dashboard-style page with summary metrics and navigation"""
    import json
    from statistics import stdev
    
    # Get all scoresheets
    scoresheets = YambScoresheet.objects.filter(final_score__isnull=False)
    
    # Key metrics
    all_scores = [s.final_score for s in scoresheets]
    total_games = YambGame.objects.count()
    total_scoresheets = scoresheets.count()
    total_players = Player.objects.filter(yamb_scoresheets__final_score__isnull=False).distinct().count()
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    high_score = max(all_scores) if all_scores else None
    low_score = min(all_scores) if all_scores else None
    
    # Top players by average
    top_players = Player.objects.annotate(
        avg_score=Avg('yamb_scoresheets__final_score'),
        games_count=Count('yamb_scoresheets', filter=Q(yamb_scoresheets__final_score__isnull=False)),
    ).filter(games_count__gte=1).order_by('-avg_score')[:5]
    
    # Most recent games
    recent_games = YambGame.objects.prefetch_related('yamb_scoresheets__player').order_by('-created_at')[:5]
    
    # Consistency metrics (lowest std dev = most consistent)
    players = Player.objects.annotate(
        games_played=Count('yamb_scoresheets', filter=Q(yamb_scoresheets__final_score__isnull=False)),
    ).filter(games_played__gte=2)
    
    consistency = []
    for player in players:
        player_scores = list(player.yamb_scoresheets.filter(final_score__isnull=False).values_list('final_score', flat=True))
        if len(player_scores) > 1:
            try:
                std_dev = stdev(player_scores)
                consistency.append({
                    'player': player,
                    'std_dev': std_dev,
                    'avg': sum(player_scores) / len(player_scores),
                })
            except:
                pass
    
    most_consistent = sorted(consistency, key=lambda x: x['std_dev'])[:3]
    
    context = {
        'total_games': total_games,
        'total_scoresheets': total_scoresheets,
        'total_players': total_players,
        'avg_score': f"{avg_score:.1f}",
        'high_score': high_score,
        'low_score': low_score,
        'top_players': top_players,
        'recent_games': recent_games,
        'most_consistent': most_consistent,
    }
    
    return render(request, 'scores/yamb_dashboard.html', context)
