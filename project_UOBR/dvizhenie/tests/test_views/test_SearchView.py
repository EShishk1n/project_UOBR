from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from dvizhenie.models import DrillingRig, type_of_DR, Contractor, Pad


class SearchViewTestCase(TestCase):
    """Проверяет функционал поиска по моделям"""

    def setUp(self):
        self.user = User.objects.create_user(username='admin')
        self.pad_1 = Pad.objects.create(number='232', field='УБ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РУО', gs_quantity=5,
                                        nns_quantity=2, status='drilling')
        self.pad_2 = Pad.objects.create(number='89989', field='ЮС',
                                        first_stage_date=date(2023, 11, 20),
                                        second_stage_date=date(2023, 11, 30),
                                        required_capacity=320, required_mud='РВО', gs_quantity=11,
                                        nns_quantity=2, status='drilling')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=234, contractor=self.contractor,
                                                         mud='РУО')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR, number=898, contractor=self.contractor,
                                                         mud='РВО')

    def test_Search(self):

        url = '/search?q=89'

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)

        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals(response_perm.context_data['object_list']['result_pads'][0][0], self.pad_2)
        self.assertEquals(response_perm.context_data['object_list']['result_rigs'][0][0], self.drilling_rig_2)
