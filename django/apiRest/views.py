from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apiRest.serializers import LabelSerializer, UserSerializer
from datetime import datetime
from utils import get_db_handle


class CustomAuthToken(ObtainAuthToken):
    def post(self, _request, *_args, **_kwargs):
        """
        (POST) Get the authentication token.
        _request: The request.
        _args: The arguments.
        _kwargs: The keyword arguments.
        """
        _serializer = UserSerializer(data=_request.data)
        _serializer.is_valid(raise_exception=True)

        _username = _serializer.validated_data['username']
        _password = _serializer.validated_data['password']

        try:
            _user = User.objects.get(username=_username)
            if not _user.check_password(_password):
                return Response('{"message": "Incorrect credentials"}', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response('{"message": "Incorrect credentials"}', status=status.HTTP_401_UNAUTHORIZED)

        _token, _created = Token.objects.get_or_create(user=_user)

        return Response({
            'token': _token.key
        })


class LabelingApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, _request, *_args, **_kwargs):
        """
        (POST) Recover labels from the request and store them in the database.
        _request: request object.
        _args: The arguments.
        _kwargs: The keyword arguments.
        """
        _label = LabelSerializer(data=_request.data)

        _db, _client = get_db_handle(db_name="labeling_database", host="asia.ujaen.es", port=8001,
                                     username="user1", password="4s1a#2022", auth_source="diabetes_project")

        if _label.is_valid():
            _collection = _db.get_collection(_label.data['collection_name'])
            _collection.insert_one({'label': _label.data['label'],
                                    'timestamp': datetime.now().timestamp()})

        return Response('{"message": "Label inserted"}', status=status.HTTP_200_OK)