from datetime import date

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from dvizhenie.models import Pad, type_of_DR, Contractor, DrillingRig, RigPosition, PositionRating, NextPosition


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
        self.position_rating_1 = PositionRating.objects.create(current_position=self.rig_position_1,
                                                               next_position=self.pad_3,
                                                               capacity_rating=10,
                                                               first_stage_date_rating=8.5,
                                                               second_stage_date_rating=7,
                                                               mud_rating=6,
                                                               logistic_rating=4,
                                                               marker_rating=10,
                                                               common_rating=76)
        self.position_rating_2 = PositionRating.objects.create(current_position=self.rig_position_1,
                                                               next_position=self.pad_2,
                                                               capacity_rating=8,
                                                               first_stage_date_rating=6.5,
                                                               second_stage_date_rating=7,
                                                               mud_rating=6,
                                                               logistic_rating=2,
                                                               marker_rating=10,
                                                               common_rating=63)
        self.next_position_1 = NextPosition.objects.create(current_position=self.rig_position_1,
                                                           next_position=self.pad_3, status='default')
        self.next_position_2 = NextPosition.objects.create(current_position=self.rig_position_2,
                                                           next_position=self.pad_4, status='changed')

    def test_NextPositionView(self):
        self.assertEquals(NextPosition.objects.all().count(), 2)
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
        self.assertEquals(list(response_perm.context_data['object_list']), [self.next_position_1, self.next_position_2])

    def test_calculateNextPositionView(self):
        url = reverse('next_position')
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.post(url,
                                           {'start_date_for_calculation': '01.02.2024',
                                            'end_date_for_calculation': '01.04.2024'})
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can view next position')
        self.user.user_permissions.add(permission)
        self.assertEquals(NextPosition.objects.all().count(), 2)
        response_perm = self.client.post(url,
                                         {'start_date_for_calculation': '01.02.2024',
                                          'end_date_for_calculation': '01.04.2024'})
        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(NextPosition.objects.all().count(), 2)
        self.assertEquals(NextPosition.objects.all()[1].current_position, self.rig_position_1)
        self.assertEquals(NextPosition.objects.all()[1].next_position, None)
        self.assertEquals(NextPosition.objects.all()[1].status, 'empty')

    def test_get_detail_info_for_next_position(self):
        url = reverse('position_rating', args=(self.next_position_1.id,))

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)
        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals(response_perm.context[0].dicts[3], {"position_rating": self.position_rating_1})

    def test_get_detail_info_for_position_rating(self):
        url = reverse('position_rating_', args=(self.position_rating_1.id,))

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)
        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals(response_perm.context[0].dicts[3], {"position_rating": self.position_rating_1})

    def test_get_rating_for_all_possible_next_positions(self):

        url = reverse('position_rating_all', args=(self.next_position_1.id,))

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)
        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals(list(response_perm.context[0].dicts[3]['position_rating']),
                          [self.position_rating_1, self.position_rating_2])

    def test_commit_next_position(self):
        """Проверяет функционал по подтверждению NextPosition"""

        url = reverse('commit_next_position', args=(self.next_position_1.id,))
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change next position')
        self.user.user_permissions.add(permission)

        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].status, 'default')
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].next_position.status,
                          '')

        response_perm = self.client.get(url)

        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].status, 'commited')
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].next_position.status,
                          'reserved')


# Вот тут остановилсяЫ
    def test_change_next_position(self):
        """Проверяет функционал по изменению NextPosition"""

        url = reverse('change_next_position', args=(self.position_rating_2.id,))
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change next position')
        self.user.user_permissions.add(permission)

        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].status, 'Требуется подтверждение')
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].next_position, self.pad_3)

        response_perm = self.client.get(url)

        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].status,
                          'Изменено. Требуется подтверждение')
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].next_position, self.pad_2)

    def test_delete_next_position(self):
        """Проверяет функционал по удалению next_position из NextPosition"""

        url = reverse('delete_next_position', args=(self.next_position_1.id,))
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change next position')
        self.user.user_permissions.add(permission)

        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].status, 'Требуется подтверждение')
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].next_position, self.pad_3)

        response_perm = self.client.get(url)

        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].status,
                          'Удалено пользователем')
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].next_position, None)

    def test_CommitedNextPositionView(self):
        """Проверяет ListView дл отображения подтвержденных позиций NextPosition"""

        url = reverse('commited_next_position')
        NextPosition.objects.filter(id=self.next_position_1.id).update(status='Подтверждено')

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)
        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals([self.next_position_1], list(response_perm.context_data['object_list']))
        self.assertEquals('Подтверждено', list(response_perm.context_data['object_list'])[0].status)

    def test_delete_commited_position(self):
        """Проверяет функционал по изменению статуса подтвержденной next_position в NextPosition"""

        url = reverse('delete_commited_position', args=(self.next_position_1.id,))
        self.client.force_login(user=self.user)

        NextPosition.objects.filter(id=self.next_position_1.id).update(status='Подтверждено')

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change next position')
        self.user.user_permissions.add(permission)
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].status, 'Подтверждено')
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].next_position, self.pad_3)

        response_perm = self.client.get(url)

        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].status,
                          'Удалено пользователем')
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].next_position, None)
        self.assertEquals(Pad.objects.filter(id=self.pad_3.id)[0].status, '')

    def test_commit_commited_position(self):
        """Проверяет функционал по переносу подтвержденной next_position в RigPosition"""

        url = reverse('commit_commited_position', args=(self.next_position_1.id,))
        self.client.force_login(user=self.user)

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 403)

        # Тест с permission
        permission = Permission.objects.get(name='Can change next position')
        self.user.user_permissions.add(permission)
        self.assertEquals(NextPosition.objects.all().count(), 3)
        self.assertEquals(RigPosition.objects.all().count(), 3)
        self.assertEquals(NextPosition.objects.filter(id=self.next_position_1.id)[0].next_position, self.pad_3)

        response_perm = self.client.get(url)

        self.assertEquals(response_perm.status_code, 302)
        self.assertEquals(NextPosition.objects.all().count(), 2)
        self.assertEquals(RigPosition.objects.all().count(), 4)
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1)[1].pad, self.pad_3)
