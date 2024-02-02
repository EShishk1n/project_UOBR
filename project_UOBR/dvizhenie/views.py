from datetime import date

import django
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.db.utils import IntegrityError

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .forms import DrillingRigForm, PadForm, RigPositionForm
from .models import DrillingRig, Pad, RigPosition, NextPosition, PositionRating
from .services.define_position import define_position_and_put_into_BD
from .services.get_rating import _get_marker_for_drilling_rig, _get_inf_about_RNB_department


def start_page(request):
    return render(request, 'dvizhenie/start_page.html')


class DrillingRigView(ListView):
    template_name = 'dvizhenie/rig.html'
    context_object_name = 'rigs'
    model = DrillingRig
    fields = '__all__'


class DrillingRigAddView(CreateView):
    form_class = DrillingRigForm
    template_name = 'dvizhenie/add_update_rig.html'
    success_url = reverse_lazy('rig')


class DrillingRigUpdateView(UpdateView):
    model = DrillingRig
    form_class = DrillingRigForm
    template_name = 'dvizhenie/add_update_rig.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')


class DrillingRigDeleteView(DeleteView):
    model = DrillingRig
    context_object_name = 'rig'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')
    template_name = 'dvizhenie/delete_rig.html'


class PadView(ListView):
    queryset = Pad.objects.exclude(status='drilling_or_drilled_pad')
    template_name = 'dvizhenie/pad.html'
    context_object_name = 'pads'


class PadAddView(CreateView):
    form_class = PadForm
    template_name = 'dvizhenie/add_update_pad.html'
    success_url = reverse_lazy('pad')


class PadUpdateView(UpdateView):
    model = Pad
    form_class = PadForm
    template_name = 'dvizhenie/add_update_pad.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('pad')


class PadDeleteView(DeleteView):
    model = Pad
    pk_url_kwarg = 'pk'
    context_object_name = 'pad'
    success_url = reverse_lazy('pad')
    template_name = 'dvizhenie/delete_pad.html'


class RigPositionView(ListView):
    template_name = 'dvizhenie/rig_position.html'
    context_object_name = 'rig_positions'
    model = RigPosition
    fields = '__all__'


class RigPositionUpdateView(UpdateView):
    model = RigPosition
    form_class = RigPositionForm
    context_object_name = 'rig_position'
    template_name = 'dvizhenie/update_rig_position.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig_position')


def define_next_position(request):
    if request.method == 'GET':
        define_position_and_put_into_BD()
    return redirect("next_position")


class NextPositionView(ListView):
    template_name = 'dvizhenie/next_position.html'
    context_object_name = 'next_positions'
    queryset = (NextPosition.objects.filter(status='Требуется подтверждение') |
                NextPosition.objects.filter(status='Изменено. Требуется подтверждение') |
                NextPosition.objects.filter(status='Отсутствют кандидаты') |
                NextPosition.objects.filter(status='Удалено пользователем'))
    ordering = "status"


class PositionRatingDetailView(View):

    def get(self, request, pk):
        next_position_object = NextPosition.objects.get(id=pk)
        position_rating = (
                PositionRating.objects.filter(current_position=next_position_object.current_position.id)
                & PositionRating.objects.filter(next_position=next_position_object.next_position.id))

        marker = _get_marker_for_drilling_rig(
            rig_for_define_next_position=position_rating[0].current_position)

        strategy = _get_inf_about_RNB_department(
            rig_for_define_next_position=position_rating[0].current_position)

        return render(request, 'dvizhenie/position_rating.html',
                      {"position_rating": position_rating[0], "marker": marker, "strategy": strategy})


class PositionRatingListView(View):

    def get(self, request, pk):
        next_position_object = NextPosition.objects.get(id=pk)
        position_rating = PositionRating.objects.filter(
            current_position=next_position_object.current_position.id).order_by('-common_rating')

        return render(request, 'dvizhenie/position_rating_all.html',
                      {"position_rating": position_rating})


def commit_next_position(request, pk):
    """Подтверждает (меняет статус пары в NextPosition на 'подтверждено') следующую позицию для БУ"""

    if request.method == 'GET':
        NextPosition.objects.filter(id=pk).update(status='Подтверждено')
        pad_id = NextPosition.objects.filter(id=pk)[0].next_position.id
        Pad.objects.filter(id=pad_id).update(status='commited_next_positions')

    return redirect('define_next_position')


def change_next_position(request, pk):
    """Берет из рейтинга другую позицию для БУ и вставляет в NextPosition со статусом
    'Изменено. Требуется подтверждение'"""

    if request.method == 'GET':
        different_next_position = PositionRating.objects.filter(id=pk)[0]
        try:
            NextPosition.objects.filter(current_position=different_next_position.current_position).update(
                next_position=different_next_position.next_position)
        except IntegrityError:
            NextPosition.objects.filter(next_position=different_next_position.next_position).update(next_position=None)
            NextPosition.objects.filter(current_position=different_next_position.current_position).update(
                next_position=different_next_position.next_position)
        finally:
            NextPosition.objects.filter(current_position=different_next_position.current_position).update(
                status='Изменено. Требуется подтверждение')

    return redirect('next_position')


def delete_next_position(request, pk):
    """Удаляет текущее предложение NextPosition"""

    if request.method == 'GET':
        NextPosition.objects.filter(id=pk).update(next_position=None)
        NextPosition.objects.filter(id=pk).update(status='Удалено пользователем')

    return redirect('next_position')


class CommitedNextPositionView(ListView):
    template_name = 'dvizhenie/commited_next_position.html'
    context_object_name = 'next_positions'
    queryset = NextPosition.objects.filter(status='Подтверждено')


def delete_commited_position(request, pk):
    """Меняет статус подтвержденной пары на 'Требуется подтверждение'"""

    if request.method == 'GET':
        next_position = NextPosition.objects.filter(id=pk)
        next_position.update(status='Требуется подтверждение')
        Pad.objects.filter(id=next_position[0].next_position.id).update(status='')
        next_position.delete()
    return redirect('commited_next_position')


def commit_commited_position(request, pk):
    """Переносит пару из подтвержденных позиций (актуальное движение) в расположение БУ"""

    if request.method == 'GET':
        next_position = NextPosition.objects.filter(id=pk)
        drilling_rig = next_position[0].current_position.drilling_rig
        pad = next_position[0].next_position

        RigPosition(drilling_rig=drilling_rig, pad=pad).save()

    return redirect('commited_next_position')
