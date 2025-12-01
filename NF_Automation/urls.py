from django.urls import path
# from rest_framework.decorators import api_view
from django.conf.urls.static import static

from . import views

# from NF_Automation.controller import NF_ECF_controller


from NF_Automation.controller import NF_ECF_controller


urlpatterns = [

    path('nf_ecf_approver', NF_ECF_controller.nf_ecf_approver, name='nf_ecf_approver'),

    path('test_report-form/', NF_ECF_controller.test_report_template, name='template_form'),
    path('trstreport',NF_ECF_controller.test_case_report,name='report'),

    path('test_temp_create',NF_ECF_controller.test_temp_create,name='report'),
    path('template-form/', NF_ECF_controller.template_form, name='template_form'),

    path('automation_runprocess', NF_ECF_controller.automation_runprocess, name='nf_ecf_creation'),
    path('run_processtemplate-form/', NF_ECF_controller.run_processtemplate, name='template_form'),
    path('run_process_summary/<test_id>',NF_ECF_controller.run_process_summary, name='run_process_summary'),

    path('return_test_scn_name', NF_ECF_controller.return_test_scn_name, name='return_test_scn_name'),
    path('dropdown_testcase', NF_ECF_controller.dropdown_testcase, name='dropdown_testcase')

]
