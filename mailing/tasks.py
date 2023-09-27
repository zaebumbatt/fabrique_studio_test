from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from .message_gateway import AbstractMessageGateway, MessageGateway
from .models import Customer, Message, Newsletter

logger = get_task_logger(__name__)


@shared_task
def send_newsletter(
        newsletter_id: int,
        gateway: AbstractMessageGateway = MessageGateway
) -> None:
    newsletter = Newsletter.objects.get(id=newsletter_id)
    for customer in newsletter.customers.all():
        send_message(gateway, newsletter, customer)


def send_message(
        gateway: AbstractMessageGateway,
        newsletter: Newsletter,
        customer: Customer,
) -> None:
    message = Message.objects.create(
        newsletter=newsletter,
        customer=customer,
    )
    if newsletter.finish < timezone.now():
        logger.info(f'{newsletter.finish} already passed {timezone.now()}')
        message.status = Message.Status.CANCELED
        message.save()
        return

    result = gateway.send_message(message.id, customer.phone_number, newsletter.message_text)
    message.status = Message.Status.SUCCESS if result else Message.Status.FAILURE
    message.save()
