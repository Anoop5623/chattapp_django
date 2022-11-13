from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(group_messages)
admin.site.register(Group)
admin.site.register(personal_messages)
admin.site.register(One_to_one_room)
admin.site.register(Notification)

