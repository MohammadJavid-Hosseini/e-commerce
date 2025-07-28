from rest_framework import status
from rest_framework.response import Response


class AddActivateEndpointMixin:

    def perform_activate(self, obj):

        if obj.is_active:
            return Response(
                {'detail': 'It is already activated'},
                status=status.HTTP_400_BAD_REQUEST)

        obj.is_active = True
        obj.save()

        return Response(
            {'detail': 'It is activated'},
            status=status.HTTP_200_OK
        )
