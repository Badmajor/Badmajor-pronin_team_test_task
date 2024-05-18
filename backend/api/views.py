from django.db.models import Sum, Prefetch
from rest_framework import viewsets, status

from payments.models import Collect, Payment
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import CollectSerializer, PaymentSerializer


class CollectViewSet(viewsets.ModelViewSet):
    queryset = (
        Collect.objects.order_by("created_at")
        .select_related("author", "reason")
        .prefetch_related(
            Prefetch("payments", queryset=Payment.objects.select_related("donator"))
        )
        .annotate(current_amount=Sum("payments__amount"))
    )
    serializer_class = CollectSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(["post"], permission_classes=(IsAuthenticated,), detail=True)
    def donate(self, *args, **kwargs):
        collect = self.get_object()
        amount = self.request.data.get("amount")
        if amount and amount.isdigit():
            payment = Payment.objects.create(
                donator=self.request.user, amount=amount, collect=collect
            )
            return Response(
                PaymentSerializer(payment).data, status=status.HTTP_201_CREATED
            )
        return Response({"amount": "Должно быть положительное число"})
