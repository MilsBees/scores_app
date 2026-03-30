from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Sum, Count, Q, Case, When, IntegerField, F, Max
from django.urls import reverse
from django.http import JsonResponse
from datetime import datetime, timedelta
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
                        defaults={"date_played": date_played},
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
        
        # Total points for / against
        points_for_as_p1 = (
            SquashSet.objects.filter(match__player_1=player).aggregate(Sum("player_1_points"))["player_1_points__sum"]
            or 0
        )
        points_for_as_p2 = (
            SquashSet.objects.filter(match__player_2=player).aggregate(Sum("player_2_points"))["player_2_points__sum"]
            or 0
        )
        points_against_as_p1 = (
            SquashSet.objects.filter(match__player_1=player).aggregate(Sum("player_2_points"))["player_2_points__sum"]
            or 0
        )
        points_against_as_p2 = (
            SquashSet.objects.filter(match__player_2=player).aggregate(Sum("player_1_points"))["player_1_points__sum"]
            or 0
        )

        points_for = points_for_as_p1 + points_for_as_p2
        points_against = points_against_as_p1 + points_against_as_p2
        total_points = points_for
        points_total = points_for + points_against
        point_win_pct = (points_for / points_total * 100.0) if points_total > 0 else 0.0
        
        # Total sets won
        sets_won_as_p1 = SquashSet.objects.filter(match__player_1=player, player_1_points__gt=F('player_2_points')).count()
        sets_won_as_p2 = SquashSet.objects.filter(match__player_2=player, player_2_points__gt=F('player_1_points')).count()
        total_sets_won = sets_won_as_p1 + sets_won_as_p2

        sets_lost_as_p1 = SquashSet.objects.filter(match__player_1=player, player_1_points__lt=F("player_2_points")).count()
        sets_lost_as_p2 = SquashSet.objects.filter(match__player_2=player, player_2_points__lt=F("player_1_points")).count()
        total_sets_lost = sets_lost_as_p1 + sets_lost_as_p2
        
        # Total sets played
        total_sets = SquashSet.objects.filter(Q(match__player_1=player) | Q(match__player_2=player)).count()
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
        },
    )

def h2h(request):
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
        
        # Get all opponents
        opponents = SquashPlayer.objects.filter(
            Q(squash_matches_as_p1__player_2=selected_player) |
            Q(squash_matches_as_p2__player_1=selected_player)
        ).distinct().order_by('name')
        
        for opponent in opponents:
            matches = SquashMatch.objects.filter(
                Q(player_1=selected_player, player_2=opponent) |
                Q(player_1=opponent, player_2=selected_player)
            ).prefetch_related('sets')
            
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
    # Preserve selected player in query string for sorting links.
    player_qs = f"player={selected_player_id}&" if selected_player_id else ""
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
        sort_links[col] = f"{player_qs}sort={col}&dir={next_dir}"
    
    return render(request, 'squash/h2h.html', {
        'players': players,
        'selected_player': selected_player,
        'h2h_data': h2h_data,
        'sort': sort,
        'dir': direction,
        'sort_links': sort_links,
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


def analysis(request):
    """Analysis page showing trends in player performance over time (by session or match)"""
    date_range = request.GET.get('range', '30')
    
    # Determine date range
    today = datetime.now().date()
    if date_range == '60':
        start_date = today - timedelta(days=60)
    elif date_range == 'ytd':
        start_date = datetime(today.year, 1, 1).date()
    else:  # default to 30
        start_date = today - timedelta(days=30)
        date_range = '30'
    
    # Get all players
    players = SquashPlayer.objects.all().order_by('name')
    
    # Get all matches in date range (from sessions AND standalone matches)
    matches = SquashMatch.objects.filter(
        date_played__gte=start_date,
        date_played__lte=today
    ).prefetch_related('sets').order_by('date_played')
    
    if not matches.exists():
        context = {
            'trend_data': {},
            'all_sessions': [],
            'date_range': date_range,
            'start_date': start_date,
            'players': [],
        }
        return render(request, 'squash/analysis.html', context)
    
    # Group matches by date
    matches_by_date = {}
    for match in matches:
        date_key = match.date_played.isoformat()
        if date_key not in matches_by_date:
            matches_by_date[date_key] = []
        matches_by_date[date_key].append(match)
    
    # Calculate trend data for each player by date
    trend_data = {}
    
    for player in players:
        player_dates = []
        has_data = False
        
        for date_key in sorted(matches_by_date.keys()):
            matches_on_date = matches_by_date[date_key]
            
            # Get all matches for this player on this date
            player_matches = [m for m in matches_on_date if m.player_1 == player or m.player_2 == player]
            
            if not player_matches:
                continue
            
            # Calculate stats for this date
            matches_won = 0
            matches_total = 0
            sets_won = 0
            sets_total = 0
            points_for = 0
            points_against = 0
            
            for match in player_matches:
                sets = match.sets.all()
                if not sets.exists():
                    continue
                
                # Calculate player's performance in this match
                if player == match.player_1:
                    match_sets_won = sum(1 for s in sets if s.player_1_points > s.player_2_points)
                    match_sets_total = sets.count()
                    match_points_for = sum(s.player_1_points for s in sets)
                    match_points_against = sum(s.player_2_points for s in sets)
                else:
                    match_sets_won = sum(1 for s in sets if s.player_2_points > s.player_1_points)
                    match_sets_total = sets.count()
                    match_points_for = sum(s.player_2_points for s in sets)
                    match_points_against = sum(s.player_1_points for s in sets)
                
                # Determine match result (more sets won = match win)
                if match_sets_won > match_sets_total - match_sets_won:
                    matches_won += 1
                matches_total += 1
                sets_won += match_sets_won
                sets_total += match_sets_total
                points_for += match_points_for
                points_against += match_points_against
            
            if matches_total > 0:
                has_data = True
                match_win_pct = (matches_won / matches_total * 100)
                set_win_pct = (sets_won / sets_total * 100) if sets_total > 0 else 0
                point_win_pct = (points_for / (points_for + points_against) * 100) if (points_for + points_against) > 0 else 0
                
                player_dates.append({
                    'date': date_key,
                    'match_win_pct': round(match_win_pct, 1),
                    'set_win_pct': round(set_win_pct, 1),
                    'point_win_pct': round(point_win_pct, 1),
                })
        
        if has_data:
            trend_data[player.name] = player_dates
    
    # Get all dates (for x-axis)
    all_dates = []
    for player_data in trend_data.values():
        for date_data in player_data:
            if date_data['date'] not in all_dates:
                all_dates.append(date_data['date'])
    all_dates.sort()
    
    context = {
        'trend_data': trend_data,
        'all_sessions': all_dates,
        'date_range': date_range,
        'start_date': start_date,
        'players': list(trend_data.keys()),
    }
    
    return render(request, 'squash/analysis.html', context)
