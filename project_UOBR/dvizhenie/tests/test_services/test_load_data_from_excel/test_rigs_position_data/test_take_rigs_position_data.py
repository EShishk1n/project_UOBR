from datetime import datetime

from django.test import TestCase

from dvizhenie.services.load_data_from_excel.pads_data.take_pads_data import take_marker_data_from_row, \
    take_pads_data_from_table, take_pads_data_from_row
from dvizhenie.services.load_data_from_excel.rigs_position_data.take_rigs_position_data import \
    take_rigs_position_data_from_row, take_rigs_position_data_from_table


class TakeRigsPositionsDataTestCase(TestCase):

    def setUp(self):
        self.row = ('303у', 'ПРОл', datetime(2023, 8, 13, 0, 0))
        self.table_start_row = 8
        self.table_end_row = 9

    def test_take_rigs_position_data_from_row(self):

        rig_position_data = take_rigs_position_data_from_row(self.row)

        self.assertEquals(rig_position_data['number'], '303у')

    def test_take_rigs_position_data_from_table(self):

        rigs_position_data = take_rigs_position_data_from_table(self.table_start_row, self.table_end_row,
                                                                path='dvizhenie/tests/test_services/'
                                                                     'test_load_data_from_excel/Движение_БУ.xlsx')

        self.assertEquals(len(rigs_position_data), 2)
        self.assertEquals(rigs_position_data[1]['number'], '3208.2')
