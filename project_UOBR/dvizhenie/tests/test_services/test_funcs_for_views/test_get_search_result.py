from datetime import date

from django.test import TestCase

from dvizhenie.models import Pad, type_of_DR, Contractor, DrillingRig, RigPosition
from dvizhenie.services.funcs_for_views.get_search_result import get_search_result_by_model, get_search_result


class GetSearchResultTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(id=1, number='133', field='САЛ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=17,
                                        nns_quantity=0, status='drilling')
        self.pad_2 = Pad.objects.create(id=2, number='110', field='УГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=15,
                                        nns_quantity=2, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(id=1, type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(id=1, drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))

    def test_get_search_result_by_model(self):
        res1 = get_search_result_by_model(model_id=self.pad_1.id, model='Pad')
        self.assertEquals(res1['model_objs'][0], Pad.objects.get(number=133))
        self.assertEquals(res1['rig_position_objs'][0], RigPosition.objects.all()[0])

        res2 = get_search_result_by_model(model_id=self.drilling_rig_1.id, model='Rig')
        self.assertEquals(res2['model_objs'][0], DrillingRig.objects.get(number=666))
        self.assertEquals(res2['rig_position_objs'][0], RigPosition.objects.all()[0])

    def test_get_search_result(self):
        result = get_search_result(rigs_id=[self.pad_1.id],
                                   pads_id=[self.drilling_rig_1.id])

        self.assertEquals(result['result_pads'][0][0], Pad.objects.get(number=133))
        self.assertEquals(result['result_rigs'][0][0], DrillingRig.objects.get(number=666))
        self.assertEquals(result['result_rigs_position'][0][0], RigPosition.objects.all()[0])
