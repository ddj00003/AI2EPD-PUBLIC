from django.urls import path

from .views import (
    LabelingApiView, CustomAuthToken,
)

urlpatterns = [
    path('labeling/', LabelingApiView.as_view(), name='labeling'),
    path('api-token-auth/', CustomAuthToken.as_view(), name='auth')
]