import abc
import os

import requests
from celery.utils.log import get_task_logger
from requests import ConnectTimeout
from rest_framework import status

logger = get_task_logger(__name__)


class AbstractMessageGateway(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def send_message(
            cls,
            message_id: int,
            customer_phone_number: str,
            newsletter_message_text: str,
    ) -> bool:
        raise NotImplementedError


class MessageGateway(AbstractMessageGateway):

    @classmethod
    def send_message(
            cls,
            message_id: int,
            customer_phone_number: str,
            newsletter_message_text: str,
    ) -> bool:
        logger.info(
            f'send_message '
            f'| message_id: {message_id} '
            f'| customer_phone_number: {customer_phone_number} '
            f'| newsletter_message_text: {newsletter_message_text}')

        url = f'https://probe.fbrq.cloud/v1/send/{message_id}'
        headers = {
            'Authorization': os.getenv('PROBE_FBRQ_JWT_TOKEN')
        }
        data = {
            'id': message_id,
            'phone': int(customer_phone_number),
            'text': newsletter_message_text,
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=5)
        except ConnectTimeout:
            logger.info(f'ConnectTimeout, message_id: {message_id}')
            return False

        if response.status_code != status.HTTP_200_OK:
            logger.info(f'{response.status_code} {response.text}')
            return False

        logger.info(f'{response.status_code} {response.json()}')
        return True
