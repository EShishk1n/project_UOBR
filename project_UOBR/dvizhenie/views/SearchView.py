from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic import ListView

from dvizhenie.models import Pad, DrillingRig
from dvizhenie.services.funcs_for_views.get_search_result import get_search_result
from dvizhenie.services.give_statuses_to_pads.common_function import convert_from_QuerySet_to_list


class Search(LoginRequiredMixin, ListView):
    """Поиск по моделям приложения"""

    template_name = "dvizhenie/search.html"
    context_object_name = "result"

    def get_id(self) -> dict:
        return {'pad': list(Pad.objects.filter(number__contains=self.request.GET.get('q')).values_list('id')),
                'rig': list(DrillingRig.objects.filter(number__contains=self.request.GET.get('q')).values_list('id'))}

    def get_queryset(self) -> dict:

        pads_id = convert_from_QuerySet_to_list(self.get_id()['pad'])
        rigs_id = convert_from_QuerySet_to_list(self.get_id()['rig'])
        result = get_search_result(pads_id, rigs_id)

        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q')

        return context
