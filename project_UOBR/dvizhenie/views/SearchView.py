from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from dvizhenie.models import Pad, DrillingRig
from dvizhenie.services.funcs_for_views.get_search_result import get_search_result


class Search(LoginRequiredMixin, ListView):
    """Поиск по моделям приложения"""

    template_name = "dvizhenie/search.html"
    context_object_name = "result"

    def get_id(self) -> dict:
        return {'pad': Pad.objects.filter(number__contains=self.request.GET.get('q')).values_list('id'),
                'rig': DrillingRig.objects.filter(number__contains=self.request.GET.get('q')).values_list('id')}

    def get_queryset(self) -> dict:
        pads_id = self.get_id()['pad']
        rigs_id = self.get_id()['rig']
        result = get_search_result(pads_id, rigs_id)

        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q')

        return context
