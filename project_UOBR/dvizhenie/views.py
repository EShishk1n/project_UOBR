from django.shortcuts import render
from django.urls import reverse_lazy

from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import DrillingRig, Pad, RigPosition, NextPosition
from .services.define_position import define_position_and_put_into_BD
from .services.services import get_info_from_BD


def start_page(request):
    return render(request, 'dvizhenie/start_page.html')


class DrillingRigView(ListView):
    model = DrillingRig
    template_name = 'dvizhenie/drilling_rig.html'
    context_object_name = 'rigs'


class DrillingRigAddView(CreateView):
    model = DrillingRig
    fields = '__all__'
    template_name = 'dvizhenie/drilling_rig.html'
    success_url = reverse_lazy('rig')


class DrillingRigUpdateView(UpdateView):
    model = DrillingRig
    fields = '__all__'
    template_name = 'dvizhenie/drilling_rig.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')


class DrillingRigDeleteView(DeleteView):
    model = DrillingRig
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')
    template_name = 'dvizhenie/drilling_rig.html'


class PadView(ListView):
    model = Pad
    template_name = 'dvizhenie/pad.html'
    context_object_name = 'pads'


class PadAddView(CreateView):
    model = Pad
    fields = '__all__'
    template_name = 'dvizhenie/pad.html'
    success_url = reverse_lazy('pad')


class PadUpdateView(UpdateView):
    model = Pad
    fields = '__all__'
    template_name = 'dvizhenie/pad.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('pad')


class PadDeleteView(DeleteView):
    model = DrillingRig
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('pad')
    template_name = 'dvizhenie/pad.html'


class RigPositionView(ListView):
    model = RigPosition
    template_name = 'dvizhenie/rig_position.html'
    context_object_name = 'rig_positions'


class RigPositionUpdateView(UpdateView):
    model = RigPosition
    fields = ('end_date',)
    template_name = 'dvizhenie/rig_position.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig_position')


# class NextPositionView(ListView):
#     model = NextPosition
#     template_name = 'info/rig_position.html'
#     context_object_name = 'rig_positions'


def next_position(request):

    if request.method == "POST":
        define_position_and_put_into_BD()

    results_of_definition = get_info_from_BD(NextPosition)

    return render(request, 'dvizhenie/result_of_definition.html',
                  {'results_of_definition': results_of_definition})


def auth(request):
    return render(request, 'dvizhenie/OAuth.html')
