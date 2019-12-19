from django.contrib import admin
from .models import Project,Module,Processor,Chassis,ProjChassis,ProjModule,ProjModuleProp

admin.site.register(Project)
admin.site.register(Module)
admin.site.register(Processor)
admin.site.register(Chassis)
admin.site.register(ProjChassis)
admin.site.register(ProjModule)
admin.site.register(ProjModuleProp)
