from datetime import datetime

from django.test import TestCase

from dvizhenie.services.load_data_from_excel.pads_data.take_pads_data import take_marker_data_from_row, \
    take_pads_data_from_table, take_pads_data_from_row


class TakePadsDataTestCase(TestCase):

    def setUp(self):
        self.row_1 = (
            541, 'ПРОп', datetime(2023, 2, 28, 0, 0), datetime(2023, 2, 28, 0, 0), 'готов', 320,
            'РУО', None, None, 5, 5)
        self.row_2 = (
            '147у', 'ПРОл', datetime(2023, 11, 30, 0, 0), datetime(2023, 12, 18, 0, 0), 'готов', 200,
            'РВО', 'ЛБТ', 'СНПХ', 6, 0)
        self.table_start_row = 8
        self.table_end_row = 9

    def test_take_marker_data_from_row(self):

        marker_data_1 = take_marker_data_from_row(self.row_1)
        marker_data_2 = take_marker_data_from_row(self.row_2)

        self.assertEquals(marker_data_1, 'нет')
        self.assertEquals(marker_data_2, 'СНПХ')

    def test_take_pads_data_from_row(self):

        pad_data = take_pads_data_from_row(self.row_1)

        self.assertEquals(pad_data['number'], 541)
        self.assertEquals(pad_data['marker'], 'нет')

    def test_take_pads_data_from_table(self):

        pads_data = take_pads_data_from_table(self.table_start_row, self.table_end_row)

        self.assertEquals(len(pads_data), 2)
        self.assertEquals(pads_data[0]['field'], 'ПРОп')
