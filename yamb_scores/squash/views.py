from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, Q, Case, When, IntegerField, F
from django.urls import reverse
from .models import SquashMatch, SquashSet, SquashPlayer
from .forms import SquashMatchForm, SquashSetFormSet

def index(request):
    return render(request, 'squash/index.html')

def new_match(request):
    if request.method == 'POST':
        form = SquashMatchForm(request.POST)
        match = SquashMatch()
        formset = SquashSetFormSet(request.POST, instance=match)
        
        if form.is_valid() and formset.is_valid():
            match = form.save()
            formset.instance = match
            
            # Set set numbers
            for i, form_instance in enumerate(formset.forms):
                if form_instance.cleaned_data.get('player_1_points') is not None:
                    form_instance.instance.set_number = i + 1
            
            formset.save()
            return redirect(reverse('squash:match_list'))
    else:
        form = SquashMatchForm()
        formset = SquashSetFormSet(instance=SquashMatch())
    
    return render(request, 'squash/new_match.html', {
        'form': form,
        'formset': formset,
    })

def match_list(request):
    matches = SquashMatch.objects.prefetch_related('sets').order_by('-date_played')[:50]
    return render(request, 'squash/match_list.html', {'matches': matches})

def leaderboard(request):
    players = SquashPlayer.objects.all()
    
    player_stats = []
    for player in players:
        # Matches where player participated
        matches = SquashMatch.objects.filter(Q(player_1=player) | Q(player_2=player))
        
        # Total points
        p1_points = SquashSet.objects.filter(match__player_1=player).aggregate(Sum('player_1_points'))['player_1_points__sum'] or 0
        p2_points = SquashSet.objects.filter(match__player_2=player).aggregate(Sum('player_2_points'))['player_2_points__sum'] or 0
        total_points = p1_points + p2_points
        
        # Total sets won
        sets_won_as_p1 = SquashSet.objects.filter(match__player_1=player, player_1_points__gt=F('player_2_points')).count()
        sets_won_as_p2 = SquashSet.objects.filter(match__player_2=player, player_2_points__gt=F('player_1_points')).count()
        total_sets_won = sets_won_as_p1 + sets_won_as_p2
        
        # Total sets played
        total_sets = SquashSet.objects.filter(Q(match__player_1=player) | Q(match__player_2=player)).count()
        
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
        
        if total_sets > 0:  # Only include players with matches
            player_stats.append({
                'player': player,
                'total_points': total_points,
                'total_sets_won': total_sets_won,
                'total_sets': total_sets,
                'last_match_date': last_match_date,
                'matches_won': matches_won,
                'matches_lost': matches_lost,
                'matches_drawn': matches_drawn,
            })
    
    # Sort by total sets won
    player_stats.sort(key=lambda x: x['total_sets_won'], reverse=True)
    
    return render(request, 'squash/leaderboard.html', {'player_stats': player_stats})

def h2h(request):
    players = SquashPlayer.objects.all().order_by('name')
    selected_player = None
    h2h_data = []
    
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
    
    return render(request, 'squash/h2h.html', {
        'players': players,
        'selected_player': selected_player,
        'h2h_data': h2h_data,
    })
