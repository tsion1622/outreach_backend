from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# ✅ Add a simple view to return status OK
def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('', health_check),  # ✅ This fixes the 404 error for "/"
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
