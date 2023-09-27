from django.contrib import admin

from .models import Customer, MailingTask, Message, Newsletter


class MailingTaskInLine(admin.StackedInline):
    model = MailingTask


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    inlines = [
        MailingTaskInLine,
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
