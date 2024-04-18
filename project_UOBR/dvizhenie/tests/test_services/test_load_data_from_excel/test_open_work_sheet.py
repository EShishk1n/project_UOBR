from django.test import TestCase

from dvizhenie.services.load_data_from_excel.open_work_sheet import open_work_sheet


class OpenWorkSheetTestCase(TestCase):

    def test_open_work_sheet(self):

        ws = open_work_sheet('dvizhenie/tests/test_services/test_load_data_from_excel/Движение_БУ.xlsx')

        self.assertEquals(ws['i1'].value, 'Дальнейшее движение')
