from django.db.models import Count, Q
from rest_framework import viewsets

from .models import Customer, Message, Newsletter
from .serializers import (CustomerSerializer, NewsletterSerializer,
                          NewsletterStatsSerializer)


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


class NewsletterViewSet(viewsets.ModelViewSet):
    serializer_class = NewsletterSerializer
    queryset = Newsletter.objects.all()


class NewsletterStatsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NewsletterStatsSerializer
    queryset = Newsletter.objects.prefetch_related('messages').annotate(
        success=Count('pk', filter=Q(messages__status=Message.Status.SUCCESS)),
        ongoing=Count('pk', filter=Q(messages__status=Message.Status.ONGOING)),
        failure=Count('pk', filter=Q(messages__status=Message.Status.FAILURE)),
        canceled=Count('pk', filter=Q(messages__status=Message.Status.CANCELED)),
    )
