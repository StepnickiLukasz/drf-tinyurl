from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APIClient


class TinyURLAPITestCase(SimpleTestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.api_url = "/api/tinyurl/"
        self.test_full_url = "http://example.com/some-long-url"

    def test_success_path(self):
        #  first save full url and generate short one
        response = self.client.post(
            self.api_url,
            data={"full_url": self.test_full_url},
        )
        self.assertTrue(response.status_code, status.HTTP_201_CREATED)
        short_url = response.json().get("short_url")
        self.assertIsNotNone(short_url)
        self.assertDictEqual(
            response.json(),
            {"short_url": short_url, "full_url": self.test_full_url},
        )
        #  second get redirect to the full URL by short one
        response = self.client.get(f"{self.api_url}{short_url}/")
        self.assertTrue(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.get("Location"), self.test_full_url)

    def test_create_empty_data(self):
        response = self.client.post(self.api_url, data={})
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_non_existing_url(self):
        response = self.client.get(f"{self.api_url}TestNotExistingShortUrl12345/")
        self.assertTrue(response.status_code, status.HTTP_404_NOT_FOUND)
