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

class ModuleType(models.Model):
    # Digital, Analog, Processor, Communications, etc
    type = models.CharField(max_length=25)

    def __str__(self):
        return self.type

class ModuleCatagory(models.Model):
    # Input, Output, etc
    catagory = models.CharField(max_length=25)

    def __str__(self):
        return self.catagory


class Module(models.Model):
    # type = models.CharField(max_length=25,blank=True,null=True)
    type = models.ForeignKey(ModuleType,on_delete=models.SET_NULL,null=True,blank=True)         # Digital, Analog, Communications, etc.
    # catagory = models.CharField(max_length=25,blank=True,null=True)
    catagory = models.ForeignKey(ModuleCatagory,on_delete=models.SET_NULL,null=True,blank=True) # input, output, etc
    series = models.CharField(max_length=25)
    catalogNumber = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    isChassis = models.BooleanField(default=False)                                              # if isChassis, xml footprint in Chassis table (e.g. 1734-AENT)
    slots = models.IntegerField(blank=True,null=True)                                           # if isChassis, slots is used to selct xml from Chassis table
    points = models.IntegerField(blank=True,null=True)                                          # number if input or output points..
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
    parent = models.CharField(max_length=100,default='Local')

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
    comments = models.CharField(max_length=1000,default='')                 # comma seperated list of comments for points

    def __str__(self):
        return self.catalogNumber

class ProjModuleProp(models.Model):
    projId = models.ForeignKey(Project,on_delete=models.CASCADE)
    chassisId = models.ForeignKey(Chassis,on_delete=models.CASCADE,null=True)
    projModuleId = models.ForeignKey(ProjModule,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=500)


class UDT(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    versionMajor = models.IntegerField()
    versionMinor = models.IntegerField()
    xml = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name

class AOI(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    versionMajor = models.IntegerField()
    versionMinor = models.IntegerField()
    dependencies = models.CharField(max_length=1000)                # comma seperated list of required UDT's
    xml = models.TextField(blank=True,null=True)
    

    def __str__(self):
        return self.name

class ProjUDT(models.Model):
    projId = models.ForeignKey(Project,on_delete=models.CASCADE)
    udtId = models.ForeignKey(UDT,on_delete=models.CASCADE)

    def __str__(self):
        return self.udtId.name

class ProjAOI(models.Model):
    projId = models.ForeignKey(Project,on_delete=models.CASCADE)
    aoiId = models.ForeignKey(AOI,on_delete=models.CASCADE)

    def __str__(self):
        return self.aoiId.name
