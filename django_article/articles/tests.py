import json
from django.test import TestCase
from django.urls import reverse
from django_article.articles.models import Article
from django_article.authors.models import Author
from django_article.regions.models import Region


class ArticleListViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("articles-list")
        self.article_1 = Article.objects.create(title="Fake Article 1")
        self.region_1 = Region.objects.create(code="AL", name="Albania")
        self.region_2 = Region.objects.create(code="UK", name="United Kingdom")
        self.article_2 = Article.objects.create(
            title="Fake Article 2", content="Lorem Ipsum"
        )
        self.article_2.regions.set([self.region_1, self.region_2])
        self.author = Author.objects.create(first_name="Henry", last_name="Benington")
        self.article_3 = Article.objects.create(title="Test Article with Author", author=self.author)
        self.article_3.regions.set([self.region_2])

    def test_serializes_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [
                {
                    "id": self.article_1.id,
                    "title": "Fake Article 1",
                    "content": "",
                    "author": {},
                    "regions": [],
                },
                {
                    "id": self.article_2.id,
                    "title": "Fake Article 2",
                    "content": "Lorem Ipsum",
                    "author": {},
                    "regions": [
                        {
                            "id": self.region_1.id,
                            "code": "AL",
                            "name": "Albania",
                        },
                        {
                            "id": self.region_2.id,
                            "code": "UK",
                            "name": "United Kingdom",
                        },
                    ],
                },
                {
                    "id": self.article_3.id,
                    "title": "Test Article with Author",
                    "content": "",
                    "author": {
                        "id": self.author.id,
                        "first_name": "Henry",
                        "last_name": "Benington",
                    },
                    "regions": [
                        {
                            "id": self.region_2.id,
                            "code": "UK",
                            "name": "United Kingdom",
                        },
                    ],
                },
            ],
        )

    def test_creates_new_article_with_regions(self):
        payload = {
            "title": "Fake Article 3",
            "content": "To be or not to be",
            "author": None,
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"code": "AU", "name": "Austria"},
            ],
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 3",
                "content": "To be or not to be",
                "author": {},
                "regions": [
                    {
                        "id": regions.all()[0].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                    {"id": regions.all()[1].id, "code": "AU", "name": "Austria"},
                ],
            },
            response.json(),
        )

    def test_creates_new_article_with_author(self):
        payload = {
            "title": "Fake Article 4",
            "content": "To be or not to be",
            "author": {
                "id": self.author.id
            },
            "regions": [],
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        author = article.author
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(article)
        self.assertIsNotNone(author)
        self.assertEqual(regions.count(), 0)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 4",
                "content": "To be or not to be",
                "author": {
                    "id": self.author.id,
                    "first_name": self.author.first_name,
                    "last_name": self.author.last_name
                },
                "regions": [],
            },
            response.json(),
        )

    def test_creates_new_article_with_non_existing_author(self):
        payload = {
            "title": "Fake Article 4",
            "content": "To be or not to be",
            "author": {
                "id": 66666
            },
            "regions": [],
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), {
            "author": [
                "Author does not exists"
            ]
        })


class ArticleViewTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(first_name="Henry", last_name="Benington")
        self.article = Article.objects.create(title="Fake Article 1", author=self.author)
        self.region_1 = Region.objects.create(code="AL", name="Albania")
        self.region_2 = Region.objects.create(code="UK", name="United Kingdom")
        self.article.regions.set([self.region_1, self.region_2])
        self.url = reverse("article", kwargs={"article_id": self.article.id})

    def test_serializes_single_record_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            {
                "id": self.article.id,
                "title": "Fake Article 1",
                "content": "",
                "author": {
                    "id": self.author.id,
                    "first_name": self.author.first_name,
                    "last_name": self.author.last_name
                },
                "regions": [
                    {
                        "id": self.region_1.id,
                        "code": "AL",
                        "name": "Albania",
                    },
                    {
                        "id": self.region_2.id,
                        "code": "UK",
                        "name": "United Kingdom",
                    },
                ],
            },
        )

    def test_updates_article_and_regions(self):
        # Change regions
        new_author = Author.objects.create(first_name="Charles", last_name="Monroe")
        payload = {
            "title": "Fake Article 1 (Modified)",
            "content": "To be or not to be here",
            "author": {
                "id": new_author.id,
                "first_name": new_author.first_name,
                "last_name": new_author.last_name
            },
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"id": self.region_2.id},
            ],
        }
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.first()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertEqual(Article.objects.count(), 1)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "author": {
                    "id": new_author.id,
                    "first_name": new_author.first_name,
                    "last_name": new_author.last_name
                },
                "regions": [
                    {
                        "id": self.region_2.id,
                        "code": "UK",
                        "name": "United Kingdom",
                    },
                    {
                        "id": regions.all()[1].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                ],
            },
            response.json(),
        )
        # Remove regions
        payload["regions"] = []
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 0)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "author": {
                    "id": new_author.id,
                    "first_name": new_author.first_name,
                    "last_name": new_author.last_name
                },
                "content": "To be or not to be here",
                "regions": [],
            },
            response.json(),
        )

        # Remove author
        payload["author"] = None
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        author = article.author
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertIsNone(author)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "author": {},
                "content": "To be or not to be here",
                "regions": [],
            },
            response.json(),
        )

    def test_get_all_articles_of_author(self):
        article1 = Article.objects.create(title="Sample Article 1", author=self.author)
        article2 = Article.objects.create(title="Sample Article 2", author=self.author)
        article3 = Article.objects.create(title="Sample Article 3", author=self.author)
        article4 = Article.objects.create(title="Sample Article 4", author=self.author)
        article5 = Article.objects.create(title="Sample Article 5", author=self.author)

        all_articles = self.author.articles.all()
        self.assertCountEqual(all_articles, [self.article, article1, article2, article3, article4, article5])

    def test_removes_article(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Article.objects.count(), 0)
