
from django.contrib import admin
from .models import CustomUser,CustomUserManager
from .models import FreeTrialUser 
from .models import SubscriptionPayment,CancelledSubscription,RssDetails

admin.site.register(CustomUser)
admin.site.register(RssDetails)
admin.site.register(CancelledSubscription)
admin.site.register(FreeTrialUser)
@admin.register(SubscriptionPayment)


class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'event_name', 'created_at', 'total_formatted', 'status', 'expiration_date']
    search_fields = ['user_name', 'event_name']
    list_filter = ['event_name', 'status']

