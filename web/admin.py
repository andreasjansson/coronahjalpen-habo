from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import redirect
from django.urls import reverse
from .models import User, Invite


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("is_coordinator",)
    list_filter = UserAdmin.list_filter + ("is_coordinator",)
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("is_coordinator",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("is_coordinator",)}),)


admin.site.register(User, CustomUserAdmin)


class InviteAdmin(admin.ModelAdmin):
    list_display = ["code", "share_link", "used", "user"]
    readonly_fields = ["code", "share_link"]

    def add_view(self, request, *args, **kwargs):
        obj = Invite.objects.create()
        return redirect(
            reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
                args=(obj.pk,),
            )
        )

    def share_link(self, obj):
        return f"https://coronahjalp-habo.se{obj.get_absolute_url()}"

    share_link.short_description = "Link to share"


admin.site.register(Invite, InviteAdmin)
