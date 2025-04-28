import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Q

from .models import (
    Category, Question, Choice,
    GameMatch, Round, RoundSession, AnswerLog
)
from .forms import SignUpForm
from .constants import (
    QUESTIONS_PER_ROUND, TIME_LIMIT_SECONDS,
    TOTAL_ROUNDS, CHOICE_COUNT
)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


class HomeView(TemplateView):
    template_name = 'game/home.html'


@login_required
def join_match(request):
    # If already in an active or waiting match, go check status
    if GameMatch.objects.filter(
        Q(player1=request.user) | Q(player2=request.user),
        status__in=['WAITING', 'IN_ROUND']
    ).exists():
        return redirect('match_status')

    # Try to pair with another waiting player
    waiting = GameMatch.objects.filter(status='WAITING').exclude(player1=request.user).first()
    if waiting:
        waiting.player2    = request.user
        waiting.status     = 'IN_ROUND'
        waiting.started_at = timezone.now()
        waiting.save()
        return redirect('start_round', match_id=waiting.id)

    # Otherwise create a new match and wait
    GameMatch.objects.create(player1=request.user)
    return redirect('match_status')


@login_required
def match_status(request):
    # Show waiting screen or jump into the in-progress match
    match = GameMatch.objects.filter(
        Q(player1=request.user) | Q(player2=request.user),
        status__in=['WAITING', 'IN_ROUND']
    ).first()

    if not match:
        return redirect('home')

    if match.status == 'IN_ROUND':
        return redirect('start_round', match_id=match.id)

    return render(request, 'game/waiting.html', {'match': match})


@login_required
def start_round(request, match_id):
    match = get_object_or_404(GameMatch, id=match_id)

    # If all rounds played, show match summary
    if match.current_round > TOTAL_ROUNDS:
        return redirect('match_complete', match_id=match.id)

    # Who’s chooser this round?
    chooser = match.player1 if match.current_round % 2 == 1 else match.player2

    # Has this round already been created? If so, skip straight into play_round
    existing = Round.objects.filter(
        match=match,
        round_number=match.current_round
    ).first()
    if existing:
        phase = 'self' if request.user == chooser else 'opponent'
        return redirect('play_round', round_id=existing.id, user_phase=phase)

    # If you’re not the chooser, show “waiting for choice” (same as before)
    if request.user != chooser:
        return render(request, 'game/wait_other_choice.html', {
            'match': match,
            'round_num': match.current_round
        })

    # Gather IDs of categories already picked in prior rounds
    used_ids = match.rounds.values_list('category_id', flat=True)
    # Available = those not yet used
    available = Category.objects.exclude(id__in=used_ids)

    # If fewer than CHOICE_COUNT remain, just use whatever is left
    options = list(available)
    if len(options) > CHOICE_COUNT:
        options = random.sample(options, CHOICE_COUNT)

    if request.method == 'POST':
        selected_slug = request.POST.get('category')
        category = get_object_or_404(Category, slug=selected_slug)

        # Create the Round and sessions
        rnd = Round.objects.create(
            match=match,
            round_number=match.current_round,
            chooser=request.user,
            category=category
        )
        for player in [match.player1, match.player2]:
            RoundSession.objects.create(round=rnd, user=player)

        return redirect('play_round', round_id=rnd.id, user_phase='self')

    return render(request, 'game/select_category.html', {
        'choices': options,
        'round_num': match.current_round
    })


@login_required
def play_round(request, round_id, user_phase):
    rnd = get_object_or_404(Round, id=round_id)

    # Determine order: [chooser, opponent]
    opponent    = rnd.match.player2 if rnd.chooser == rnd.match.player1 else rnd.match.player1
    order       = [rnd.chooser, opponent]
    phase_index = 0 if user_phase == 'self' else 1

    # If it’s not your turn, send to waiting_phase
    if request.user != order[phase_index]:
        return redirect('waiting_phase', round_id=rnd.id, phase=user_phase)

    # Get (or create) this player’s RoundSession
    session = get_object_or_404(RoundSession, round=rnd, user=request.user)

    # On first view, seed AnswerLog entries
    if not session.answers.exists():
        qs = rnd.category.question_set.filter(approved=True).order_by('?')[:QUESTIONS_PER_ROUND]
        for q in qs:
            AnswerLog.objects.create(session=session, question=q)

    logs = list(session.answers.all())
    # Next unanswered
    try:
        log = next(l for l in logs if l.selected_choice is None)
    except StopIteration:
        # All done → to round_complete
        return redirect('round_complete', round_id=rnd.id)

    idx = logs.index(log)

    if request.method == 'POST':
        choice = get_object_or_404(Choice, id=request.POST['choice'])
        log.selected_choice = choice
        log.is_correct      = choice.is_correct
        log.save()

        if choice.is_correct:
            session.score += 1
            session.save()

        # More questions?
        if idx + 1 < QUESTIONS_PER_ROUND:
            return redirect('play_round', round_id=rnd.id, user_phase=user_phase)

        # Phase done
        session.completed_at = timezone.now()
        session.save()

        # If chooser just finished, move to opponent’s turn
        if user_phase == 'self':
            return redirect('play_round', round_id=rnd.id, user_phase='opponent')

        # Both done → wrap up round
        match = rnd.match
        match.current_round += 1
        if match.current_round > TOTAL_ROUNDS:
            match.status = 'COMPLETED'
        match.save()
        return redirect('round_complete', round_id=rnd.id)

    return render(request, 'game/quiz_question.html', {
        'question':  log.question,
        'choices':   log.question.choices.all(),
        'time_limit': TIME_LIMIT_SECONDS,
        'idx':        idx + 1,
        'total':      QUESTIONS_PER_ROUND,
    })


@login_required
def waiting_phase(request, round_id, phase):
    rnd = get_object_or_404(Round, id=round_id)
    return render(request, 'game/waiting_phase.html', {
        'round': rnd,
        'phase': phase
    })


@login_required
def round_complete(request, round_id):
    rnd = get_object_or_404(Round, id=round_id)
    sess1 = get_object_or_404(RoundSession, round=rnd, user=rnd.match.player1)
    sess2 = get_object_or_404(RoundSession, round=rnd, user=rnd.match.player2)
    return render(request, 'game/round_complete.html', {
        'rnd':   rnd,
        'sess1': sess1,
        'sess2': sess2,
    })


@login_required
def match_complete(request, match_id):
    match   = get_object_or_404(GameMatch, id=match_id)
    results = []
    total_p1 = total_p2 = 0

    for rnd in match.rounds.order_by('round_number'):
        s1 = rnd.sessions.get(user=match.player1)
        s2 = rnd.sessions.get(user=match.player2)
        results.append((rnd.round_number, s1.score, s2.score))
        total_p1 += s1.score
        total_p2 += s2.score

    return render(request, 'game/match_complete.html', {
        'match':    match,
        'results':  results,
        'total_p1': total_p1,
        'total_p2': total_p2,
    })