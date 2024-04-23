import datetime

from django.test import TestCase

from dvizhenie.models import Pad, type_of_DR, Contractor, DrillingRig, RigPosition
from dvizhenie.services.load_data_from_excel.pads_data.put_pads_data import create_Pad_object, update_Pad_object, \
    put_pads_data
from dvizhenie.services.load_data_from_excel.rigs_position_data.put_rigs_position_data import put_rigs_position_data


class PutRigsPositionDataTestCase(TestCase):

    def setUp(self):
        self.pad_1 = Pad.objects.create(number='3208.2', field='ПРЗ',
                                        first_stage_date=datetime.date(2023, 12, 20),
                                        second_stage_date=datetime.date(2023, 12, 20),
                                        required_capacity=200, required_mud='РВО', gs_quantity=0,
                                        nns_quantity=24, status='drilled')
        self.type_of_DR = type_of_DR.objects.create(type='2900/200')
        self.contractor = Contractor.objects.create(contractor='ТБНГ')
        self.drilling_rig_1 = DrillingRig.objects.create(type=self.type_of_DR, number=666, contractor=self.contractor,
                                                         mud='РВО')
        self.rig_position_1 = RigPosition.objects.create(drilling_rig=self.drilling_rig_1, pad=self.pad_1,
                                                         start_date=datetime.date(2023, 2, 10),
                                                         end_date=datetime.date(2024, 3, 1))
        self.table_start_row = 9
        self.table_end_row = 9

    def test_put_rigs_position_data(self):
        self.assertEquals(RigPosition.objects.get(drilling_rig=DrillingRig.objects.get(number=666)).end_date,
                          datetime.date(2024, 3, 1))

        put_rigs_position_data(self.table_start_row, self.table_end_row, path='dvizhenie/tests/test_services/'
                                                                              'test_load_data_from_excel/'
                                                                              'Движение_БУ.xlsx')

        self.assertEquals(RigPosition.objects.get(drilling_rig=DrillingRig.objects.get(number=666)).end_date,
                          datetime.date(2023, 8, 21))
