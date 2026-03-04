from rest_framework import serializers, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.conf import settings
from .models import SubscriptionPlan, Subscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'status', 'started_at', 'expires_at', 'razorpay_subscription_id']


@extend_schema(tags=['Subscriptions'])
class PlanListView(generics.ListAPIView):
    """List all subscription plans."""
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=['Subscriptions'])
class MySubscriptionView(generics.ListAPIView):
    """Get current owner's active subscription."""
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(owner=self.request.user, status='active')


@extend_schema(tags=['Subscriptions'])
class CreateOrderView(APIView):
    """
    Create a Razorpay order for a subscription plan.
    Client uses the returned order_id to open Razorpay checkout.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        try:
            plan = SubscriptionPlan.objects.get(pk=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({'detail': 'Plan not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not settings.RAZORPAY_KEY_ID:
            return Response({'detail': 'Payment gateway not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({
            'amount': plan.price_monthly,
            'currency': 'INR',
            'receipt': f'sub_{request.user.id}_{plan.tier}',
            'notes': {'user_id': request.user.id, 'plan_tier': plan.tier},
        })
        return Response({'order_id': order['id'], 'amount': plan.price_monthly, 'currency': 'INR'})


@extend_schema(tags=['Subscriptions'])
class VerifyPaymentView(APIView):
    """Verify Razorpay payment signature and activate subscription."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        import razorpay
        import hmac, hashlib

        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        plan_id = request.data.get('plan_id')

        msg = f'{razorpay_order_id}|{razorpay_payment_id}'
        expected = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(), msg.encode(), hashlib.sha256
        ).hexdigest()

        if expected != razorpay_signature:
            return Response({'detail': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils import timezone
        from datetime import timedelta
        plan = SubscriptionPlan.objects.get(pk=plan_id)
        Subscription.objects.filter(owner=request.user, status='active').update(status='expired')
        sub = Subscription.objects.create(
            owner=request.user,
            plan=plan,
            status='active',
            razorpay_payment_id=razorpay_payment_id,
            expires_at=timezone.now() + timedelta(days=30),
        )
        return Response(SubscriptionSerializer(sub).data, status=status.HTTP_201_CREATED)
