from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils.timezone import make_aware
from faker import Faker

from payments.models import Collect, Payment, Reason

User = get_user_model()

AMOUNT_USERS = 100
AMOUNT_REASONS = 10
AMOUNT_COLLECTS = 1_000
AMOUNT_PAYMENTS = 2_000
MAX_LENGTH_CHAR_SHORT = 10
MAX_LENGTH_CHAR_LONG = 156
MIN_AMOUNT = 100
MAX_AMOUNT = 100_000


class Command(BaseCommand):
    help = "Add mock data"

    def __init__(self):
        self.faker = Faker("ru_RU")
        self._create_users()
        self._create_reasons()
        self._create_collects()
        self._create_payments()
        super().__init__(self)

    def handle(self, *args, **options):
        pass

    def _create_users(self):
        self.users = User.objects.bulk_create(
            [
                User(
                    username=f"{self.faker.user_name()}{i}",
                    email=self.faker.email(),
                    password=self.faker.password(length=MAX_LENGTH_CHAR_SHORT),
                )
                for i in range(AMOUNT_USERS)
            ]
        )

    def _create_reasons(self):
        self.reasons = Reason.objects.bulk_create(
            [
                Reason(title=self.faker.text(
                    max_nb_chars=MAX_LENGTH_CHAR_SHORT
                ))
                for _ in range(AMOUNT_REASONS)
            ]
        )

    def _create_collects(self):
        self.collects = Collect.objects.bulk_create(
            [
                Collect(
                    author=self.faker.random_element(self.users),
                    title=self.faker.text(max_nb_chars=MAX_LENGTH_CHAR_SHORT),
                    description=self.faker.text(
                        max_nb_chars=MAX_LENGTH_CHAR_LONG
                    ),
                    target=self.faker.random_int(
                        min=MIN_AMOUNT, max=MAX_AMOUNT, step=MIN_AMOUNT
                    ),
                    collection_end_time=make_aware(
                        self.faker.date_time_this_year(after_now=True)
                    ),
                    created_at=make_aware(
                        self.faker.date_time_this_year(before_now=True)
                    ),
                    reason=self.faker.random_element(self.reasons),
                )
                for _ in range(AMOUNT_COLLECTS)
            ]
        )

    def _create_payments(self):
        payments = list()
        for _ in range(AMOUNT_PAYMENTS):
            collect = self.faker.random_element(self.collects)
            donator = self.faker.random_element(self.users)
            if collect.author == donator:
                donator = User.objects.create_user(
                    username=self.faker.user_name(),
                    email=self.faker.email(),
                    password=self.faker.password(length=MAX_LENGTH_CHAR_SHORT),
                )
                donator.save()
            payment = Payment(
                donator=donator,
                collect=collect,
                amount=self.faker.random_int(max=collect.target),
                created_at=make_aware(
                    self.faker.date_time_between(
                        start_date=collect.created_at,
                        end_date=collect.collection_end_time,
                    )
                ),
            )
            payments.append(payment)
        Payment.objects.bulk_create(payments)
