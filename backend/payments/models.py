from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.tasks import task_send_email

User = get_user_model()
MAX_LENGTH = 156


class Payment(models.Model):
    donator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Донатор")
    amount = models.PositiveIntegerField(
        "сумма",
    )
    collect = models.ForeignKey(
        "Collect",
        on_delete=models.DO_NOTHING,
        verbose_name="Групповой сбор",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "платеж"
        verbose_name_plural = "Платежи"
        default_related_name = "payments"


class Reason(models.Model):
    title = models.CharField(
        "Название",
        max_length=MAX_LENGTH,
    )

    class Meta:
        verbose_name = "цель сбора"
        verbose_name_plural = "Цели сбора"
        default_related_name = "reason"

    def __str__(self):
        return self.title


class Collect(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор сбора"
    )
    title = models.CharField(
        "Название",
        max_length=MAX_LENGTH,
    )
    reason = models.ForeignKey(
        Reason, on_delete=models.SET_NULL, null=True, verbose_name="Цель сбора"
    )
    description = models.TextField("Описание")
    target = models.PositiveIntegerField(
        "Необходимая сумма",
        default=None,
        null=True,
    )
    image = models.ImageField(
        upload_to="collect/images",
        null=True,
        default=None,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    collection_end_time = models.DateTimeField()

    class Meta:
        verbose_name = "групповой сбор"
        verbose_name_plural = "Групповые сборы"
        default_related_name = "collect"

    @property
    def amount_donators(self):
        return self.all_payments.count()

    @property
    def all_payments(self):
        return self.payments


@receiver(post_save, sender=Payment)
@receiver(post_save, sender=Collect)
def send_email_on_create(sender, instance, created, **kwargs):
    if created:
        task_send_email(instance)
