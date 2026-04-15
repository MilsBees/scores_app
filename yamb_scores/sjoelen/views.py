from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.db.models import Avg, Max, Count, F, ExpressionWrapper, IntegerField, Min
from datetime import date, timedelta
from statistics import median
from .models import SjoelenPlayer, SjoelenGame, SjoelenScore
from .forms import SjoelenPlayerForm, SjoelenGameForm, SjoelenScoreFormSet


def index(request):
    return render(request, 'sjoelen/index.html')


def new_game(request):
    """Create a new Sjoelen game with scores for multiple players"""
    if request.method == 'POST':
        form = SjoelenGameForm(request.POST)
        game = SjoelenGame()
        formset = SjoelenScoreFormSet(request.POST, instance=game)
        
        if form.is_valid() and formset.is_valid():
            # Check that at least one score entry has a player
            has_valid_scores = any(
                form_instance.cleaned_data.get('player')
                for form_instance in formset.forms
                if not form_instance.cleaned_data.get('DELETE')
            )
            
            if not has_valid_scores:
                formset.non_form_errors().append('At least one player with a score is required.')
            else:
                # Check for duplicate players
                players = [
                    form_instance.cleaned_data.get('player')
                    for form_instance in formset.forms
                    if not form_instance.cleaned_data.get('DELETE') and form_instance.cleaned_data.get('player')
                ]
                
                if len(players) != len(set(players)):
                    formset.non_form_errors().append('Each player can only appear once in a game.')
                else:
                    with transaction.atomic():
                        game = form.save()
                        formset.instance = game
                        formset.save()
                    return redirect(reverse('sjoelen:game_list'))
    else:
        form = SjoelenGameForm()
        formset = SjoelenScoreFormSet(instance=SjoelenGame())
    
    # Get all players for the form
    players = SjoelenPlayer.objects.all().order_by('name').values('id', 'name')
    import json
    players_json = json.dumps(list(players))
    
    context = {
        'form': form,
        'formset': formset,
        'players_json': players_json,
    }
    return render(request, 'sjoelen/new_game.html', context)


def game_list(request):
    """List all Sjoelen games"""
    games = SjoelenGame.objects.prefetch_related('scores__player').order_by('-played_at')[:50]
    return render(request, 'sjoelen/game_list.html', {'games': games})


def player_list(request):
    """List all players"""
    players = SjoelenPlayer.objects.all().order_by('name')
    return render(request, 'sjoelen/player_list.html', {'players': players})


def new_player(request):
    """Create a new player"""
    if request.method == 'POST':
        form = SjoelenPlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('sjoelen:player_list'))
    else:
        form = SjoelenPlayerForm()
    
    return render(request, 'sjoelen/new_player.html', {'form': form})


def edit_player(request, pk):
    """Edit an existing player"""
    player = get_object_or_404(SjoelenPlayer, pk=pk)
    
    if request.method == 'POST':
        form = SjoelenPlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect(reverse('sjoelen:player_list'))
    else:
        form = SjoelenPlayerForm(instance=player)
    
    return render(request, 'sjoelen/edit_player.html', {'form': form, 'player': player})


def delete_player(request, pk):
    """Delete a player"""
    player = get_object_or_404(SjoelenPlayer, pk=pk)
    
    if request.method == 'POST':
        player.delete()
        return redirect(reverse('sjoelen:player_list'))
    
    return render(request, 'sjoelen/delete_player.html', {'player': player})


def statistics(request):
    """General statistics page for Sjoelen"""
    import json
    from statistics import stdev
    
    # Get all scores
    all_scores_qs = SjoelenScore.objects.all()
    all_scores = [s.final_score for s in all_scores_qs]
    total_games = all_scores_qs.count()  # Each Score = 1 game (player participation)
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    high_score = max(all_scores) if all_scores else None
    low_score = min(all_scores) if all_scores else None
    
    # Score distribution data for histogram
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
    final_score_expr = ExpressionWrapper(
        F('scores__round_1') + F('scores__round_2') + F('scores__round_3'),
        output_field=IntegerField()
    )
    
    players = SjoelenPlayer.objects.annotate(
        avg_score=Avg(final_score_expr),
        games_played=Count('scores__game', distinct=True),
    ).filter(games_played__gt=0).order_by('-avg_score')
    
    # Count unique players
    unique_players_count = players.count()
    
    # Calculate std dev and stats for each player
    player_stats = []
    player_box_data = {}
    for player in players:
        player_scores = player.scores.all()
        scores_list = [s.final_score for s in player_scores]
        
        if scores_list and len(scores_list) > 1:
            try:
                std_dev = stdev(scores_list)
            except:
                std_dev = 0
        else:
            std_dev = 0
        
        player_stats.append({
            'player': player,
            'avg_score': player.avg_score,
            'std_dev': std_dev,
            'min': min(scores_list) if scores_list else None,
            'max': max(scores_list) if scores_list else None,
            'count': player.games_played,
        })
        
        # Store scores for box plot
        player_box_data[player.name] = sorted(scores_list)
    
    # Games over time - count scores by date (player participations) for the entire year 2026
    scores_all = SjoelenScore.objects.all().select_related('game')
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
    
    # Calculate extremes for each round
    round_1_scores = SjoelenScore.objects.filter(round_1__isnull=False).values_list('round_1', flat=True)
    round_2_scores = SjoelenScore.objects.filter(round_2__isnull=False).values_list('round_2', flat=True)
    round_3_scores = SjoelenScore.objects.filter(round_3__isnull=False).values_list('round_3', flat=True)
    
    # Collect all individual round scores for "Any round"
    all_round_scores = []
    for score in SjoelenScore.objects.all():
        if score.round_1 is not None:
            all_round_scores.append(score.round_1)
        if score.round_2 is not None:
            all_round_scores.append(score.round_2)
        if score.round_3 is not None:
            all_round_scores.append(score.round_3)
    
    extremes = {
        'round_1': {
            'highest': max(round_1_scores) if round_1_scores else None,
            'lowest': min(round_1_scores) if round_1_scores else None,
        },
        'round_2': {
            'highest': max(round_2_scores) if round_2_scores else None,
            'lowest': min(round_2_scores) if round_2_scores else None,
        },
        'round_3': {
            'highest': max(round_3_scores) if round_3_scores else None,
            'lowest': min(round_3_scores) if round_3_scores else None,
        },
        'any_round': {
            'highest': max(all_round_scores) if all_round_scores else None,
            'lowest': min(all_round_scores) if all_round_scores else None,
        }
    }

    context = {
        'total_games': total_games,
        'avg_score': f"{avg_score:.1f}",
        'high_score': high_score,
        'low_score': low_score,
        'unique_players_count': unique_players_count,
        'player_stats': player_stats,
        'score_bins': json.dumps(score_bins),
        'games_by_date': json.dumps(games_by_date),
        'player_box_data': json.dumps(player_box_data),
        'extremes': extremes,
    }
    return render(request, 'sjoelen/statistics.html', context)


def leaderboard(request):
    # Get sort parameter from query string (default to 'avg')
    sort_by = request.GET.get('sort', 'avg')
    direction = request.GET.get('dir', 'desc')
    show_all = request.GET.get('show_all', 'false') == 'true'
    
    if sort_by not in {'best', 'avg', 'games', 'median'}:
        sort_by = 'avg'
    if direction not in {'asc', 'desc'}:
        direction = 'desc'
    
    # Calculate final_score as sum of rounds using database expression
    final_score_expr = ExpressionWrapper(
        F('scores__round_1') + F('scores__round_2') + F('scores__round_3'),
        output_field=IntegerField()
    )
    
    # Annotate players with stats
    players = SjoelenPlayer.objects.annotate(
        avg_score=Avg(final_score_expr),
        best_score=Max(final_score_expr),
        games_played=Count('scores__game', distinct=True),
    )
    
    # Filter out players with fewer than 5 games unless show_all is True
    if not show_all:
        players = players.filter(games_played__gte=5)
    
    # Calculate median for each player and add to the queryset
    player_list = []
    for player in players:
        scores = [s.final_score for s in player.scores.all()]
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
    
    # Get top 10 highest individual game scores
    # Calculate final scores and sort in Python
    all_scores = SjoelenScore.objects.select_related('player').all()
    all_scores_with_final = [(score, score.final_score) for score in all_scores]
    top_scores = sorted(all_scores_with_final, key=lambda x: x[1], reverse=True)[:10]
    top_scores = [score[0] for score in top_scores]  # Extract just the score objects
    
    # Get bottom 10 lowest individual game scores
    low_scores = sorted(all_scores_with_final, key=lambda x: x[1])[:10]
    low_scores = [score[0] for score in low_scores]  # Extract just the score objects
    
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
    return render(request, 'sjoelen/leaderboard.html', context)


def player_stats(request):
    """Landing + detail page for player statistics"""
    players = (
        SjoelenPlayer.objects.annotate(games_played=Count("scores__game", distinct=True)).order_by("name")
    )

    selected_player = None
    stats = None
    recent_scores = []
    top_scores = []
    low_scores = []
    last_score = None

    player_id = request.GET.get("player")
    if player_id:
        selected_player = get_object_or_404(SjoelenPlayer, pk=player_id)

        scores_qs = (
            SjoelenScore.objects.filter(player=selected_player)
            .select_related("game")
        )

        # Calculate final scores and get stats
        all_player_scores = [s for s in scores_qs]
        final_scores = [s.final_score for s in all_player_scores]
        
        if final_scores:
            stats = {
                'avg_score': sum(final_scores) / len(final_scores),
                'best_score': max(final_scores),
                'worst_score': min(final_scores),
                'games_played': len(all_player_scores),
            }
            
            last_score = scores_qs.order_by("-game__played_at").first()
            
            # Get recent, top, and bottom scores
            scores_with_final = [(s, s.final_score) for s in all_player_scores]
            
            recent_scores = [s[0] for s in sorted(scores_with_final, key=lambda x: x[0].game.played_at, reverse=True)[:10]]
            top_scores = [s[0] for s in sorted(scores_with_final, key=lambda x: (-x[1], -x[0].game.played_at.timestamp()))[:5]]
            low_scores = [s[0] for s in sorted(scores_with_final, key=lambda x: (x[1], -x[0].game.played_at.timestamp()))[:5]]

    return render(
        request,
        "sjoelen/player_stats.html",
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
