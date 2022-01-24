import django
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_article.settings")
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), "..", ".."))
django.setup()

from django_article.articles.models import Article
from django_article.regions.models import Region
from django_article.authors.models import Author
from django.core import management

# Migrate
management.call_command("migrate", no_input=True)
# Seed
Article.objects.create(title="Fake Article", content="Fake Content").regions.set(
    [
        Region.objects.create(code="AL", name="Albania"),
        Region.objects.create(code="UK", name="United Kingdom"),
    ]
)
Article.objects.create(title="Fake Article", content="Fake Content")
Article.objects.create(title="Fake Article", content="Fake Content")
Article.objects.create(title="Fake Article", content="Fake Content")
Article.objects.create(title="Fake Article", content="Fake Content").regions.set(
    [
        Region.objects.create(code="AU", name="Austria"),
        Region.objects.create(code="US", name="United States of America"),
    ]
)

Author.objects.create(first_name="Russell", last_name="Wormald")
Author.objects.create(first_name="Livia", last_name="Hobbs")
Author.objects.create(first_name="Luca", last_name="Amos")
Author.objects.create(first_name="Diego", last_name="Tanner")
