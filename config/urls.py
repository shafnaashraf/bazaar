
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView,
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("core.urls")),
    path("api/", include("catalog.urls")),
    path("", TemplateView.as_view(template_name = "index.html"), name="home"),
    path("api/", include("cart.urls")),
    path("api/", include("orders.urls")),

     # --- API documentation ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),          # raw OpenAPI
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)