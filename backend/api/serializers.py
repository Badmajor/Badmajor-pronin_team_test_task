import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import Sum
from rest_framework import serializers

from payments.models import Collect, Payment, Reason

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class PaymentSerializer(serializers.ModelSerializer):
    donator = serializers.CharField()
    collect = serializers.PrimaryKeyRelatedField(
        queryset=Collect.objects.all(), write_only=True
    )

    class Meta:
        model = Payment
        fields = ("donator", "amount", "created_at", "collect")


class CollectSerializer(serializers.ModelSerializer):
    current_amount = serializers.SerializerMethodField(read_only=True)
    amount_donators = serializers.SerializerMethodField(read_only=True)
    is_completed = serializers.SerializerMethodField(read_only=True)
    all_payments = PaymentSerializer(source="payments", many=True, read_only=True)
    image = Base64ImageField(
        required=False,
    )
    author = serializers.CharField(read_only=True)
    reason = serializers.SlugRelatedField(
        slug_field="title", queryset=Reason.objects.all()
    )

    class Meta:
        model = Collect
        fields = "__all__"

    def get_current_amount(self, obj):
        if hasattr(obj, "current_amount"):
            return obj.current_amount or 0
        return obj.payments.aggregate(total=Sum("amount"))["total"] or 0

    def get_amount_donators(self, obj):
        if hasattr(obj, "amount_donators"):
            return obj.amount_donators or 0
        return obj.payments.values("donator").distinct().count() or 0

    def get_is_completed(self, obj):
        return obj.target <= self.get_current_amount(obj)
