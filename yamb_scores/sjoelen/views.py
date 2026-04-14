from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
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
