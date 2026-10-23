import hashlib
import json
from datetime import date

from decouple import config
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .decorators import SESSION_FLAG, noindex, wedding_view
from .models import BoardColumn, Card, Subtask
from .texts import UI_TEXT

SESSION_MAX_AGE = 90 * 24 * 60 * 60
LOGIN_FAILURE_TTL = 15 * 60
LOGIN_FAILURE_LIMIT = 5


def _set_secure_session_cookie(request, response):
    request.session.save()
    response.set_cookie(
        settings.SESSION_COOKIE_NAME,
        request.session.session_key,
        max_age=request.session.get_expiry_age(),
        path=settings.SESSION_COOKIE_PATH,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=True,
        httponly=True,
        samesite='Lax',
    )
    request.session.modified = False


def _client_ip(request):
    return request.META.get('REMOTE_ADDR', 'unknown')


def _rate_limit_keys(request):
    ip_hash = hashlib.sha256(_client_ip(request).encode('utf-8')).hexdigest()
    prefix = f'wedding:login:{ip_hash}'
    return f'{prefix}:failures', f'{prefix}:lock'


def _register_login_failure(request):
    failure_key, lock_key = _rate_limit_keys(request)
    if not cache.add(failure_key, 1, timeout=LOGIN_FAILURE_TTL):
        failures = cache.get(failure_key, 0) + 1
        cache.set(failure_key, failures, timeout=LOGIN_FAILURE_TTL)
    else:
        failures = 1
    if failures >= LOGIN_FAILURE_LIMIT:
        lock_seconds = min(60 * (2 ** ((failures - LOGIN_FAILURE_LIMIT) // LOGIN_FAILURE_LIMIT)), 15 * 60)
        cache.set(lock_key, lock_seconds, timeout=lock_seconds)


def _json_body(request):
    try:
        value = json.loads(request.body or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse({'error': 'Invalid JSON.'}, status=400)
    if not isinstance(value, dict):
        return None, JsonResponse({'error': 'JSON object required.'}, status=400)
    return value, None


def _serialize_subtask(subtask):
    return {
        'id': subtask.pk,
        'title': subtask.title,
        'done': subtask.is_done,
        'position': subtask.position,
    }


def _serialize_card(card):
    return {
        'id': card.pk,
        'title': card.title,
        'owner': card.owner,
        'notes': card.notes,
        'due_date': card.due_date.isoformat() if card.due_date else None,
        'column_id': card.column_id,
        'position': card.position,
        'created_at': card.created_at.isoformat(),
        'updated_at': card.updated_at.isoformat(),
        'subtasks': [_serialize_subtask(item) for item in card.subtasks.all()],
    }


def _serialize_board():
    columns = []
    for column in BoardColumn.objects.all():
        cards = Card.objects.filter(column=column).prefetch_related('subtasks')
        columns.append({
            'id': column.pk,
            'name': column.name,
            'position': column.position,
            'cards': [_serialize_card(card) for card in cards],
        })
    return {
        'columns': columns,
        'counts': {
            'done': Card.objects.filter(column__name='Klaar').count(),
            'total': Card.objects.count(),
        },
    }


@noindex
@require_http_methods(['GET', 'POST'])
def login_view(request):
    passphrase_hash = config('WEDDING_PASSPHRASE_HASH', default='')
    if request.method == 'POST':
        if not passphrase_hash:
            return render(request, 'wedding/login.html', {
                'texts': UI_TEXT, 'error': UI_TEXT['login_unavailable'],
            }, status=503)

        failure_key, lock_key = _rate_limit_keys(request)
        if cache.get(lock_key):
            return render(request, 'wedding/login.html', {
                'texts': UI_TEXT, 'error': UI_TEXT['login_limited'],
            }, status=429)

        submitted = request.POST.get('passphrase', '')
        if check_password(submitted, passphrase_hash):
            cache.delete(failure_key)
            cache.delete(lock_key)
            request.session.cycle_key()
            request.session[SESSION_FLAG] = True
            request.session.set_expiry(SESSION_MAX_AGE)
            response = redirect(reverse('wedding:board'))
            _set_secure_session_cookie(request, response)
            response['X-Robots-Tag'] = 'noindex, nofollow'
            return response

        _register_login_failure(request)
        return render(request, 'wedding/login.html', {
            'texts': UI_TEXT, 'error': UI_TEXT['login_failed'],
        }, status=401)

    return render(request, 'wedding/login.html', {'texts': UI_TEXT})


@wedding_view()
@require_http_methods(['GET'])
def board(request):
    response = render(request, 'wedding/board.html', {'texts': UI_TEXT})
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response


@wedding_view()
@require_POST
def logout_view(request):
    request.session.flush()
    response = redirect(reverse('wedding:login'))
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response


@wedding_view(api=True)
@require_http_methods(['GET'])
def board_api(request):
    response = JsonResponse(_serialize_board())
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response


def _validate_card_fields(data, current=None):
    values = {}
    if 'title' in data or current is None:
        title = data.get('title', '')
        if not isinstance(title, str) or not title.strip() or len(title.strip()) > 200:
            return None, 'Title must contain 1 to 200 characters.'
        values['title'] = title.strip()
    if 'owner' in data or current is None:
        owner = data.get('owner', '')
        if owner not in Card.Owner.values:
            return None, 'Invalid owner.'
        values['owner'] = owner
    if 'notes' in data:
        notes = data.get('notes', '')
        if not isinstance(notes, str) or len(notes) > 10000:
            return None, 'Notes must be at most 10000 characters.'
        values['notes'] = notes
    if 'due_date' in data:
        due_date = data['due_date']
        if due_date in ('', None):
            values['due_date'] = None
        elif isinstance(due_date, str):
            try:
                values['due_date'] = date.fromisoformat(due_date)
            except ValueError:
                return None, 'Invalid due date.'
        else:
            return None, 'Invalid due date.'
    return values, None


def _sync_subtasks(card, submitted):
    existing = {item.pk: item for item in card.subtasks.all()}
    keep_ids = set()
    new_items = []
    for position, item in enumerate(submitted):
        if not isinstance(item, dict):
            return 'Each subtask must be an object.'
        title = item.get('title')
        done = item.get('done', False)
        if not isinstance(title, str) or not title.strip() or len(title.strip()) > 200:
            return 'Subtask titles must contain 1 to 200 characters.'
        if not isinstance(done, bool):
            return 'Subtask done values must be true or false.'
        subtask_id = item.get('id')
        if subtask_id is None:
            new_items.append(Subtask(card=card, title=title.strip(), is_done=done, position=position))
            continue
        try:
            subtask_id = int(subtask_id)
        except (TypeError, ValueError):
            return 'Invalid subtask id.'
        subtask = existing.get(subtask_id)
        if subtask is None:
            return 'Subtask does not belong to this card.'
        subtask.title = title.strip()
        subtask.is_done = done
        subtask.position = position
        keep_ids.add(subtask_id)
    card.subtasks.exclude(pk__in=keep_ids).delete()
    if keep_ids:
        Subtask.objects.bulk_update(
            [existing[item_id] for item_id in keep_ids], ['title', 'is_done', 'position']
        )
    if new_items:
        Subtask.objects.bulk_create(new_items)
    return None


def _validate_subtasks(submitted, card=None):
    if not isinstance(submitted, list):
        return 'Subtasks must be a list.'
    existing_ids = set(card.subtasks.values_list('pk', flat=True)) if card else set()
    seen_ids = set()
    for item in submitted:
        if not isinstance(item, dict):
            return 'Each subtask must be an object.'
        title = item.get('title')
        if not isinstance(title, str) or not title.strip() or len(title.strip()) > 200:
            return 'Subtask titles must contain 1 to 200 characters.'
        if not isinstance(item.get('done', False), bool):
            return 'Subtask done values must be true or false.'
        if item.get('id') is not None:
            try:
                subtask_id = int(item['id'])
            except (TypeError, ValueError):
                return 'Invalid subtask id.'
            if subtask_id not in existing_ids or subtask_id in seen_ids:
                return 'Subtask does not belong to this card.'
            seen_ids.add(subtask_id)
    return None


@wedding_view(api=True)
@require_http_methods(['POST'])
def cards_api(request):
    data, error_response = _json_body(request)
    if error_response:
        return error_response
    values, error = _validate_card_fields(data)
    if error:
        return JsonResponse({'error': error}, status=400)
    if 'subtasks' in data:
        error = _validate_subtasks(data['subtasks'])
        if error:
            return JsonResponse({'error': error}, status=400)
    try:
        column = BoardColumn.objects.get(pk=data.get('column_id'))
    except (BoardColumn.DoesNotExist, TypeError, ValueError):
        return JsonResponse({'error': 'Invalid column.'}, status=400)

    with transaction.atomic():
        column = BoardColumn.objects.select_for_update().get(pk=column.pk)
        card = Card.objects.create(**values, column=column, position=Card.objects.filter(column=column).count())
        if 'subtasks' in data:
            _sync_subtasks(card, data['subtasks'])
    return JsonResponse(_serialize_card(card), status=201)


@wedding_view(api=True)
@require_http_methods(['PUT', 'PATCH', 'DELETE'])
def card_api(request, card_id):
    if request.method == 'DELETE':
        with transaction.atomic():
            list(BoardColumn.objects.select_for_update().order_by('pk'))
            try:
                card = Card.objects.select_for_update().get(pk=card_id)
            except Card.DoesNotExist:
                return JsonResponse({'error': 'Card not found.'}, status=404)
            column = BoardColumn.objects.select_for_update().get(pk=card.column_id)
            cards = list(Card.objects.select_for_update().filter(column=column).order_by('position', 'pk'))
            cards.remove(card)
            card.delete()
            for position, remaining in enumerate(cards):
                remaining.position = position
            Card.objects.bulk_update(cards, ['position'])
        return JsonResponse({'deleted': True})
    data, error_response = _json_body(request)
    if error_response:
        return error_response
        return error_response
    with transaction.atomic():
        try:
            card = Card.objects.select_for_update().get(pk=card_id)
        except Card.DoesNotExist:
            return JsonResponse({'error': 'Card not found.'}, status=404)
        values, error = _validate_card_fields(data, current=card)
        if error:
            return JsonResponse({'error': error}, status=400)
        if 'subtasks' in data:
            error = _validate_subtasks(data['subtasks'], card)
            if error:
                return JsonResponse({'error': error}, status=400)
        for field, value in values.items():
            setattr(card, field, value)
        card.save()
        if 'subtasks' in data:
            _sync_subtasks(card, data['subtasks'])
    return JsonResponse(_serialize_card(card))


@wedding_view(api=True)
@require_http_methods(['POST'])
def move_card_api(request, card_id):
    data, error_response = _json_body(request)
    if error_response:
        return error_response
    try:
        target_id = int(data.get('column_id'))
        target_position = int(data.get('position', 0))
        if target_position < 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid destination or position.'}, status=400)

    with transaction.atomic():
        try:
            locked_columns = list(BoardColumn.objects.select_for_update().order_by('pk'))
            column_by_id = {column.pk: column for column in locked_columns}
            if target_id not in column_by_id:
                raise KeyError(target_id)
            card = Card.objects.select_for_update().get(pk=card_id)
        except (Card.DoesNotExist, KeyError):
            return JsonResponse({'error': 'Card or column not found.'}, status=404)

        source_id = card.column_id
        if source_id == target_id:
            cards = list(Card.objects.select_for_update().filter(column_id=source_id).order_by('position', 'pk'))
            cards.remove(card)
            cards.insert(min(target_position, len(cards)), card)
            updates = [(item, source_id, position) for position, item in enumerate(cards)]
        else:
            source_cards = list(Card.objects.select_for_update().filter(column_id=source_id).order_by('position', 'pk'))
            target_cards = list(Card.objects.select_for_update().filter(column_id=target_id).order_by('position', 'pk'))
            source_cards.remove(card)
            target_cards.insert(min(target_position, len(target_cards)), card)
            updates = (
                [(item, source_id, position) for position, item in enumerate(source_cards)]
                + [(item, target_id, position) for position, item in enumerate(target_cards)]
            )
        now = timezone.now()
        for item, column_id, position in updates:
            item.column_id = column_id
            item.position = position
            item.updated_at = now
        Card.objects.bulk_update([item for item, _, _ in updates], ['column', 'position', 'updated_at'])
        card = Card.objects.get(pk=card_id)
    return JsonResponse(_serialize_card(card))
