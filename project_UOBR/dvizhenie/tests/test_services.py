from datetime import date, datetime
from django.test import TestCase

from dvizhenie.models import Pad, type_of_DR, Contractor, DrillingRig, RigPosition, NextPosition, PositionRating
from dvizhenie.services.data_putter import put_rigs_position_data, put_pads_data
from dvizhenie.services.data_taker import open_work_sheet, take_rigs_position_data, take_pads_data, \
    take_file_cration_data
from dvizhenie.services.define_position import calculate_all_ratings_and_put_into_BD, _define_next_position, \
    define_position_and_put_into_BD

from dvizhenie.services.give_statuses_to_pads import give_statuses_to_pads


class DataTakerTestCase(TestCase):

    def test_open_work_sheet(self):
        self.assertEquals(open_work_sheet()['a2'].value, 'Месяц')

    def test_take_rigs_position_data(self):
        result = take_rigs_position_data(table_start_row=182, table_end_row=182)
        self.assertEquals(result, [{'number': 89, 'field': 'УБ', 'end_date': date(2024, 2, 18)}])

    def test_take_pads_data(self):
        result = take_pads_data(table_start_row=182, table_end_row=182)
        self.assertEquals(result, [{'number': 143, 'field': 'УБ', 'first_stage_date': date(2024, 9, 20),
                                    'second_stage_date': date(2024, 9, 20), 'required_capacity': 320,
                                    'required_mud': 'РУО', 'marker': 'нет', 'gs_quantity': 3, 'nns_quantity': 5}])

    def test_take_file_cration_data(self):
        # Дату для сравнения нужно поставить вручную
        result = take_file_cration_data()
        self.assertEquals(result, '27-02-2024, 06:06')


class DataPutterTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='89', field='УБ',
                                        first_stage_date=date(2023, 12, 20),
                                        second_stage_date=date(2023, 12, 20),
                                        required_capacity=320, required_mud='РУО', gs_quantity=5,
                                        nns_quantity=2, status='drilling')
        self.pad_2 = Pad.objects.create(number='143', field='УБ',
                                        first_stage_date=date(2024, 8, 20),
                                        second_stage_date=date(2024, 8, 20),
                                        required_capacity=320, required_mud='РУО', gs_quantity=5,
                                        nns_quantity=2, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РУО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2024, 4, 10), end_date=date(2024, 2, 10))

    def test_put_rigs_position_data(self):
        put_rigs_position_data(table_start_row=182, table_end_row=182)
        self.assertEquals(RigPosition.objects.filter(drilling_rig=self.drilling_rig_1)[0].end_date, date(2024, 2, 18))

    def test_put_pads_data(self):
        put_pads_data(table_start_row=182, table_end_row=182)
        self.assertEquals(Pad.objects.filter(number='143')[0].first_stage_date, date(2024, 9, 20))


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
            result.append(_get_capacity_rating(self.rig_position_1, pad))

        self.assertEquals(result, [10, 3, 0])

    def test__get_first_stage_date_rating(self):
        result = []
        for pad in (self.pad_2, self.pad_9, self.pad_10):
            result.append(_get_first_stage_date_rating(self.rig_position_1, pad))

        self.assertEquals(result, [10, 0.5, 6])

    def test__get_second_stage_date_rating(self):
        result = []
        for pad in (self.pad_2, self.pad_9, self.pad_10):
            result.append(_get_second_stage_date_rating(self.rig_position_1, pad))

        self.assertEquals(result, [10, 4, 0.5])

    def test__get_mud_rating(self):
        result = []
        for pad in (self.pad_2, self.pad_3, self.pad_9):
            result.append(_get_mud_rating(self.rig_position_1, pad))

        self.assertEquals(result, [10, 5, 10])

    def test__logistic_rating(self):
        result = []
        for pad in (
                self.pad_2, self.pad_3, self.pad_4, self.pad_5, self.pad_6, self.pad_7, self.pad_8, self.pad_9,
                self.pad_10):
            result.append(_get_logistic_rating(self.rig_position_1, pad))

        self.assertEquals(result, [4, 5, 4, 5, 10, 7, 5, 4, 10])

    def test__get_marker_for_drilling_rig(self):
        result1 = _get_marker_for_drilling_rig(self.rig_position_1)
        result2 = _get_marker_for_drilling_rig(self.rig_position_2)

        self.assertEquals(result1, 'стандартная БУ')
        self.assertEquals(result2, 'СНПХ')

    def test__marker_rating(self):
        result1 = _get_marker_rating(self.rig_position_1, self.pad_7)
        result2 = []
        for pad in (self.pad_5, self.pad_2, self.pad_7, self.pad_8):
            result2.append(_get_marker_rating(self.rig_position_2, pad))

        self.assertEquals(result1, 4)
        self.assertEquals(result2, [10, 0, 10, 0])

    def test__get_rating_and_put_into_BD(self):

        self.assertEquals(PositionRating.objects.all().count(), 0)

        for pad in (
                self.pad_2, self.pad_3, self.pad_4, self.pad_5, self.pad_6, self.pad_7, self.pad_8, self.pad_9,
                self.pad_10):
            _get_rating_and_put_into_BD(self.rig_position_1, pad)
            _get_rating_and_put_into_BD(self.rig_position_2, pad)

        self.assertEquals(PositionRating.objects.all().count(), 9)



class DefineRigsForDefinitionNextpositionTestCase(TestCase):

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
        self.pad_7 = Pad.objects.create(number='2136у', field='ПРОл',
                                        first_stage_date=date(2023, 12, 7),
                                        second_stage_date=date(2024, 1, 12),
                                        required_capacity=250, required_mud='РВО', gs_quantity=0,
                                        nns_quantity=24, status='', marker='СНПХ')
        self.pad_4 = Pad.objects.create(number='58', field='СУГ',
                                        first_stage_date=date(2024, 2, 20),
                                        second_stage_date=date(2024, 2, 20),
                                        required_capacity=250, required_mud='РВО', gs_quantity=9,
                                        nns_quantity=5, status='')
        self.pad_9 = Pad.objects.create(number='60', field='СУГ',
                                        first_stage_date=date(2024, 3, 23),
                                        second_stage_date=date(2024, 3, 24),
                                        required_capacity=320, required_mud='РУО', gs_quantity=4,
                                        nns_quantity=20, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_2,
                                                         start_date=date(2024, 5, 1), end_date=date(2024, 10, 1))
        self.next_position = NextPosition.objects.create(current_position=self.rig_position_2, next_position=self.pad_3,
                                                         status='commited')
        self.contractor2 = Contractor.objects.create(contractor='СНПХ')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR, number=777, contractor=self.contractor2,
                                                         mud='РВО')
        self.rig_position_3 = RigPosition.objects.create(drilling_rig=self.drilling_rig_2, pad=self.pad_9,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 9, 20))

    def test_get_statuses_to_pads(self):
        get_statuses_to_pads()

        self.assertEquals(Pad.objects.filter(number='133')[0].status, 'drilled')
        self.assertEquals(Pad.objects.filter(number='110')[0].status, 'drilling')
        self.assertEquals(Pad.objects.filter(number='669')[0].status, 'reserved')
        self.assertEquals(Pad.objects.filter(number='58')[0].status, 'free')

    def test__get_rigs_for_calculation_rating(self):
        result = _get_rigs_for_calculation_rating(start_date_for_calculation=date(2024, 9, 1),
                                                  end_date_for_calculation=date(2024, 11, 1))

        self.assertEquals(result[1], RigPosition.objects.filter(pad__number='110')[0])

    def test__put_rigs_for_define_in_NextPosition(self):
        _calculate_all_ratings_and_put_into_BD(start_date_for_calculation=date(2024, 9, 1),
                                               end_date_for_calculation=date(2024, 11, 1))

        self.assertEquals(NextPosition.objects.all().count(), 1)

        _put_rigs_for_define_in_NextPosition(start_date_for_calculation=date(2024, 9, 1),
                                             end_date_for_calculation=date(2024, 11, 1))

        self.assertEquals(NextPosition.objects.all().count(), 2)

    def test_form_next_position(self):
        _calculate_all_ratings_and_put_into_BD(start_date_for_calculation=date(2024, 9, 1),
                                               end_date_for_calculation=date(2024, 11, 1))
        form_next_position(start_date_for_calculation=date(2024, 9, 1),
                           end_date_for_calculation=date(2024, 11, 1))

        self.assertEquals(NextPosition.objects.all().count(), 2)

    def test_define_sequence_of_rigs_for_definition_positions(self):
        self.type_of_DR_3 = type_of_DR.objects.create(type='2900/200')
        self.contractor3 = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_3 = DrillingRig.objects.create(type=self.type_of_DR_3, number=888,
                                                         contractor=self.contractor3,
                                                         mud='РВО')
        self.pad_13 = Pad.objects.create(number='2142у', field='ПРОл',
                                         first_stage_date=date(2024, 2, 20),
                                         second_stage_date=date(2024, 2, 20),
                                         required_capacity=200, required_mud='РВО', gs_quantity=0,
                                         nns_quantity=10, status='')
        self.rig_position_3 = RigPosition.objects.create(drilling_rig=self.drilling_rig_3, pad=self.pad_13,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 9, 20))

        self.pad_15 = Pad.objects.create(number='2133e', field='ПРОп',
                                         first_stage_date=date(2024, 2, 20),
                                         second_stage_date=date(2024, 2, 20),
                                         required_capacity=200, required_mud='РВО', gs_quantity=0,
                                         nns_quantity=10, status='')

        self.type_of_DR_4 = type_of_DR.objects.create(type='4500/270')
        self.contractor4 = Contractor.objects.create(contractor='ХМФ РНБ')
        self.drilling_rig_4 = DrillingRig.objects.create(type=self.type_of_DR_4, number=999,
                                                         contractor=self.contractor2,
                                                         mud='РВО')
        self.pad_14 = Pad.objects.create(number='176', field='УБ',
                                         first_stage_date=date(2024, 2, 20),
                                         second_stage_date=date(2024, 2, 20),
                                         required_capacity=270, required_mud='РВО', gs_quantity=4,
                                         nns_quantity=10, status='')
        self.rig_position_4 = RigPosition.objects.create(drilling_rig=self.drilling_rig_4, pad=self.pad_14,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 9, 20))

        _calculate_all_ratings_and_put_into_BD(start_date_for_calculation=date(2024, 9, 1),
                                               end_date_for_calculation=date(2024, 11, 1))

        form_next_position(start_date_for_calculation=date(2024, 9, 1),
                           end_date_for_calculation=date(2024, 11, 1))

        result = define_sequence_of_rigs_for_definition_positions()

        self.assertEquals(result[0].current_position.pad.number, '2142у')
        self.assertEquals(result[1].current_position.pad.number, '176')
        self.assertEquals(result[2].current_position.pad.number, '60')


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
                                        nns_quantity=2, status='')
        self.pad_3 = Pad.objects.create(number='669', field='МБ',
                                        first_stage_date=date(2024, 2, 26),
                                        second_stage_date=date(2024, 3, 16),
                                        required_capacity=320, required_mud='РУО', gs_quantity=14,
                                        nns_quantity=4, status='')
        self.pad_7 = Pad.objects.create(number='2136у', field='ПРОл',
                                        first_stage_date=date(2023, 12, 7),
                                        second_stage_date=date(2024, 1, 12),
                                        required_capacity=250, required_mud='РВО', gs_quantity=0,
                                        nns_quantity=24, status='', marker='СНПХ')
        self.pad_4 = Pad.objects.create(number='58', field='СУГ',
                                        first_stage_date=date(2024, 2, 20),
                                        second_stage_date=date(2024, 2, 20),
                                        required_capacity=250, required_mud='РВО', gs_quantity=9,
                                        nns_quantity=5, status='')
        self.pad_9 = Pad.objects.create(number='60', field='СУГ',
                                        first_stage_date=date(2024, 3, 23),
                                        second_stage_date=date(2024, 3, 24),
                                        required_capacity=320, required_mud='РУО', gs_quantity=4,
                                        nns_quantity=20, status='')
        self.type_of_DR = type_of_DR.objects.create(type='5000/320')
        self.contractor = Contractor.objects.create(contractor='НФ РНБ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 3, 1))
        self.rig_position_2 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_2,
                                                         start_date=date(2024, 5, 1), end_date=date(2024, 10, 1))
        self.next_position = NextPosition.objects.create(current_position=self.rig_position_2, next_position=self.pad_3,
                                                         status='Подтверждено')
        self.contractor2 = Contractor.objects.create(contractor='СНПХ')
        self.drilling_rig_2 = DrillingRig.objects.create(type=self.type_of_DR, number=777, contractor=self.contractor2,
                                                         mud='РВО')
        self.rig_position_3 = RigPosition.objects.create(drilling_rig=self.drilling_rig_2, pad=self.pad_9,
                                                         start_date=date(2023, 2, 10), end_date=date(2024, 9, 20))

    def test__calculate_all_ratings_and_put_into_BD(self):
        _calculate_all_ratings_and_put_into_BD(start_date_for_calculation=date(2024, 9, 1),
                                               end_date_for_calculation=date(2024, 11, 1))

        self.assertEquals(PositionRating.objects.all().count(), 3)

    def test__define_next_position(self):
        _calculate_all_ratings_and_put_into_BD(start_date_for_calculation=date(2024, 9, 1),
                                               end_date_for_calculation=date(2024, 11, 1))

        rig_for_define_next_position = self.rig_position_2
        result = _define_next_position(rig_for_define_next_position)

        self.assertEquals(result['next_position'].number, '58')
        self.assertEquals(result['status'], 'Требуется подтверждение')

    def test_define_position_and_put_into_BD(self):
        self.assertEquals(NextPosition.objects.all().count(), 1)

        define_position_and_put_into_BD(start_date_for_calculation=date(2024, 9, 1),
                                        end_date_for_calculation=date(2024, 11, 1))

        self.assertEquals(NextPosition.objects.all().count(), 2)
        self.assertEquals(NextPosition.objects.filter(current_position=self.rig_position_2.id)[0].next_position.number,
                          '669')
        self.assertEquals(NextPosition.objects.filter(current_position=self.rig_position_3.id)[0].next_position.number,
                          '2136у')
