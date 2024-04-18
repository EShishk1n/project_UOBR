from datetime import date

from django.test import TestCase

from dvizhenie.models import type_of_DR, Contractor, DrillingRig, RigPosition, Pad, NextPosition, PositionRating
from dvizhenie.services.define_position.define_position import put_result_of_definition_in_NextPosition, \
    give_status_booked_to_PositionRating, get_objs_from_PositionRating, define_next_position, \
    define_position_and_put_into_DB


class DefinePositionTestCase(TestCase):
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
                                        nns_quantity=2, status='drilling')
        self.pad_3 = Pad.objects.create(number='669', field='МБ',
                                        first_stage_date=date(2024, 2, 26),
                                        second_stage_date=date(2024, 3, 16),
                                        required_capacity=320, required_mud='РУО', gs_quantity=14,
                                        nns_quantity=4, status='')
        self.pad_4 = Pad.objects.create(number='58', field='СУГ',
                                        first_stage_date=date(2024, 2, 20),
                                        second_stage_date=date(2024, 2, 20),
                                        required_capacity=320, required_mud='РВО', gs_quantity=9,
                                        nns_quantity=5, status='')
        self.pad_5 = Pad.objects.create(number='165', field='ВС',
                                        first_stage_date=date(2024, 3, 19),
                                        second_stage_date=date(2024, 3, 24),
                                        required_capacity=320, required_mud='РВО', gs_quantity=6,
                                        nns_quantity=5, status='', marker='СНПХ')
        self.pad_6 = Pad.objects.create(number='902', field='ПРЗ',
                                        first_stage_date=date(2024, 3, 31),
                                        second_stage_date=date(2024, 4, 30),
                                        required_capacity=320, required_mud='РУО', gs_quantity=17,
                                        nns_quantity=2, status='')
        self.pad_7 = Pad.objects.create(number='2136у', field='ПРОл',
                                        first_stage_date=date(2023, 12, 7),
                                        second_stage_date=date(2024, 1, 12),
                                        required_capacity=250, required_mud='РВО', gs_quantity=0,
                                        nns_quantity=24, status='', marker='СНПХ')
        self.pad_8 = Pad.objects.create(number='155', field='ВС',
                                        first_stage_date=date(2023, 11, 30),
                                        second_stage_date=date(2023, 11, 30),
                                        required_capacity=320, required_mud='РВО', gs_quantity=7,
                                        nns_quantity=2, status='')
        self.pad_9 = Pad.objects.create(number='60', field='СУГ',
                                        first_stage_date=date(2024, 3, 23),
                                        second_stage_date=date(2024, 3, 24),
                                        required_capacity=320, required_mud='РУО', gs_quantity=4,
                                        nns_quantity=20, status='')
        self.pad_10 = Pad.objects.create(number='584у', field='ПРЗ',
                                         first_stage_date=date(2024, 3, 13),
                                         second_stage_date=date(2024, 4, 10),
                                         required_capacity=200, required_mud='РВО', gs_quantity=0,
                                         nns_quantity=8, status='', marker='СНПХ')

        self.type_of_DR_1 = type_of_DR.objects.create(type='5000/320')
        self.contractor_1 = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR_1, number=666,
                                                         contractor=self.contractor_1,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.next_position_1 = NextPosition.objects.create(current_position=self.rig_position_1, next_position=None,
                                                           status='default')

        self.contractor_2 = Contractor.objects.create(contractor='СНПХ')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR_1, number=777,
                                                         contractor=self.contractor_2,
                                                         mud='РВО')
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_2, pad=self.pad_2,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.next_position_2 = NextPosition.objects.create(current_position=self.rig_position_2,
                                                           next_position=self.pad_5,
                                                           status='default')

        self.type_of_DR_3 = type_of_DR.objects.create(type='2900/200')
        self.contractor_3 = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_3 = DrillingRig.objects.create(type=self.type_of_DR_3, number=888,
                                                         contractor=self.contractor_3,
                                                         mud='РВО')
        self.rig_position_3 = RigPosition.objects.create(drilling_rig=self.drilling_rig_3, pad=self.pad_7,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.next_position_3 = NextPosition.objects.create(current_position=self.rig_position_3, next_position=None,
                                                           status='')
        self.position_rating_3_1 = PositionRating.objects.create(current_position=self.rig_position_3,
                                                                 next_position=self.pad_10,
                                                                 capacity_rating=6,
                                                                 first_stage_date_rating=5,
                                                                 second_stage_date_rating=5,
                                                                 mud_rating=6,
                                                                 logistic_rating=4,
                                                                 marker_rating=7,
                                                                 common_rating=55,
                                                                 status='')
        self.position_rating_3_2 = PositionRating.objects.create(current_position=self.rig_position_3,
                                                                 next_position=self.pad_5,
                                                                 capacity_rating=6,
                                                                 first_stage_date_rating=5,
                                                                 second_stage_date_rating=5,
                                                                 mud_rating=6,
                                                                 logistic_rating=4,
                                                                 marker_rating=7,
                                                                 common_rating=80,
                                                                 status='')

    def test_put_result_of_definition_in_NextPosition(self):
        self.assertEquals(self.next_position_3.next_position, None)

        put_result_of_definition_in_NextPosition(self.rig_position_3, self.pad_7, 'default')

        self.assertEquals(NextPosition.objects.get(current_position=self.rig_position_3).next_position, self.pad_7)
        self.assertEquals(NextPosition.objects.get(current_position=self.rig_position_3).status, 'default')

    def test_give_status_booked_to_PositionRating(self):
        give_status_booked_to_PositionRating(self.pad_10)

        self.assertEquals(PositionRating.objects.get(next_position=self.pad_10).status, 'booked')

    def test_get_objs_from_PositionRating(self):
        objs_from_PositionRating = get_objs_from_PositionRating(self.rig_position_3)

        self.assertEquals(objs_from_PositionRating[0], self.position_rating_3_2)
        self.assertEquals(objs_from_PositionRating[1], self.position_rating_3_1)

    def test_define_next_position(self):

        res = define_next_position(self.rig_position_3)
        res1 = define_next_position(self.rig_position_2)

        self.assertEquals(res['next_position'], self.pad_10)
        self.assertEquals(res['status'], 'default')

        self.assertEquals(res1['next_position'], None)

    def test_define_position_and_put_into_DB(self):
        start_date_for_calculation = date(2024, 2, 29)
        end_date_for_calculation = date(2024, 3, 2)

        define_position_and_put_into_DB(start_date_for_calculation, end_date_for_calculation)

        self.assertEquals(NextPosition.objects.get(current_position=self.rig_position_1).next_position, self.pad_8)
        self.assertEquals(NextPosition.objects.get(current_position=self.rig_position_1).status, 'default')
