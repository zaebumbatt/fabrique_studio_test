import zoneinfo
from datetime import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Customer, MailingTask, Message, Newsletter

DATE_FORMAT = '%Y-%m-%d %H:%M:%S%z'
DEFAULT_MOBILE_OPERATOR_CODES = ['903', '910', '920']
DEFAULT_TAGS = ['gamer', 'programmer', 'manager']


class CustomerTests(APITestCase):

    def test_create_customer(self):
        """
        Ensure we can create a new customer object.
        """
        url = reverse('customer-list')
        data = {
            'phone_number': '79991234567',
            'mobile_operator_code': '903',
            'tag': 'gamer',
            'timezone': 'Asia/Bangkok',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)

        customer = Customer.objects.get()
        self.assertEqual(customer.phone_number, data.get('phone_number'))
        self.assertEqual(customer.mobile_operator_code, data.get('mobile_operator_code'))
        self.assertEqual(customer.tag, data.get('tag'))
        self.assertEqual(customer.timezone, zoneinfo.ZoneInfo(data.get('timezone')))

    def test_update_customer(self):
        """
        Ensure we can update a customer object.
        """
        customer = _create_customer()
        self.assertEqual(Customer.objects.filter(id=customer.id).count(), 1)

        url = reverse(
            'customer-detail',
            kwargs={'pk': customer.id}
        )
        data = {'phone_number': '79997654321'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_customer = Customer.objects.get()
        self.assertEqual(updated_customer.phone_number, data.get('phone_number'))

    def test_delete_customer(self):
        """
        Ensure we can delete a customer object.
        """
        customer = _create_customer()
        self.assertEqual(Customer.objects.filter(id=customer.id).count(), 1)

        url = reverse(
            'customer-detail',
            kwargs={'pk': customer.id}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Customer.objects.filter(id=customer.id).count(), 0)

    def test_phone_number_format(self):
        """
        Ensure we can't create a customer with incorrect phone number.
        """
        url = reverse('customer-list')
        data = {
            'mobile_operator_code': '921',
            'tag': 'gamer',
            'timezone': 'Asia/Bangkok',
        }
        for incorrect_phone_number in (
            '7999123456',    # one symbol shorter
            '7999123456a',   # with not a digit
            '19991234567',   # not starting with 7
        ):
            data['phone_number'] = incorrect_phone_number
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                response.json(),
                {'phone_number': ['should be in the format 7XXXXXXXXXX']},
            )

    def test_added_to_newsletter(self):
        """
        Ensure customer have been added to a newsletter that matched by
        mobile_operator_code and tag.
        """
        newsletter = _create_newsletter(
            mobile_operator_codes=DEFAULT_MOBILE_OPERATOR_CODES,
            tags=DEFAULT_TAGS,
        )
        customer = _create_customer(
            mobile_operator_code=DEFAULT_MOBILE_OPERATOR_CODES[0],
            tag=DEFAULT_TAGS[0],
        )
        self.assertEqual(newsletter.customers.first(), customer)

    def test_removed_from_newsletter_after_tag_changed(self):
        """
        Ensure customer has been removed from a newsletter if he doesn't
        match tag anymore.
        """
        newsletter = _create_newsletter(
            mobile_operator_codes=DEFAULT_MOBILE_OPERATOR_CODES,
            tags=DEFAULT_TAGS,
        )
        customer = _create_customer(
            mobile_operator_code=DEFAULT_MOBILE_OPERATOR_CODES[0],
            tag=DEFAULT_TAGS[0],
        )
        self.assertEqual(newsletter.customers.first(), customer)

        customer.tag = 'HR'
        customer.save()
        self.assertEqual(newsletter.customers.count(), 0)

    def test_removed_from_newsletter_after_mobile_operator_code_changed(self):
        """
        Ensure customer has been removed from a newsletter if he doesn't
        match mobile_operator_codes anymore.
        """
        newsletter = _create_newsletter(
            mobile_operator_codes=DEFAULT_MOBILE_OPERATOR_CODES,
            tags=DEFAULT_TAGS,
        )
        customer = _create_customer(
            mobile_operator_code=DEFAULT_MOBILE_OPERATOR_CODES[0],
            tag=DEFAULT_TAGS[0],
        )
        self.assertEqual(newsletter.customers.first(), customer)

        customer.mobile_operator_code = '915'
        customer.save()
        self.assertEqual(newsletter.customers.count(), 0)


class NewsletterTests(APITestCase):

    def test_create_newsletter(self):
        """
        Ensure we can create a new newsletter object.
        """
        url = reverse('newsletter-list')
        data = {
            'start': '2023-10-01 00:00:00+00:00',
            'finish': '2023-10-02 00:00:00+00:00',
            'message_text': 'Newsletter test',
            'mobile_operator_codes': DEFAULT_MOBILE_OPERATOR_CODES,
            'tags': DEFAULT_TAGS,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Newsletter.objects.count(), 1)

        newsletter = Newsletter.objects.get()
        self.assertEqual(newsletter.start, datetime.strptime(data.get('start'), DATE_FORMAT))
        self.assertEqual(newsletter.finish, datetime.strptime(data.get('finish'), DATE_FORMAT))
        self.assertEqual(newsletter.message_text, data.get('message_text'))
        self.assertEqual(newsletter.mobile_operator_codes, data.get('mobile_operator_codes'))
        self.assertEqual(newsletter.tags, data.get('tags'))

    def test_update_newsletter(self):
        """
        Ensure we can update a newsletter object.
        """
        newsletter = _create_newsletter()
        self.assertEqual(Newsletter.objects.filter(id=newsletter.id).count(), 1)

        url = reverse(
            'newsletter-detail',
            kwargs={'pk': newsletter.id}
        )
        data = {'message_text': 'Text after update'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_newsletter = Newsletter.objects.get()
        self.assertEqual(updated_newsletter.message_text, data.get('message_text'))

    def test_delete_newsletter(self):
        """
        Ensure we can delete a newsletter object
        """
        newsletter = _create_newsletter()
        self.assertEqual(Newsletter.objects.filter(id=newsletter.id).count(), 1)

        url = reverse(
            'newsletter-detail',
            kwargs={'pk': newsletter.id}
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Newsletter.objects.filter(id=newsletter.id).count(), 0)

    def test_customers_have_been_added(self):
        """
        Ensure all customers filtered by mobile_operator_code and tag
        have been added to a newsletter object after creation.
        """
        for i in range(10):
            _create_customer(
                phone_number=f'7921123456{i}',
                mobile_operator_code=f'99{i % 3}',
                tag='gamer' if not i % 3 else 'programmer',
            )
        self.assertEqual(Customer.objects.count(), 10)

        url = reverse('newsletter-list')
        data = {
            'start': '2023-10-01 00:00:00+00:00',
            'finish': '2023-10-02 00:00:00+00:00',
            'message_text': 'Newsletter test',
            'mobile_operator_codes': ['990'],
            'tags': ['gamer'],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Newsletter.objects.count(), 1)

        newsletter = Newsletter.objects.get()
        self.assertEqual(newsletter.customers.count(), 4)
        for i, customer in enumerate(newsletter.customers.all()):
            self.assertEqual(customer.phone_number, f'7921123456{i * 3}')
            self.assertTrue(customer.mobile_operator_code in data.get('mobile_operator_codes'))
            self.assertTrue(customer.tag in data.get('tags'))

    def test_periodic_task_has_been_created(self):
        """
        Ensure mailing task with correct clocked schedule has been created.
        """
        url = reverse('newsletter-list')
        data = {
            'start': '2023-10-01 00:00:00+00:00',
            'finish': '2023-10-02 00:00:00+00:00',
            'message_text': 'Newsletter test',
            'mobile_operator_codes': ['990'],
            'tags': ['gamer'],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Newsletter.objects.count(), 1)

        mailing_task = MailingTask.objects.get(newsletter=response.json()['id'])
        self.assertEqual(mailing_task.start_time, datetime.strptime(data.get('start'), DATE_FORMAT))
        self.assertTrue(mailing_task.enabled, True)
        self.assertEqual(mailing_task.clocked.clocked_time, datetime.strptime(data.get('start'), DATE_FORMAT))

    def test_newsletter_overall_stats(self):
        """
        Check newsletter stats annotated values.
        """
        for i in range(10):
            _create_customer(
                phone_number=f'7999123456{i}',
                mobile_operator_code=DEFAULT_MOBILE_OPERATOR_CODES[i % 3],
                tag=DEFAULT_TAGS[i % 3]
            )
        newsletter = _create_newsletter(
            mobile_operator_codes=['903', '910', '920'],
            tags=['gamer', 'programmer', 'manager'],
        )
        for i, customer in enumerate(newsletter.customers.all()):
            message_status = ''
            match i % 4:
                case 0: message_status = Message.Status.SUCCESS
                case 1: message_status = Message.Status.FAILURE
                case 2: message_status = Message.Status.ONGOING
                case 3: message_status = Message.Status.CANCELED
            _create_message(
                newsletter=newsletter,
                customer=customer,
                message_status=message_status,
            )
        url = reverse('newsletter-stats-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()[0]
        self.assertEqual(result.get('success'), 3)
        self.assertEqual(result.get('ongoing'), 2)
        self.assertEqual(result.get('failure'), 3)
        self.assertEqual(result.get('canceled'), 2)


def _create_customer(
        phone_number: str = '79991234567',
        mobile_operator_code: str = '903',
        tag: str = 'gamer',
        timezone: str = 'Asia/Bangkok',
) -> Customer:
    return Customer.objects.create(
        phone_number=phone_number,
        mobile_operator_code=mobile_operator_code,
        tag=tag,
        timezone=timezone,
    )


def _create_newsletter(
        start: str = datetime.strptime('2023-10-01 00:00:00+00:00', DATE_FORMAT),
        finish: str = datetime.strptime('2023-10-02 00:00:00+00:00', DATE_FORMAT),
        message_text: str = 'Newsletter test',
        mobile_operator_codes: list[str] = DEFAULT_MOBILE_OPERATOR_CODES,
        tags: list[str] = DEFAULT_TAGS,
) -> Newsletter:
    return Newsletter.objects.create(
        start=start,
        finish=finish,
        message_text=message_text,
        mobile_operator_codes=mobile_operator_codes,
        tags=tags,
    )


def _create_message(
        newsletter: Newsletter,
        customer: Customer,
        message_status: Message.Status = Message.Status.ONGOING,
) -> Message:
    return Message.objects.create(
        newsletter=newsletter,
        customer=customer,
        status=message_status,
    )
