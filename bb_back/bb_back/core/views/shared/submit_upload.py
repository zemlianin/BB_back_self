import codecs
import csv

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from bb_back.core.models import Submit, Round
from bb_back.core.utils.view_utils import failed_validation_response, response
from bb_back.core.views.utils.base_serializers import BaseResponseSerializer
from bb_back.settings import SUBMIT_MAX_SIZE
from services.submit_service import SubmitService


class SubmitRequestSerializer(serializers.Serializer):
    file = serializers.FileField()
    round_num = serializers.IntegerField()


class SubmitResponseSerializer(BaseResponseSerializer):
    response_data = SubmitRequestSerializer()


class SubmitView(APIView):
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "file",
                in_=openapi.IN_FORM,
                description="file",
                type=openapi.TYPE_FILE,
                required=True,
            )
        ],
        request_body=SubmitRequestSerializer,
        responses={status.HTTP_200_OK: SubmitResponseSerializer},
    )
    def post(self, request):
        if request.user.id is None:
            return response(status_code=status.HTTP_400_BAD_REQUEST,
                            data={},
                            message="User not found")

        team = request.user.team
        request_data = SubmitRequestSerializer(data=request.data)
        submit_file = request.FILES.get("file")

        if not request_data.is_valid() or request.FILES.get("file") is None:
            return failed_validation_response(serializer=request_data)

        if submit_file.size > SUBMIT_MAX_SIZE:
            return failed_validation_response(serializer=request_data)

        submit_schema = request_data.data
        round = Round.objects.filter(id=submit_schema.get("round_num")).first()

        if not round:
            return response(
                status_code=status.HTTP_400_BAD_REQUEST,
                data={},
                message=f"Round with id={submit_schema.get('round_num')} not found")

        try:
            response_data = SubmitService.save_submit(
                submit_file, team, submit_schema)

            response_data.is_valid()
            data = Response(data=response_data.data, status=status.HTTP_200_OK)

            return SubmitResponseSerializer(data)

        except ValueError as ex:
            return response(status_code=status.HTTP_400_BAD_REQUEST,
                            data={},
                            message=f"{str(ex)}")

