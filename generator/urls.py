from django.urls import path
from . import views
from django.conf import settings

urlpatterns = [
                path('projects', views.projects, name='projects'),
                path('createProject', views.createProject, name='createProject'),
                path('deleteProject/<int:projectId>',views.deleteProject,name='deleteProject'),
                path('deleteChassis/<int:chassisId>',views.deleteChassis,name='deleteChassis'),

                path('project/<int:projectId>',views.editProject,name='projects/editProject'),

                path('chassis/<int:chassisId>',views.editChassis,name='chassis/editChassis'),
                path('chassis/addModule/<int:chassisId>',views.addModule,name='chassis/addModule'),
                path('chassis/addModule/<int:chassisId>/<slug:catalogNumber>',views.addModule,name='chassis/addModule'),
                path('project/addChassis/<int:projectId>',views.addChassis,name='project/addChassis'),
                path('project/addChassis/<int:projectId>/<slug:catalogNumber>',views.addChassis,name='project/addChassis'),
                path('project/importChassis/<int:projectId>',views.importChassis,name='project/importChassis'),
                path('project/importChassisResults/<int:chassisId>',views.importChassisResults,name='project/importChassisResults'),
                path('project/generateXML/<int:projectId>',views.generateXML,name='project/generateXML')


]
