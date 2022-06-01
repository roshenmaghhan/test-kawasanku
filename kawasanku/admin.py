from django.contrib import admin
from .models import AreaType, Pyramid, Test, JsonStore, SnapshotJSON, Doughnuts, Links, Geo, Dropdown, Jitter, AreaType

admin.site.register(Test)
admin.site.register(JsonStore)
admin.site.register(SnapshotJSON)
admin.site.register(Doughnuts)
admin.site.register(Pyramid)
admin.site.register(Links)
admin.site.register(Geo)
admin.site.register(Dropdown)
admin.site.register(Jitter)
admin.site.register(AreaType)