from datetime import datetime

from django.views.generic import UpdateView
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.utils import timezone
from rest_framework.views import APIView

from Yordamchi.help import send_email
# from rest_framework.permissions import IsAuthenticated, AllowAny
# from tutorial.quickstart.serializers import UserSerializer

from asosiy.models import User, UserTasdiqlash, YANGI, KODNI_TASDIQLASH
from asosiy.serializers import SingupSerializer, ChangeUserInformation


class CreateUserView(CreateAPIView):
    serializer_class = SingupSerializer
    queryset = User.objects.all()
    permission_classes =(permissions.AllowAny,)

class ChangeUserInformationView(UpdateAPIView):
    serializer_class = ChangeUserInformation
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user
    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView,self).update(request, *args, **kwargs)
        data = {
            'success': True,
            'message': 'User information successfully updated',
            "ro'yxatdan o'tish bosqichi : ": request.user.royxat_bosqichi,
        }
        return Response(data, status=status.HTTP_200_OK)
    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        data = {
            'success': True,
            'message': 'User information successfully updated',
            'auth_status': request.user.auth_status,
        }
        return Response(data, status=status.HTTP_200_OK)

class Kodni_tekshirish(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request, *args, **kwargs):
        user = request.user
        kod = request.data.get('kod')
        self.kodni_tekshir(user,kod)
        data = {
            'success': True,
            "auth_status": user.user_roli,
            "access_token": user.token()['access_token'],
            "refresh_token": user.token()['refresh_token']
        }
        return Response(data, status=status.HTTP_200_OK)
    @staticmethod
    def kodni_tekshir(user,kod):
        tekshirish = user.tasdiqlash_kodi.filter(kod=kod, kod_vaqti__gte = datetime.now(), tasdiqlandimi = False)
        if tekshirish.exists():
            tekshirish.update(tasdiqlandimi = True)
        else:
            data = {
                'success': False,
                "message": "Tasdiqlash kodingniz xato yoki eskirgan ."
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if user.user_roli == YANGI:
            user.user_roli = KODNI_TASDIQLASH
            user.save()
        return True

class GetNewVerifationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        self.check_verification(user)
        code = user.kodni_olish()
        send_email(user.email, code)
        return Response({
            'success': True,
            'message': "Tasdiqlash kodingiz jo'natildi . "
        })
    @staticmethod
    def check_verification(user):
        yaroqlimi = user.tasdiqlash_kodi.filter(kod_vaqti__gte=datetime.now(), tasdiqlandimi = False)
        if yaroqlimi.exists():
            data ={
                'success': False,
                'message': "Eski kodingiz ishlatishga yaroqli iltimos kutib turing !"
            }
            raise ValidationError(data)














