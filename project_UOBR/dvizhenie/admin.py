from django.contrib import admin

from .models import DrillingRig, Pad, type_of_DR, Contractor, RigPosition, NextPosition, PositionRating

admin.site.register(DrillingRig)
admin.site.register(Pad)
admin.site.register(type_of_DR)
admin.site.register(Contractor)
admin.site.register(RigPosition)
admin.site.register(NextPosition)
admin.site.register(PositionRating)
