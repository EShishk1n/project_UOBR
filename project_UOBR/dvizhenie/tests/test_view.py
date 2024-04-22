from datetime import date

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from dvizhenie.models import DrillingRig, type_of_DR, Contractor, Pad, RigPosition, NextPosition, PositionRating





class SearchTestCase(TestCase):
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

    def test_search(self):
        """Проверяет функцию поиска"""

        url = '/search?q=89'

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)

        response_perm = self.client.get(url)

        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals(response_perm.context_data['result'][0][0][0][0], self.pad_2)
        self.assertEquals(response_perm.context_data['result'][1][0][0][0], self.drilling_rig_2)


class ExportDataTestCase(TestCase):
    """Проверяет функционал экспорта данных из эксель-файла"""
    # Проверяются данные вставленные в строку №182.

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
                                                 'table_end_row': 182})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change rig position')
        self.user.user_permissions.add(permission)

        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1)[0].end_date, date(2024, 2, 10))

        response_perm = self.client.post(url, {'table_start_row': 182,
                                               'table_end_row': 182})
        self.assertEquals(response_perm.status_code, 302)

        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1)[0].end_date, date(2024, 2, 18))

    def test_export_data_pads(self):
        url = reverse('export_data_pads')
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url, {'table_start_row': 182,
                                                 'table_end_row': 182})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change pad')
        self.user.user_permissions.add(permission)

        self.assertEquals(Pad.objects.filter(number='143')[0].first_stage_date, date(2024, 8, 20))

        response_perm = self.client.post(url, {'table_start_row': 182,
                                               'table_end_row': 182})
        self.assertEquals(response_perm.status_code, 302)

        self.assertEquals(Pad.objects.filter(number='143')[0].first_stage_date, date(2024, 9, 20))
