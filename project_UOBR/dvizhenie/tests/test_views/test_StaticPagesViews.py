from django.test import TestCase
from django.urls import reverse


class SinglePagesTestCase(TestCase):

    def test_start_page(self):
        url = reverse('start_page')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_about_app(self):
        url = reverse('about_app')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_contacts(self):
        url = reverse('contacts')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
