from django import template
from Evenement.models import Notification
from Evenement.forms import EventForm
register = template.Library()

@register.inclusion_tag('show_notification.html', takes_context=True)
def show_notifications(context):
    request_user= context['request'].user
    notifications = Notification.objects.filter(to_user=request_user).exclude(user_has_seen=True).order_by('-date')
    return {'notifications':notifications}
