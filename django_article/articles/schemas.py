from marshmallow import validate
from marshmallow import fields
from marshmallow import Schema
from marshmallow.decorators import post_load

from django_article.articles.models import Article
from django_article.regions.models import Region
from django_article.regions.schemas import RegionSchema
from django_article.utils import must_not_be_blank


class ArticleSchema(Schema):
    class Meta(object):
        model = Article

    id = fields.Integer()
    title = fields.String(validate=[validate.Length(max=255), must_not_be_blank], required=True, allow_blank=False)
    content = fields.String()
    regions = fields.Method(
        required=False, serialize="get_regions", deserialize="load_regions"
    )

    def get_regions(self, article):
        return RegionSchema().dump(article.regions.all(), many=True)

    def load_regions(self, regions):
        return [
            Region.objects.get_or_create(id=region.pop("id", None), defaults=region)[0]
            for region in regions
        ]

    @post_load
    def update_or_create(self, data, *args, **kwargs):
        regions = data.pop("regions", None)
        article, _ = Article.objects.update_or_create(
            id=data.pop("id", None), defaults=data
        )
        if isinstance(regions, list):
            article.regions.set(regions)
        return article
