from datetime import date

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from dvizhenie.models import Pad, type_of_DR, Contractor, DrillingRig, RigPosition


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
                                        nns_quantity=2, status='free')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РУО')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR, number=777, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2024, 4, 10), end_date=date(2024, 12, 1))
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_2, pad=self.pad_2,
                                                         start_date=date(2024, 4, 10), end_date=date(2024, 12, 1))

    def test_RigPositionView(self):

        self.assertEquals(RigPosition.objects.all().count(), 2)
        url = reverse('rig_position')

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)

        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)

        self.assertEquals(list(response_perm.context_data['object_list']), [self.rig_position_1, self.rig_position_2])
        self.assertEquals(Pad.objects.get(number=226).status, 'drilling')

    def test_RigPositionAddView(self):

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
                                          'start_date': '10.03.2024',
                                          'end_date': '11.04.2023'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(RigPosition.objects.all().count(), 3)
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1)[0].end_date, date(2023, 4, 11))

    def test_RigPositionUpdateView(self):

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
                                               'start_date': '10.05.2024',
                                               'end_date': '01.01.2025'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1.id)[0].start_date,
                          date(2024, 5, 10))
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1.id)[0].end_date, date(2025, 1, 1))
        # Куст не меняется (был pad_1, меняем на pad_2, остается pad_1)
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1.id)[0].pad, self.pad_1)
        self.assertEquals(RigPosition.objects.all().count(), 2)

    def test_RigPositionDeleteView(self):

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
