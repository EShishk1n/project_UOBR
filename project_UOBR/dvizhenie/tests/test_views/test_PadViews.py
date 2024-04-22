from datetime import date

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from dvizhenie.models import Pad


class PadTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='admin')
        self.pad_1 = Pad.objects.create(number='89', field='УБ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РУО', gs_quantity=5,
                                        nns_quantity=2)
        self.pad_2 = Pad.objects.create(number='226', field='ЮС',
                                        first_stage_date=date(2023, 11, 20),
                                        second_stage_date=date(2023, 11, 30),
                                        required_capacity=320, required_mud='РВО', gs_quantity=11,
                                        nns_quantity=2)
        # Не должен отображаться, т.к. статус 'drilled'
        self.pad_3 = Pad.objects.create(number='155', field='ВС',
                                        first_stage_date=date(2023, 11, 10),
                                        second_stage_date=date(2023, 11, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=6,
                                        nns_quantity=3, status='drilled')

    def test_PadView(self):

        self.assertEquals(Pad.objects.all().count(), 3)
        url = reverse('pad')

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)

        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals(list(response_perm.context_data['object_list']), [self.pad_2, self.pad_1])

    def test_PadAddView(self):

        url = reverse('pad_add')
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url,
                                           {'number': '165', 'field': 'ВС',
                                            'first_stage_date': '2024-03-10',
                                            'second_stage_date': '2023-04-10',
                                            'required_capacity': 270, 'required_mud': 'РВО', 'gs_quantity': 4,
                                            'nns_quantity': 8, 'marker': 'нет'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can add pad')
        self.user.user_permissions.add(permission)

        self.assertEquals(Pad.objects.all().count(), 3)

        response_perm = self.client.post(url,
                                         {'number': '165', 'field': 'ВС',
                                          'first_stage_date': '10.03.2024',
                                          'second_stage_date': '10.04.2023',
                                          'required_capacity': 270, 'required_mud': 'РВО', 'gs_quantity': 4,
                                          'nns_quantity': 8, 'marker': 'нет'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(Pad.objects.all().count(), 4)
        self.assertEquals(Pad.objects.filter(number='165')[0].nns_quantity, 8)

    def test_PadUpdateView(self):

        url = reverse('pad_update', args=(self.pad_1.id,))
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url, {'number': '89', 'field': 'УБ',
                                                 'first_stage_date': '2024-03-10',
                                                 'second_stage_date': '2023-04-10',
                                                 'required_capacity': 270, 'required_mud': 'РУО', 'gs_quantity': 4,
                                                 'nns_quantity': 8, 'marker': 'нет'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change pad')
        self.user.user_permissions.add(permission)

        self.assertEquals(Pad.objects.filter(number='89')[0].first_stage_date, date(2023, 12, 20))
        self.assertEquals(Pad.objects.filter(number='89')[0].second_stage_date, date(2023, 12, 20))
        self.assertEquals(Pad.objects.filter(number='89')[0].required_capacity, 320)

        self.assertEquals(Pad.objects.all().count(), 3)

        response_perm = self.client.post(url, {'number': '89', 'field': 'УБ',
                                               'first_stage_date': '10.03.2024',
                                               'second_stage_date': '10.04.2023',
                                               'required_capacity': 270, 'required_mud': 'РУО', 'gs_quantity': 4,
                                               'nns_quantity': 8, 'marker': 'нет'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(Pad.objects.filter(number='89')[0].first_stage_date, date(2024, 3, 10))
        self.assertEquals(Pad.objects.filter(number='89')[0].second_stage_date, date(2023, 4, 10))
        self.assertEquals(Pad.objects.filter(number='89')[0].required_capacity, 270)
        self.assertEquals(Pad.objects.all().count(), 3)

    def test_PadDeleteView(self):

        url = reverse('pad_delete', args=(self.pad_2.id,))
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url)
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can delete pad')
        self.user.user_permissions.add(permission)
        self.assertEquals(Pad.objects.all().count(), 3)

        response_perm = self.client.post(url)
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(Pad.objects.all().count(), 2)
