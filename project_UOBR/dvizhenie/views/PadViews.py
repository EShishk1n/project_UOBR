from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from dvizhenie.forms import PadForm
from dvizhenie.models import Pad


class PadView(LoginRequiredMixin, ListView):
    """Отображает данные из модели Pad"""
    status_to_exclude = ['drilling', 'drilled']
    queryset = Pad.objects.exclude(status__in=status_to_exclude)
    template_name = 'dvizhenie/PadViews_templates/pad.html'
    context_object_name = 'pads'


class PadAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Добавляет экземпляры в модель Pad"""

    form_class = PadForm
    template_name = 'dvizhenie/PadViews_templates/add_update_pad.html'
    success_url = reverse_lazy('pad')
    permission_required = 'dvizhenie.add_pad'


class PadUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Обновляет информацию в модели Pad"""

    model = Pad
    form_class = PadForm
    template_name = 'dvizhenie/PadViews_templates/add_update_pad.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('pad')
    permission_required = 'dvizhenie.change_pad'


class PadDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаляет экземпляры из модели Pad"""

    model = Pad
    pk_url_kwarg = 'pk'
    context_object_name = 'pad'
    success_url = reverse_lazy('pad')
    template_name = 'dvizhenie/PadViews_templates/delete_pad.html'
    permission_required = 'dvizhenie.delete_pad'
