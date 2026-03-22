from celery import shared_task
from django.utils import timezone


@shared_task
def release_expired_reservations():
    """Release seat reservations that have exceeded their lock time."""
    from apps.seats.models import SeatStatus

    expired = SeatStatus.objects.filter(
        status="reserved",
        locked_until__lt=timezone.now(),
    )
    count = expired.update(status="available", locked_by=None, locked_until=None)
    return f"Released {count} expired reservations"
