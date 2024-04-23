import datetime

from django.test import TestCase

from dvizhenie.models import Pad
from dvizhenie.services.load_data_from_excel.pads_data.put_pads_data import create_Pad_object, update_Pad_object, \
    put_pads_data


class PutPadsDataTestCase(TestCase):

    def setUp(self):
        self.pad_data_1 = {'number': 541, 'field': 'ПРОп', 'first_stage_date': datetime.date(2023, 2, 28),
                           'second_stage_date': datetime.date(2023, 2, 28), 'required_capacity': 320,
                           'required_mud': 'РУО', 'marker': 'нет', 'gs_quantity': 5, 'nns_quantity': 0}
        self.pad_data_2 = {'number': '147у', 'field': 'ПРОл', 'first_stage_date': datetime.date(2023, 11, 30),
                           'second_stage_date': datetime.date(2023, 12, 18), 'required_capacity': 200,
                           'required_mud': 'РВО', 'marker': 'СНПХ', 'gs_quantity': 0, 'nns_quantity': 6}
        self.pad_already_in_Pad = Pad.objects.create(number='147у', field='ПРОл',
                                                     first_stage_date=datetime.date(2023, 12, 20),
                                                     second_stage_date=datetime.date(2023, 12, 20),
                                                     required_capacity=320, required_mud='РВО', gs_quantity=17,
                                                     nns_quantity=0, status='')
        self.table_start_row = 8
        self.table_end_row = 9

    def test_create_Pad_object(self):
        self.assertEquals(len(Pad.objects.all()), 1)

        create_Pad_object(self.pad_data_1)

        self.assertEquals(len(Pad.objects.all()), 2)
        self.assertEquals(Pad.objects.get(number=541).gs_quantity, 5)

    def test_update_Pad_object(self):

        self.assertEquals(Pad.objects.get(number='147у').nns_quantity, 0)

        update_Pad_object(Pad.objects.get(number='147у'), self.pad_data_2)

        self.assertEquals(Pad.objects.get(number='147у').nns_quantity, 6)

    def test_put_pads_data(self):

        self.assertEquals(len(Pad.objects.all()), 1)
        self.assertEquals(Pad.objects.get(number='147у').nns_quantity, 0)

        put_pads_data(self.table_start_row, self.table_end_row, path='dvizhenie/tests/test_services/'
                                                                     'test_load_data_from_excel/Движение_БУ.xlsx')

        self.assertEquals(len(Pad.objects.all()), 2)
        self.assertEquals(Pad.objects.get(number='147у').nns_quantity, 6)
        self.assertEquals(Pad.objects.get(number=541).gs_quantity, 5)
