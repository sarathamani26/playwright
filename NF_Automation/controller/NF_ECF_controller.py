import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated




# from NF_Automation.service.NF_ECF_service import NFECF,Report
from NF_Automation.service.NF_ECF_service import NFECF,Report
from NF_Automation.controller.schedularfile import automation_schedular


from django.shortcuts import render

from NF_Automation.util import VysfinList
# from utilityservice.middleware.auth import AutoAuthenticate
from utilityservice.middleware.auth import AutoAuthenticate

from utilityservice.service.autopermission import AutoPermission



def run_processtemplate (request):
    return render(request, 'testcase.html')

@csrf_exempt
@api_view(['POST'])
def automation_runprocess(request):
    client = request.GET.get("clientname")
    testcasecode=request.GET.get("Testcasecode")
    testcase_id=request.GET.get("testcase_id")

    # call_vendor = automation_schedular(testcasecode,client,testcase_id)
    # call_vendor =NFECF().automation_script(testcasecode, client,testcase_id)
    call_vendor =NFECF().automation_script2(testcasecode, client,testcase_id)
    # call_vendor =NFECF().nf_vendor_creationtre(testcasecode,testcase_id,client)
    # serv=call_vendor. (testcasecode,client,testcase_id))
    return JsonResponse(call_vendor, safe=False)


def template_form(request):
    return render(request, 'testtemptab.html')

@csrf_exempt
@api_view(['POST'])
# @authentication_classes([AutoAuthenticate])
# @permission_classes([IsAuthenticated, AutoPermission])
def test_temp_create(request):
    data=json.loads(request.body)
    service=NFECF().tempalte_create(data)
    response = JsonResponse(service, safe=False)
    return response


@csrf_exempt
@api_view(['POST'])
def run_process_summary(request,test_id):
    serv=NFECF().process_summary(test_id)
    return JsonResponse(serv, safe=False)


@csrf_exempt
@api_view(['POST'])
def nf_ecf_approver(request):
    uploaded_file = request.FILES['file']
    call_vendor = NFECF().nf_ecf_approver(request, uploaded_file)
    response = JsonResponse(call_vendor, content_type='application/json')
    return response


@csrf_exempt
@api_view(['POST'])
def test_case_report(request):
    clientnme=request.GET.get("clientname")
    fromdate=request.GET.get('fromdate')
    todate=request.GET.get("todate")
    module=request.GET.get("module")
    testcasecode=request.GET.get("Testcase_code")
    # test_case_id=request.GET.get("C VXtest_case_id")
    report=Report()
    return report.test_report_pdf(clientnme, fromdate, todate, module,testcasecode)

    # response = JsonResponse(report, content_type='application/json')
    # return response

def test_report_template (request):
    return render(request, 'reportdownload.html')



@csrf_exempt
@api_view(['GET'])
def return_test_scn_name(request):
    testcasecode= request.GET.get("Testcasecode")
    serv=NFECF().get_scnario_name(request, testcasecode)
    response = JsonResponse(serv, safe=False)
    return response


@csrf_exempt
@api_view(['POST'])
def dropdown_testcase(request):
    clientname= request.GET.get("clientname")
    module=request.GET.get("module")
    environment=request.GET.get("environment")
    serv=NFECF().dropdown_teastcasecode(request, clientname,module,environment)
    response = JsonResponse(serv, safe=False)
    return response
