import json

from django.test import TestCase
from django.urls import reverse

from django_article.authors.models import Author


class AuthorListViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("authors-list")
        self.author_name_1 = ("Chelsy", "Schmidt")
        self.author_name_2 = ("Tomas", "Fulton")
        self.author_1 = Author.objects.create(first_name=self.author_name_1[0], last_name=self.author_name_1[1])
        self.author_2 = Author.objects.create(first_name=self.author_name_2[0], last_name=self.author_name_2[1])

    def test_serializes_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [
                {
                    "id": self.author_1.id,
                    "first_name": self.author_name_1[0],
                    "last_name": self.author_name_1[1],
                },
                {
                    "id": self.author_2.id,
                    "first_name": self.author_name_2[0],
                    "last_name": self.author_name_2[1],
                },
            ],
        )

    def test_creates_new_author(self):
        payload = {
            "first_name": "Jonny",
            "last_name": "Calvert",
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        author = Author.objects.last()
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(author)
        self.assertEqual(Author.objects.count(), 3)
        self.assertDictEqual(
            {
                "id": author.id,
                **payload
            },
            response.json(),
        )


class AuthorViewTestCase(TestCase):
    def setUp(self):
        self.author_name = {
            "first_name": "Jonny",
            "last_name": "Calvert",
        }
        self.author = Author.objects.create(**self.author_name)
        self.url = reverse("author", kwargs={"author_id": self.author.id})

    def test_serializes_single_record_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            {
                "id": self.author.id,
                **self.author_name
            },
        )

    def test_updates_author(self):
        self.updated_author = {
            "first_name": "Deborah",
            "last_name": "Glenn",
        }
        payload = {
            "id": self.author.id,
            **self.updated_author
        }
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        author = Author.objects.filter(id=self.author.id).first()
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(author)
        self.assertEqual(Author.objects.count(), 1)
        self.assertDictEqual(
            {
                "id": author.id,
                **self.updated_author
            },
            response.json(),
        )

    def test_removes_author(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Author.objects.count(), 0)
