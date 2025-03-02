from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from ride_app.forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User, Ride, RideEvent


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = [
        "email",
        "username",
        "phone_number",
        "role",
        "is_staff",
    ]
    # fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("name",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("phone_number", "role")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "phone_number",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("id_ride", "status", "id_rider", "id_driver", "pickup_time")
    list_filter = ("status",)
    search_fields = ("id_rider__username", "id_driver__username")
    ordering = ("-pickup_time",)


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = ("id_ride_event", "id_ride", "description", "created_at")
    list_filter = ("created_at",)
    search_fields = ("id_ride__id_ride", "description")
    ordering = ("-created_at",)
