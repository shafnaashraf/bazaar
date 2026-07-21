from django.shortcuts import render
from django.db import connection
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
@api_view(["GET"])
def healthCheck(request):
    checks = {"database": "OK", "cache": "OK"}
    healthy = True

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        healthy = False

    try:
        cache.set("health_check_probe", "OK", timeout = 5)
        if cache.get("health_check_probe") != "OK":
            raise RuntimeError("cache get-set failed")
    except Exception as exc:
        checks["cache"] = f"error: {exc}"
        healthy = False
    
    body = {"status": " OK" if healthy else "degaraded","checks":checks}
    code = status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(body, status = code)
