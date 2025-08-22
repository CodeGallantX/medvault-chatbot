from django.urls import path
from .views import ChatbotPredictView, ChatbotChatView, HealthCheckView

urlpatterns = [
    path('predict/', ChatbotPredictView.as_view(), name='predict'),
    path('chat/', ChatbotChatView.as_view(), name='chat'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
