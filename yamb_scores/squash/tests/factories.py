"""Small helpers that create realistic Squash data for tests."""
from datetime import date, timedelta

from squash.models import SquashMatch, SquashPlayer, SquashSession, SquashSet


def make_player(name):
    return SquashPlayer.objects.create(name=name)


def make_match(player_1, player_2, sets, set_type="11", date_played=None, session=None):
    """sets: list of (player_1_points, player_2_points)."""
    match = SquashMatch.objects.create(
        player_1=player_1,
        player_2=player_2,
        date_played=date_played or date(2026, 8, 9),
        set_type=set_type,
        session=session,
    )
    for number, (p1, p2) in enumerate(sets, start=1):
        SquashSet.objects.create(match=match, set_number=number, player_1_points=p1, player_2_points=p2)
    return match


def make_squash_dataset():
    """Three players, both set types, a session, and some incomplete sets."""
    milan, guus, cleo = make_player("Milan"), make_player("Guus"), make_player("Cleo")
    start = date(2026, 1, 5)
    session = SquashSession.objects.create(date_played=start)
    make_match(milan, guus, [(11, 7), (9, 11), (11, 5)], session=session, date_played=start)
    make_match(guus, cleo, [(11, 13), (6, 4)], session=session, date_played=start)  # second set incomplete
    for week in range(1, 6):
        day = start + timedelta(weeks=week)
        make_match(milan, cleo, [(21, 15 + week), (18, 21)], set_type="21", date_played=day)
        make_match(milan, guus, [(11, 9), (12, 14)], date_played=day)
    make_match(milan, guus, [(21, 17), (22, 22)], set_type="21", date_played=date(2026, 8, 9))
    return milan, guus, cleo
