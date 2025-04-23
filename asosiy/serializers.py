import re

from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from asosiy.models import User, KODNI_TASDIQLASH, YANGI, TASDIQLANDI
from Yordamchi.help import send_email
email_regax = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class SingupSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(SingupSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'royxat_bosqichi',
        )
        extra_kwargs = {
            'royxat_bosqichi':{'required':False , 'read_only':True},
        }
    def validate(self,data):
        super(SingupSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data
    def create(self, validated_data):
        user = super(SingupSerializer, self).create(validated_data)
        kod = user.kodni_olish()
        send_email(user.email, kod)
        user.save()
        return user

    @staticmethod
    def auth_validate(data):
        email = str(data.get('email')).lower()
        # print(email)
        global email_regax
        if re.fullmatch(email_regax, email):
            data = {
                'email': email,
            }
        else:
            data = {
                'success': False,
                'message': 'Email xato kiritilgan . Iltimos tekshirib qaytadan kiriting ! '
            }
            raise ValidationError(data)
        return data
    def validate_email(self, email):
        email = email.lower()
        # global email_regax
        # if re.fullmatch(email_regax, email):
        #     data = {
        #         'success': False,
        #         'message': 'Email xato kiritilgan . Iltimos tekshirib qaytadan kiriting ! '
        #     }
        #     raise ValidationError(data)
        if email and User.objects.filter(email=email).exists():
            raise ValidationError({
                'success': False,
                'message': "Email oldin ro'yxatdan o'tgan . "
            })

        return email
    def to_representation(self, instance):
        data = super(SingupSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data

class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError({
                'success': False,
                'message': "Kiritilgan parollar bir birga mos emas !"
            })
        if password:
            validate_password(password)
        return data
    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            raise ValidationError({
                'success': False,
                'message': "Username 5 dan katta 30 dan kichik bo'lishi shart !"
            })
        if User.objects.filter(username=username).exists():
            raise ValidationError({
                'success': False,
                'message': "Username allaqachon ishlatilgan !"
            })
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.royxat_bosqichi==KODNI_TASDIQLASH:
            instance.royxat_bosqichi = TASDIQLANDI
        instance.save()
        return instance

class Rasmni_ozgartirish(serializers.Serializer):
    photo = serializers.ImageField(
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'heic', 'heif',])
        ]
    )

    def update(self, instance, validated_data):
        photo = validated_data.get('photo', None)
        if photo:
            instance.photo = photo
            instance.royxat_bosqichi =








