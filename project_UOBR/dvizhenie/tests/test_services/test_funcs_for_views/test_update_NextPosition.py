from datetime import date

from django.test import TestCase

from dvizhenie.models import NextPosition, RigPosition, DrillingRig, Contractor, type_of_DR, Pad
from dvizhenie.services.funcs_for_views.update_NextPosition import update_NextPosition


class UpdateNextPositionTestCase(TestCase):

    def setUp(self):
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
                                                           next_position=self.pad_3, status='default')
        self.next_position_2 = NextPosition.objects.create(current_position=self.rig_position_2,
                                                           next_position=self.pad_4, status='changed')

    def test_update_NextPosition(self):
        update_NextPosition(next_position_queryset=NextPosition.objects.filter(current_position=self.rig_position_1),
                            status='commited')
        self.assertEquals(NextPosition.objects.get(current_position=self.rig_position_1).status, 'commited')

        update_NextPosition(next_position_queryset=NextPosition.objects.filter(current_position=self.rig_position_2),
                            status='deleted', reset_next_position=True)
        self.assertEquals(NextPosition.objects.get(current_position=self.rig_position_2).status, 'deleted')
        self.assertEquals(NextPosition.objects.get(current_position=self.rig_position_2).next_position, None)

        update_NextPosition(next_position_queryset=NextPosition.objects.filter(current_position=self.rig_position_2),
                            delete_next_position=True)
        self.assertEquals(NextPosition.objects.all().count(), 1)
