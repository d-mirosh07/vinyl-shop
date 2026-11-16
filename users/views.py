import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User registered: id={user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(
            f"Registration rejected: invalid fields {list(serializer.errors.keys())}"
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
