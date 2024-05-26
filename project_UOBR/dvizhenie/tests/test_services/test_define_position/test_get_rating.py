from datetime import date
from types import NoneType

from django.test import TestCase

from dvizhenie.models import Pad, type_of_DR, Contractor, DrillingRig, RigPosition, PositionRating
from dvizhenie.services.define_position.get_rating import get_capacity_rating, get_first_stage_date_rating, \
    get_second_stage_date_rating, get_mud_rating, get_logistic_rating, get_marker_for_drilling_rig, get_marker_rating, \
    get_rating, get_rating_and_put_into_DB


class GetRatingTestCase(TestCase):

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

    def test__get_capacity_rating(self):
        result = []
        for pad in (self.pad_2, self.pad_7, self.pad_10):
            result.append(get_capacity_rating(self.rig_position_1, pad))

        self.assertEquals(result, [10, 3, 0])

    def test__get_first_stage_date_rating(self):
        result_rating = []
        result_downtime = []
        for pad in (self.pad_2, self.pad_9, self.pad_10):
            result_rating.append(get_first_stage_date_rating(self.rig_position_1, pad)[0])
            result_downtime.append(get_first_stage_date_rating(self.rig_position_1, pad)[1])

        self.assertEquals(result_rating, [10, 1, 1])
        self.assertEquals(result_downtime, [0, 12, 2])

    def test__get_second_stage_date_rating(self):
        result = []
        for pad in (self.pad_2, self.pad_9, self.pad_10):
            result.append(get_second_stage_date_rating(self.rig_position_1, pad))

        self.assertEquals(result, [10, 4, 0.5])

    def test__get_mud_rating(self):
        result = []
        for pad in (self.pad_2, self.pad_3, self.pad_9):
            result.append(get_mud_rating(self.rig_position_1, pad))

        self.assertEquals(result, [10, 5, 10])

    def test__logistic_rating(self):
        result = []
        for pad in (
                self.pad_2, self.pad_3, self.pad_4, self.pad_5, self.pad_6, self.pad_7, self.pad_8, self.pad_9,
                self.pad_10):
            result.append(get_logistic_rating(self.rig_position_1, pad))

        self.assertEquals(result, [4, 5, 4, 5, 10, 7, 5, 4, 10])

    def test__get_marker_for_drilling_rig(self):
        result1 = get_marker_for_drilling_rig(self.rig_position_1)
        result2 = get_marker_for_drilling_rig(self.rig_position_2)

        self.assertEquals(result1, 'стандартная БУ')
        self.assertEquals(result2, 'СНПХ')

    def test__marker_rating(self):
        result1 = get_marker_rating(self.rig_position_1, self.pad_7)
        result2 = []
        for pad in (self.pad_5, self.pad_2, self.pad_7, self.pad_8):
            result2.append(get_marker_rating(self.rig_position_2, pad))

        self.assertEquals(result1, 4)
        self.assertEquals(result2, [10, 0, 10, 0])

    def test_get_rating(self):

        rating = get_rating(self.rig_position_1, self.pad_7)
        rating1 = get_rating(self.rig_position_2, self.pad_4)
        self.assertEquals(type(rating), PositionRating)
        self.assertEquals(type(rating1), NoneType)
        self.assertEquals(rating.common_rating, 72.9)

    def test_get_rating_and_put_into_DB(self):

        self.assertEquals(len(PositionRating.objects.all()), 0)
        get_rating_and_put_into_DB(self.rig_position_1, self.pad_7)
        get_rating_and_put_into_DB(self.rig_position_2, self.pad_4)
        self.assertEquals(len(PositionRating.objects.all()), 1)
