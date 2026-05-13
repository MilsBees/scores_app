from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Sum, Count, Q, Case, When, IntegerField, F, Max
from django.urls import reverse
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from .models import SquashMatch, SquashSet, SquashPlayer, SquashSession
from .forms import (
    SquashMatchForm,
    SquashSessionForm,
    SquashSessionSetEntryFormSet,
    SquashSetFormSet,
    get_or_create_player_case_insensitive,
)

def index(request):
    return render(request, 'squash/index.html')

def new_match(request):
    if request.method == 'POST':
        form = SquashMatchForm(request.POST)
        match = SquashMatch()
        formset = SquashSetFormSet(request.POST, instance=match)
        
        if form.is_valid() and formset.is_valid():
            if formset.forms and formset.forms[0].cleaned_data.get('DELETE'):
                formset.forms[0].add_error('DELETE', 'The first set cannot be deleted.')
                return render(request, 'squash/new_match.html', {
                    'form': form,
                    'formset': formset,
                })

            match = form.save()
            formset.instance = match
            
            # Set set numbers
            set_number = 0
            for form_instance in formset.forms:
                if form_instance.cleaned_data.get('DELETE'):
                    continue
                if form_instance.cleaned_data.get('player_1_points') is not None:
                    set_number += 1
                    form_instance.instance.set_number = set_number
            
            formset.save()
            return redirect(reverse('squash:match_list'))
    else:
        form = SquashMatchForm()
        formset = SquashSetFormSet(instance=SquashMatch())
    
    return render(request, 'squash/new_match.html', {
        'form': form,
        'formset': formset,
    })


def new_session(request):
    if request.method == "POST":
        session_form = SquashSessionForm(request.POST)
        set_formset = SquashSessionSetEntryFormSet(request.POST, prefix="sets")

        if session_form.is_valid() and set_formset.is_valid():
            if set_formset.forms and set_formset.forms[0].cleaned_data.get("DELETE"):
                set_formset.forms[0].add_error("DELETE", "The first set cannot be deleted.")
                return render(
                    request,
                    "squash/new_session.html",
                    {
                        "session_form": session_form,
                        "set_formset": set_formset,
                    },
                )

            date_played = session_form.cleaned_data["date_played"]
            set_type = session_form.cleaned_data["set_type"]

            with transaction.atomic():
                session, _ = SquashSession.objects.get_or_create(date_played=date_played)

                for entry_form in set_formset:
                    if not entry_form.cleaned_data or entry_form.cleaned_data.get("DELETE"):
                        continue

                    player_a = entry_form.cleaned_data["player_a"]
                    player_b = entry_form.cleaned_data["player_b"]
                    a_points = entry_form.cleaned_data["player_a_points"]
                    b_points = entry_form.cleaned_data["player_b_points"]

                    # Canonical ordering so a pair maps to exactly one match per session
                    if player_a.id < player_b.id:
                        player_1, player_2 = player_a, player_b
                        p1_points, p2_points = a_points, b_points
                    else:
                        player_1, player_2 = player_b, player_a
                        p1_points, p2_points = b_points, a_points

                    match, _ = SquashMatch.objects.get_or_create(
                        session=session,
                        player_1=player_1,
                        player_2=player_2,
                        defaults={"date_played": date_played, "set_type": set_type},
                    )

                    current_max = (
                        SquashSet.objects.filter(match=match).aggregate(Max("set_number")).get("set_number__max")
                        or 0
                    )

                    SquashSet.objects.create(
                        match=match,
                        set_number=current_max + 1,
                        player_1_points=p1_points,
                        player_2_points=p2_points,
                    )

            return redirect(reverse("squash:match_list"))
    else:
        session_form = SquashSessionForm()
        set_formset = SquashSessionSetEntryFormSet(prefix="sets")

    return render(
        request,
        "squash/new_session.html",
        {
            "session_form": session_form,
            "set_formset": set_formset,
        },
    )

def match_list(request):
    matches = SquashMatch.objects.prefetch_related('sets').order_by('-date_played')[:50]
    return render(request, 'squash/match_list.html', {'matches': matches})

def leaderboard(request):
    # Get set_type filter from query params
    set_type_filter = request.GET.get('set_type')
    if set_type_filter not in ('11', '21'):
        set_type_filter = None
    
    abs_allowed_sorts = {
        "matches_won",
        "matches_drawn",
        "matches_lost",
        "matches_played",
        "points_for",
        "points_against",
        "point_diff",
        "last_match_date",
    }
    rel_allowed_sorts = {
        "match_win_pct",
        "set_win_pct",
        "point_win_pct",
        "points_for",
        "points_against",
        "matches_played",
        "total_sets",
    }

    abs_sort = request.GET.get("abs_sort", "matches_won")
    abs_dir = request.GET.get("abs_dir", "desc")
    if abs_sort not in abs_allowed_sorts:
        abs_sort = "matches_won"
    if abs_dir not in {"asc", "desc"}:
        abs_dir = "desc"

    rel_sort = request.GET.get("rel_sort", "match_win_pct")
    rel_dir = request.GET.get("rel_dir", "desc")
    if rel_sort not in rel_allowed_sorts:
        rel_sort = "match_win_pct"
    if rel_dir not in {"asc", "desc"}:
        rel_dir = "desc"

    players = SquashPlayer.objects.all()
    
    player_stats = []
    for player in players:
        # Matches where player participated
        matches = SquashMatch.objects.filter(Q(player_1=player) | Q(player_2=player))
        if set_type_filter:
            matches = matches.filter(set_type=set_type_filter)
        
        # Base queryset for sets, filtered by set_type if specified
        sets_as_p1 = SquashSet.objects.filter(match__player_1=player)
        sets_as_p2 = SquashSet.objects.filter(match__player_2=player)
        if set_type_filter:
            sets_as_p1 = sets_as_p1.filter(match__set_type=set_type_filter)
            sets_as_p2 = sets_as_p2.filter(match__set_type=set_type_filter)
        
        # Total points for / against
        points_for_as_p1 = sets_as_p1.aggregate(Sum("player_1_points"))["player_1_points__sum"] or 0
        points_for_as_p2 = sets_as_p2.aggregate(Sum("player_2_points"))["player_2_points__sum"] or 0
        points_against_as_p1 = sets_as_p1.aggregate(Sum("player_2_points"))["player_2_points__sum"] or 0
        points_against_as_p2 = sets_as_p2.aggregate(Sum("player_1_points"))["player_1_points__sum"] or 0

        points_for = points_for_as_p1 + points_for_as_p2
        points_against = points_against_as_p1 + points_against_as_p2
        total_points = points_for
        points_total = points_for + points_against
        point_win_pct = (points_for / points_total * 100.0) if points_total > 0 else 0.0
        
        # Total sets won (using filtered querysets)
        sets_won_as_p1 = sets_as_p1.filter(player_1_points__gt=F('player_2_points')).count()
        sets_won_as_p2 = sets_as_p2.filter(player_2_points__gt=F('player_1_points')).count()
        total_sets_won = sets_won_as_p1 + sets_won_as_p2

        sets_lost_as_p1 = sets_as_p1.filter(player_1_points__lt=F("player_2_points")).count()
        sets_lost_as_p2 = sets_as_p2.filter(player_2_points__lt=F("player_1_points")).count()
        total_sets_lost = sets_lost_as_p1 + sets_lost_as_p2
        
        # Total sets played
        all_player_sets = SquashSet.objects.filter(Q(match__player_1=player) | Q(match__player_2=player))
        if set_type_filter:
            all_player_sets = all_player_sets.filter(match__set_type=set_type_filter)
        total_sets = all_player_sets.count()
        set_win_pct = (total_sets_won / total_sets * 100.0) if total_sets > 0 else 0.0
        
        # Last match date
        last_match = matches.order_by('-date_played').first()
        last_match_date = last_match.date_played if last_match else None
        
        # Match record (W-L-D)
        matches_won = 0
        matches_lost = 0
        matches_drawn = 0
        
        for match in matches:
            sets = match.sets.all()
            
            if match.player_1 == player:
                sets_won = sum(1 for s in sets if s.player_1_points > s.player_2_points)
                sets_lost = sum(1 for s in sets if s.player_2_points > s.player_1_points)
            else:
                sets_won = sum(1 for s in sets if s.player_2_points > s.player_1_points)
                sets_lost = sum(1 for s in sets if s.player_1_points > s.player_2_points)
            
            if sets_won > sets_lost:
                matches_won += 1
            elif sets_lost > sets_won:
                matches_lost += 1
            else:
                matches_drawn += 1

        matches_played = matches_won + matches_lost + matches_drawn
        # Spec: draws are not wins; win% is wins / played.
        match_win_pct = (matches_won / matches_played * 100.0) if matches_played > 0 else 0.0
        
        if total_sets > 0:  # Only include players with matches
            player_stats.append({
                'player': player,
                'points_for': points_for,
                'points_against': points_against,
                'points_total': points_total,
                'point_diff': points_for - points_against,
                'point_win_pct': point_win_pct,
                'total_sets_won': total_sets_won,
                'total_sets': total_sets,
                'total_sets_lost': total_sets_lost,
                'set_win_pct': set_win_pct,
                'last_match_date': last_match_date,
                'matches_won': matches_won,
                'matches_lost': matches_lost,
                'matches_drawn': matches_drawn,
                'matches_played': matches_played,
                'match_win_pct': match_win_pct,
            })

    def _date_key(stat):
        return stat["last_match_date"]

    relative_stats = list(player_stats)
    absolute_stats = list(player_stats)

    # Relative sorting (primary table)
    rel_reverse = rel_dir == "desc"
    if rel_sort == "match_win_pct":
        # Spec: default sorting is match% with ties broken by set%, then point%.
        relative_stats.sort(
            key=lambda s: (
                s["match_win_pct"],
                s["set_win_pct"],
                s["point_win_pct"],
            ),
            reverse=rel_reverse,
        )
    else:
        relative_stats.sort(key=lambda s: s.get(rel_sort, 0), reverse=rel_reverse)

    # Absolute sorting (legacy table)
    abs_reverse = abs_dir == "desc"
    if abs_sort == "last_match_date":
        # Sort with None-safe behavior
        if abs_reverse:
            absolute_stats.sort(key=lambda s: (s["last_match_date"] is None, s["last_match_date"]), reverse=False)
        else:
            absolute_stats.sort(key=lambda s: (s["last_match_date"] is not None, s["last_match_date"]), reverse=False)
    else:
        absolute_stats.sort(key=lambda s: s.get(abs_sort, 0), reverse=abs_reverse)

    def _qs(**updates):
        params = {
            "abs_sort": abs_sort,
            "abs_dir": abs_dir,
            "rel_sort": rel_sort,
            "rel_dir": rel_dir,
        }
        if set_type_filter:
            params["set_type"] = set_type_filter
        params.update(updates)
        return "&".join([f"{k}={v}" for k, v in params.items()])

    abs_sort_links = {}
    for col in [
        "matches_won",
        "matches_drawn",
        "matches_lost",
        "matches_played",
        "points_for",
        "points_against",
        "point_diff",
        "last_match_date",
    ]:
        next_dir = "asc" if (abs_sort == col and abs_dir == "desc") else "desc"
        abs_sort_links[col] = _qs(abs_sort=col, abs_dir=next_dir)

    rel_sort_links = {}
    for col in [
        "match_win_pct",
        "set_win_pct",
        "point_win_pct",
        "points_for",
        "points_against",
        "matches_played",
        "total_sets",
    ]:
        next_dir = "asc" if (rel_sort == col and rel_dir == "desc") else "desc"
        rel_sort_links[col] = _qs(rel_sort=col, rel_dir=next_dir)

    return render(
        request,
        "squash/leaderboard.html",
        {
            "relative_stats": relative_stats,
            "absolute_stats": absolute_stats,
            "abs_sort": abs_sort,
            "abs_dir": abs_dir,
            "rel_sort": rel_sort,
            "rel_dir": rel_dir,
            "abs_sort_links": abs_sort_links,
            "rel_sort_links": rel_sort_links,
            "set_type_filter": set_type_filter,
        },
    )

def h2h(request):
    # Get set_type filter from query params
    set_type_filter = request.GET.get('set_type')
    if set_type_filter not in ('11', '21'):
        set_type_filter = None
    
    players = SquashPlayer.objects.all().order_by('name')
    selected_player = None
    h2h_data = []

    allowed_sorts = {
        "points_for",
        "points_against",
        "point_diff",
        "sets_won",
        "sets_lost",
        "matches_won",
        "matches_lost",
        "matches_drawn",
    }
    sort = request.GET.get("sort", "point_diff")
    direction = request.GET.get("dir", "desc")
    if sort not in allowed_sorts:
        sort = "point_diff"
    if direction not in {"asc", "desc"}:
        direction = "desc"
    
    selected_player_id = request.GET.get('player')
    if selected_player_id:
        selected_player = get_object_or_404(SquashPlayer, id=selected_player_id)
        
        # Get all opponents - filter by set_type if specified
        opponent_matches = SquashMatch.objects.filter(
            Q(player_1=selected_player) | Q(player_2=selected_player)
        )
        if set_type_filter:
            opponent_matches = opponent_matches.filter(set_type=set_type_filter)
        
        opponents = SquashPlayer.objects.filter(
            Q(squash_matches_as_p1__in=opponent_matches, squash_matches_as_p1__player_2=selected_player) |
            Q(squash_matches_as_p2__in=opponent_matches, squash_matches_as_p2__player_1=selected_player)
        ).distinct().order_by('name')
        
        for opponent in opponents:
            matches = SquashMatch.objects.filter(
                Q(player_1=selected_player, player_2=opponent) |
                Q(player_1=opponent, player_2=selected_player)
            ).prefetch_related('sets')
            if set_type_filter:
                matches = matches.filter(set_type=set_type_filter)
            
            total_points_for = 0
            total_points_against = 0
            matches_won = 0
            matches_lost = 0
            matches_drawn = 0
            total_sets_won = 0
            total_sets_lost = 0
            
            for match in matches:
                sets = match.sets.all()
                
                if match.player_1 == selected_player:
                    points_for = sum(s.player_1_points for s in sets)
                    points_against = sum(s.player_2_points for s in sets)
                else:
                    points_for = sum(s.player_2_points for s in sets)
                    points_against = sum(s.player_1_points for s in sets)
                
                total_points_for += points_for
                total_points_against += points_against
                
                # Count sets won
                if match.player_1 == selected_player:
                    sets_won = sum(1 for s in sets if s.player_1_points > s.player_2_points)
                    sets_lost = sum(1 for s in sets if s.player_2_points > s.player_1_points)
                else:
                    sets_won = sum(1 for s in sets if s.player_2_points > s.player_1_points)
                    sets_lost = sum(1 for s in sets if s.player_1_points > s.player_2_points)
                
                total_sets_won += sets_won
                total_sets_lost += sets_lost
                
                # Count match results
                if sets_won > sets_lost:
                    matches_won += 1
                elif sets_lost > sets_won:
                    matches_lost += 1
                else:
                    matches_drawn += 1
            
            point_diff = total_points_for - total_points_against
            
            h2h_data.append({
                'opponent': opponent,
                'points_for': total_points_for,
                'points_against': total_points_against,
                'point_diff': point_diff,
                'sets_won': total_sets_won,
                'sets_lost': total_sets_lost,
                'matches_won': matches_won,
                'matches_lost': matches_lost,
                'matches_drawn': matches_drawn,
            })

        h2h_data.sort(key=lambda r: r.get(sort, 0), reverse=(direction == "desc"))

    sort_links = {}
    # Preserve selected player and set_type in query string for sorting links.
    base_qs = ""
    if selected_player_id:
        base_qs += f"player={selected_player_id}&"
    if set_type_filter:
        base_qs += f"set_type={set_type_filter}&"
    for col in [
        "points_for",
        "points_against",
        "point_diff",
        "sets_won",
        "sets_lost",
        "matches_won",
        "matches_lost",
        "matches_drawn",
    ]:
        next_dir = "asc" if (sort == col and direction == "desc") else "desc"
        sort_links[col] = f"{base_qs}sort={col}&dir={next_dir}"
    
    return render(request, 'squash/h2h.html', {
        'players': players,
        'selected_player': selected_player,
        'h2h_data': h2h_data,
        'sort': sort,
        'dir': direction,
        'sort_links': sort_links,
        'set_type_filter': set_type_filter,
    })


def player_list(request):
    """List all players"""
    players = SquashPlayer.objects.all().order_by('name')
    return render(request, 'squash/player_list.html', {'players': players})


def new_player(request):
    """Create a new player"""
    if request.method == 'POST':
        from .forms import SquashPlayerForm
        form = SquashPlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('squash:player_list'))
    else:
        from .forms import SquashPlayerForm
        form = SquashPlayerForm()
    
    return render(request, 'squash/new_player.html', {'form': form})


def edit_player(request, pk):
    """Edit a player"""
    player = get_object_or_404(SquashPlayer, pk=pk)
    
    if request.method == 'POST':
        from .forms import SquashPlayerForm
        form = SquashPlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect(reverse('squash:player_list'))
    else:
        from .forms import SquashPlayerForm
        form = SquashPlayerForm(instance=player)
    
    return render(request, 'squash/edit_player.html', {'form': form, 'player': player})


def delete_player(request, pk):
    """Delete a player"""
    player = get_object_or_404(SquashPlayer, pk=pk)
    
    if request.method == 'POST':
        player.delete()
        return redirect(reverse('squash:player_list'))
    
    return render(request, 'squash/delete_player.html', {'player': player})


def statistics(request):
    """General statistics page with key metrics, charts and player performance"""
    import json
    from statistics import stdev
    
    # Get set_type filter from query params (None = all, '11' = 11-point, '21' = 21-point)
    set_type_filter = request.GET.get('set_type')
    if set_type_filter not in ('11', '21'):
        set_type_filter = None
    
    # Get all matches and sets, filtered by set_type if specified
    all_matches = SquashMatch.objects.all().prefetch_related('sets')
    if set_type_filter:
        all_matches = all_matches.filter(set_type=set_type_filter)
    total_matches = all_matches.count()
    
    # Get all sets with scores, filtered by match set_type if specified
    all_sets = SquashSet.objects.filter(player_1_points__isnull=False, player_2_points__isnull=False)
    if set_type_filter:
        all_sets = all_sets.filter(match__set_type=set_type_filter)
    all_set_scores = []
    
    for s in all_sets:
        all_set_scores.append(s.player_1_points)
        all_set_scores.append(s.player_2_points)
    
    avg_score = sum(all_set_scores) / len(all_set_scores) if all_set_scores else 0
    high_score = max(all_set_scores) if all_set_scores else None
    low_score = min(all_set_scores) if all_set_scores else None
    
    # Get all players with match counts
    players = SquashPlayer.objects.all().order_by('name')
    
    # Count unique players (filtered by set_type if specified)
    if set_type_filter:
        unique_players_count = SquashPlayer.objects.filter(
            Q(squash_matches_as_p1__set_type=set_type_filter) |
            Q(squash_matches_as_p2__set_type=set_type_filter)
        ).distinct().count()
    else:
        unique_players_count = players.count()
    
    # Player performance stats - match/set/point win percentages
    player_performance_data = {}
    
    for player in players:
        # Matches played and won by this player
        player_matches = SquashMatch.objects.filter(
            Q(player_1=player) | Q(player_2=player)
        ).prefetch_related('sets')
        if set_type_filter:
            player_matches = player_matches.filter(set_type=set_type_filter)
        
        matches_won = 0
        matches_total = 0
        sets_won = 0
        sets_total = 0
        points_won = 0
        points_total = 0
        
        for match in player_matches:
            sets = match.sets.all().exclude(player_1_points__isnull=True, player_2_points__isnull=True)
            
            if player == match.player_1:
                match_sets_won = sum(1 for s in sets if s.player_1_points > s.player_2_points)
                match_points = sum(s.player_1_points for s in sets)
                opponent_points = sum(s.player_2_points for s in sets)
            else:
                match_sets_won = sum(1 for s in sets if s.player_2_points > s.player_1_points)
                match_points = sum(s.player_2_points for s in sets)
                opponent_points = sum(s.player_1_points for s in sets)
            
            match_sets_total = sets.count()
            if match_sets_won > match_sets_total - match_sets_won:
                matches_won += 1
            
            matches_total += 1
            sets_won += match_sets_won
            sets_total += match_sets_total
            points_won += match_points
            points_total += match_points + opponent_points
        
        if player_matches.exists():
            match_win_pct = (matches_won / matches_total * 100) if matches_total > 0 else 0
            set_win_pct = (sets_won / sets_total * 100) if sets_total > 0 else 0
            points_win_pct = (points_won / points_total * 100) if points_total > 0 else 0
            
            player_performance_data[player.name] = {
                'match_win_pct': round(match_win_pct, 1),
                'set_win_pct': round(set_win_pct, 1),
                'points_win_pct': round(points_win_pct, 1),
            }
    
    # Player stats - collect scores for each player
    player_stats = []
    player_box_data = {}
    player_box_data_11 = {}
    player_box_data_21 = {}
    
    for player in players:
        player_sets = SquashSet.objects.filter(
            Q(match__player_1=player) | Q(match__player_2=player),
            player_1_points__isnull=False,
            player_2_points__isnull=False
        )
        if set_type_filter:
            player_sets = player_sets.filter(match__set_type=set_type_filter)
        
        player_scores = []
        player_scores_11 = []
        player_scores_21 = []
        
        for s in player_sets:
            if s.match.player_1 == player:
                score = s.player_1_points
            else:
                score = s.player_2_points
            
            player_scores.append(score)
            
            # Collect by set type (for Overall view)
            if not set_type_filter:
                if s.match.set_type == '11':
                    player_scores_11.append(score)
                else:
                    player_scores_21.append(score)
        
        if player_scores:
            avg = sum(player_scores) / len(player_scores)
            if len(player_scores) > 1:
                try:
                    std_dev = stdev(player_scores)
                except:
                    std_dev = 0
            else:
                std_dev = 0
            
            player_stats.append({
                'player': player,
                'avg_score': round(avg, 1),
                'std_dev': round(std_dev, 1),
                'min': min(player_scores),
                'max': max(player_scores),
                'count': len(player_scores),
            })
            
            player_box_data[player.name] = sorted(player_scores)
            
            # For Overall view, build separate data
            if not set_type_filter:
                if player_scores_11:
                    player_box_data_11[player.name] = sorted(player_scores_11)
                if player_scores_21:
                    player_box_data_21[player.name] = sorted(player_scores_21)
    
    # Matches over time - all time
    matches_by_date_dict = {}
    for match in all_matches:
        date_key = match.date_played.strftime('%Y-%m-%d')
        matches_by_date_dict[date_key] = matches_by_date_dict.get(date_key, 0) + 1
    
    # Generate data for all dates (include zeros)
    start_date = date(2026, 1, 1)
    end_date = date(2026, 12, 31)
    current_date = start_date
    matches_by_date = {}
    
    while current_date <= end_date:
        date_key = current_date.strftime('%Y-%m-%d')
        matches_by_date[date_key] = matches_by_date_dict.get(date_key, 0)
        current_date += timedelta(days=1)
    
    # Match extremes - three types: Set Differential, Point Differential in Set, Point Differential in Match
    # Option to include incomplete sets (default: exclude)
    include_incomplete = request.GET.get('include_incomplete') == '1'
    
    match_extremes = []
    
    if all_matches.exists():
        # 1. SET DIFFERENTIAL (SINGLE MATCH) - how many sets won in a match
        set_diffs_data = []
        for match in all_matches:
            sets = match.sets.all().exclude(player_1_points__isnull=True, player_2_points__isnull=True)
            if not include_incomplete:
                sets = sets.filter(is_incomplete=False)
            if sets.exists():
                p1_sets_won = sum(1 for s in sets if s.player_1_points > s.player_2_points)
                p2_sets_won = sum(1 for s in sets if s.player_2_points > s.player_1_points)
                differential = abs(p1_sets_won - p2_sets_won)
                total_sets = p1_sets_won + p2_sets_won
                
                # Record the player with more sets won
                if p1_sets_won > p2_sets_won:
                    player_name = match.player_1.name
                    opponent_name = match.player_2.name
                else:
                    player_name = match.player_2.name
                    opponent_name = match.player_1.name
                
                score_str = f"{max(p1_sets_won, p2_sets_won)}-{min(p1_sets_won, p2_sets_won)}"
                
                set_diffs_data.append({
                    'value': differential,
                    'total': total_sets,
                    'display': f"{player_name} {score_str} {opponent_name}",
                    'match': match,
                })
        
        if set_diffs_data:
            # Sort by differential desc, then by total desc for tiebreaking
            set_diffs_sorted = sorted(set_diffs_data, key=lambda x: (x['value'], x['total']), reverse=True)
            
            # Largest differential (first after sorting)
            largest_entry = set_diffs_sorted[0]
            largest_display = largest_entry['display']
            largest_tooltip = None
            
            # Smallest differential (filter to smallest value, then pick highest total)
            smallest_value = min(d['value'] for d in set_diffs_data)
            smallest_candidates = sorted(
                [d for d in set_diffs_data if d['value'] == smallest_value],
                key=lambda x: x['total'],
                reverse=True
            )
            smallest_entry = smallest_candidates[0]
            smallest_display = smallest_entry['display']
            smallest_tooltip = None
            
            match_extremes.append({
                'type': 'Set Differential (Single match)',
                'largest_display': largest_display,
                'largest_tooltip': largest_tooltip,
                'smallest_display': smallest_display,
                'smallest_tooltip': smallest_tooltip,
            })
        
        # 2. POINT DIFFERENTIAL (SINGLE SET)
        set_point_diffs_data = []
        extremes_sets = all_sets.filter(match__isnull=False)
        if not include_incomplete:
            extremes_sets = extremes_sets.filter(is_incomplete=False)
        for s in extremes_sets:
            differential = abs(s.player_1_points - s.player_2_points)
            total_points = s.player_1_points + s.player_2_points
            
            if s.player_1_points > s.player_2_points:
                player_name = s.match.player_1.name
                opponent_name = s.match.player_2.name
                score_str = f"{s.player_1_points}-{s.player_2_points}"
            else:
                player_name = s.match.player_2.name
                opponent_name = s.match.player_1.name
                score_str = f"{s.player_2_points}-{s.player_1_points}"
            
            set_point_diffs_data.append({
                'value': differential,
                'total': total_points,
                'display': f"{player_name} {score_str} {opponent_name}",
            })
        
        if set_point_diffs_data:
            # Sort by differential desc, then by total desc for tiebreaking
            set_point_diffs_sorted = sorted(set_point_diffs_data, key=lambda x: (x['value'], x['total']), reverse=True)
            
            # Largest point differential (first after sorting)
            largest_entry = set_point_diffs_sorted[0]
            largest_display = largest_entry['display']
            largest_tooltip = None
            
            # Smallest point differential (filter to smallest value, then pick highest total)
            smallest_value = min(d['value'] for d in set_point_diffs_data)
            smallest_candidates = sorted(
                [d for d in set_point_diffs_data if d['value'] == smallest_value],
                key=lambda x: x['total'],
                reverse=True
            )
            smallest_entry = smallest_candidates[0]
            smallest_display = smallest_entry['display']
            smallest_tooltip = None
            
            match_extremes.append({
                'type': 'Point differential (Single set)',
                'largest_display': largest_display,
                'largest_tooltip': largest_tooltip,
                'smallest_display': smallest_display,
                'smallest_tooltip': smallest_tooltip,
            })
        
        # 3. POINT DIFFERENTIAL (SINGLE MATCH)
        match_point_diffs_data = []
        for match in all_matches:
            sets = match.sets.all().exclude(player_1_points__isnull=True, player_2_points__isnull=True)
            if not include_incomplete:
                sets = sets.filter(is_incomplete=False)
            if sets.exists():
                total_p1 = sum(s.player_1_points for s in sets)
                total_p2 = sum(s.player_2_points for s in sets)
                differential = abs(total_p1 - total_p2)
                total_points = total_p1 + total_p2
                
                if total_p1 > total_p2:
                    player_name = match.player_1.name
                    opponent_name = match.player_2.name
                    score_str = f"{total_p1}-{total_p2}"
                else:
                    player_name = match.player_2.name
                    opponent_name = match.player_1.name
                    score_str = f"{total_p2}-{total_p1}"
                
                match_point_diffs_data.append({
                    'value': differential,
                    'total': total_points,
                    'display': f"{player_name} {score_str} {opponent_name}",
                })
        
        if match_point_diffs_data:
            # Sort by differential desc, then by total desc for tiebreaking
            match_point_diffs_sorted = sorted(match_point_diffs_data, key=lambda x: (x['value'], x['total']), reverse=True)
            
            # Largest point differential (first after sorting)
            largest_entry = match_point_diffs_sorted[0]
            largest_display = largest_entry['display']
            largest_tooltip = None
            
            # Smallest point differential (filter to smallest value, then pick highest total)
            smallest_value = min(d['value'] for d in match_point_diffs_data)
            smallest_candidates = sorted(
                [d for d in match_point_diffs_data if d['value'] == smallest_value],
                key=lambda x: x['total'],
                reverse=True
            )
            smallest_entry = smallest_candidates[0]
            smallest_display = smallest_entry['display']
            smallest_tooltip = None
            
            match_extremes.append({
                'type': 'Point Differential (Single match)',
                'largest_display': largest_display,
                'largest_tooltip': largest_tooltip,
                'smallest_display': smallest_display,
                'smallest_tooltip': smallest_tooltip,
            })
    
    # Calculate 11-point and 21-point set counts (from database field, unfiltered for display)
    all_sets_unfiltered = SquashSet.objects.filter(player_1_points__isnull=False, player_2_points__isnull=False)
    sets_11_point = all_sets_unfiltered.filter(match__set_type='11').count()
    sets_21_point = all_sets_unfiltered.filter(match__set_type='21').count()
    
    # Total sets and incomplete sets for current filter
    total_sets = all_sets.count()
    incomplete_sets = all_sets.filter(is_incomplete=True).count() if set_type_filter else 0
    
    context = {
        'total_matches': total_matches,
        'total_sets': total_sets,
        'incomplete_sets': incomplete_sets,
        'unique_players_count': unique_players_count,
        'sets_11_point': sets_11_point,
        'sets_21_point': sets_21_point,
        'set_type_filter': set_type_filter,
        'include_incomplete': include_incomplete,
        'player_performance_data': json.dumps(player_performance_data),
        'player_stats': player_stats,
        'player_box_data': json.dumps(player_box_data),
        'player_box_data_11': json.dumps(player_box_data_11),
        'player_box_data_21': json.dumps(player_box_data_21),
        'matches_by_date': json.dumps(matches_by_date),
        'match_extremes': match_extremes,
    }
    
    return render(request, 'squash/statistics.html', context)
