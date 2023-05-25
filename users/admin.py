from django.contrib import admin
from .models import User


admin.site.register(User)

# from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
# from rest_framework_simplejwt.token_blacklist.models import OutstandingToken


# class CustomOutstandingTokenAdmin(OutstandingTokenAdmin):
#     def has_delete_permission(self, *args, **kwargs):
#         return True


# admin.site.unregister(OutstandingToken)