from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from dvizhenie.forms import DefinePositionForm
from dvizhenie.models import NextPosition, PositionRating, RigPosition
from dvizhenie.services.define_position.define_position import define_position_and_put_into_DB
from dvizhenie.services.funcs_for_views.change_next_position import _change_next_position

from dvizhenie.services.funcs_for_views.define_next_position_after_changes import define_next_position_after_changes
from dvizhenie.services.funcs_for_views.update_NextPosition import update_NextPosition
from dvizhenie.services.give_statuses_to_pads.give_status_free_to_pads import give_status_free_to_pads
from dvizhenie.services.give_statuses_to_pads.give_status_reserved_to_pads import give_status_reserved_to_pads


class NextPositionView(LoginRequiredMixin, PermissionRequiredMixin, ListView, FormMixin):
    """Отображает экземпляры из модели NextPosition по которым требуются действия специалиста"""

    template_name = 'dvizhenie/NextPositionsViews_templates/next_position.html'
    context_object_name = 'next_positions'
    queryset = NextPosition.objects.exclude(status='commited').select_related('next_position').select_related(
        'current_position').select_related('current_position__pad').select_related(
        'current_position__drilling_rig__type').select_related('current_position__drilling_rig__contractor')
    ordering = "current_position__end_date"
    permission_required = 'dvizhenie.view_nextposition'
    form_class = DefinePositionForm

    @transaction.atomic
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            define_position_and_put_into_DB(start_date_for_calculation=form.cleaned_data['start_date_for_calculation'],
                                            end_date_for_calculation=form.cleaned_data['end_date_for_calculation'])
            return redirect('next_position')

        else:
            return render(request, 'dvizhenie/NextPositionsViews_templates/next_position_not_valid_data.html')


@login_required(login_url='accounts/')
def get_detail_info_for_next_position(request, pk):
    """Получает подробную информацию об экземляре NextPosition (рейтинг, маркер, стратегию)"""

    if request.method == 'GET':
        next_position_object = NextPosition.objects.get(id=pk)
        try:
            position_rating = (
                PositionRating.objects.filter(current_position=next_position_object.current_position.id,
                                              next_position=next_position_object.next_position.id).select_related(
                    'current_position').select_related('current_position__pad').select_related(
                    'current_position__drilling_rig').select_related(
                    'current_position__drilling_rig__type').select_related(
                    'next_position'))
        except AttributeError:
            position_rating = [None]

        return render(request, 'dvizhenie/NextPositionsViews_templates/position_rating.html',
                      {"position_rating": position_rating[0]})


@login_required(login_url='accounts/')
def get_detail_info_for_position_rating(request, pk):
    """Получает подробную информацию об экземляре PositionRating (рейтинг, маркер, стратегию)"""

    if request.method == 'GET':
        position_rating = PositionRating.objects.filter(id=pk).select_related('current_position').select_related(
            'current_position__pad').select_related('current_position__drilling_rig').select_related(
            'current_position__drilling_rig__type').select_related('next_position')

        return render(request, 'dvizhenie/NextPositionsViews_templates/position_rating.html',
                      {"position_rating": position_rating[0]})


@login_required(login_url='accounts/')
def get_rating_for_all_possible_next_positions(request, pk):
    """Получает все экземпляры модели PositionRating для БУ, для которой определяется следующая позиция"""

    if request.method == 'GET':
        next_position_object = NextPosition.objects.get(id=pk)
        position_rating = PositionRating.objects.filter(
            current_position=next_position_object.current_position.id).order_by('-common_rating').select_related(
            'current_position').select_related(
            'current_position__pad').select_related('current_position__drilling_rig').select_related(
            'current_position__drilling_rig__contractor').select_related(
            'current_position__drilling_rig__type').select_related('next_position')

        return render(request, 'dvizhenie/NextPositionsViews_templates/position_rating_all.html',
                      {"position_rating": position_rating})


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
@transaction.atomic
def commit_next_position(request, pk):
    """Подтверждает (меняет статус пары в NextPosition на 'подтверждено') следующую позицию для БУ"""

    if request.method == 'GET':
        update_NextPosition(next_position_queryset=NextPosition.objects.filter(id=pk), status='commited')
        give_status_reserved_to_pads()

    return redirect('next_position')


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
def change_next_position(request, pk):
    """Берет из рейтинга другую позицию для БУ и вставляет в NextPosition со статусом
    'Изменено. Требуется подтверждение'"""

    if request.method == 'GET':
        _change_next_position(different_next_position=PositionRating.objects.get(id=pk))

        define_next_position_after_changes()

    return redirect('next_position')


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
@transaction.atomic
def delete_next_position(request, pk):
    """Удаляет текущее предложение NextPosition"""

    if request.method == 'GET':
        update_NextPosition(next_position_queryset=NextPosition.objects.filter(id=pk), status='deleted',
                            reset_next_position=True)

        define_next_position_after_changes()

    return redirect('next_position')


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
@transaction.atomic
def reset_all_changes(request):
    """Сбрасывает все пользовательские изменения"""

    if request.method == 'GET':
        update_NextPosition(next_position_queryset=NextPosition.objects.exclude(status='commited'), status='default',
                            reset_next_position=True)

        define_next_position_after_changes()

    return redirect('next_position')


class CommitedNextPositionView(LoginRequiredMixin, ListView):
    """Отображает, подтвержденные специалистом, экземплры модели NextPosition"""

    template_name = 'dvizhenie/NextPositionsViews_templates/commited_next_position.html'
    context_object_name = 'next_positions'
    queryset = NextPosition.objects.filter(status='commited').order_by('current_position__end_date').select_related(
        'next_position').select_related(
        'current_position').select_related('current_position__pad').select_related(
        'current_position__drilling_rig__type').select_related('current_position__drilling_rig__contractor')


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
@transaction.atomic
def delete_commited_position(request, pk):
    """Меняет статус подтвержденной пары на 'Требуется подтверждение'"""

    if request.method == 'GET':
        update_NextPosition(next_position_queryset=NextPosition.objects.filter(id=pk), status='deleted',
                            reset_next_position=True)

        give_status_free_to_pads()

    return redirect('commited_next_position')


@login_required(login_url='accounts/')
@permission_required(perm='dvizhenie.change_nextposition', raise_exception=True)
@transaction.atomic
def commit_commited_position(request, pk):
    """Переносит пару из подтвержденных позиций (актуальное движение) в расположение БУ"""

    if request.method == 'GET':

        next_position = NextPosition.objects.get(id=pk)
        update_NextPosition(next_position_queryset=NextPosition.objects.filter(id=pk), delete_next_position=True)

        drilling_rig = next_position.current_position.drilling_rig
        pad = next_position.next_position
        RigPosition(drilling_rig=drilling_rig, pad=pad).save()

    return redirect('commited_next_position')
