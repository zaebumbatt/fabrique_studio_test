import re

from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from .models import Customer, Newsletter


class CustomerSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(required=False)

    def validate(self, data):
        phone_number = data.get('phone_number')
        if phone_number and not re.match(r'^7\d{10}$', phone_number):
            raise serializers.ValidationError(
                {
                    'phone_number': 'should be in the format 7XXXXXXXXXX',
                }
            )
        return data

    class Meta:
        model = Customer
        fields = [
            'id',
            'phone_number',
            'mobile_operator_code',
            'tag',
            'timezone',
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    customers = CustomerSerializer(many=True, read_only=True)

    def validate(self, data):
        start = data.get('start')
        finish = data.get('finish')

        if self.partial:
            start = start or self.instance.start
            finish = finish or self.instance.finish

        if start > finish:
            raise serializers.ValidationError(
                {
                    'finish': 'must occur after start',
                }
            )
        return data

    class Meta:
        model = Newsletter
        fields = [
            'id',
            'start',
            'finish',
            'message_text',
            'mobile_operator_codes',
            'tags',
            'customers',
        ]


class NewsletterStatsSerializer(serializers.ModelSerializer):
    success = serializers.IntegerField()
    ongoing = serializers.IntegerField()
    failure = serializers.IntegerField()
    canceled = serializers.IntegerField()

    class Meta:
        model = Newsletter
        fields = [
            'id',
            'start',
            'finish',
            'message_text',
            'mobile_operator_codes',
            'tags',
            'success',
            'ongoing',
            'failure',
            'canceled',
        ]
