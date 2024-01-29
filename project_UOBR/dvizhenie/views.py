from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from .forms import DrillingRigForm, PadForm, RigPositionForm
from .models import DrillingRig, Pad, RigPosition, NextPosition, PositionRating
from .services.define_position import define_position_and_put_into_BD
from .services.services import get_info_from_BD


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
    model = Pad
    template_name = 'dvizhenie/pad.html'
    context_object_name = 'pads'
    fields = '__all__'


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


# class NextPositionView(ListView):
#     model = NextPosition
#     template_name = 'info/rig_position.html'
#     context_object_name = 'rig_positions'


def define_next_position(request):
    define_position_and_put_into_BD()
    return redirect("next_position")


class NextPositionView(ListView):
    template_name = 'dvizhenie/next_position.html'
    context_object_name = 'next_positions'
    model = NextPosition
    fields = '__all__'


class PositionRatingDetailView(View):

    def get(self, request, pk):
        next_position_object = NextPosition.objects.get(id=pk)
        position_rating = (
                PositionRating.objects.filter(current_position=next_position_object.current_position.id)
                & PositionRating.objects.filter(next_position=next_position_object.next_position.id))

        marker = 'стандартная БУ'
        if position_rating[0].current_position.drilling_rig.type in ('ZJ-50 0.5эш', 'ZJ-50 2эш'):
            marker = position_rating[0].current_position.drilling_rig.type
        if position_rating[0].current_position.drilling_rig.contractor == 'СНПХ':
            marker = position_rating[0].current_position.drilling_rig.contractor

        if position_rating[0].current_position.drilling_rig.contractor == 'НФ РНБ':
            if position_rating[0].current_position.field in ('ПРОл', 'ПРОп'):
                strategy = 'НФ 1ый УБР'
            elif position_rating[0].current_position.field in ('ПРЗ', 'САЛ'):
                strategy = 'НФ 2ой УБР'
            else:
                strategy = 'НФ 3ий УБР'
        elif position_rating[0].current_position.drilling_rig.contractor == 'ХМФ РНБ':
            if position_rating[0].current_position.field in ('ПРОл', 'ПРОп', 'ПРЗ', 'САЛ'):
                strategy = 'ХМФ 1ый УБР'
            else:
                strategy = 'ХМФ 4ый УБР'
        else:
            strategy = position_rating[0].current_position.drilling_rig.contractor

        return render(request, 'dvizhenie/position_rating.html',
                      {"position_rating": position_rating[0], "marker": marker, "strategy": strategy})


class PositionRatingListView(View):

    def get(self, request, pk):
        next_position_object = NextPosition.objects.get(id=pk)
        position_rating = PositionRating.objects.filter(
            current_position=next_position_object.current_position.id).order_by('-common_rating')

        return render(request, 'dvizhenie/position_rating_all.html',
                      {"position_rating": position_rating})
