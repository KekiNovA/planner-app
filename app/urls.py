from django.urls import path
from .views import PlannerAPIView

urlpatterns = [
    path('plan', PlannerAPIView.as_view()),
]
