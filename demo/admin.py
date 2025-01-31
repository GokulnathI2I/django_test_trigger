from django.contrib import admin
from demo.models import Demo, SuperOrg



@admin.register(Demo)
class DemoAdmin(admin.ModelAdmin):
    list_display = ("first_name", "middle_name", "last_name", "suffix")


admin.site.register([SuperOrg])


