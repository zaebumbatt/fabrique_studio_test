import datetime
import json

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from django_prometheus.models import ExportModelOperationsMixin
from timezone_field import TimeZoneField

from core import models as core_models


class Customer(ExportModelOperationsMixin('customer'), core_models.TimeTrackable):
    phone_number = models.CharField(max_length=11, unique=True)
    mobile_operator_code = models.CharField(max_length=3)
    tag = models.CharField(max_length=30)
    timezone = TimeZoneField(default='Europe/Moscow')

    __original_mobile_operator_code: str
    __original_tag: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_mobile_operator_code = self.mobile_operator_code
        self.__original_tag = self.tag

    def save(self, *args, **kwargs):

        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            # add a customer to a newsletters that matched the filter
            self._add_to_newsletter()
        elif (
                self.mobile_operator_code != self.__original_mobile_operator_code
                or self.tag != self.__original_tag
        ):
            # remove a customer from a newsletters if they changed
            # mobile_operator_code or tag and doesn't match a filter anymore
            self._remove_from_newsletter()

            # add a customer to a newsletters that matched the filter
            self._add_to_newsletter()

        self.__original_mobile_operator_code = self.mobile_operator_code
        self.__original_tag = self.tag

    def _add_to_newsletter(self):
        newsletters = Newsletter.objects.filter(
            mobile_operator_codes__contains=[self.mobile_operator_code],
            tags__contains=[self.tag],
        )
        for newsletter in newsletters:
            newsletter.customers.add(self)

    def _remove_from_newsletter(self):
        newsletters = self.newsletters.filter(
            mobile_operator_codes__contains=[
                self.__original_mobile_operator_code],
            tags__contains=[self.__original_tag],
        )
        for newsletter in newsletters:
            newsletter.customers.remove(self)

    def __str__(self):
        return (f'id: {self.id} '
                f'| phone_number: {self.phone_number} '
                f'| mobile_operator_code: {self.mobile_operator_code} '
                f'| tag: {self.tag}')


class Newsletter(ExportModelOperationsMixin('newsletter'), core_models.TimeTrackable):
    start = models.DateTimeField()
    finish = models.DateTimeField()
    message_text = models.TextField()
    mobile_operator_codes = ArrayField(models.CharField(max_length=3))
    tags = ArrayField(models.CharField(max_length=30))
    customers = models.ManyToManyField(Customer, related_name='newsletters')

    __original_start: datetime.datetime
    __original_finish: datetime.datetime

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_start = self.start
        self.__original_finish = self.finish

    def save(self, *args, **kwargs):

        is_new = self._state.adding
        super().save(*args, **kwargs)

        # add customers that matched the filter
        customers = Customer.objects.filter(
            mobile_operator_code__in=self.mobile_operator_codes,
            tag__in=self.tags,
        )
        self.customers.add(*customers)
        if is_new and timezone.now() < self.finish:
            # create a task to run once at self.start
            self._create_task()
        elif (
                self.start != self.__original_start
                or self.finish != self.__original_finish
        ):
            # delete old and create a new task if start has been changed
            if hasattr(self, 'task'):
                self._delete_task()
            self._create_task()

        self.__original_start = self.start
        self.__original_finish = self.finish

    def _create_task(self):
        clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=self.start)
        MailingTask.objects.create(
            clocked=clocked,
            name=f'Send newsletter {self.id}',
            task='mailing.tasks.send_newsletter',
            kwargs=json.dumps({'newsletter_id': self.id}),
            one_off=True,
            start_time=self.start,
            newsletter=self,
        )

    def _delete_task(self):
        self.task.delete()

    def __str__(self):
        return (f'id: {self.id} '
                f'| start: {self.start} '
                f'| finish: {self.finish} '
                f'| messages: {self.messages.count()}')


class Message(ExportModelOperationsMixin('message'), core_models.TimeTrackable):
    class Status(models.TextChoices):
        SUCCESS = 'success'
        ONGOING = 'ongoing'
        FAILURE = 'failure'
        CANCELED = 'canceled'

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ONGOING)
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='messages')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='messages')

    def __str__(self):
        return (f'id: {self.id} '
                f'| newsletter_id: {self.newsletter_id} '
                f'| customer_id: {self.customer_id} '
                f'| status: {self.status}')


class MailingTask(ExportModelOperationsMixin('mailing_task'), PeriodicTask):
    newsletter = models.OneToOneField(Newsletter, on_delete=models.CASCADE, related_name='task')
