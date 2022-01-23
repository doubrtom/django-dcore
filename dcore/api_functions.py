from typing import Type

from django.db import transaction
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework import status as http_status
from .validation_utils import validation_failed_dict


@transaction.atomic
def bulk_update(
    request: Request,
    queryset: QuerySet,
    serializer_class: Type[ModelSerializer],
    pk_name: str = 'id',
):
    """Function to add bulk_update endpoint into rest_framework.viewsets.ModelViewSet"""
    request_data = request.data
    if not isinstance(request_data, list):
        err = validation_failed_dict([(2513, None, "Expected list of dictionaries.")])
        return Response(err, status=http_status.HTTP_400_BAD_REQUEST)
    any_error = False
    serializers = []
    for item_data in request_data:
        if not isinstance(item_data, dict):
            any_error = True
            break
        pk_value = item_data.pop(pk_name, None)
        if pk_value is None:
            any_error = True
            break
        try:
            item = queryset.get(**{pk_name: pk_value})
        except (ObjectDoesNotExist, ValidationError):
            any_error = True
            break
        serializer = serializer_class(item, data=item_data, partial=True, context={'request': request})
        if not serializer.is_valid():
            any_error = True
            break
        serializers.append(serializer)
    if any_error:
        err = validation_failed_dict([(2951, None, 'Error in data for bulk action.')])
        return Response(err, status=http_status.HTTP_400_BAD_REQUEST)
    instances = [serializer.save() for serializer in serializers]
    response_serializer = serializer_class(instances, many=True, context={'request': request})
    return Response(response_serializer.data, status=http_status.HTTP_200_OK)
