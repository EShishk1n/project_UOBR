from datetime import date

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from dvizhenie.models import DrillingRig, type_of_DR, Contractor, Pad, RigPosition, NextPosition


class DrillingRigTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.user2 = User.objects.create_user(username='admin')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РУО')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR, number=777, contractor=self.contractor,
                                                         mud='РВО')

    def test_get(self):
        """Проверяет ListView DrillingRig"""
        url = reverse('rig')

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)
        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals([self.drilling_rig_1, self.drilling_rig_2], list(response_perm.context_data['object_list']))

    def test_create(self):
        """Проверяет CreateView DrillingRig"""
        url = reverse('rig_add')
        self.client.force_login(user=self.user2)

        # Тест без permission
        response_noperm = self.client.post(url,
                                           {'type': self.type_of_DR.id,
                                            'number': 555,
                                            'contractor': self.contractor.id,
                                            'mud': 'РВО'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can add drilling rig')
        self.user2.user_permissions.add(permission)

        self.assertEquals(DrillingRig.objects.all().count(), 2)

        response_perm = self.client.post(url,
                                         {'type': self.type_of_DR.id,
                                          'number': 555,
                                          'contractor': self.contractor.id,
                                          'mud': 'РВО'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(DrillingRig.objects.all().count(), 3)
        self.assertEquals(DrillingRig.objects.filter(number=555)[0].mud, 'РВО')

    def test_update(self):
        """Проверяет UpdateView DrillingRig"""
        url = reverse('rig_update', args=(self.drilling_rig_1.id,))
        self.client.force_login(user=self.user2)

        # Тест без permission
        response_noperm = self.client.post(url, {'type': self.type_of_DR.id,
                                                 'number': 555,
                                                 'contractor': self.contractor.id,
                                                 'mud': 'РУО'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change drilling rig')
        self.user2.user_permissions.add(permission)

        self.assertEquals(DrillingRig.objects.filter(number=666)[0].mud, 'РУО')

        self.assertEquals(DrillingRig.objects.all().count(), 2)

        response_perm = self.client.post(url, {'type': self.type_of_DR.id,
                                               'number': 555,
                                               'contractor': self.contractor.id,
                                               'mud': 'РУО'})
        self.assertEquals(response_perm.status_code, 302)

        self.assertEquals(DrillingRig.objects.filter(number=555)[0].number, '555')
        self.assertEquals(DrillingRig.objects.filter(number=555)[0].mud, 'РУО')
        self.assertEquals(DrillingRig.objects.all().count(), 2)

    def test_delete(self):
        """Проверяет DeleteView DrillingRig"""

        # Создаем объект
        self.type_of_DR_2 = type_of_DR.objects.create(type='3000/200')
        self.contractor_2 = Contractor.objects.create(contractor='ТБНГ')
        self.drilling_rig_3 = DrillingRig.objects.create(id=10, type=self.type_of_DR_2, number=1488,
                                                         contractor=self.contractor_2, mud='РВО')

        url = reverse('rig_delete', args=(self.drilling_rig_3.id,))
        self.client.force_login(user=self.user2)

        # Тест без permission
        response_noperm = self.client.post(url)
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can delete drilling rig')
        self.user2.user_permissions.add(permission)
        self.assertEquals(DrillingRig.objects.all().count(), 3)

        response_perm = self.client.post(url)
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(DrillingRig.objects.all().count(), 2)


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

    def test_get(self):
        """Проверяет ListView Pad"""

        self.assertEquals(Pad.objects.all().count(), 3)
        url = reverse('pad')

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)

        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals([self.pad_2, self.pad_1], list(response_perm.context_data['object_list']))

    def test_create(self):
        """Проверяет CreateView Pad"""

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
                                          'first_stage_date': '2024-03-10',
                                          'second_stage_date': '2023-04-10',
                                          'required_capacity': 270, 'required_mud': 'РВО', 'gs_quantity': 4,
                                          'nns_quantity': 8, 'marker': 'нет'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(Pad.objects.all().count(), 4)
        self.assertEquals(Pad.objects.filter(number='165')[0].nns_quantity, 8)

    def test_update(self):
        """Проверяет UpdateView Pad"""
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
                                               'first_stage_date': '2024-03-10',
                                               'second_stage_date': '2023-04-10',
                                               'required_capacity': 270, 'required_mud': 'РУО', 'gs_quantity': 4,
                                               'nns_quantity': 8, 'marker': 'нет'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(Pad.objects.filter(number='89')[0].first_stage_date, date(2024, 3, 10))
        self.assertEquals(Pad.objects.filter(number='89')[0].second_stage_date, date(2023, 4, 10))
        self.assertEquals(Pad.objects.filter(number='89')[0].required_capacity, 270)
        self.assertEquals(Pad.objects.all().count(), 3)

    def test_delete(self):
        """Проверяет DeleteView Pad"""

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


class RigPositionTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='admin')
        self.pad_1 = Pad.objects.create(number='89', field='УБ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РУО', gs_quantity=5,
                                        nns_quantity=2, status='drilling')
        self.pad_2 = Pad.objects.create(number='226', field='ЮС',
                                        first_stage_date=date(2023, 11, 20),
                                        second_stage_date=date(2023, 11, 30),
                                        required_capacity=320, required_mud='РВО', gs_quantity=11,
                                        nns_quantity=2, status='drilled')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РУО')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR, number=777, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2024, 4, 10), end_date=date(2024, 12, 1))
        # Должен отображаться, т.к. статус 'drilled' должен поменяться на 'drilling'
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_2, pad=self.pad_2,
                                                         start_date=date(2024, 4, 10), end_date=date(2024, 12, 1))

    def test_get(self):
        """Проверяет ListView RigPosition"""

        self.assertEquals(RigPosition.objects.all().count(), 2)
        url = reverse('rig_position')

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)

        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)

        self.assertEquals([self.rig_position_1, self.rig_position_2], list(response_perm.context_data['object_list']))

    def test_create(self):
        """Проверяет CreateView RigPosition"""

        url = reverse('rig_position_add')
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url,
                                           {'drilling_rig': self.drilling_rig_1.id,
                                            'pad': self.pad_2.id,
                                            'start_date': '2024-03-10',
                                            'end_date': '2023-04-11'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can add rig position')
        self.user.user_permissions.add(permission)

        self.assertEquals(RigPosition.objects.all().count(), 2)

        response_perm = self.client.post(url,
                                         {'drilling_rig': self.drilling_rig_1.id,
                                          'pad': self.pad_2.id,
                                          'start_date': '2024-03-10',
                                          'end_date': '2023-04-11'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(RigPosition.objects.all().count(), 3)
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1)[0].end_date, date(2023, 4, 11))

    def test_update(self):
        """Проверяет UpdateView RigPosition"""
        url = reverse('rig_position_update', args=(self.rig_position_1.id,))
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url, {'drilling_rig': self.drilling_rig_1.id,
                                                 'pad': self.pad_1.id,
                                                 'start_date': '2024-05-10',
                                                 'end_date': '2025-01-01'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change rig position')
        self.user.user_permissions.add(permission)

        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1.id)[0].start_date,
                          date(2024, 4, 10))
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1.id)[0].end_date,
                          date(2024, 12, 1))

        self.assertEquals(RigPosition.objects.all().count(), 2)

        response_perm = self.client.post(url, {'drilling_rig': self.drilling_rig_1.id,
                                               'pad': self.pad_2.id,
                                               'start_date': '2024-05-10',
                                               'end_date': '2025-01-01'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1.id)[0].start_date,
                          date(2024, 5, 10))
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1.id)[0].end_date, date(2025, 1, 1))
        # Куст не меняется (был pad_1, меняем на pad_2, остается pad_1)
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1.id)[0].pad, self.pad_1)
        self.assertEquals(RigPosition.objects.all().count(), 2)

    def test_delete(self):
        """Проверяет DeleteView RigPosition"""

        url = reverse('rig_position_delete', args=(self.rig_position_2.id,))
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url)
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can delete rig position')
        self.user.user_permissions.add(permission)
        self.assertEquals(RigPosition.objects.all().count(), 2)

        response_perm = self.client.post(url)
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(RigPosition.objects.all().count(), 1)


class NextPositionTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='admin')
        self.pad_1 = Pad.objects.create(number='89', field='УБ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РУО', gs_quantity=5,
                                        nns_quantity=2, status='drilling')
        self.pad_2 = Pad.objects.create(number='226', field='ЮС',
                                        first_stage_date=date(2023, 11, 20),
                                        second_stage_date=date(2023, 11, 30),
                                        required_capacity=320, required_mud='РВО', gs_quantity=11,
                                        nns_quantity=2, status='drilling')
        self.pad_3 = Pad.objects.create(number='45', field='КИН',
                                        first_stage_date=date(2024, 1, 20),
                                        second_stage_date=date(2024, 2, 10),
                                        required_capacity=400, required_mud='РВО', gs_quantity=6,
                                        nns_quantity=3, status='')
        self.pad_4 = Pad.objects.create(number='13', field='СОР',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=13,
                                        nns_quantity=5, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РУО')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR, number=777, contractor=self.contractor,
                                                         mud='РВО')
        self.drilling_rig_3 = DrillingRig.objects.create(type=self.type_of_DR, number=888, contractor=self.contractor,
                                                         mud='РУО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2024, 4, 10), end_date=date(2024, 2, 10))
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_2, pad=self.pad_2,
                                                         start_date=date(2024, 4, 10), end_date=date(2024, 12, 1))
        self.rig_position_3 = RigPosition.objects.create(drilling_rig=self.drilling_rig_3, pad=self.pad_1,
                                                         start_date=date(2024, 4, 10), end_date=date(2024, 12, 1))
        self.next_position_1 = NextPosition.objects.create(current_position=self.rig_position_1,
                                                           next_position=self.pad_3, status='Требуется подтверждение')
        self.next_position_2 = NextPosition.objects.create(current_position=self.rig_position_2,
                                                           next_position=self.pad_4,
                                                           status='Изменено. Требуется подтверждение')
        # Не отображается, т.к. status=''
        self.next_position_3 = NextPosition.objects.create(current_position=self.rig_position_3,
                                                           status='')

    def test_get(self):
        """Проверяет ListView NextPosition"""

        self.assertEquals(NextPosition.objects.all().count(), 3)
        url = reverse('next_position')
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can view next position')
        self.user.user_permissions.add(permission)

        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals([self.next_position_1, self.next_position_2], list(response_perm.context_data['object_list']))

    def test_calculate(self):
        """Проверяет FormMixin NextPosition"""
        url = reverse('next_position')
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url,
                                           {'start_date_for_calculation': '2024-02-01',
                                            'end_date_for_calculation': '2024-04-01'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can view next position')
        self.user.user_permissions.add(permission)
        self.assertEquals(NextPosition.objects.all().count(), 3)
        response_perm = self.client.post(url,
                                         {'start_date_for_calculation': '2024-02-01',
                                          'end_date_for_calculation': '2024-04-01'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(NextPosition.objects.all().count(), 1)
        self.assertEquals(NextPosition.objects.all()[0].current_position, self.rig_position_1)
        self.assertEquals(NextPosition.objects.all()[0].next_position, self.pad_4)
        self.assertEquals(NextPosition.objects.all()[0].status, 'Требуется подтверждение')
