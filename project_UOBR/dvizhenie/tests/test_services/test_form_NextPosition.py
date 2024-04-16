from datetime import date

from django.test import TestCase

from dvizhenie.models import Pad, type_of_DR, Contractor, DrillingRig, RigPosition, NextPosition
from dvizhenie.services.form_NextPosition import put_rigs_for_define_in_NextPosition, \
    check_availability_of_rig_in_NextPosition, get_rigs_for_put_into_DB, form_next_position


class FormNextPositionTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='133', field='САЛ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=17,
                                        nns_quantity=0, status='drilling')
        self.pad_2 = Pad.objects.create(number='110', field='УГ',
                                        first_stage_date=date(2024, 2, 29),
                                        second_stage_date=date(2024, 2, 29),
                                        required_capacity=320, required_mud='РВО', gs_quantity=15,
                                        nns_quantity=2, status='')
        self.pad_3 = Pad.objects.create(number='669', field='МБ',
                                        first_stage_date=date(2024, 2, 26),
                                        second_stage_date=date(2024, 3, 16),
                                        required_capacity=320, required_mud='РУО', gs_quantity=14,
                                        nns_quantity=4, status='')
        self.pad_9 = Pad.objects.create(number='60', field='СУГ',
                                        first_stage_date=date(2024, 3, 23),
                                        second_stage_date=date(2024, 3, 24),
                                        required_capacity=320, required_mud='РУО', gs_quantity=4,
                                        nns_quantity=20, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.contractor2 = Contractor.objects.create(contractor='СНПХ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR, number=777, contractor=self.contractor2,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_2,
                                                         start_date=date(2024, 5, 1), end_date=date(2024, 10, 1))
        self.rig_position_3 = RigPosition.objects.create(drilling_rig=self.drilling_rig_2, pad=self.pad_9,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 9, 20))
        self.next_position = NextPosition.objects.create(current_position=self.rig_position_2, next_position=self.pad_3,
                                                         status='')

    def test_check_availability_of_rig_in_NextPosition(self):

        res = check_availability_of_rig_in_NextPosition(self.rig_position_1)
        res1 = check_availability_of_rig_in_NextPosition(self.rig_position_2)
        self.assertEquals(res, False)
        self.assertEquals(res1, True)

    def test_get_rigs_for_put_into_DB(self):
        start_date_for_calculation = date(2024, 1, 1)
        end_date_for_calculation = date(2024, 12, 31)
        rigs_for_put_into_DB = get_rigs_for_put_into_DB(start_date_for_calculation, end_date_for_calculation)

        self.assertEquals(len(rigs_for_put_into_DB), 1)

    def test_put_rigs_for_define_in_NextPosition(self):
        start_date_for_calculation = date(2024, 1, 1)
        end_date_for_calculation = date(2024, 12, 31)

        self.assertEquals(len(NextPosition.objects.all()), 1)
        put_rigs_for_define_in_NextPosition(start_date_for_calculation, end_date_for_calculation)
        self.assertEquals(len(NextPosition.objects.all()), 2)

    def test_form_next_position(self):
        start_date_for_calculation = date(2024, 1, 1)
        end_date_for_calculation = date(2024, 12, 31)
        self.assertEquals(len(NextPosition.objects.all()), 1)
        self.assertEquals(NextPosition.objects.get(current_position=self.rig_position_2).next_position, self.pad_3)
        form_next_position(start_date_for_calculation, end_date_for_calculation)
        self.assertEquals(len(NextPosition.objects.all()), 2)
        self.assertEquals(NextPosition.objects.get(current_position=self.rig_position_2).next_position, None)
