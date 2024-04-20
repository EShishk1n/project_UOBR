from django.test import TestCase

from dvizhenie.services.funcs_for_views.handle_upload_file import handle_uploaded_file


class HandleUploadFileTestCase(TestCase):

    def test_handle_upload_file(self):

        handle_uploaded_file(f="dvizhenie/tests/test_services/test_load_data_from_excel/Движение_БУ.xlsx",
                             path="dvizhenie/tests/test_services/test_funcs_for_views/Движение_БУ.xlsx")
