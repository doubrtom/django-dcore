try:
    from rest_framework.response import Response
    from rest_framework.request import Request
    from rest_framework.decorators import action
    from rest_framework import status as http_status
    from django.db.models import Q
except ImportError:
    pass  # Nothing to do, do not define InheritanceModelSerializer
else:
    class BatchEndpointMixin:
        batch_create_method = 'create'
        batch_allow_empty_items = True

        @action(methods=['put', 'post', 'patch'], detail=False)
        def batch(self, request: Request):
            """Endpoint for batch actions.

            PUT - replace whole collection with new items, remove old items
            POST - add new items to collection, keep old items
            PATCH - update sent items
                - you have to pass PK for each item, if PK is missing (or entity does not exist), item is ignored.

            You can use query_params to filter collection.

            Settings by class attribute:
            ----------------------------
            batch_create_method : string
                Method to use on queryset to create new items - create/get_or_create
            """
            assert self.batch_create_method in ['create', 'get_or_create'], \
                'Invalid value in "batch_create_method" field.'

            response = {'errors': [], 'items': []}
            qs = self.get_queryset()
            pk_field_name = qs.model._meta.pk.name

            data: dict = request.data
            if type(data) is not dict:
                data = data.dict()
            items = data.get('items', None)

            if items is None:
                return Response('Invalid data, missing "items" field in data.', status=http_status.HTTP_400_BAD_REQUEST)

            if not isinstance(items, list):
                return Response('Invalid data, "items" field has to be list.', status=http_status.HTTP_400_BAD_REQUEST)

            if len(items) == 0 and not self.batch_allow_empty_items:
                return Response('Invalid data, "items" list is empty.', status=http_status.HTTP_400_BAD_REQUEST)

            # Validate all:
            any_error = False
            for item in items:
                serializer = self.get_serializer(data=item, partial=(request.method == 'PATCH'))
                if not serializer.is_valid():
                    any_error = True
                    serializer_errors = serializer.errors
                    if isinstance(serializer_errors, dict) and 'errors' in serializer_errors:
                        response['errors'].append(serializer_errors['errors'])
                    else:
                        response['errors'].append(serializer_errors)
                else:
                    response['errors'].append(None)

            if any_error:
                del response['items']
                return Response(response, status=http_status.HTTP_400_BAD_REQUEST)
            else:
                del response['errors']

            # Use filters
            if filter_class := getattr(self, 'filterset_class', None):
                filter_obj = filter_class(data=request.query_params, queryset=qs)
                qs = filter_obj.qs

            # create items
            if request.method in ['PUT', 'POST']:
                created_pks = []
                for item_data in items:
                    if self.batch_create_method == 'create':
                        created_obj = qs.create(**item_data)
                    elif self.batch_create_method == 'get_or_create':
                        created_obj, __ = qs.get_or_create(**item_data)
                    created_pks.append(created_obj.pk)
                    response['items'].append(self.get_serializer(created_obj).data)
                # delete old items
                if request.method == 'PUT':
                    qs.filter(~Q(pk__in=created_pks)).delete()

            # update items
            if request.method == 'PATCH':
                for item in items:
                    try:
                        instance = qs.get(**{f'{pk_field_name}': item.get(pk_field_name)})
                    except qs.model.DoesNotExist:
                        response['items'].append(None)
                        continue
                    serializer = self.get_serializer(instance, data=item, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    response['items'].append(serializer.data)

            return Response(response, status=http_status.HTTP_200_OK)
