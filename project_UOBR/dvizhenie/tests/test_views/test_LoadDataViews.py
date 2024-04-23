from datetime import date

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from dvizhenie.models import Pad, type_of_DR, Contractor, RigPosition, DrillingRig


class LoadDataViewsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='admin')
        self.pad_1 = Pad.objects.create(number='89', field='УБ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РУО', gs_quantity=5,
                                        nns_quantity=2, status='drilling')
        self.pad_2 = Pad.objects.create(number='143', field='УБ',
                                        first_stage_date=date(2024, 8, 20),
                                        second_stage_date=date(2024, 8, 20),
                                        required_capacity=320, required_mud='РУО', gs_quantity=5,
                                        nns_quantity=2, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РУО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2024, 4, 10), end_date=date(2024, 2, 10))

    def test_export_data_rig_positions(self):
        url = reverse('export_data_rig_positions')
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url, {'table_start_row': 182,
                                                 'table_end_row': 182,
                                                 'path': 'dvizhenie/tests/test_services/test_load_data_from_excel/'
                                                         'Движение_БУ.xlsx'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change rig position')
        self.user.user_permissions.add(permission)

        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1)[0].end_date, date(2024, 2, 10))

        response_perm = self.client.post(url, {'table_start_row': 182,
                                               'table_end_row': 182,
                                               'path': 'dvizhenie/tests/test_services/test_load_data_from_excel/'
                                                       'Движение_БУ.xlsx'})
        self.assertEquals(response_perm.status_code, 302)

        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1)[0].end_date, date(2024, 2, 18))

    def test_export_data_pads(self):
        url = reverse('export_data_pads')
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url, {'table_start_row': 182,
                                                 'table_end_row': 182,
                                                 'path': 'dvizhenie/tests/test_services/test_load_data_from_excel/'
                                                         'Движение_БУ.xlsx'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change pad')
        self.user.user_permissions.add(permission)

        self.assertEquals(Pad.objects.filter(number='143')[0].first_stage_date, date(2024, 8, 20))

        response_perm = self.client.post(url, {'table_start_row': 182,
                                               'table_end_row': 182,
                                               'path': 'dvizhenie/tests/test_services/test_load_data_from_excel/'
                                                       'Движение_БУ.xlsx'})
        self.assertEquals(response_perm.status_code, 302)

        self.assertEquals(Pad.objects.filter(number='143')[0].first_stage_date, date(2024, 9, 20))
