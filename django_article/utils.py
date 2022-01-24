import json
from django.http.response import HttpResponse
from marshmallow import ValidationError


def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


def json_response(data=None, status=200):
    if data is None:
        data = {}
    return HttpResponse(
        content=json.dumps(data), status=status, content_type="application/json"
    )
