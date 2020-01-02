from django.contrib import admin
from .models import *

admin.site.register(Project)
admin.site.register(Module)
admin.site.register(Processor)
admin.site.register(Chassis)
admin.site.register(ProjChassis)
admin.site.register(ProjModule)
admin.site.register(ModuleType)
admin.site.register(ModuleCatagory)
admin.site.register(UDT)
admin.site.register(AOI)
admin.site.register(ProjUDT)
admin.site.register(ProjAOI)
