from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'newsletters', views.NewsletterViewSet)
router.register(r'newsletter_stats', views.NewsletterStatsViewSet, basename='newsletter-stats')

urlpatterns = [
    path('', include(router.urls)),
]
