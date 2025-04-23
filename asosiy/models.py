import random
import uuid
import re
from datetime import timedelta, datetime
# from random import random

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from Yordamchi.models import BaseModel

email_regax = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


ODDIY, MANAGER, ADMIN = ('oddiy', 'manager', 'admin')
YANGI , KODNI_TASDIQLASH, TASDIQLANDI , RASM = ('yangi', 'kodni_tasdiqlash', 'tasdiqlandi', 'rasm')

# kodni tasdiqlash emas , kod_tasdiqlandi    kodni_tasdiqlash-> kod_tasdiqlandi
# tasdiqlandi emas , o'zgartirish saqlandi bo'ladi odatda username , parol , ism , familiya
# o'zgartirganda o'zgartirildi degan ma'lumot chiqarish uchun tasdiqlandi->ozgartirildi



class User(AbstractUser, BaseModel):
    user_rollari = (
        (ODDIY , ODDIY),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    royxat_bosqichlari = (
        (YANGI, YANGI),
        (KODNI_TASDIQLASH, KODNI_TASDIQLASH),
        (TASDIQLANDI, TASDIQLANDI),
        (RASM, RASM)
    )


    user_roli = models.CharField(max_length=31, choices=user_rollari , default=ODDIY)
    royxat_bosqichi = models.CharField(max_length=31, choices=royxat_bosqichlari , default=YANGI)
    email = models.EmailField(null=True, blank=True, unique=True)
    photo = models.ImageField(null=True, blank=True, upload_to='user_photos',
                              # faqat rasm yuklash uchun validators qo'shildi
                              validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'heic', 'heif'])])
    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def kodni_olish(self):
        kod = "".join([
            str(random.randint(0,100)%10) for _ in range(4)
        ])

        UserTasdiqlash.objects.create(
            foydalanuvchi_id = self.id,
            kod = kod,
        )
        return kod

    def check_username(self):
        if not self.username:
            temp_username = f'instagramm-{uuid.uuid4().__str__().split("-")[-1]}'
            while User.objects.filter(username=temp_username):
                temp_username = f'instagram-{uuid.uuid4().__str__().split("-")[-1]}'
            self.username = temp_username

    def check_pass(self):
        if not self.password:
            self.password = f"password-{uuid.uuid4().__str__().split("-")[-1]}"
    def check_email(self):
        if self.email:
            self.email = self.email.lower()
        # global email_regax
        # if re.fullmatch(email_regax, self.email):
        #     data = {
        #         'success': False,
        #         'message': 'Email xato kiritilgan . Iltimos tekshirib qaytadan kiriting ! '
        #     }
        #     raise ValidationError(data)

    def hashing_pass(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
    def token(self):
        token = RefreshToken.for_user(self)
        return {
            'access_token': str(token.access_token),
            'refresh_token': str(token),
        }
    def clean(self):
        self.check_pass()
        self.check_email()
        self.check_username()
        self.hashing_pass()

    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)

class UserTasdiqlash(BaseModel):
    kod = models.CharField(max_length=4)
    foydalanuvchi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasdiqlash_kodi')

    kod_vaqti = models.DateTimeField(null=True, blank=True)
    tasdiqlandimi = models.BooleanField(default=False)
    def __str__(self):
        return str(self.foydalanuvchi.__str__())
    def save(self, *args, **kwargs):
        self.kod_vaqti = datetime.now()+timedelta(minutes=2)
        super(UserTasdiqlash, self).save(*args, **kwargs)


