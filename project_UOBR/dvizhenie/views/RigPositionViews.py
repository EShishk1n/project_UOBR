from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from dvizhenie.forms import RigPositionAddForm, RigPositionForm
from dvizhenie.models import RigPosition
from dvizhenie.services.give_statuses_to_pads.give_statuses_to_pads import give_statuses_to_pads


class RigPositionView(LoginRequiredMixin, ListView):
    """Отображает данные из модели RigPosition"""

    template_name = 'dvizhenie/RigPositionViews_templates/rig_position.html'
    context_object_name = 'rig_positions'
    queryset = RigPosition.objects.filter(pad__status='drilling').select_related('drilling_rig').select_related(
        'pad').select_related(
        'drilling_rig__type').select_related('drilling_rig__contractor')

    def get(self, request, *args, **kwargs):

        give_statuses_to_pads()

        self.object_list = self.get_queryset()

        context = self.get_context_data()
        return self.render_to_response(context)


class RigPositionAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Добавляет экземпляры в модель RigPosition"""

    form_class = RigPositionAddForm
    template_name = 'dvizhenie/RigPositionViews_templates/add_rig_position.html'
    success_url = reverse_lazy('rig_position')
    permission_required = 'dvizhenie.add_rigposition'


class RigPositionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Обновляет информацию в модели RigPosition"""

    model = RigPosition
    form_class = RigPositionForm
    context_object_name = 'rig_position'
    template_name = 'dvizhenie/RigPositionViews_templates/update_rig_position.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('rig_position')
    permission_required = 'dvizhenie.change_rigposition'


class RigPositionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаляет экземпляры из модели RigPosition"""

    model = RigPosition
    pk_url_kwarg = 'pk'
    context_object_name = 'rig_position'
    success_url = reverse_lazy('rig_position')
    template_name = 'dvizhenie/RigPositionViews_templates/delete_rig_position.html'
    permission_required = 'dvizhenie.delete_rigposition'
