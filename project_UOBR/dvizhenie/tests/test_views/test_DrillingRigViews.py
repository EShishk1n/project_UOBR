from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from dvizhenie.models import type_of_DR, Contractor, DrillingRig


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

    def test_DrillingRigView(self):
        """Проверяет ListView DrillingRig"""
        url = reverse('rig')

        # Тест без permission
        response_noperm = self.client.get(url)
        self.assertEquals(response_noperm.status_code, 302)

        # Тест с permission
        self.client.force_login(user=self.user)
        response_perm = self.client.get(url)
        self.assertEquals(response_perm.status_code, 200)
        self.assertEquals(list(response_perm.context_data['object_list']), [self.drilling_rig_1, self.drilling_rig_2], )

    def test_DrillingRigAddView(self):

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

    def test_DrillingRigUpdateView(self):

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

    def test_DrillingRigDeleteView(self):

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
