from datetime import date

from django.test import TestCase

from dvizhenie.models import RigPosition, DrillingRig, Contractor, type_of_DR, Pad, PositionRating
from dvizhenie.services.define_position.calculate_all_ratings_and_put_into_DB import calculate_ratings_for_positions_and_put_into_DB, \
    get_rigs_for_calculation_rating, calculate_all_ratings_and_put_into_DB, get_free_pads, clear_PositionRating


class CalculateAllRatingsAndPutIntoDBTestCase(TestCase):
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
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.contractor2 = Contractor.objects.create(contractor='СНПХ')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR, number=777, contractor=self.contractor2,
                                                         mud='РВО')
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_2, pad=self.pad_2,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))

    def test_get_free_pads(self):
        free_pads = get_free_pads()
        self.assertEquals(len(free_pads), 8)

    def test_calculate_ratings_for_positions_and_put_into_DB(self):
        free_pads = Pad.objects.all()
        rigs = RigPosition.objects.all()
        calculate_ratings_for_positions_and_put_into_DB(rigs, free_pads)
        self.assertEquals(len(PositionRating.objects.all()), 10)

    def test_clear_PositionRating(self):
        free_pads = Pad.objects.all()
        rigs = RigPosition.objects.all()
        calculate_ratings_for_positions_and_put_into_DB(rigs, free_pads)

        self.assertEquals(len(PositionRating.objects.all()), 10)
        clear_PositionRating()
        self.assertEquals(len(PositionRating.objects.all()), 0)

    def test_get_rigs_for_calculation_rating(self):
        start_date_for_calculation = date(2024, 2, 29)
        end_date_for_calculation = date(2024, 3, 2)
        rigs_for_calculation_rating = get_rigs_for_calculation_rating(start_date_for_calculation,
                                                                      end_date_for_calculation)

        self.assertEquals(len(rigs_for_calculation_rating), 2)

    def test_calculate_all_ratings_and_put_into_DB(self):
        start_date_for_calculation = date(2024, 2, 29)
        end_date_for_calculation = date(2024, 3, 2)
        calculate_all_ratings_and_put_into_DB(start_date_for_calculation, end_date_for_calculation)

        self.assertEquals(len(PositionRating.objects.all()), 8)
