from django.db import models
from django.contrib.auth.models import User

class Chassis(models.Model):
    series = models.CharField(max_length=25)
    catalogNumber = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    size = models.IntegerField()
    xml = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.catalogNumber + ' ' + str(self.size) + ' Slots'

class Module(models.Model):
    type = models.CharField(max_length=25)
    series = models.CharField(max_length=25)
    catalogNumber = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    isChassis = models.BooleanField(default=False)          # if isChassis, xml footprint in Chassis table (e.g. 1734-AENT)
    slots = models.IntegerField(blank=True,null=True)       # if isChassis, slots is used to selct xml from Chassis table
    props = models.CharField(max_length=200)
    xml = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.catalogNumber

class Processor(models.Model):
    series = models.CharField(max_length=25)
    catalogNumber = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    isSafety = models.BooleanField(default=False)

    def __str__(self):
        return self.catalogNumber

class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    createdBy = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    createdOn = models.DateTimeField()

    # invoked whe this model object is foriegn key of other model
    def __str__(self):
        return self.name


class ProjChassis(models.Model):
    projId = models.ForeignKey(Project,on_delete=models.CASCADE)
    catalogId = models.ForeignKey(Chassis,on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=50,default='')

    def __str__(self):
        return self.name

class ProjModule(models.Model):
    projId =  models.ForeignKey(Project,on_delete=models.CASCADE,null=True)
    chassisId = models.ForeignKey(ProjChassis,on_delete=models.CASCADE)
    moduleId = models.ForeignKey(Module,on_delete=models.CASCADE,null=True)
    slot = models.IntegerField()
    name = models.CharField(max_length=100,default='')
    catalogNumber = models.CharField(max_length=50,default='')
    catalogDescription = models.CharField(max_length=100,default='')
    parent = models.CharField(max_length=100,default='Local')
    registered = models.BooleanField(default=False)

    def __str__(self):
        return self.catalogNumber

class ProjModuleProp(models.Model):
    projId = models.ForeignKey(Project,on_delete=models.CASCADE)
    chassisId = models.ForeignKey(Chassis,on_delete=models.CASCADE,null=True)
    projModuleId = models.ForeignKey(ProjModule,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=500)
