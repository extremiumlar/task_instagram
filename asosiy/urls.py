from django.urls import path

from asosiy.views import CreateUserView, ChangeUserInformationView, GetNewVerifationView, Kodni_tekshirish

urlpatterns = [
    path('sign-up/', CreateUserView.as_view(), name='sign-up'),
    path('verify/', Kodni_tekshirish.as_view(), name='verify'),
    path('new-verify/', GetNewVerifationView.as_view(), name='new-verifies'),
    path('change-user/', ChangeUserInformationView.as_view(), name='change-user'),

]