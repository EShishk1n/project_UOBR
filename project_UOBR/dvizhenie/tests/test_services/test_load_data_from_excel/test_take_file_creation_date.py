from datetime import date
from django.test import TestCase

from dvizhenie.services.load_data_from_excel.take_file_creation_date import take_file_creation_date


class TakeFileCreationDataTestCase(TestCase):

    def setUp(self):
        self.file_creation_date = '03-03-2024, 14:24'

    def test_take_file_cration_data(self):

        result = take_file_creation_date()
        self.assertEquals(result, self.file_creation_date)
