from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from . import services

@require_GET
def api_today_schedule(request):
    now = timezone.localtime()
    schedule = services.get_today_schedule(now=now)

    if not schedule:
        return JsonResponse(
            {"success": False, "message": "لا يوجد جدول مفعّل لهذا اليوم."},
            status=404,
        )

    result = services.get_periods_with_state(schedule, now=now)
    periods_with_state = result["periods"]
    current_index = result["current_index"]

    periods_data = []
    for (p, start_dt, end_dt) in periods_with_state:
        periods_data.append(
            {
                "id": p.id,
                "name": p.name,
                "type": p.period_type,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
            }
        )

    return JsonResponse(
        {
            "success": True,
            "date": now.date().isoformat(),
            "now": now.isoformat(),
            "schedule_name": str(schedule),
            "current_period_index": current_index,
            "periods": periods_data,
        }
    )
