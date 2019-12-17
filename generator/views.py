from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from django.utils import timezone
from django.db import IntegrityError
from django.http import HttpResponse
from .util import parseAutoGenImport,prettify
from .xml import buildXML



def home(request):
    return render(request,'generator/home.html')

def projects(request):
    projects = Project.objects
    return render(request,'generator/projects.html',{'projects':projects})

def createProject(request):
    if request.method == 'POST':
        if request.POST['name'] and request.POST['description'] :
            project = Project()
            project.name = request.POST['name']
            project.description = request.POST['description']
            project.createdOn = timezone.datetime.now()
            project.createdBy = request.user
            project.save()
            return redirect('/projects/')
        else:
            return render(request,'generator/createProject.html',{'error':'All fields are required!'})
    else:
        return render(request,'generator/createProject.html')

def editProject(request,projectId):
    project = Project.objects.get(id=projectId)
    chassis = ProjChassis.objects.filter(projId=project.id)
    return render(request,'generator/editProject.html',{'project':project,'chassis':chassis})

def deleteProject(request,projectId):
    project = Project.objects.get(id=projectId)
    project.delete()
    return redirect('/projects/')

def editChassis(request,chassisId):
    chassis = ProjChassis.objects.get(id=chassisId)
    modules = ProjModule.objects.filter(chassisId=chassis.id).order_by('slot')
    #size = chassis.chassisId.size
    #moduleCatalogNumbers = []
    #for i in range(size):
    #    try:
    #        moduleCatalogNumbers.append(modules[i].catalogId.catalogNumber)
    #    except IndexError:
    #        moduleCatalogNumbers.append('')

    params = {'chassis':chassis,'modules':modules}
    return render(request,'generator/editChassis.html',params)


def deleteChassis(request,chassisId):
    chassis = ProjChassis.objects.get(id=chassisId)
    projectId = chassis.projId.id
    chassis.delete()
    project = Project.objects.get(id=projectId)
    #return render(request,'generator/editProject.html',{'project':project})
    return redirect('/generator/' + str(projectId))



def addChassis(request,projectId,catalogNumber=None):
    '''
        Add a chassis to a project and size it by adding blank modules
        in ProjModule
    '''
    if request.method == 'POST':
        newChassis = ProjChassis()
        newChassis.projId = Project.objects.get(id=projectId)
        newChassis.catalogNumber = catalogNumber
        newChassis.description = Chassis.objects.get(catalogNumber=catalogNumber)
        newChassis.save()

        return redirect('/generator/' + str(projectId))
    else:
        project = Project.objects.get(id=projectId)
        series = [c.series for c in Chassis.objects.all()]
        series = set(series)
        # filter
        filter = {}
        seriesFilter = request.GET.get('seriesFilter','')
        if seriesFilter != '':
            filter['series__iexact'] = seriesFilter
        catalogFilter = request.GET.get('catalogFilter','')
        if catalogFilter != '':
            filter['catalogNumber__icontains'] = catalogFilter
        if len(filter) > 0:
            chassis = Chassis.objects.filter(**filter)
        else:
            chassis = Chassis.objects.all()

        params = {'project':project,'chassis':chassis,'series':series}
        return render(request,'generator/addChassis.html',params)


def addModule(request,chassisId,catalogNumber=None):
    if request.method == "POST":
        chassis = ProjChassis.objects.get(id=chassisId)
        modules = ProjModule.objects
        # template returns a selected value through a submit button
        nm = Module.objects.get(catalogNumber=catalogNumber)
        newModule = ProjModule()
        newModule.projId = chassis.projId
        newModule.chassisId = ProjChassis.objects.get(id=chassis.chassisId.id)


        newModule.slot = 0
        newModule.catalogId = Module.objects.get(catalogNumber=catalogNumber)
        newModule.save()
        return redirect('/generator/chassis/' + str(chassis.id))
        #return render(request,'generator/editChassis.html',{'chassis':chassis,'modules':modules},{'error':'hello'})
    else:
        # filters
        chassis = ProjChassis.objects.get(id=chassisId)

        series = Chassis.objects.get(id=chassis.chassisId.id).series
        filter = {'series__exact':series}
        typeFilter = request.GET.get('typeFilter','')
        catalogFilter = request.GET.get('catalogFilter','')
        if  typeFilter != '':
            filter['type__iexact'] = request.GET['typeFilter']
        if catalogFilter != '':
            filter['catalogNumber__icontains'] = request.GET['catalogFilter']
        modules = Module.objects.filter(**filter)

        moduleTypes = Module.objects.all().values_list('type',flat=True).distinct()
        params = {'chassis':chassis,'modules':modules,'moduleTypes':moduleTypes
                    ,'series':series}
        return render(request,'generator/addModule.html',params)

def importChassis(request,projectId):
    '''
        open an import file from AutoGen and import the chassisId

    '''
    project = Project.objects.get(id=projectId)
    if request.method == 'POST':
        import csv
        chassisName = request.POST.get('chassisName','')
        if chassisName == '':
            params = {'project':project, 'error': 'A valid chassis name must be entered!'}
            return render(request,'generator/importChassis.html',params)
        try:
            tryID = ProjChassis.objects.get(name=chassisName)
            params = {'project':project, 'error': 'Chassis name already in use!'}
            return render(request,'generator/importChassis.html',params)
        except:
            pass
        try:
            file = request.FILES['inputFile']
        except :
            params = {'project':project, 'error': 'A file must be selected!'}
            return render(request,'generator/importChassis.html',params)
        if file is None:
            params = {'projectId':projectId,'message': 'A valid file must be selected!'}
            # return render(request,'generator/importChassis.html',params)  #WTF this doesn't work!!!
            return render(request,'generator/importChassisResults.html',params)
        else:
            pass
        # do the import

            # create the chassis
            newChassis = ProjChassis()
            newChassis.projId = Project.objects.get(id=projectId)
            newChassis.name = chassisName
            newChassis.save()
            newChassisId = ProjChassis.objects.get(name=chassisName).id
            importData = parseAutoGenImport(file)
            modCount = 0
            chassisParent = ''
            for i in range(1,len(importData)):
                # create the modules in the chassis
                newModule = ProjModule()
                newModule.projId = Project.objects.get(id=projectId)
                newModule.chassisId = ProjChassis.objects.get(id=newChassisId)
                try:
                    newModule.moduleId = Module.objects.get(catalogNumber=importData[i][1])
                except:
                    pass

                newModule.slot = importData[i][0]
                newModule.name = newChassis.name + '_' + str(newModule.slot).zfill(2)
                newModule.catalogNumber = importData[i][1]
                #newModule.catalogDescription = Module.objects.get(catalogNumber=importData[i][1]).description
                newModule.registered = False

                if request.POST['parentModule'] == 'Local':
                    newModule.parent = 'Local'
                else:
                    if newModule.slot == '0':
                        pmLst = request.POST['parentModule'].split(' ')
                        newModule.parent = pmLst[0]
                        chassisParent = newModule.name
                    else:
                        newModule.parent=chassisParent

                newModule.save()
                modCount += 1
                series = newModule.catalogNumber[:4]
            ###############################################
            # determine chassis type/size for simplicities sake, make 1756 always 17
            # This should be handled somewhat differently though...
            if series in ('1756'):
                filter = {'series__exact':'1756','size__exact':17}
            elif series in ('1734'):
                filter = {'series__exact':'1734','size__exact':modCount}
            chassis = Chassis.objects.get(**filter)
            newChassis.catalogId = chassis
            newChassis.save()
            ##############################################

            # add empty slots for 1756 chassisId
            if series in ('1756'):
                for i in range(len(importData),17):
                    newModule = ProjModule()
                    newModule.chassisId = ProjChassis.objects.get(id=newChassisId)
                    newModule.slot = i
                    newModule.save()

            return redirect('/generator/project/importChassisResults/' + str(newChassis.id))


    elif request.method == 'GET':
        filter = {'moduleId__type':'Communications','moduleId__series':'1756'}
        mods = ProjModule.objects.filter(projId=projectId).filter(**filter)

        params = {'project':project,'parents':mods}
        return render(request,'generator/importChassis.html',params)

def importChassisResults(request,chassisId):

    chassis = ProjChassis.objects.get(id=chassisId)
    project = Project.objects.get(id=chassis.projId.id)
    modules = ProjModule.objects.filter(chassisId=chassis.id).order_by('slot')
    # TODO:  parent chassis should probably be a property ProjChassis
    parentChassis = modules[0].parent
    params = {'project':project,'chassis':chassis,'modules':modules,'parentChassis':parentChassis}
    return render(request,'generator/importChassisResults.html',params)

def generateXML(request,projectId):
    import xml.etree.ElementTree as ET

    project = Project.objects.get(id=projectId)

    #if request.method == 'POST':
    project = Project.objects.get(id=projectId)
    xml = buildXML(project)
    output = prettify(xml)
    fileName = project.name + '.xml'
    response = HttpResponse(output,content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + fileName

    return response


    params ={'project':project,'message':output}
    return render(request,'generator/generateXML.html',params)
    # else:
    #     params = {'project':project}
    #     return render(request,'generator/generateXML.html',params)
