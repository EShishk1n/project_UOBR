from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from dvizhenie.forms import DrillingRigForm
from dvizhenie.models import DrillingRig


class DrillingRigView(LoginRequiredMixin, ListView):
    """Отображает данные из модели DrillingRig"""

    template_name = 'dvizhenie/DrillingRigViews_templates/rig.html'
    context_object_name = 'rigs'
    queryset = DrillingRig.objects.all().select_related('type', 'contractor')


class DrillingRigAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Добавляет экземпляры в модель DrillingRig"""

    form_class = DrillingRigForm
    template_name = 'dvizhenie/DrillingRigViews_templates/add_update_rig.html'
    success_url = reverse_lazy('rig')
    permission_required = 'dvizhenie.add_drillingrig'


class DrillingRigUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Обновляет информацию в модели DrillingRig"""

    model = DrillingRig
    form_class = DrillingRigForm
    template_name = 'dvizhenie/DrillingRigViews_templates/add_update_rig.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')
    permission_required = 'dvizhenie.change_drillingrig'


class DrillingRigDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаляет экземпляры из модели DrillingRig"""

    model = DrillingRig
    context_object_name = 'rig'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig')
    template_name = 'dvizhenie/DrillingRigViews_templates/delete_rig.html'
    permission_required = 'dvizhenie.delete_drillingrig'
