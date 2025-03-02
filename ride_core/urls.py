from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ride_app.urls")),
    path("auth/", include("rest_framework.urls")),
    path("rest-auth/", include("dj_rest_auth.urls")),
    path(
        "rest-auth/registration/",  # new
        include("dj_rest_auth.registration.urls"),
    ),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
