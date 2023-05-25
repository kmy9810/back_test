from django.contrib import admin
from users.models import User

<<<<<<< HEAD

admin.site.register(User)

# from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
# from rest_framework_simplejwt.token_blacklist.models import OutstandingToken


# class CustomOutstandingTokenAdmin(OutstandingTokenAdmin):
#     def has_delete_permission(self, *args, **kwargs):
#         return True


# admin.site.unregister(OutstandingToken)
=======
admin.site.register(User)
>>>>>>> e725c037ab15604c1f939de96b5d8adadb0bb728
