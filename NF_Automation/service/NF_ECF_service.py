import ast
import base64
import json
from asyncio import Queue
from modulefinder import Module
from threading import Thread

import pandas as pd
from datetime import datetime
from webscraping import settings
from asgiref.sync import sync_to_async
from django.contrib.messages import success
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import condition
from pdfkit import pdfkit
from playwright.async_api import async_playwright

from weasyprint import HTML
from playwright.sync_api import Playwright, sync_playwright

from NF_Automation.data.response.automationresp import Aut_Response
from NF_Automation.models import Testcase_Run, Testcase_Scenario_Template, \
    Testcase_Result, Test_run_process_summary
from NF_Automation.service.automation_report import Report_Download
import random
import os
# from django.conf import settings

from NF_Automation.util import SuccessMessage, SuccessStatus, Error, Success


class Module_Selection:
    def select_module(self, page,Module,client):
        try:
            if Module == 'ECF' and  client=='NF':

                # page.get_by_title("ECF Claim").locator("i").click()
                # page.get_by_text("ECF Claim").click()
                # print("test")
                # page.get_by_role("button", name=" + CREATE ECF").click()
                print("select iocn")
                page.locator("xpath=/html/body/app-root/mat-toolbar/button/mat-icon").click(force=True)
                page.wait_for_timeout(3000)

                page.get_by_text("ECF Claim").click()

                # Click create button
                page.get_by_role("button", name="+ CREATE ECF").click()

            elif Module == 'ECF' and client == 'NAC':
                page.get_by_title("ECF").locator("i").click()
                page.get_by_text("ECF").click()
                print("test")

                page.get_by_role("button", name="+ Add ECF").click()

            elif Module =="Vendor" and client=="NF"  :
                page.get_by_title("Vendor").locator("i").click()
                page.get_by_text("Vendor").click()
                print("test")
                page.get_by_role("button", name=" Add Vendor").click()

            elif Module =="Vendor" and client =="WR":
                # page.get_by_title("Vendor").locator("i").click()
                page.locator("xpath=/html/body/app-root/main/nav/div[2]/p[1]/span").click(force=True)
                # page.get_by_text("Vendor").click()
                print("test")
                page.get_by_role("button", name=" Add Vendor").click()


            elif Module=="ECF" and client=="KVB":
                print("module select")
                page.wait_for_timeout(3000)
                page.get_by_text("ECF Claim").click()
                # page.wait_for_timeout(6000)
                print("clk")
                # page.locator("xpath=/html/body/app-root/body/div[1]/div[2]/app-ecfap/div[1]/div[2]/div/form/div/div/button[3]").click()
                print("cfr")
                page.wait_for_timeout(1000)

            elif Module=="JV" and client=="KVB":
                print("module select")
                page.wait_for_timeout(3000)
                page.get_by_text("ECF Claim").click()





        except Exception as e:
            print(e)


class NFECF:

    def nf_ecf_approver(self,request, uploaded_file):
            try:
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(headless=True, args=["--start-maximized"])
                    context = browser.new_context(no_viewport=True)
                    page = context.new_page()
                    page.goto("http://192.168.5.4:4201/#/login")
                    # page.goto("http://13.200.50.27:2000/#/login")
                    sheetname = 'Sheet1'
                    df = pd.read_excel(uploaded_file, sheet_name=sheetname)
                    rows = df.to_dict(orient='records')
                    for row in rows:
                        page.get_by_role("textbox", name="Username").click()
                        page.get_by_role("textbox", name="Username").fill(str(row['Username']))

                        page.get_by_role("textbox", name="Password").click()
                        page.get_by_role("textbox", name="Password").fill(str(row['Password']))

                        page.get_by_text("visibility_off").click()
                        page.once("dialog", lambda dialog: dialog.dismiss())
                        page.get_by_role("button", name="Login").click()

                        page.get_by_title("ECF Claim").locator("i").click()
                        page.get_by_text("ECF Claim").click()
                        print("test")
                        page.get_by_role("tab", name="ECF Approval Summary").click()
                        page.wait_for_timeout(3000)

                        page.get_by_role("textbox", name="CR No").click()
                        page.get_by_role("textbox", name="CR No").fill(str(row['ECF_no']))
                        page.wait_for_timeout(3000)
                        page.get_by_role("button", name="search").click()

                        page.get_by_text(str(row['ECF_no'])).click()
                        page.wait_for_timeout(3000)

                        page.get_by_role("button", name="Next").click()
                        page.get_by_role("button", name="Next").click()
                        page.wait_for_timeout(3000)

                        page.get_by_role("combobox", name="Branch").click()
                        page.get_by_role("option",name=str(row['Approverbranch'])).click()
                        page.wait_for_timeout(3000)

                        page.get_by_role("combobox", name="Approver Name").click()
                        page.get_by_role("option",name=str(row['Approvername'])).click()
                        page.wait_for_timeout(3000)

                        page.get_by_role("textbox", name="Remarks").click()
                        page.get_by_role("textbox", name="Remarks").fill(str(row['Remarks']))
                        page.wait_for_timeout(3000)

                        page.get_by_role("button", name=str(row['Action']), exact=True).click()
                        page.wait_for_timeout(3000)

                        print("completed")

                        df['Status'] = "SUCCESS"
                        report_obj = Report_Download()
                        report = report_obj.report_download(df, sheetname)
                        print("completed")
                        return report

            except:
                print('error')
                df['Status'] = "Fail"
                report_obj = Report_Download()
                report = report_obj.report_download(df, sheetname)
                print("completed")
                return report

    # def nf_ecf_creation(self,testcasecode,client):
    #         global testscanrio
    #         testcasecode=ast.literal_eval(testcasecode)
    #         for testcode in testcasecode:
    #             test_run=Testcase_Run.objects.filter(Testcase_code=testcode)
    #             for run in test_run:
    #                 input_str = run.Testcase_template_input
    #                 module=run.module# This is a JSON string
    #                 test_case = json.loads(input_str)
    #                 # Convert to dict
    #
    #                 filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    #                 file_path1 = os.path.join(settings.MEDIA_ROOT, filename)
    #                 try:
    #                     playwright = sync_playwright().start()
    #                     browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
    #                     context = browser.new_context(no_viewport=True)
    #                     page = context.new_page()
    #                     page.goto("http://192.168.5.4:4201/#/login")
    #                     for i in test_case['data']:
    #
    #                         for x in i:
    #                             if x == 'Testcase_scnarios':
    #                                 testscanrio=i[x]
    #                                 continue
    #                             # with sync_playwright() as playwright:
    #
    #                             # page.goto("http://13.200.50.27:2000/#/login")
    #                             itr = 0
    #
    #                             page.wait_for_timeout(1000)
    #                             if x.startswith("button"):
    #                                 page.get_by_role("button", name=i[x]).click()
    #                                 if i[x] == 'Login':
    #                                     Module=module
    #                                     Module_Selection().select_module(page, Module)
    #
    #                             elif i[x] == 'click':
    #                                 page.locator(f'[formcontrolname={x}]').click()
    #
    #                             elif i[x] == 'file':
    #                                 crk_wrk = os.getcwd()
    #                                 file_path = os.path.join(crk_wrk, x)
    #                                 page.set_input_files('input[type="file"]', file_path)
    #                             # elif x.startswith("name"):
    #                             #     a = 'name'
    #                             #     locator = page.locator(f'[formcontrolname={a}]').nth(itr)
    #                             #     locator.wait_for(state="attached")
    #                             #     locator.fill(i[x])
    #                             #     itr += 1
    #                             # elif x.startswith("id"):
    #                             #     page.wait_for_timeout(3000)
    #                             #     locator = page.locator(f'[id={i[x]}]').nth(0).click()
    #                             elif isinstance(i[x], list):
    #                                 for idx, val in enumerate(i[x]):
    #
    #                                     locator = page.locator(f'[formcontrolname={x}]').nth(idx)
    #                                     locator.wait_for(state="attached")
    #
    #                                     try:
    #                                         locator.fill(val)
    #                                         locator.click()
    #                                         page.wait_for_timeout(500)
    #                                         options = page.locator('mat-option')
    #                                         if options.count() > 0:
    #                                             # page.wait_for_timeout(1000)
    #                                             page.locator(f'mat-option >> text="{val}"').click()
    #                                     except Exception:
    #                                         locator.click()
    #                                         # page.wait_for_timeout(1000)
    #                                         page.locator(f'mat-option >> text="{val}"').click()
    #
    #                             else:
    #                                 # page.locator(f'[formcontrolname={x}]').fill(i[x])
    #                                 locator = page.locator(f'[formcontrolname={x}]').nth(0)
    #                                 locator.wait_for(state="attached")  # Wait until it’s in the DOM
    #                                 if locator.get_attribute("readonly"):
    #                                     page.get_by_role("button", name="Open calendar").click()
    #                                     page.locator('.mat-calendar-header').click()
    #                                     given_date = i[x]
    #                                     # date_obj = datetime.strptime(given_date, "%Y-%m-%d %H:%M:%S")
    #                                     date_obj = datetime.strptime(given_date, "%d-%m-%Y")
    #                                     date = str(date_obj.day)
    #                                     month = date_obj.strftime("%b").upper()
    #                                     year = str(date_obj.year)
    #                                     page.locator(".mat-calendar-body-cell-content", has_text=year).click()
    #                                     page.locator(".mat-calendar-body-cell-content", has_text=month).click()
    #                                     page.locator(".mat-calendar-body-cell-content", has_text=date).click()
    #
    #                                 else:
    #
    #                                     try:
    #                                         locator.fill(i[x])
    #                                         locator.click()
    #                                         page.wait_for_timeout(500)
    #
    #                                         options = page.locator('mat-option')
    #                                         if options.count() > 0:
    #                                             # page.wait_for_timeout(1000)
    #                                             page.locator(f'mat-option >> text="{i[x]}"').click()
    #                                     except Exception:
    #                                         locator.click()
    #                                         # page.wait_for_timeout(1000)
    #                                         page.locator(f'mat-option >> text="{i[x]}"').click()
    #
    #
    #                         print('SUCCESS')
    #                         path = rf"D:\pfffimage\{filename}"
    #                         page.screenshot(path=path)
    #                         print("frg")
    #                         page.wait_for_timeout(5000)
    #                         page.locator("mat-icon.person_icon").click()
    #                         page.locator('a:has-text("Logout")').nth(0).click()
    #                         from asgiref.sync import sync_to_async
    #                         Testcase_Result.objects.create(
    #                             client_name=client,
    #                             status='SUCCESS',
    #                             Testcase_Result='Pass',
    #                             created_date=datetime.now(),
    #                             inputdata=input_str,
    #                             outputdata=testscanrio,
    #                             Testcase_Code=testcode,
    #                             screenshoot=path
    #                         )
    #
    #                         # Testcase_Result.objects.create(client_name=client, status='SUCCESS', Testcase_Result='Pass',
    #                         #                                created_date=datetime.now(),outputdata=testscanrio,
    #                         #                                Testcase_code=testcode, screenshoot=path)
    #                         print("tableentry")
    #                         page.wait_for_timeout(5000)
    #
    #                     data={"completed"}
    #                     return data
    #
    #                 except Exception as e:
    #                     print(e)
    #                     filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    #                     path ="D:\pfffimage\{filename}"
    #                     # path=rf"D:\Auomation_Testing\media\{filename}"
    #                     page.screenshot(path=path)
    #                     print('fail')
    #                     page.locator("mat-icon.person_icon").click()
    #                     page.locator('a:has-text("Logout")').nth(0).click()
    #                     from asgiref.sync import sync_to_async
    #                     sync_to_async(Testcase_Result.objects.create)(
    #                         client_name=client,
    #                         status='Fail',
    #                         Testcase_Result='Failed',
    #                         created_date=datetime.now(),
    #                         inputdata=input_str,
    #                         outputdata=testscanrio,
    #                         Testcase_Code=testcode,
    #                         screenshoot=path
    #                     )
    #                     print("failtable entty")
    #                     data = {"Failed"}
    #                     return data
    def nf_ecf_creation(self, testcasecode, client):
        test_run=Testcase_Run.objects.filter(Testcase_code=testcasecode)
        try:
            for run in test_run:
                input_str = run.Testcase_template_input
                module=run.module# This is a JSON string
                test_case = json.loads(input_str)
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                file_path1 = os.path.join(settings.MEDIA_ROOT, filename)

                try:
                        playwright = sync_playwright().start()
                        browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
                        context = browser.new_context(no_viewport=True)
                        page = context.new_page()
                        # page.goto("http://192.168.5.4:4201/#/login")
                        # page.goto("http://13.200.50.27:2000/#/login")
                        page.goto("http://3.108.200.134:9089/ECF/ecf")
                        itr = 0
                        for i in test_case['data']:
                            for x in i:
                                if x == 'Testcase_scnarios':
                                    testscanrio=i[x]
                                    continue
                                page.wait_for_timeout(1000)
                                if x.startswith("button"):
                                    page.get_by_role("button", name=i[x]).click()
                                    # After clicking a button
                                    page.wait_for_timeout(2000)

                                    if i[x] == 'Login':
                                        Module_Selection().select_module(page, module,client )

                                elif x=='tooltip':
                                    if client=="NF":
                                            page.locator('span.fa.fa-arrow-up.mat-mdc-tooltip-trigger').click()
                                    elif client=="NAC" :
                                            page.locator('h3[mattooltip="Add Notes"]').click()

                                elif i[x] == 'click':
                                    page.locator(f'[formcontrolname={x}]').click()



                                elif i[x] == 'file':
                                    crk_wrk = os.getcwd()
                                    file_path = os.path.join(crk_wrk, x)
                                    page.set_input_files('input[type="file"]', file_path)

                                elif isinstance(i[x], list):
                                    for idx, val in enumerate(i[x]):

                                        locator = page.locator(f'[formcontrolname={x}]').nth(idx)
                                        locator.wait_for(state="attached")

                                        try:
                                            locator.fill(val)
                                            locator.click()
                                            page.wait_for_timeout(500)
                                            options = page.locator('mat-option')
                                            if options.count() > 0:
                                                # page.wait_for_timeout(1000)
                                                page.locator(f'mat-option >> text="{val}"').click()
                                        except Exception:
                                            locator.click()
                                            # page.wait_for_timeout(1000)
                                            page.locator(f'mat-option >> text="{val}"').click()

                                else:
                                    # page.locator(f'[formcontrolname={x}]').fill(i[x])
                                    locator = page.locator(f'[formcontrolname={x}]').nth(0)
                                    locator.wait_for(state="attached")  # Wait until it’s in the DOM
                                    if locator.get_attribute("readonly"):
                                        page.get_by_role("button", name="Open calendar").click()
                                        page.locator('.mat-calendar-header').click()
                                        given_date = i[x]
                                        # date_obj = datetime.strptime(given_date, "%Y-%m-%d %H:%M:%S")
                                        date_obj = datetime.strptime(given_date, "%d-%m-%Y")
                                        date = str(date_obj.day)
                                        month = date_obj.strftime("%b").upper()
                                        year = str(date_obj.year)
                                        page.locator(".mat-calendar-body-cell-content", has_text=year).click()
                                        page.locator(".mat-calendar-body-cell-content", has_text=month).click()
                                        page.locator(".mat-calendar-body-cell-content", has_text=date).click()

                                    else:

                                        try:
                                            locator.fill(i[x])
                                            locator.click()
                                            page.wait_for_timeout(500)

                                            options = page.locator('mat-option')
                                            if options.count() > 0:
                                                # page.wait_for_timeout(1000)
                                                page.locator(f'mat-option >> text="{i[x]}"').click()
                                        except Exception:
                                            locator.click()
                                            # page.wait_for_timeout(1000)
                                            page.locator(f'mat-option >> text="{i[x]}"').click()
                            print('SUCCESS')
                            page.wait_for_timeout(5000)
                            print('SUCCESS')
                            path = rf"D:\pfffimage\{filename}"
                            page.screenshot(path=path)
                            print("frg")
                            page.wait_for_timeout(5000)
                            page.locator("mat-icon.person_icon").click()
                            page.locator('a:has-text("Logout")').nth(0).click()
                            print("fins")

                            def save_result():
                                Testcase_Result.objects.create(
                                    client_name=client,
                                    status='SUCCESS',
                                    Testcase_Result='Pass',
                                    created_date=datetime.now(),
                                    inputdata=input_str,
                                    outputdata=input_str,
                                    Testcase_code=testcasecode,
                                    screenshoot=path,
                                    Test_scnarios=testscanrio
                                )
                            Thread(target=save_result).start()
                            print("succdb")
                        data={"completed"}
                        return data

                except Exception as e:
                    # browser.close()
                    print(e)
                    print('fail')
                    path = rf"D:\pfffimage\{filename}"
                    page.screenshot(path=path)
                    print("frg")
                    page.wait_for_timeout(5000)
                    # page.locator("mat-icon.person_icon").click()
                    # page.locator('a:has-text("Logout")').nth(0).click()
                    print('errr')

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='Fail',
                            Testcase_Result='Failed',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            Testcase_code=testcasecode,
                            Test_scnarios=testscanrio,
                            screenshoot=path,
                            remarks=e

                        )
                    Thread(target=save_result).start()
                    print('tb')

        except Exception as e:
            print(e)

    def nf_ecf_creation12(self, testcasecode, client):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module  # JSON string
            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path = rf"D:\pfffimage\{filename}"

            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            # page.goto("http://13.200.50.27:2000/#/login")
            page.goto("http://192.168.5.4:4201/#/login")

            def flatten_input(data):
                flattened = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        flattened.append(value)
                    elif isinstance(value, list):
                        for subitem in value:
                            flattened.append(subitem)
                return flattened

            for input_data in test_case['data']:
                scenario_name = input_data.get("Testcase_scnarios", "Unnamed")
                merged_steps = flatten_input(input_data)
                print(merged_steps)
                try:
                    for section in merged_steps:
                        for key, value in section.items():
                                if key.startswith("button"):
                                    page.get_by_role("button", name=value).click()
                                    page.wait_for_timeout(3000)

                                    toasts = page.locator(".toast-top-right.toast-container .toast-success")
                                    page.wait_for_timeout(2000)

                                    toast_count = toasts.count()

                                    if toast_count > 0:
                                        print(f"✅ {toast_count} toast message(s) found:")
                                        for i in range(toast_count):
                                            if toasts.nth(i).is_visible():
                                                msg = toasts.nth(i).inner_text()

                                                print(f"🔔 Toast {i + 1}: {msg}")
                                    else:
                                        print("❌ No toast message visible.")

                                    if value == 'Login':
                                        Module_Selection().select_module(page, module)

                                elif key == "tooltip":
                                    page.locator('span.fa.fa-arrow-up.mat-mdc-tooltip-trigger').click()

                                elif value == "file":
                                    filepath = os.path.join(os.getcwd(), key)
                                    page.set_input_files('input[type="file"]', filepath)

                                elif value == 'click':
                                    page.locator(f'[formcontrolname={key}]').click()

                                elif isinstance(value, list):
                                    for idx, item in enumerate(value):
                                        locator = page.locator(f'[formcontrolname="{key}"]').nth(idx)
                                        locator.wait_for(state="attached")

                                        try:
                                            locator.fill(item)
                                            locator.click()
                                            options = page.locator("mat-option")
                                            if options.count() > 0:
                                                page.locator(f'mat-option >> text="{item}"').click()
                                        except:
                                            locator.click()
                                            page.locator(f'mat-option >> text="{item}"').click()

                                elif "date" in key.lower():
                                    locator = page.locator(f'[formcontrolname="{key}"]')
                                    locator.wait_for(state="attached")
                                    if locator.get_attribute("readonly"):
                                        page.get_by_role("button", name="Open calendar").click()
                                        page.locator('.mat-calendar-header').click()
                                        page.wait_for_timeout(2000)

                                        dt = datetime.strptime(value, "%d-%m-%Y")
                                        page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                        page.locator(".mat-calendar-body-cell-content",
                                                     has_text=dt.strftime("%b").upper()).click()
                                        page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).click()
                                else:
                                    locator = page.locator(f'[formcontrolname="{key}"]').nth(0)
                                    locator.wait_for(state="attached")
                                    try:
                                        locator.fill(value)
                                        locator.click()
                                        page.wait_for_timeout(300)
                                        if page.locator("mat-option").count() > 0:
                                            page.locator(f'mat-option >> text="{value}"').click()
                                    except:
                                        locator.click()
                                        page.locator(f'mat-option >> text="{value}"').click()
                                        page.wait_for_timeout(2000)

                        value = page.locator("span.nf_icon").first.text_content()
                        print(value)

                        print('SUCCESS')
                        page.screenshot(path=path)
                        print("screenshot taken")
                        page.wait_for_timeout(3000)
                        page.locator("mat-icon.person_icon").click(force=True)
                        page.wait_for_timeout(1000)
                        page.locator('a:has-text("Logout")').nth(0).click()
                        print("Logged out")

                        def save_result():
                            Testcase_Result.objects.create(
                                client_name=client,
                                status='Fail',
                                Testcase_Result='Failed',
                                created_date=datetime.now(),
                                inputdata=input_str,
                                Testcase_code=testcasecode,
                                # Test_scnarios=testscanrio,
                                screenshoot=path,
                                remarks=e,
                                code=value,

                            )

                        Thread(target=save_result).start()

                        Thread(target=save_result).start()
                        print('completed')
                        continue

                except Exception as e:
                            print("Error in ECF creation:", e)
                            print('FAIL')
                            page.screenshot(path=path)
                            print("screenshot taken")
                            def save_result():
                                Testcase_Result.objects.create(
                                    client_name=client,
                                    status='FAIL',
                                    Testcase_Result='FAIL',
                                    created_date=datetime.now(),
                                    inputdata=input_str,
                                    outputdata=input_data,
                                    Testcase_code=testcasecode,
                                    screenshoot=path,
                                    Test_scnarios=scenario_name,
                                    remarks=e

                                )
                            Thread(target=save_result).start()
                            print("fail DB saved")
                            page.locator("mat-icon.person_icon").click(force=True)
                            page.locator('a:has-text("Logout")').nth(0).click()
                            print("failLogged out")
                            continue


    def nf_vendor_creation(self, testcasecode, client):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module

            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)
            # path = rf"D:\Auomation_Testing\Screenshot\{filename}"
            path = rf"D:\pfffimage\{filename}"
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"],slow_mo=0.5)
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            # page.goto("http://192.168.5.4:4201/#/login")
            page.goto("http://13.200.50.27:2000/#/login")
            # page.goto("http://3.108.200.134:9089/#login")
            code=[]
            # page.goto(url)
            def flatten_input(data):
                flattened = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        flattened.append(value)
                    elif isinstance(value, list):
                        for subitem in value:
                            flattened.append(subitem)
                return flattened
            for input_data in test_case['data']:
                scenario_name = input_data.get("Testcase_scnarios", "Unnamed")
                merged_steps = flatten_input(input_data)
                print(merged_steps)

                try:

                    for section in merged_steps:
                        status_report = []
                        section_name = None
                        fail_fields = []
                        success_fields = []
                        for key, value in section.items():
                            section_name = section_name or key

                            if key.startswith("button"):

                                page.get_by_role("button", name=value).click()
                                page.wait_for_timeout(3000)
                                if value == 'Login' or value=="Sign in":
                                    Module_Selection().select_module(page, module,client)

                            elif key=="ecf-inventory-00071":
                                page.locator('button#ecf-inventory-00071.btn.btn-light').click()

                            elif key =="choosetype":
                                page.locator(f"text={value}").click()

                            elif key=="radiobutton":
                                if value=="Yes":
                                    page.locator('mat-radio-button:has-text("Yes")').click()
                                else:
                                        page.locator('mat-radio-button:has-text("No")').click()

                                # locator = page.locator('h3:has-text("Add Notes")')
                                # locator.wait_for(state="visible")
                                # locator.click()




                            # elif key == "tooltip":
                                # page.locator(f'span.fa.fa-arrow-up[mattooltip="{key}"]').click()
                                # page.locator('span.fa.fa-arrow-up.mat-mdc-tooltip-trigger').click()
                            elif key.startswith('tooltip'):
                                locator = page.locator(f'[mattooltip="{value}"]')
                                locator.wait_for(state="visible")
                                locator.click()
                                success_fields.append(key)
                                # page.locator(f'span.fa.fa-arrow-up[mattooltip="{key}"]').click()

                            elif value == 'click':
                                text_locator = page.get_by_text(f"{key}", exact=True)
                                if text_locator.count() > 0:
                                    text_locator.first.click()
                                else:
                                    form_locator = page.locator(f'[formcontrolname="{key}"]')
                                    placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                    id_locator = page.locator(f'[id="{key}"]')
                                    if form_locator.count() > 0:
                                        form_locator.click()
                                    elif placeholder_locator.count() > 0:
                                        placeholder_locator.click()
                                    elif id_locator.count() > 0:
                                        id_locator.click()


                            elif value == 'file':
                              if  client== 'NF':
                                    crk_wrk = os.getcwd()
                                    file_path = os.path.join(crk_wrk, key)
                                    page.set_input_files('input[type="file"]', file_path)

                              else:
                                  crk_wrk = os.getcwd()
                                  file_path = os.path.join(crk_wrk, key)
                                  # Upload the file using Playwright (click is NOT required)
                                  page.set_input_files('input[type="file"]', file_path)
                                  page.set_input_files('#ecf-inventory-00066', file_path)

                            elif isinstance(value, list):
                                for idx, item in enumerate(value):
                                    form_locator = page.locator(f'[formcontrolname="{key}"]')
                                    placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                    id_locator = page.locator(f'[id="{key}"]')
                                    if form_locator.count() > 0:
                                        locator = form_locator.nth(idx)
                                    elif placeholder_locator.count() > 0:
                                        locator = placeholder_locator.nth(idx)
                                    elif id_locator.count() > 0:
                                        locator = placeholder_locator.nth(idx)
                                    locator.wait_for(state="attached")

                                    try:
                                        tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                        if tag_name == 'mat-select':
                                            locator = page.locator(f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(idx)
                                            locator.scroll_into_view_if_needed()
                                            locator.click(force=True)
                                        else:
                                            locator.click()
                                            locator.fill(item)
                                        options = page.locator("mat-option")
                                        if options.count() > 0:
                                            mat_option = page.locator(f'mat-option >> text="{value}"')
                                            if mat_option.count() > 0:
                                                mat_option.first.click()
                                            else:
                                                options.nth(0).click()
                                    except:
                                        locator.click()
                                        page.locator(f'mat-option >> text="{item}"').click()
                            elif key.startswith("scrool"):
                                if value=="vertical":
                                    page.evaluate("window.scrollBy(0, 100)")
                                else:
                                    # page.evaluate("window.scrollBy(500, 0)")
                                    locator = page.locator(
                                        'xpath=/html/body/app-root/body/div[1]/div[2]/app-ecf/div[1]/mat-card/div[1]/app-ecf-inventory/div[1]/div/mat-card/div/div[2]/div/form/div/tr/td/button[1]')
                                    locator.scroll_into_view_if_needed()
                                    pixel = page.evaluate("window.pageYOffset")


                            elif "date" in key.lower() or "dob" in key.lower():

                                if client=="NAC":
                                    calendar_btn =page.get_by_role("button", name="Open calendar").nth(1)
                                    calendar_btn.wait_for(state="visible")
                                    calendar_btn.click()
                                    page.locator('.mat-calendar-header').click()
                                    dt = datetime.strptime(value, "%d-%m-%Y")
                                    page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                    page.locator(".mat-calendar-body-cell-content",
                                                 has_text=dt.strftime("%b").upper()).click()
                                    page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(0).click()

                                else:
                                    form_locator = page.locator(f'[formcontrolname="{key}"]')
                                    placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                    id_locator = page.locator(f'[id="{key}"]')
                                    if form_locator.count() > 0:
                                        locator = form_locator
                                    elif placeholder_locator.count() > 0:
                                        locator = placeholder_locator
                                    elif id_locator.count() > 0:
                                        locator = id_locator
                                    locator.wait_for(state="attached") # Wait until it's in the DOM
                                    date_tag_name =locator.evaluate("el => el.tagName.toLowerCase()")
                                    if date_tag_name == 'mat-datepicker-toggle':
                                        locator.get_by_role("button", name="Open calendar").click()
                                    else:
                                        page.get_by_role("button", name="Open calendar").nth(0).click()
                                    page.locator('.mat-calendar-header').click()
                                    dt = datetime.strptime(value, "%d-%m-%Y")
                                    page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                    page.locator(".mat-calendar-body-cell-content", has_text=dt.strftime("%b").upper()).click()
                                    page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(0).click()
                            else:
                                all_locators = page.locator(f'[formcontrolname="{key}"]')
                                count = all_locators.count()

                                for i in range(count):
                                    locator = all_locators.nth(i)

                                    locator.wait_for(state="attached", timeout=3000)
                                    if locator.is_visible():
                                            try:
                                                locator.fill(value)
                                                locator.click()
                                                page.wait_for_timeout(2000)
                                                if page.locator("mat-option").count() > 0:
                                                    page.locator(f'mat-option >> text="{value}"').click()
                                                    success_fields.append(key)
                                            except:
                                                locator.click()
                                                page.locator(f'mat-option >> text="{value}"').click()
                                                page.wait_for_timeout(2000)
                                                success_fields.append(key)
                                            break  # Stop after successfully filling visible locator
                                else:
                                    locator = page.locator(f'[formcontrolname="{key}"]').nth(0)
                                    locator.wait_for(state="attached")
                                    try:
                                        locator.fill(value)
                                        locator.click()
                                        page.wait_for_timeout(3000)
                                        if page.locator("mat-option").count() > 0:
                                            page.locator(f'mat-option >> text="{value}"').click()
                                            success_fields.append(key)
                                    except:
                                        locator.click()
                                        page.locator(f'mat-option >> text="{value}"').click()
                                        success_fields.append(key)
                                        page.wait_for_timeout(2000)

                    print('SUCCESS')
                    page.screenshot(path=path)
                    print("screenshot taken")
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()
                        print("Logged out")
                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='SUCCESS',
                            Testcase_Result='Pass',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,
                            Test_scnarios=scenario_name,
                            Module=module,
                        )
                    Thread(target=save_result).start()
                    print("DB saved")
                    print("completed")
                    continue
                    # context.close()
                    # browser.close()
                except Exception as e:
                    print("Error in ECF creation:", e)

                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()
                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='Failed',
                            Testcase_Result='Fail',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,
                            Test_scnarios=scenario_name,
                            Module=module,
                            remarks=e,
                        )
                    Thread(target=save_result).start()
                    print('tb')
                    continue

    def tempalte_create(self,data):
        with transaction.atomic():
            try:
                if data.get('id') is not None:
                    Testcase_Scenario_Template.objects.filter(id=data.id).update(Testcase_scenario_template=data.Testcase_scenario_template,Testcase_scenario_name=data.Testcase_scenario_name,
                                                                                updated_date=datetime.now(),environment=data.environment,scenario_type=data.scenario_type)

                else:
                    test=Testcase_Scenario_Template.objects.create(client_name=data['client_name'],Project_module=data['Project_module'],Testcase_scenario_name=data['Testcase_scenario_name'],
                                         Testcase_scenario_template=data['Testcase_scenario_template'],environment=data['environment'],created_date=datetime.now(),environment_url=data['environment_url'],scenario_type=data['scenario_type'])
                    test_id=test.id

                    prefix = "AUT"
                    module = data['Project_module'].upper()  # ECF
                    env = data['environment'].upper()
                    cli_nm=data['client_name'].upper()# SIT or DO

                    # Count how many test cases already exist for this module + environment
                    existing_count = Testcase_Run.objects.filter(
                        module=data['Project_module'],
                        environment=data['environment']

                    ).count()

                    suffix = f"{existing_count + 1:03}"  # Pad number like 001, 002, ...
                    testcase_code = f"{prefix}{module}{env}{cli_nm}{suffix}"  # AUTECFSIT001
                    template=data['Testcase_scenario_template']
                    template_input=json.dumps(template)

                    Testcase_Run.objects.create(
                        module=data['Project_module'],
                        Testcase_template_input=template_input,
                        Testcase_code=testcase_code,
                        created_date=datetime.now(),
                        environment=data['environment'],
                        testcase_scn_id=test_id,
                        environment_url=data['environment_url']

                    )
                    res = {"MESSAGE": "Template Created Successfully"}
                    return res

            except Exception as e:
                return {"MESSAGE": "ERROR_OCCURED", "DATA": str(e),
                                     "e.__traceback__.tb_lineno": str(e.__traceback__.tb_lineno)}


    def nf_vendor_creation4(self, testcasecode, client):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module
            # url = run.url
            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)
            path = rf"D:\pfffimage\{filename}"

            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"], slow_mo=0.5)
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            # url="http://13.200.50.27:2000/#/login"
            page.goto("http://13.200.50.27:2000/#/login")

            # page.set_default_timeout(15000)
            # page.set_default_navigation_timeout(30000)

            def flatten_input(data):
                flattened = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        flattened.append(value)
                    elif isinstance(value, list):
                        for subitem in value:
                            flattened.append(subitem)
                return flattened

            for input_data in test_case['data']:
                scenario_name = input_data.get("Testcase_scnarios", "Unnamed")
                merged_steps = flatten_input(input_data)
                print(merged_steps)

                try:
                    for section in merged_steps:
                        for key, value in section.items():
                            def handle_dialog(dialog):
                                print(f"Dialog type: {dialog.type}")  # Should show 'confirm'
                                print(f"Dialog message: {dialog.message}")  # Should show the confirm text
                                dialog.accept()

                            # if key == 'code':
                            #     value_code = Testcase_Result.objects.filter().order_by('-id').values('code')
                            #     value = value_code['code'][0]
                            if key.startswith("button"):
                                if value == 'NEXT':
                                    page.get_by_role("button", name=value).click()

                                if (module == 'Vendor' and value != 'NEXT') or value != 'NEXT':
                                    # page.once("dialog", lambda dialog: (
                                    #     print(f"Confirm message: {dialog.message}"),
                                    #     dialog.accept()  # or dialog.dismiss()
                                    # ))
                                    page.get_by_role("button", name=value, exact=True).click()
                                    # toasts = page.locator(".toast-top-right.toast-container .toast-success")
                                    # toast_count = toasts.count()
                                    # if toast_count > 0:
                                    #     print(f":white_check_mark: {toast_count} toast message(s) found:")
                                    #     for i in range(toast_count):
                                    #         if toasts.nth(i).is_visible():
                                    #             message = toasts.nth(i).inner_text()
                                    #             print(f":bell: Toast {i + 1}: {message}")
                                    # else:
                                    #     message = ""
                                    #     print(":x: No toast message visible.")
                                # if (module == 'Vendor' and value == 'Submit') or value == 'Proceed':
                                #     toast = page.locator(".toast-top-right.toast-container")
                                #     message = toast.inner_text()
                                #     print(f"✅ Toast message: {message}")
                                if value == 'Login' or value == 'Sign in' or value == 'login':
                                    Module_Selection().select_module(page, module,client)
                                if module == 'Vendor' and (value == 'Submit' or value == 'Proceed'):
                                    toast = page.locator(".toast-top-right.toast-container")
                                    message = toast.inner_text()
                                    print(f"✅ Toast message: {message}")
                                else:
                                    message = ""
                            elif key == "tooltip":
                                page.locator('span.fa.fa-arrow-up.mat-mdc-tooltip-trigger').click()
                            elif value == 'click':
                                text_locator = page.get_by_text(f"{key}", exact=True)
                                if text_locator.count() > 0:
                                    text_locator.first.click()
                                else:
                                    form_locator = page.locator(f'[formcontrolname="{key}"]')
                                    placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                    id_locator = page.locator(f'[id="{key}"]')
                                    if form_locator.count() > 0:
                                        form_locator.click()
                                    elif placeholder_locator.count() > 0:
                                        placeholder_locator.click()
                                    elif id_locator.count() > 0:
                                        id_locator.click()
                            elif value == 'file':
                                crk_wrk = os.getcwd()
                                file_path = os.path.join(crk_wrk, key)
                                page.set_input_files('input[type="file"]', file_path)
                            elif isinstance(value, list):
                                for idx, item in enumerate(value):
                                    form_locator = page.locator(f'[formcontrolname="{key}"]')
                                    placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                    id_locator = page.locator(f'[id="{key}"]')
                                    if form_locator.count() > 0:
                                        locator = form_locator.nth(idx)
                                    elif placeholder_locator.count() > 0:
                                        locator = placeholder_locator.nth(idx)
                                    elif id_locator.count() > 0:
                                        locator = placeholder_locator.nth(idx)
                                    locator.wait_for(state="attached")
                                    try:
                                        tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                        if tag_name == 'mat-select':
                                            locator = page.locator(
                                                f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(idx)
                                            locator.scroll_into_view_if_needed()
                                            locator.click(force=True)
                                        else:
                                            locator.click()
                                            locator.fill(item)
                                        options = page.locator("mat-option")
                                        if options.count() > 0:
                                            mat_option = page.locator(f'mat-option >> text="{value}"')
                                            if mat_option.count() > 0:
                                                mat_option.first.click()
                                            else:
                                                options.nth(0).click()
                                    except:
                                        pass
                            elif "date" in key.lower() or "dob" in key.lower():
                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                id_locator = page.locator(f'[id="{key}"]')
                                if form_locator.count() > 0:
                                    locator = form_locator
                                elif placeholder_locator.count() > 0:
                                    locator = placeholder_locator
                                elif id_locator.count() > 0:
                                    locator = id_locator
                                locator.wait_for(state="attached")  # Wait until it's in the DOM
                                date_tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                if date_tag_name == 'mat-datepicker-toggle':
                                    locator.get_by_role("button", name="Open calendar").click()
                                else:
                                    page.get_by_role("button", name="Open calendar").nth(0).click()
                                page.locator('.mat-calendar-header').click()
                                dt = datetime.strptime(value, "%d-%m-%Y")
                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                page.locator(".mat-calendar-body-cell-content",
                                             has_text=dt.strftime("%b").upper()).click()
                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(0).click()
                            else:
                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                id_locator = page.locator(f'[id="{key}"]')
                                if form_locator.count() > 0:
                                    locator = form_locator.nth(0)
                                elif placeholder_locator.count() > 0:
                                    locator = placeholder_locator.nth(0)
                                elif id_locator.count() > 0:
                                    locator = id_locator.nth(0)
                                locator.wait_for(state="attached")
                                try:
                                    tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                    if tag_name == 'mat-select':
                                        form_locator = page.locator(
                                            f'[formcontrolname="{key}"] .mat-mdc-select-trigger')
                                        placeholder_locator = page.locator(
                                            f'[placeholder="{key}"] .mat-mdc-select-trigger')
                                        id_locator = page.locator(f'[id="{key}"] .mat-mdc-select-trigger')
                                        if form_locator.count() > 0:
                                            locator = form_locator.nth(0)
                                        elif placeholder_locator.count() > 0:
                                            locator = placeholder_locator.nth(0)
                                        elif id_locator.count() > 0:
                                            locator = id_locator.nth(0)
                                        locator.scroll_into_view_if_needed()
                                        locator.click(force=True)
                                    else:
                                        locator.fill(value)
                                        locator.click()
                                        page.wait_for_timeout(1000)
                                        # locator.fill(value)
                                    options = page.locator('mat-option')
                                    if options.count() > 0:
                                        mat_option = page.locator(f'mat-option >> text="{value}"')
                                        if mat_option.count() > 0:
                                            mat_option.first.click()
                                        else:
                                            options.nth(0).click()
                                except:
                                    locator.click()
                                    page.locator(f'mat-option >> text="{value}"').click()
                    print('SUCCESS')
                    page.screenshot(path=path)
                    print("screenshot taken")
                    code = page.locator('tbody tr').nth(0).locator('td').nth(1).inner_text()
                    print("First row code:", code)
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()
                        print("Logged out")
                    elif client == 'NAC':
                        page.get_by_text("logout", exact=True).click()

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='SUCCESS',
                            Testcase_Result='Pass',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,
                            Test_scnarios=scenario_name,
                            Module=module,

                            code=code
                        )

                    Thread(target=save_result).start()
                    print("DB saved")
                    print("completed")
                    continue
                    # context.close()
                    # browser.close()
                except Exception as e:
                    page.screenshot(path=path)
                    print("Error in ECF creation:", e)
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()
                    elif client == 'NAC':
                        page.get_by_text("logout", exact=True).click()

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='Failed',
                            Testcase_Result='Fail',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,
                            Test_scnarios=scenario_name,
                            Module=module,
                            remarks=e,
                            code=value

                        )

                    Thread(target=save_result).start()
                    print('tb')
                    continue



    def nf_vendor_creationdr(self, testcasecode, client,testcase_id):
        from asgiref.sync import async_to_sync, sync_to_async
        print("smd")
        test_runs = Testcase_Run.objects.filter(Testcase_code=testcasecode).values('Testcase_template_input', 'module',
                                                                                   'id')
        for run in test_runs:
            input_str = run['Testcase_template_input']
            module = run['module']
            id = run['id']

            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)
            print("smd2")
            video_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"

            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)


            # path = rf"D:\Auomation_Testing\Screenshot\{filename}"
            path = rf"D:\pfffimage\{filename}"
            video_path=rf"D:\plyvid\{video_filename}"
            playwright = sync_playwright().start()
            print("edr")
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"])
            print("frd")
            # context = browser.new_context(no_viewport=True)
            context = browser.new_context(
                no_viewport=True,
                record_video_dir=video_path,
                # record_video_size={"width": 1280, "height": 720}  # optional
            )

            page = context.new_page()

            page.goto("http://13.200.50.27:2000/#/login")
            try:
                    test_ids = ast.literal_eval(testcase_id)
                    for input_data in test_case['data']:
                        scenario_name = input_data.get("Testcase_scnarios", "Unnamed")
                        print(f"\nScenario: {scenario_name}")
                        section_status_dict = {}
                        percentage = ""
                        if isinstance(input_data, dict):

                            for section_key, section_value in input_data.items():
                                if section_key == "Testcase_scnarios":
                                    continue

                                fail_fields = []
                                success_fields = []
                                per = 0
                                merged_steps = section_value if isinstance(section_value, list) else [section_value]
                                test_ids = ast.literal_eval(testcase_id)

                                for test_id in test_ids:
                                    print(f"\n🔁 Running for Testcase ID: {test_id}")

                                    def status_update(test_id):
                                        Testcase_Result.objects.filter(id=test_id).update(client_name=client, Module=module,
                                                                                          status="STARTED")

                                    t1 = Thread(target=status_update, args=(test_id,))
                                    t1.start()
                                    t1.join()


                                for section in merged_steps:
                                    if isinstance(section, dict):
                                        for key, value in section.items():
                                            try:
                                                per += 10
                                                percen = f"{per}%"

                                                if key.startswith("button"):
                                                    try:
                                                        page.get_by_role("button", name=value).click()
                                                    except:
                                                        page.get_by_text(value, exact=True).click()

                                                    page.wait_for_timeout(2000)

                                                    if value in ['Login', "Sign in"]:
                                                        Module_Selection().select_module(page, module, client)

                                                elif key == "ecf-inventory-00071":
                                                    page.locator('button#ecf-inventory-00071.btn.btn-light').click()
                                                elif key == "ecf-inventory-00135":
                                                    page.locator("#ecf-inventory-00135").click()
                                                elif key == "choosetype":
                                                    page.locator(f"text={value}").click()
                                                elif key == "radiobutton":
                                                    page.locator(f'mat-radio-button:has-text("{value}")').click()
                                                elif key.startswith('tooltip'):
                                                    locator = page.locator(f'[mattooltip="{value}"]')
                                                    locator.wait_for(state="visible")
                                                    locator.click()
                                                    success_fields.append(key)

                                                elif value == 'click':
                                                    text_locator = page.get_by_text(f"{key.strip()}", exact=True)
                                                    if text_locator.count() > 0:
                                                        text_locator.first.click()
                                                    else:
                                                        form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                        placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                        id_locator = page.locator(f'[id="{key}"]')
                                                        if form_locator.count() > 0:
                                                            form_locator.click()
                                                        elif placeholder_locator.count() > 0:
                                                            placeholder_locator.click()
                                                        elif id_locator.count() > 0:
                                                            id_locator.click()

                                                elif value == 'file':
                                                    crk_wrk = os.getcwd()
                                                    file_path = os.path.join(crk_wrk, key)
                                                    page.set_input_files('input[type="file"]', file_path)
                                                    if client != 'NF':
                                                        page.set_input_files('#ecf-inventory-00066', file_path)
                                                    per += 10
                                                    percen = f"{per}%"


                                                elif isinstance(value, list):
                                                    for idx, item in enumerate(value):
                                                        locator = page.locator(f'[formcontrolname="{key}"]').nth(idx)
                                                        locator.wait_for(state="attached")
                                                        try:
                                                            tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                            if tag_name == 'mat-select':
                                                                locator = page.locator(
                                                                    f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(
                                                                    idx)
                                                                locator.scroll_into_view_if_needed()
                                                                locator.click(force=True)
                                                            else:
                                                                locator.click()
                                                                locator.fill(item)
                                                            options = page.locator("mat-option")
                                                            if options.count() > 0:
                                                                mat_option = page.locator(f'mat-option >> text="{value}"')
                                                                if mat_option.count() > 0:
                                                                    mat_option.first.click()
                                                                else:
                                                                    options.nth(0).click()
                                                        except:
                                                            locator.click()
                                                            page.locator(f'mat-option >> text="{item}"').click()

                                                elif key.startswith("scrool"):
                                                    if value == "vertical":
                                                        page.evaluate("window.scrollBy(0, 100)")
                                                    else:
                                                        locator = page.locator(
                                                            'xpath=/html/body/app-root/body/div[1]/div[2]/app-ecf/div[1]/mat-card/div[1]/app-ecf-inventory/div[1]/div/mat-card/div/div[2]/div/form/div/tr/td/button[1]')
                                                        locator.scroll_into_view_if_needed()
                                                        pixel = page.evaluate("window.pageYOffset")

                                                elif "date" in key.lower() or "dob" in key.lower():
                                                    dt = datetime.strptime(value, "%d-%m-%Y")
                                                    if client == "NAC":
                                                        page.get_by_role("button", name="Open calendar").nth(1).click()
                                                        page.locator('.mat-calendar-header').click()
                                                    else:
                                                        page.get_by_role("button", name="Open calendar").nth(0).click()
                                                        page.locator('.mat-calendar-header').click()
                                                    page.locator(".mat-calendar-body-cell-content",
                                                                 has_text=str(dt.year)).click()
                                                    page.locator(".mat-calendar-body-cell-content",
                                                                 has_text=dt.strftime("%b").upper()).click()
                                                    page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(
                                                        0).click()
                                                    per += 10
                                                    percen = f"{per}%"

                                                else:
                                                    all_locators = page.locator(f'[formcontrolname="{key}"]')
                                                    count = all_locators.count()
                                                    for i in range(count):
                                                        locator = all_locators.nth(i)
                                                        locator.wait_for(state="attached", timeout=3000)
                                                        if locator.is_visible():
                                                            try:
                                                                locator.fill(value)
                                                                locator.click()
                                                                page.wait_for_timeout(2000)
                                                                if page.locator("mat-option").count() > 0:
                                                                    page.locator(f'mat-option >> text="{value}"').click()
                                                                    success_fields.append(key)
                                                                    per += 10
                                                                    percen = f"{per}%"
                                                            except:
                                                                locator.click()
                                                                page.locator(f'mat-option >> text="{value}"').click()
                                                                per += 10
                                                                percen = f"{per}%"
                                                                success_fields.append(key)
                                                            break
                                                    else:
                                                        locator = page.locator(f'[formcontrolname="{key}"]').nth(0)
                                                        locator.wait_for(state="attached")
                                                        try:
                                                            locator.fill(value)
                                                            locator.click()
                                                            page.wait_for_timeout(3000)
                                                            if page.locator("mat-option").count() > 0:
                                                                page.locator(f'mat-option >> text="{value}"').click()
                                                                per += 10
                                                                percen = f"{per}%"
                                                                success_fields.append(key)
                                                        except:
                                                            locator.click()
                                                            page.locator(f'mat-option >> text="{value}"').click()
                                                            per += 10
                                                            percen = f"{per}%"
                                                            success_fields.append(key)

                                                success_fields.append(key)

                                            except Exception as e:
                                                fail_fields.append(key)

                                        status = "✓" if not fail_fields else "✗"
                                        section_status_dict[section_key] = status

                                def section_status_update():
                                    Testcase_Result.objects.filter(id=test_id).update(
                                        test_implement_status=section_status_dict,
                                        status="Processing"
                                    )

                                Thread(target=section_status_update).start()
                                print(f"{section_key} : {status}")

                                # value = page.locator("span.nf_icon").first.text_content()
                                # print(value)
                                print("SUCCESS")
                                video_file_path = page.video.path()
                                print(f"Recorded video path: {video_file_path}")
                                page.screenshot(path=path)
                                print("Screenshot taken")

                                if client == 'NF':
                                    page.get_by_text("person").click()
                                    page.locator("a").filter(has_text="Logout").click()
                                    print("Logged out")

                                def save_result():
                                    print("entrytab")
                                    Testcase_Result.objects.filter(id=test_id).update(
                                        client_name=client,
                                        status='SUCCESS',
                                        Testcase_Result='Pass',
                                        created_date=datetime.now(),
                                        inputdata=input_str,
                                        outputdata=input_data,
                                        code=value,
                                        percentage=percen,
                                        screenshoot=path,
                                        video_link=video_file_path
                                    )

                                t2 = Thread(target=save_result)
                                t2.start()
                                t2.join()
                                print("DB saved")
                                print("completed")
                            continue

            except Exception as e:
                print("Error in ECF creation:", e)
                status = "x"
                print(f"{section_key} : {status}")
                if fail_fields:
                    print(f"  Failed Fields: {fail_fields}")
                page.screenshot(path=path)
                print("Screenshot taken on failure")
                video_file_path = page.video.path()
                print(f"Recorded video path: {video_file_path}")

                if client == 'NF':
                    page.get_by_text("person").click()
                    page.locator("a").filter(has_text="Logout").click()

                def save_result():
                    Testcase_Result.objects.filter(id=test_id).update(
                        status='Failed',
                        Testcase_Result='Fail',
                        created_date=datetime.now(),
                        inputdata=input_str,
                        outputdata=input_data,
                        Testcase_code=testcasecode,
                        screenshoot=path,
                        Test_scnarios=scenario_name,
                        Module=module,
                        remarks=e,
                        percentage=percen,
                        video_link=video_file_path
                    )

                Thread(target=save_result).start()
                print("Failed test case saved.")



    def nf_vendor_creationtre(self,testcasecode,testcase_id,client):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module
            id=run.id

            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)

            video_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)

            # path = rf"D:\Auomation_Testing\Screenshot\{filename}"
            path = rf"D:\pfffimage\{filename}"
            video_path=rf"D:\plyvid\{video_filename}"
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"], slow_mo=0.5)
            # context = browser.new_context(no_viewport=True)
            context = browser.new_context(
                no_viewport=True,
                record_video_dir=video_path,
                record_video_size={"width": 1280, "height": 720}  # optional
            )

            page = context.new_page()
            # page.goto("http://192.168.5.4:4201/#/login")
            # page.goto("http://13.200.50.27:2000/#/login")
            page.goto("https://s3.ap-south-1.amazonaws.com/kvb.vsolv.co.in/index.html#/login")


            for input_data in test_case['data']:
                scenario_name = input_data.get("Testcase_scnarios", "Unnamed")

                print(f"\nScenario: {scenario_name}")
                percentage=""
                try:
                    for section_key, section_value in input_data.items():
                        if section_key == "Testcase_scnarios":
                            continue
                        fail_fields = []
                        success_fields = []
                        per=0
                        merged_steps = section_value if isinstance(section_value, list) else [section_value]

                        for section in merged_steps:
                                for key, value in section.items():
                                    try:


                                        if key.startswith("button"):
                                            try:
                                                page.get_by_role("button", name=value).click()
                                            except:
                                                page.get_by_text(value, exact=True).click()

                                            page.wait_for_timeout(3000)
                                            if value == 'Login' or value == "Sign in" or value=="login":
                                                Module_Selection().select_module(page, module, client)
                                        # elif key=="has_text":
                                        #     page.locator('span', has_text=value).click()
                                        # elif key=="mat-icon":
                                        #     page.locator("mat-icon", has_text=value).click()

                                        elif key == "ecf-inventory-00071":
                                            page.locator('button#ecf-inventory-00071.btn.btn-light').click()
                                        elif key =="ecf-inventory-00135":
                                            page.locator("#ecf-inventory-00135").click()
                                        elif key =="ecf-inventory-00280":
                                            page.locator("#ecf-inventory-00280").click()
                                        elif key=="ecf-inventory-00200":
                                            page.locator("#ecf-inventory-00200").click()
                                        elif key=="ecf-inventory-00169":
                                            page.locator("#ecf-inventory-00169").click()
                                        elif key=="ecf-inventory-00181":
                                            page.locator("#ecf-inventory-00181").click()

                                        elif key == "choosetype":
                                            page.locator(f"text={value}").click()

                                        elif key == "Add Notes":

                                            page.locator("//h3[contains(text(), 'Add Notes')]").click()
                                            page.wait_for_timeout(800)

                                            note_editor = page.locator(".note-editable")
                                            # Ensure it is visible and interactable
                                            note_editor.wait_for(state="visible")

                                            # Click inside and fill the text
                                            note_editor.click()
                                            note_editor.fill(value)

                                        elif key == "radiobutton":
                                            if value == "Yes":
                                                page.locator('mat-radio-button:has-text("Yes")').click()
                                            else:
                                                page.locator('mat-radio-button:has-text("No")').click()
                                        elif key.startswith('tooltip'):
                                            locator = page.locator(f'[mattooltip="{value}"]')
                                            locator.wait_for(state="visible")
                                            locator.click()
                                            success_fields.append(key)
                                            # page.locator(f'span.fa.fa-arrow-up[mattooltip="{key}"]').click()

                                        elif value == 'click':
                                            text_locator = page.get_by_text(f"{key.strip()}", exact=True)
                                            if text_locator.count() > 0:
                                                text_locator.first.click()
                                            else:
                                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                id_locator = page.locator(f'[id="{key}"]')
                                                if form_locator.count() > 0:
                                                    form_locator.click()
                                                elif placeholder_locator.count() > 0:
                                                    placeholder_locator.click()
                                                elif id_locator.count() > 0:
                                                    id_locator.click()

                                        elif value == 'file':
                                            if client == 'NF':
                                                crk_wrk = os.getcwd()
                                                file_path = os.path.join(crk_wrk, key)
                                                page.set_input_files('input[type="file"]', file_path)


                                            else:
                                                crk_wrk = os.getcwd()
                                                file_path = os.path.join(crk_wrk, key)
                                                # Upload the file using Playwright (click is NOT required)
                                                page.set_input_files('input[type="file"]', file_path)
                                                page.set_input_files('#ecf-inventory-00066', file_path)

                                        elif isinstance(value, list):
                                            for idx, item in enumerate(value):
                                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                id_locator = page.locator(f'[id="{key}"]')
                                                if form_locator.count() > 0:
                                                    locator = form_locator.nth(idx)
                                                elif placeholder_locator.count() > 0:
                                                    locator = placeholder_locator.nth(idx)
                                                elif id_locator.count() > 0:
                                                    locator = placeholder_locator.nth(idx)
                                                locator.wait_for(state="attached")

                                                try:
                                                    tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                    if tag_name == 'mat-select':
                                                        locator = page.locator(
                                                            f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(idx)
                                                        locator.scroll_into_view_if_needed()
                                                        locator.click(force=True)
                                                    else:
                                                        locator.click()
                                                        locator.fill(item)
                                                    options = page.locator("mat-option")
                                                    if options.count() > 0:
                                                        mat_option = page.locator(f'mat-option >> text="{value}"')
                                                        if mat_option.count() > 0:
                                                            mat_option.first.click()
                                                        else:
                                                            options.nth(0).click()
                                                except:
                                                    locator.click()
                                                    page.locator(f'mat-option >> text="{item}"').click()
                                        elif key.startswith("scrool"):
                                            if value == "vertical":
                                                page.evaluate("window.scrollBy(0, 100)")


                                            else:
                                                page.evaluate("window.scrollBy(500, 100)")
                                                # locator = page.locator(
                                                #     'xpath=/html/body/app-root/body/div[1]/div[2]/app-ecf/div[1]/mat-card/div[1]/app-ecf-inventory/div[1]/div/mat-card/div/div[2]/div/form/div/tr/td/button[1]')
                                                # locator.scroll_into_view_if_needed()
                                                pixel = page.evaluate("window.pageYOffset")


                                        elif "date" in key.lower() or "dob" in key.lower():

                                            if client == "NAC":
                                                calendar_btn = page.get_by_role("button", name="Open calendar").nth(1)
                                                calendar_btn.wait_for(state="visible")
                                                calendar_btn.click()
                                                page.locator('.mat-calendar-header').click()
                                                dt = datetime.strptime(value, "%d-%m-%Y")
                                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                                page.locator(".mat-calendar-body-cell-content",
                                                             has_text=dt.strftime("%b").upper()).click()
                                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(0).click()
                                                per += 10
                                                percen = f"{per}%"

                                            else:
                                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                id_locator = page.locator(f'[id="{key}"]')
                                                if form_locator.count() > 0:
                                                    locator = form_locator
                                                elif placeholder_locator.count() > 0:
                                                    locator = placeholder_locator
                                                elif id_locator.count() > 0:
                                                    locator = id_locator
                                                locator.wait_for(state="attached")  # Wait until it's in the DOM
                                                date_tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                if date_tag_name == 'mat-datepicker-toggle':
                                                    locator.get_by_role("button", name="Open calendar").click()
                                                else:
                                                    page.get_by_role("button", name="Open calendar").nth(0).click()
                                                page.locator('.mat-calendar-header').click()
                                                dt = datetime.strptime(value, "%d-%m-%Y")
                                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                                page.locator(".mat-calendar-body-cell-content",
                                                             has_text=dt.strftime("%b").upper()).click()
                                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(0).click()

                                        else:
                                            all_locators = page.locator(f'[formcontrolname="{key}"]')
                                            count = all_locators.count()

                                            for i in range(count):
                                                locator = all_locators.nth(i)

                                                locator.wait_for(state="attached", timeout=3000)
                                                if locator.is_visible():
                                                    try:
                                                        locator.fill(value)
                                                        locator.click()
                                                        page.wait_for_timeout(2000)
                                                        if page.locator("mat-option").count() > 0:
                                                            page.locator(f'mat-option >> text="{value}"').click()
                                                            success_fields.append(key)

                                                    except:
                                                        locator.click()
                                                        page.locator(f'mat-option >> text="{value}"').click()
                                                        page.wait_for_timeout(2000)
                                                        success_fields.append(key)

                                                    break  # Stop after successfully filling visible locator
                                            else:
                                                locator = page.locator(f'[formcontrolname="{key}"]').nth(0)
                                                locator.wait_for(state="attached")
                                                try:
                                                    locator.fill(value)
                                                    locator.click()
                                                    page.wait_for_timeout(3000)
                                                    if page.locator("mat-option").count() > 0:
                                                        page.locator(f'mat-option >> text="{value}"').click()

                                                        success_fields.append(key)
                                                except:
                                                    locator.click()
                                                    page.locator(f'mat-option >> text="{value}"').click()

                                                    success_fields.append(key)
                                                    page.wait_for_timeout(2000)


                                            success_fields.append(key)
                                    except Exception as e:
                                        fail_fields.append(key)


                        status = "✓" if not fail_fields else "✗"
                        print(f"{section_key} : {status}")
                                # if fail_fields:
                                #     print(f"  Failed Fields: {fail_fields}")
                    value = page.locator("span.nf_icon").first.text_content()
                    print(value)
                    print('SUCCESS')
                    video_file_path = page.video.path()
                    print(f"Recorded video path: {video_file_path}")
                    page.screenshot(path=path)
                    print("screenshot taken")
                    # percentage.append(percen)
                    # if client == 'NF':
                    #     page.get_by_text("person").click()
                    #     page.locator("a").filter(has_text="Logout").click()
                    #     print("Logged out")

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='SUCCESS',
                            Testcase_Result='Pass',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,

                            Module=module,
                            code=value,
                            percentage=percen,
                            video_link=video_file_path
                        )

                    Thread(target=save_result).start()
                    print("DB saved")
                    print("completed")
                    continue

                except Exception as e:
                    print("Error in ECF creation:", e)
                    status = "x"
                    print(f"{section_key} : {status}")
                    if fail_fields:
                        print(f"  Failed Fields: {fail_fields}")
                    page.screenshot(path=path)
                    print("Screenshot taken on failure")
                    video_file_path = page.video.path()
                    print(f"Recorded video path: {video_file_path}")
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='Failed',
                            Testcase_Result='Fail',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,
                            Test_scnarios=scenario_name,
                            Module=module,
                            remarks=e,
                            percentage=percen,
                            video_link=video_file_path
                        )

                    Thread(target=save_result).start()
                    print('tb')
                    continue








    def nf_vendor_creationtre_testing(self, testcasecode,testcase_id,client):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module


            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)

            video_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)

            # path = rf"D:\Auomation_Testing\Screenshot\{filename}"
            path = rf"D:\pfffimage\{filename}"
            video_path=rf"D:\plyvid\{video_filename}"
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"], slow_mo=0.5)
            # context = browser.new_context(no_viewport=True)
            context = browser.new_context(
                no_viewport=True,
                record_video_dir=video_path,
                record_video_size={"width": 1280, "height": 720}  # optional
            )

            page = context.new_page()
            # page.goto("http://192.168.5.4:4201/#/login")
            # page.goto("http://13.200.50.27:2000/#/login")
            page.goto("https://s3.ap-south-1.amazonaws.com/kvb.vsolv.co.in/index.html#/login")

            for input_data in test_case['data']:
                scenario_name = input_data.get("Testcase_scnarios", "Unnamed")

                print(f"\nScenario: {scenario_name}")
                percentage=""
                try:
                    for section_key, section_value in input_data.items():
                        if section_key == "Testcase_scnarios":
                            continue
                        fail_fields = []
                        success_fields = []
                        per=0
                        merged_steps = section_value if isinstance(section_value, list) else [section_value]

                        for section in merged_steps:
                                for key, value in section.items():
                                    try:
                                        per +=10
                                        percen = f"{per}%"

                                        if key.startswith("button"):
                                            try:
                                                page.get_by_role("button", name=value).click()
                                            except:
                                                page.get_by_text(value, exact=True).click()

                                            page.wait_for_timeout(3000)
                                            if value == 'Login' or value == "Sign in" or value=="login":
                                                Module_Selection().select_module(page, module, client)
                                        # elif key=="has_text":
                                        #     page.locator('span', has_text=value).click()
                                        # elif key=="mat-icon":
                                        #     page.locator("mat-icon", has_text=value).click()

                                        elif key == "ecf-inventory-00071":
                                            page.locator('button#ecf-inventory-00071.btn.btn-light').click()
                                        elif key =="ecf-inventory-00135":
                                            page.locator("#ecf-inventory-00135").click()

                                        elif key == "Add Notes":
                                            # Click the Add Notes section
                                            page.locator("//h3[contains(text(), 'Add Notes')]").click()
                                            page.wait_for_timeout(800)
                                            # Wait for the note editor to appear
                                            note_editor = page.locator(".note-editable")
                                            # Ensure it is visible and interactable
                                            note_editor.wait_for(state="visible")

                                            # Click inside and fill the text
                                            note_editor.click()
                                            note_editor.fill(value)


                                        elif key == "choosetype":
                                            page.locator(f"text={value}").click()

                                        elif key == "radiobutton":
                                            if value == "Yes":
                                                page.locator('mat-radio-button:has-text("Yes")').click()
                                            else:
                                                page.locator('mat-radio-button:has-text("No")').click()
                                        elif key.startswith('tooltip'):
                                            locator = page.locator(f'[mattooltip="{value}"]')
                                            locator.wait_for(state="visible")
                                            locator.click()
                                            success_fields.append(key)
                                            # page.locator(f'span.fa.fa-arrow-up[mattooltip="{key}"]').click()

                                        elif value == 'click':
                                            text_locator = page.get_by_text(f"{key.strip()}", exact=True)
                                            if text_locator.count() > 0:
                                                text_locator.first.click()
                                            else:
                                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                id_locator = page.locator(f'[id="{key}"]')
                                                if form_locator.count() > 0:
                                                    form_locator.click()
                                                elif placeholder_locator.count() > 0:
                                                    placeholder_locator.click()
                                                elif id_locator.count() > 0:
                                                    id_locator.click()

                                        elif value == 'file':
                                            if client == 'NF':
                                                crk_wrk = os.getcwd()
                                                file_path = os.path.join(crk_wrk, key)
                                                page.set_input_files('input[type="file"]', file_path)
                                                per += 10
                                                percen = f"{per}%"

                                            else:
                                                crk_wrk = os.getcwd()
                                                file_path = os.path.join(crk_wrk, key)
                                                # Upload the file using Playwright (click is NOT required)
                                                page.set_input_files('input[type="file"]', file_path)
                                                page.set_input_files('#ecf-inventory-00066', file_path)

                                        elif isinstance(value, list):
                                            for idx, item in enumerate(value):
                                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                id_locator = page.locator(f'[id="{key}"]')
                                                if form_locator.count() > 0:
                                                    locator = form_locator.nth(idx)
                                                elif placeholder_locator.count() > 0:
                                                    locator = placeholder_locator.nth(idx)
                                                elif id_locator.count() > 0:
                                                    locator = placeholder_locator.nth(idx)
                                                locator.wait_for(state="attached")

                                                try:
                                                    tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                    if tag_name == 'mat-select':
                                                        locator = page.locator(
                                                            f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(idx)
                                                        locator.scroll_into_view_if_needed()
                                                        locator.click(force=True)
                                                    else:
                                                        locator.click()
                                                        locator.fill(item)
                                                    options = page.locator("mat-option")
                                                    if options.count() > 0:
                                                        mat_option = page.locator(f'mat-option >> text="{value}"')
                                                        if mat_option.count() > 0:
                                                            mat_option.first.click()
                                                        else:
                                                            options.nth(0).click()
                                                except:
                                                    locator.click()
                                                    page.locator(f'mat-option >> text="{item}"').click()
                                        elif key.startswith("scrool"):
                                            if value == "vertical":
                                                page.evaluate("window.scrollBy(0, 100)")
                                            else:
                                                # page.evaluate("window.scrollBy(500, 0)")
                                                locator = page.locator(
                                                    'xpath=/html/body/app-root/body/div[1]/div[2]/app-ecf/div[1]/mat-card/div[1]/app-ecf-inventory/div[1]/div/mat-card/div/div[2]/div/form/div/tr/td/button[1]')
                                                locator.scroll_into_view_if_needed()
                                                pixel = page.evaluate("window.pageYOffset")


                                        elif "date" in key.lower() or "dob" in key.lower():

                                            if client == "NAC":
                                                calendar_btn = page.get_by_role("button", name="Open calendar").nth(1)
                                                calendar_btn.wait_for(state="visible")
                                                calendar_btn.click()
                                                page.locator('.mat-calendar-header').click()
                                                dt = datetime.strptime(value, "%d-%m-%Y")
                                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                                page.locator(".mat-calendar-body-cell-content",
                                                             has_text=dt.strftime("%b").upper()).click()
                                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(0).click()
                                                per += 10
                                                percen = f"{per}%"

                                            else:
                                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                id_locator = page.locator(f'[id="{key}"]')
                                                if form_locator.count() > 0:
                                                    locator = form_locator
                                                elif placeholder_locator.count() > 0:
                                                    locator = placeholder_locator
                                                elif id_locator.count() > 0:
                                                    locator = id_locator
                                                locator.wait_for(state="attached")  # Wait until it's in the DOM
                                                date_tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                if date_tag_name == 'mat-datepicker-toggle':
                                                    locator.get_by_role("button", name="Open calendar").click()
                                                else:
                                                    page.get_by_role("button", name="Open calendar").nth(0).click()
                                                page.locator('.mat-calendar-header').click()
                                                dt = datetime.strptime(value, "%d-%m-%Y")
                                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                                page.locator(".mat-calendar-body-cell-content",
                                                             has_text=dt.strftime("%b").upper()).click()
                                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(0).click()
                                                per+=10
                                                percen = f"{per}%"
                                        else:
                                            all_locators = page.locator(f'[formcontrolname="{key}"]')
                                            count = all_locators.count()

                                            for i in range(count):
                                                locator = all_locators.nth(i)

                                                locator.wait_for(state="attached", timeout=3000)
                                                if locator.is_visible():
                                                    try:
                                                        locator.fill(value)
                                                        locator.click()
                                                        page.wait_for_timeout(2000)
                                                        if page.locator("mat-option").count() > 0:
                                                            page.locator(f'mat-option >> text="{value}"').click()
                                                            success_fields.append(key)
                                                            per += 10
                                                            percen = f"{per}%"
                                                    except:
                                                        locator.click()
                                                        page.locator(f'mat-option >> text="{value}"').click()
                                                        page.wait_for_timeout(2000)
                                                        success_fields.append(key)
                                                        per += 10
                                                        percen = f"{per}%"
                                                    break  # Stop after successfully filling visible locator
                                            else:
                                                locator = page.locator(f'[formcontrolname="{key}"]').nth(0)
                                                locator.wait_for(state="attached")
                                                try:
                                                    locator.fill(value)
                                                    locator.click()
                                                    page.wait_for_timeout(3000)
                                                    if page.locator("mat-option").count() > 0:
                                                        page.locator(f'mat-option >> text="{value}"').click()
                                                        per+=10
                                                        percen = f"{per}%"
                                                        success_fields.append(key)
                                                except:
                                                    locator.click()
                                                    page.locator(f'mat-option >> text="{value}"').click()
                                                    per+=10
                                                    percen = f"{per}%"
                                                    success_fields.append(key)
                                                    page.wait_for_timeout(2000)


                                            success_fields.append(key)
                                    except Exception as e:
                                        fail_fields.append(key)


                        status = "✓" if not fail_fields else "✗"
                        print(f"{section_key} : {status}")
                                # if fail_fields:
                                #     print(f"  Failed Fields: {fail_fields}")
                    value = page.locator("span.nf_icon").first.text_content()
                    print(value)
                    print('SUCCESS')
                    video_file_path = page.video.path()
                    print(f"Recorded video path: {video_file_path}")
                    page.screenshot(path=path)
                    print("screenshot taken")
                    # percentage.append(percen)
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()
                        print("Logged out")

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='SUCCESS',
                            Testcase_Result='Pass',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,

                            Module=module,
                            code=value,
                            percentage=percen,
                            video_link=video_file_path
                        )

                    Thread(target=save_result).start()
                    print("DB saved")
                    print("completed")
                    continue

                except Exception as e:
                    print("Error in ECF creation:", e)
                    status = "x"
                    print(f"{section_key} : {status}")
                    if fail_fields:
                        print(f"  Failed Fields: {fail_fields}")
                    page.screenshot(path=path)
                    print("Screenshot taken on failure")
                    video_file_path = page.video.path()
                    print(f"Recorded video path: {video_file_path}")
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='Failed',
                            Testcase_Result='Fail',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,
                            Test_scnarios=scenario_name,
                            Module=module,
                            remarks=e,
                            percentage=percen,
                            video_link=video_file_path
                        )

                    Thread(target=save_result).start()
                    print('tb')
                    continue




    def nf_vendor_creationtre22(self, testcasecode, client):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module
            id = run.id

            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)
            path = rf"D:\pfffimage\{filename}"

            video_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
            video_path = rf"D:\plyvid\{video_filename}"

            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"], slow_mo=0.5)
            context = browser.new_context(
                no_viewport=True,
                record_video_dir=video_path,
                record_video_size={"width": 1280, "height": 720}
            )
            page = context.new_page()
            page.goto("http://3.108.200.134:9089/ECF/ecf")

            for input_data in test_case['data']:
                scenario_name = input_data.get("Testcase_scnarios", "Unnamed")
                print(f"\nScenario: {scenario_name}")

                fail_fields = []
                success_fields = []
                per = 0

                # Iterate dynamically over all sections
                for section_key, section_value in input_data.items():
                    if section_key == "Testcase_scnarios":
                        continue

                    # Merge section into list if it is a single dict
                    merged_steps = section_value if isinstance(section_value, list) else [section_value]

                    for section in merged_steps:
                        for key, value in section.items():
                            try:
                                per += 10
                                percen = f"{per}%"

                                # BUTTON CLICK
                                if key.startswith("button"):
                                    try:
                                        page.get_by_role("button", name=value).click()
                                    except:
                                        page.get_by_text(value, exact=True).click()
                                    page.wait_for_timeout(3000)
                                    if value in ["Login", "Sign in"]:
                                        Module_Selection().select_module(page, module, client)
                                        page.wait_for_load_state("networkidle")

                                # RADIO BUTTON
                                elif key == "radiobutton":
                                    page.locator(f'mat-radio-button:has-text("{value}")').click()

                                # TOOLTIP
                                elif key.startswith('tooltip'):
                                    locator = page.locator(f'[mattooltip="{value}"]')
                                    locator.wait_for(state="visible")
                                    locator.click()

                                # CLICK
                                elif value == 'click':
                                    text_locator = page.get_by_text(f"{key.strip()}", exact=True)
                                    if text_locator.count() > 0:
                                        text_locator.first.click()
                                    else:
                                        fallback = [
                                            page.locator(f'[formcontrolname="{key}"]'),
                                            page.locator(f'[placeholder="{key}"]'),
                                            page.locator(f'[id="{key}"]')
                                        ]
                                        for loc in fallback:
                                            if loc.count() > 0:
                                                loc.first.click()
                                                break

                                # FILE UPLOAD
                                elif value == 'file':
                                    if client == 'NF':
                                        crk_wrk = os.getcwd()
                                        file_path = os.path.join(crk_wrk, key)
                                        page.set_input_files('input[type="file"]', file_path)
                                        per += 10
                                        percen = f"{per}%"

                                    else:
                                        crk_wrk = os.getcwd()
                                        file_path = os.path.join(crk_wrk, key)
                                        # Upload the file using Playwright (click is NOT required)
                                        page.set_input_files('input[type="file"]', file_path)
                                        page.set_input_files('#ecf-inventory-00066', file_path)

                                # LIST / DROPDOWNS
                                elif isinstance(value, list):
                                    for idx, item in enumerate(value):
                                        locator = page.locator(f'[formcontrolname="{key}"]').nth(idx)
                                        locator.wait_for(state="attached")
                                        tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                        if tag_name == 'mat-select':
                                            locator.locator(".mat-mdc-select-trigger").click(force=True)
                                        else:
                                            locator.click()
                                            locator.fill(item)
                                        # select option if exists
                                        options = page.locator("mat-option")
                                        if options.count() > 0:
                                            option = page.locator(f'mat-option >> text="{item}"')
                                            if option.count() > 0:
                                                option.first.click()
                                            else:
                                                options.nth(0).click()

                                # DATE PICKER
                                elif "date" in key.lower() or "dob" in key.lower():
                                    dt = datetime.strptime(value, "%d-%m-%Y")
                                    page.get_by_role("button", name="Open calendar").nth(0).click()
                                    page.locator('.mat-calendar-header').click()
                                    page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                    page.locator(".mat-calendar-body-cell-content",
                                                 has_text=dt.strftime("%b").upper()).click()
                                    page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(0).click()

                                # SCROLL
                                elif key.startswith("scrool"):
                                    page.evaluate("window.scrollBy(0, 100)")

                                # DEFAULT INPUT FIELD
                                else:
                                    all_locators = page.locator(f'[formcontrolname="{key}"]')
                                    for i in range(all_locators.count()):
                                        locator = all_locators.nth(i)
                                        locator.wait_for(state="attached", timeout=3000)
                                        if locator.is_visible():
                                            try:
                                                locator.fill(value)
                                                locator.click()
                                                if page.locator("mat-option").count() > 0:
                                                    page.locator(f'mat-option >> text="{value}"').click()
                                                success_fields.append(key)
                                                break
                                            except:
                                                locator.click()
                                                page.locator(f'mat-option >> text="{value}"').click()
                                                success_fields.append(key)
                                                break

                            except Exception as e:
                                fail_fields.append(key)
                                print(f"❌ Failed field: {key} -> {e}")

                    status = "✓" if not fail_fields else "✗"
                    print(f"{section_key} : {status}")

                # Post-section tasks: screenshot, video, logout
                page.screenshot(path=path)
                video_file_path = page.video.path() if page.video else ""
                print(f"Screenshot saved at: {path}, Video saved at: {video_file_path}")

                # if client == 'NF':
                #     page.get_by_text("person").click()
                #     page.locator("a").filter(has_text="Logout").click()
                #     print("Logged out")

                # Save result in DB
                def save_result():
                    Testcase_Result.objects.create(
                        client_name=client,
                        status='SUCCESS' if not fail_fields else 'Failed',
                        Testcase_Result='Pass' if not fail_fields else 'Fail',
                        created_date=datetime.now(),
                        inputdata=input_str,
                        outputdata=input_data,
                        Testcase_code=testcasecode,
                        screenshoot=path,
                        Module=module,
                        code="NF_ICON_VALUE",  # or whatever you get from page
                        percentage=f"{per}%",
                        video_link=video_file_path
                    )

                Thread(target=save_result).start()


    def nf_vendor_creationlast(self, testcasecode, client):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module
            # url = run.url
            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)
            path = rf"D:\Auomation_Testing\Screenshot\{filename}"
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"], slow_mo=0.5)
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            page.goto("http://13.200.50.27:2000/#/login")

            # page.set_default_timeout(15000)
            # page.set_default_navigation_timeout(30000)

            def flatten_input(data):
                flattened = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        flattened.append(value)
                    elif isinstance(value, list):
                        for subitem in value:
                            flattened.append(subitem)
                return flattened

            for input_data in test_case['data']:
                scenario_name = input_data.get("Testcase_scnarios", "Unnamed")
                merged_steps = flatten_input(input_data)
                print(merged_steps)

                try:
                    for section in merged_steps:
                        for key, value in section.items():
                            def handle_dialog(dialog):
                                print(f"Dialog type: {dialog.type}")  # Should show 'confirm'
                                print(f"Dialog message: {dialog.message}")  # Should show the confirm text
                                dialog.accept()

                            if key.startswith("button"):
                                if value == 'NEXT':
                                    page.get_by_role("button", name=value).click()
                                    page.wait_for_timeout(3000)


                                if (module == 'Vendor' and value != 'NEXT') or value != 'NEXT':
                                    page.once("dialog", lambda dialog: (
                                        print(f"Confirm message: {dialog.message}"),
                                        dialog.accept()))
                                    page.get_by_role("button", name=value, exact=True).click()

                                if value == 'Login' or value == 'Sign in' or value == 'login':
                                    Module_Selection().select_module(page, module,client)
                                if module == 'Vendor' and (value == 'Submit' or value == 'Proceed'):
                                    toast = page.locator(".toast-top-right.toast-container")
                                    message = toast.inner_text()
                                    print(f"✅ Toast message: {message}")
                                else:
                                    message = ""
                            elif key == "tooltip":
                                page.locator('span.fa.fa-arrow-up.mat-mdc-tooltip-trigger').click()
                            elif value == 'click':
                                text_locator = page.get_by_text(f"{key}", exact=True)
                                if text_locator.count() > 0:
                                    text_locator.first.click()
                                else:
                                    form_locator = page.locator(f'[formcontrolname="{key}"]')
                                    placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                    id_locator = page.locator(f'[id="{key}"]')
                                    if form_locator.count() > 0:
                                        form_locator.click()
                                    elif placeholder_locator.count() > 0:
                                        placeholder_locator.click()
                                    elif id_locator.count() > 0:
                                        id_locator.click()
                            elif value == 'file':
                                crk_wrk = os.getcwd()
                                file_path = os.path.join(crk_wrk, key)
                                page.set_input_files('input[type="file"]', file_path)
                            elif isinstance(value, list):
                                for idx, item in enumerate(value):
                                    form_locator = page.locator(f'[formcontrolname="{key}"]')
                                    placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                    id_locator = page.locator(f'[id="{key}"]')
                                    if form_locator.count() > 0:
                                        locator = form_locator.nth(idx)
                                    elif placeholder_locator.count() > 0:
                                        locator = placeholder_locator.nth(idx)
                                    elif id_locator.count() > 0:
                                        locator = placeholder_locator.nth(idx)
                                    locator.wait_for(state="attached")
                                    try:
                                        tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                        if tag_name == 'mat-select':
                                            locator = page.locator(
                                                f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(idx)
                                            locator.scroll_into_view_if_needed()
                                            locator.click(force=True)
                                        else:
                                            locator.click()
                                            locator.fill(item)
                                        options = page.locator("mat-option")
                                        if options.count() > 0:
                                            mat_option = page.locator(f'mat-option >> text="{value}"')
                                            if mat_option.count() > 0:
                                                mat_option.first.click()
                                            else:
                                                options.nth(0).click()
                                    except:
                                        locator.click()
                                        page.locator(f'mat-option >> text="{item}"').click()
                            elif "date" in key.lower() or "dob" in key.lower():
                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                id_locator = page.locator(f'[id="{key}"]')
                                if form_locator.count() > 0:
                                    locator = form_locator
                                elif placeholder_locator.count() > 0:
                                    locator = placeholder_locator
                                elif id_locator.count() > 0:
                                    locator = id_locator
                                locator.wait_for(state="attached")  # Wait until it's in the DOM
                                date_tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                if date_tag_name == 'mat-datepicker-toggle':
                                    locator.get_by_role("button", name="Open calendar").click()
                                else:
                                    page.get_by_role("button", name="Open calendar").nth(0).click()
                                page.locator('.mat-calendar-header').click()
                                dt = datetime.strptime(value, "%d-%m-%Y")
                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.year)).click()
                                page.locator(".mat-calendar-body-cell-content", has_text=dt.strftime("%b").upper()).click()
                                page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(0).click()
                            else:
                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                id_locator = page.locator(f'[id="{key}"]')
                                if form_locator.count() > 0:
                                    locator = form_locator.nth(0)
                                elif placeholder_locator.count() > 0:
                                    locator = placeholder_locator.nth(0)
                                elif id_locator.count() > 0:
                                    locator = id_locator.nth(0)
                                locator.wait_for(state="attached")
                                try:
                                    tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                    if tag_name == 'mat-select':
                                        form_locator = page.locator(f'[formcontrolname="{key}"] .mat-mdc-select-trigger')
                                        placeholder_locator = page.locator(f'[placeholder="{key}"] .mat-mdc-select-trigger')
                                        id_locator = page.locator(f'[id="{key}"] .mat-mdc-select-trigger')
                                        if form_locator.count() > 0:
                                            locator = form_locator.nth(0)
                                        elif placeholder_locator.count() > 0:
                                            locator = placeholder_locator.nth(0)
                                        elif id_locator.count() > 0:
                                            locator = id_locator.nth(0)
                                        locator.scroll_into_view_if_needed()
                                        locator.click(force=True)
                                    else:
                                        locator.fill(value)
                                        locator.click()
                                        # locator.fill(value)
                                    page.wait_for_timeout(3000)
                                    options = page.locator('mat-option')
                                    if options.count() > 0:
                                        mat_option = page.locator(f'mat-option >> text="{value}"')
                                        if mat_option.count() > 0:
                                            mat_option.first.click()
                                        else:
                                            options.nth(0).click()
                                except:
                                    locator.click()
                                    page.locator(f'mat-option >> text="{value}"').click()
                    print('SUCCESS')
                    page.screenshot(path=path)
                    print("screenshot taken")
                    code = page.locator('tbody tr').nth(0).locator('td').nth(1).inner_text()
                    print("First row code:", code)
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()
                        print("Logged out")
                    elif client == 'NAC':
                        page.get_by_text("logout", exact=True).click()

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='SUCCESS',
                            Testcase_Result='Pass',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,
                            Test_scnarios=scenario_name,
                            Module=module,
                            code=code
                        )
                    Thread(target=save_result).start()
                    print("DB saved")
                    print("completed")
                    continue
                    # context.close()
                    # browser.close()
                except Exception as e:
                    page.screenshot(path=path)
                    print("Error in ECF creation:", e)
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()
                    elif client == 'NAC':
                        page.get_by_text("logout", exact=True).click()

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='Failed',
                            Testcase_Result='Fail',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,
                            Test_scnarios=scenario_name,
                            Module=module,
                            remarks=e,

                        )

                    Thread(target=save_result).start()
                    print('tb')
                    continue

    def playwright_test(self, testcasecode,testcase_id,client):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module
            url = run.environment_url
            environment = run.environment
            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path1 = os.path.join(settings.MEDIA_ROOT,filename)
            path = rf"D:\Auomation_Testing\media\{filename}"
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"], slow_mo=1000)
            page.evaluate("document.body.style.zoom='0.9'")
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            page.goto(url)

            def handle_dialog(dialog):
                print(f"Dialog message: {dialog.message}")
                dialog.accept()

            def wait_for_screen_to_load(page):
                try:
                    page.wait_for_selector(".loading-text", timeout=2000)
                    try:
                        page.wait_for_selector(".loading-text", state="detached", timeout=4000)
                    except:
                        page.wait_for_selector(".loading-text", state="hidden", timeout=4000)
                except:
                    print("No loading-text found, or it disappeared too quickly.")

            scenrios_status_dict = {}
            test_ids = ast.literal_eval(testcase_id)

            try:
                for test_id in test_ids:
                    print(f"\n🔁 Running for Testcase ID: {test_id}")

                    def status_update(test_id):
                        Testcase_Result.objects.filter(id=test_id).update(client_name=client, Module=module,
                                                                           status="STARTED")

                    t1 = Thread(target=status_update, args=(test_id,))
                    t1.start()
                    t1.join()

                    for input_data in test_case['data']:
                        print(input_data)
                        scenario_name = input_data.get("Testcase_scnarios", "Unnamed")
                        print(f"\nScenario: {scenario_name}")
                        section_status_dict = {}
                        date = datetime.now().strftime('%Y-%m-%d')
                        safe_module = "".join(c if c.isalnum() or c in " _-" else "_" for c in module)
                        safe_scenario = "".join(c if c.isalnum() or c in " _-" else "_" for c in scenario_name)
                        screenshot_paths = []
                        i = 0
                        for section_key, section_value in input_data.items():
                            if section_key == "Testcase_scnarios":
                                continue

                            fail_fields = []
                            success_fields = []
                            merged_steps = section_value if isinstance(section_value, list) else [section_value]
                            for section in merged_steps:
                                for key, value in section.items():
                                    try:
                                        scenrios_status_dict[scenario_name] = 'Started'
                                        if key.startswith("button"):
                                            page.once("dialog", handle_dialog)
                                            locator = page.get_by_role("button", name=value)
                                            if locator.count() > 0:
                                                btn_type = locator.get_attribute("type")
                                                if btn_type is None or btn_type == "button" or btn_type == 'submit':
                                                    locator.nth(0).click()
                                                    wait_for_screen_to_load(page)
                                                    if client == 'NF' and (module == 'ECF' or module == 'AP'):
                                                        wait_for_screen_to_load(page)
                                            elif locator.count() == 0:
                                                locator = page.locator(f"#{value}")
                                                locator.nth(0).click()
                                                wait_for_screen_to_load(page)
                                                if client == 'NF' and (module == 'ECF' or module == 'AP'):
                                                    wait_for_screen_to_load(page)
                                            # page.wait_for_selector(".spinner", state="hidden")
                                            # page.wait_for_selector(".data-loaded")
                                            if value == 'Login' or value == 'Sign in' or value == 'login':
                                                Module_Selection().select_module(page, module, client)
                                                wait_for_screen_to_load(page)

                                            toast = page.locator(".toast-top-right.toast-container")
                                            toast_count = toast.count()
                                            if toast_count > 0:
                                                message = toast.inner_text()
                                                print(f"✅ Toast message: {message}")


                                            else:
                                                message = ""
                                                print("No toast message visible")
                                        elif key == "tooltip":
                                            page.locator('span.fa.fa-arrow-up.mat-mdc-tooltip-trigger').click()
                                        elif value == "link":
                                            page.locator("a", has_text=f"{key}").click()

                                        elif key == "Add Notes":
                                            print("addnotes")

                                            page.locator("//h3[contains(text(), 'Add Notes')]").click()
                                            page.wait_for_timeout(800)

                                            note_editor = page.locator(".note-editable")
                                            # Ensure it is visible and interactable
                                            note_editor.wait_for(state="visible")

                                            # Click inside and fill the text
                                            note_editor.click()
                                            note_editor.fill(value)


                                        elif value == 'click':
                                            if client == 'NAC' and module == 'Vendor' and key == 'payment':
                                                page.get_by_text(f"{key}", exact=True).nth(i).click()
                                                i += 1
                                            elif client == 'NF' and module == 'AP' and key == 'invdetail-0016':
                                                rows = page.locator('#invdetail-0015 tbody tr')
                                                count = rows.count()
                                                for i in range(count):
                                                    i += i
                                                    page.locator('tbody tr').locator('label:has-text("OK")').nth(
                                                        i).click()
                                            else:
                                                text_locator = page.get_by_text(f"{key}", exact=True)
                                                if text_locator.count() > 0:
                                                    text_locator.first.click()
                                                    wait_for_screen_to_load(page)
                                                else:
                                                    form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                    placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                    id_locator = page.locator(f'[id="{key}"]')
                                                    if form_locator.count() > 0:
                                                        form_locator.click()
                                                    elif placeholder_locator.count() > 0:
                                                        placeholder_locator.click()
                                                    elif id_locator.count() > 0:
                                                        id_locator.click()

                                        elif key == "Add Notes":
                                            print("addnotes")

                                            page.locator("//h3[contains(text(), 'Add Notes')]").click()
                                            page.wait_for_timeout(800)

                                            note_editor = page.locator(".note-editable")
                                            # Ensure it is visible and interactable
                                            note_editor.wait_for(state="visible")

                                            # Click inside and fill the text
                                            note_editor.click()
                                            note_editor.fill(value)


                                        elif value == 'file':
                                            crk_wrk = os.getcwd()
                                            file_path = os.path.join(crk_wrk, key)
                                            page.set_input_files('input[type="file"]', file_path)

                                        elif key.startswith('Horizontal_scroll'):
                                            # page.locator(f"#{value}").scroll_into_view_if_needed()
                                            page.locator(".table-responsive").evaluate(
                                                "el => el.scrollLeft = el.scrollWidth")
                                            page.wait_for_timeout(2000)
                                        elif key.startswith('Vertical_scroll'):
                                            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                            page.wait_for_timeout(2000)
                                        elif isinstance(value, list):
                                            for idx, item in enumerate(value):
                                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                id_locator = page.locator(f'[id="{key}"]')
                                                if form_locator.count() > 0:
                                                    locator = form_locator.nth(idx)
                                                elif placeholder_locator.count() > 0:
                                                    locator = placeholder_locator.nth(idx)
                                                elif id_locator.count() > 0:
                                                    locator = placeholder_locator.nth(idx)
                                                locator.wait_for(state="attached")
                                                try:
                                                    tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                    if tag_name == 'mat-select':
                                                        locator = page.locator(
                                                            f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(
                                                            idx)
                                                        locator.scroll_into_view_if_needed()
                                                        locator.click(force=True)
                                                    else:
                                                        locator.click()
                                                        locator.fill(item)
                                                    options = page.locator("mat-option")
                                                    if options.count() > 0:
                                                        mat_option = page.locator(f'mat-option >> text="{value}"')
                                                        if mat_option.count() > 0:
                                                            mat_option.first.click()
                                                        else:
                                                            options.nth(0).click()
                                                except:
                                                    pass



                                        elif "date" in key.lower() or "dob" in key.lower():
                                            form_locator = page.locator(f'[formcontrolname="{key}"]')
                                            placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                            id_locator = page.locator(f'[id="{key}"]')
                                            if form_locator.count() > 0:
                                                locator = form_locator
                                            elif placeholder_locator.count() > 0:
                                                locator = placeholder_locator
                                            elif id_locator.count() > 0:
                                                locator = id_locator
                                            locator.wait_for(state="attached")  # Wait until it's in the DOM
                                            date_tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                            if date_tag_name == 'mat-datepicker-toggle':
                                                locator.get_by_role("button", name="Open calendar").click()
                                            else:
                                                page.get_by_role("button", name="Open calendar").nth(0).click()
                                            page.locator('.mat-calendar-header').click()
                                            dt = datetime.strptime(value, "%d-%m-%Y")
                                            page.locator(".mat-calendar-body-cell-content",
                                                         has_text=str(dt.year)).click()
                                            page.locator(".mat-calendar-body-cell-content",
                                                         has_text=dt.strftime("%b").upper()).click()
                                            page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(
                                                0).click()
                                        else:
                                            form_locator = page.locator(f'[formcontrolname="{key}"]')
                                            placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                            id_locator = page.locator(f'[id="{key}"]')
                                            if form_locator.count() > 0:
                                                locator = form_locator.nth(0)
                                            elif placeholder_locator.count() > 0:
                                                locator = placeholder_locator.nth(0)
                                            elif id_locator.count() > 0:
                                                locator = id_locator.nth(0)
                                            locator.wait_for(state="attached")
                                            try:
                                                tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                if tag_name == 'mat-select':
                                                    form_locator = page.locator(
                                                        f'[formcontrolname="{key}"] .mat-mdc-select-trigger')
                                                    placeholder_locator = page.locator(
                                                        f'[placeholder="{key}"] .mat-mdc-select-trigger')
                                                    id_locator = page.locator(f'[id="{key}"] .mat-mdc-select-trigger')
                                                    if form_locator.count() > 0:
                                                        locator = form_locator.nth(0)
                                                    elif placeholder_locator.count() > 0:
                                                        locator = placeholder_locator.nth(0)
                                                    elif id_locator.count() > 0:
                                                        locator = id_locator.nth(0)
                                                    locator.scroll_into_view_if_needed()
                                                    locator.click(force=True)
                                                else:
                                                    if module == 'ECF' and client == 'NF':
                                                        locator.click()
                                                        locator.fill(value)
                                                    # elif module == 'ECF' and client == 'NF' and scenario_name == 'ECF_CRN' and key in ['category_code', 'subcategory_code']:
                                                    #     locator.nth(1).click()
                                                    #     locator.fill(value)
                                                    else:
                                                        locator.fill(value)
                                                        locator.click()
                                                    # page.wait_for_timeout(2000)
                                                    # locator.click()
                                                options = page.locator('mat-option')
                                                if options.count() > 0:
                                                    page.wait_for_timeout(2000)
                                                    mat_option = page.locator(f'mat-option >> text="{value}"')
                                                    if mat_option.count() > 0:
                                                        mat_option.first.click()
                                                    else:
                                                        options.nth(0).click()
                                                    success_fields.append(key)
                                            except:
                                                locator.click()
                                                page.locator(f'mat-option >> text="{value}"').click()
                                                success_fields.append(key)
                                        success_fields.append(key)
                                    except Exception as e:
                                        fail_fields.append(key)
                                        break
                            status = "✓" if not fail_fields else "✗"
                            section_status_dict[section_key] = status
                            scenrios_status_dict[scenario_name] = 'Processing'

                            def section_status_update():
                                Testcase_Result.objects.filter(id=test_id).update(
                                    test_implement_status=section_status_dict,
                                    status="Processing",

                                )
                                # Testcase_Run.objects.filter(Testcase_code=testcasecode).update(
                                #     Process_status=scenrios_status_dict, updated_date=datetime.now())

                            Thread(target=section_status_update).start()
                            print(f"{section_key} : {status}")

                        print('SUCCESS')
                        # page.screenshot(path=file_path1)
                        print("screenshot taken")
                        code = page.locator('tbody tr').nth(0).locator('td').nth(1).inner_text()
                        print("First row code:", code)

                        # if client == 'NF':
                        #     page.get_by_text("person").click()
                        #     page.locator("a").filter(has_text="Logout").click()
                        #     print("Logged out")
                        # elif client == 'NAC':
                        #     page.get_by_text("logout", exact=True).click()
                        #
                        # scenrios_status_dict[scenario_name] = 'Success'

                        def save_result():
                            print("entrytab")
                            Testcase_Result.objects.filter(id=test_id).update(
                                client_name=client,
                                status='Success',
                                Testcase_Result='Pass',
                                created_date=datetime.now(),
                                inputdata=input_str,
                                outputdata=input_data,
                                screenshoot=json.dumps(screenshot_paths),
                                code=code,
                                Module=module,

                            )
                            Testcase_Run.objects.filter(Testcase_code=testcasecode).update(status=scenrios_status_dict,
                                                                                           updated_date=datetime.now())

                        t2 = Thread(target=save_result)
                        t2.start()
                        t2.join()
                        print("DB saved")
                        print("completed")
                        continue
            except Exception as e:
                print("Error in ECF creation:", e)
                status = "x"
                print(f"{section_key} : {status}")
                if client == 'NF':
                    page.get_by_text("person").click()
                    page.locator("a").filter(has_text="Logout").click()
                elif client == 'NAC':
                    page.get_by_text("logout", exact=True).click()

                scenrios_status_dict[scenario_name] = 'Failed'

                def save_result():
                    Testcase_Result.objects.create(
                        client_name=client,
                        status='SUCCESS' if not fail_fields else 'Failed',
                        Testcase_Result='Pass' if not fail_fields else 'Fail',
                        created_date=datetime.now(),
                        inputdata=input_str,
                        outputdata=input_data,
                        Testcase_code=testcasecode,
                        screenshoot=path,
                        Module=module,
                        code="NF_ICON_VALUE",  # or whatever you get from page
                        percentage=f"{per}%",
                        video_link=video_file_path


                    )
                    Testcase_Run.objects.filter(Testcase_code=testcasecode).update(status=scenrios_status_dict,
                                                                                   updated_date=datetime.now())

                Thread(target=save_result).start()
                print('tb')
                continue

    def automation_script(self, testcasecode, client,testcase_id):
            test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)

            for run in test_run:
                input_str = run.Testcase_template_input
                module = run.module
                scenario_type=run.scenario_type
                test_case = json.loads(input_str)
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                path1= os.path.join(settings.MEDIA_ROOT, filename)
                video_filename=f"testing_video{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
                video_path = rf"D:\plyvid\{video_filename}"
                playwright = sync_playwright().start()
                browser = playwright.chromium.launch(headless=False, args=["--start-maximized"],slow_mo=900)
                context = browser.new_context(no_viewport=True)
                page = context.new_page()
                page.goto("https://s3.ap-south-1.amazonaws.com/kvb.vsolv.co.in/index.html#/login")

                def handle_dialog(dialog):
                    print(f"Dialog message: {dialog.message}")
                    dialog.accept()

                def wait_for_screen_to_load(page):
                    try:
                        page.wait_for_selector(".loading-text", timeout=2000)
                        try:
                            page.wait_for_selector(".loading-text", state="detached", timeout=3000)
                        except:
                            page.wait_for_selector(".loading-text", state="hidden", timeout=3000)
                    except:
                        print("No loading-text found, or it disappeared too quickly.")

                scenrios_status_dict = {}

                test_ids = ast.literal_eval(testcase_id)

                for test_id in test_ids:
                     print(f"\n🔁 Running for Testcase ID: {test_id}")
                     try:

                                for input_data in test_case['data']:
                                    print(input_data)
                                    scenario_name = input_data.get("Testcase_scnarios", "Unnamed")
                                    print(f"\nScenario: {scenario_name}")
                                    section_status_dict = {}
                                    date = datetime.now().strftime('%Y-%m-%d')
                                    safe_module = "".join(c if c.isalnum() or c in " _-" else "_" for c in module)
                                    safe_scenario = "".join(c if c.isalnum() or c in " _-" else "_" for c in scenario_name)
                                    screenshot_paths = []
                                    i = 0
                                    for section_key, section_value in input_data.items():
                                        if section_key == "Testcase_scnarios":
                                            continue

                                        fail_fields = []
                                        success_fields = []
                                        merged_steps = section_value if isinstance(section_value, list) else [section_value]
                                        for section in merged_steps:
                                            for key, value in section.items():
                                                try:
                                                    scenrios_status_dict[scenario_name] = 'Started'
                                                    if key.startswith("button"):
                                                        # if value == 'NEXT':
                                                        #     page.get_by_role("button", name=value).click()
                                                        # if (module == 'Vendor' and value != 'NEXT') or value != 'NEXT':
                                                        # page.once("dialog", lambda dialog: (
                                                        #     print(f"Confirm message: {dialog.message}"),
                                                        #     dialog.accept()  # or dialog.dismiss()
                                                        # ))
                                                        #     page.get_by_role("button", name=value, exact=True).click()
                                                        page.once("dialog", handle_dialog)
                                                        locator = page.get_by_role("button", name=value)
                                                        if locator.count() > 0:
                                                            btn_type = locator.get_attribute("type")
                                                            if btn_type is None or btn_type == "button" or btn_type == 'submit':
                                                                locator.nth(0).click()
                                                                wait_for_screen_to_load(page)
                                                                if client == 'NF' and (module == 'ECF' or module == 'AP'):
                                                                    wait_for_screen_to_load(page)
                                                        elif locator.count() == 0:
                                                                locator = page.locator(f"#{value}")
                                                                locator.nth(0).click()
                                                                wait_for_screen_to_load(page)
                                                                if client == 'NF' and (module == 'ECF' or module == 'AP'):
                                                                    wait_for_screen_to_load(page)
                                                        # page.wait_for_selector(".spinner", state="hidden")
                                                            # page.wait_for_selector(".data-loaded")
                                                        if value == 'Login' or value == 'Sign in' or value == 'login':
                                                            Module_Selection().select_module(page, module,client)
                                                            wait_for_screen_to_load(page)


                                                        toast = page.locator(".toast-top-right.toast-container")
                                                        toast_count = toast.count()
                                                        if toast_count > 0:
                                                            message = toast.inner_text()
                                                            print(f"✅ Toast message: {message}")
                                                            # page.screenshot(path=file_path)
                                                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                                                            filename = f"screenshot_{timestamp}.png"
                                                            folder_path = os.path.join(settings.MEDIA_ROOT, date,
                                                                                       client, safe_module,
                                                                                       safe_scenario)
                                                            os.makedirs(folder_path, exist_ok=True)
                                                            file_path = os.path.join(folder_path, filename)
                                                            page.screenshot(path=file_path)
                                                            relative_path = os.path.relpath(file_path,
                                                                                            settings.MEDIA_ROOT).replace(
                                                                "\\", "/")
                                                            screenshot_paths.append(relative_path)
                                                        else:
                                                            message = ""
                                                            print("No toast message visible")

                                                        # toast = page.locator(".toast-top-right.toast-container")
                                                        # toast_count = toast.count()
                                                        # if toast_count > 0:
                                                        #     message = toast.inner_text()
                                                        #     print(f"✅ Toast message: {message}")
                                                        #     page.screenshot(path=path1)
                                                        #     timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                                                        #     filename = f"screenshot_{timestamp}.png"
                                                        #
                                                        # else:
                                                        #     message = ""
                                                        #     print("No toast message visible")

                                                    elif key == "tooltip":
                                                        page.locator('span.fa.fa-arrow-up.mat-mdc-tooltip-trigger').click()
                                                    elif value == "product":
                                                        field = page.locator("//input[@formcontrolname='description']")
                                                        field.click()
                                                        field.fill("product")
                                                    elif value == "popup":
                                                        page.locator(
                                                            "xpath=/html/body/app-root/body/div[1]/div[2]/app-ecfap/div[1]/div[2]/app-invoice-detail/section/div[22]/div/div/div[2]/div[2]/button[2]").click()

                                                    elif value == "link":
                                                        page.locator("a", has_text=f"{key}").click()
                                                    elif key == "case":
                                                        page.locator(
                                                            "xpath=/html/body/app-root/body/div[1]/div[2]/app-ecfap/div[1]/div[2]/app-create-ecf/div[8]/div/div/div[3]/button[1]").click()

                                                    elif key == "Add Notes":
                                                        # Click the Add Notes section
                                                        page.locator("//h3[contains(text(), 'Add Notes')]").click()
                                                        page.wait_for_timeout(800)
                                                        # Wait for the note editor to appear
                                                        note_editor = page.locator(".note-editable")
                                                        # Ensure it is visible and interactable
                                                        note_editor.wait_for(state="visible")

                                                        # Click inside and fill the text
                                                        note_editor.click()
                                                        note_editor.fill(value)

                                                    elif value == 'click':
                                                        if client == 'NAC' and module == 'Vendor' and key == 'payment':
                                                            page.get_by_text(f"{key}", exact=True).nth(i).click()
                                                            i += 1
                                                        elif client == 'NF' and module == 'AP' and key == 'invdetail-0016':
                                                            rows = page.locator('#invdetail-0015 tbody tr')
                                                            count = rows.count()
                                                            for i in range(count):
                                                                i += i
                                                                page.locator('tbody tr').locator('label:has-text("OK")').nth(i).click()
                                                        else:
                                                            text_locator = page.get_by_text(f"{key}", exact=True)
                                                            if text_locator.count() > 0:
                                                                text_locator.first.click()
                                                                wait_for_screen_to_load(page)
                                                            else:
                                                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                                id_locator = page.locator(f'[id="{key}"]')
                                                                if form_locator.count() > 0:
                                                                    form_locator.click()
                                                                elif placeholder_locator.count() > 0:
                                                                    placeholder_locator.click()
                                                                elif id_locator.count() > 0:
                                                                    id_locator.click()
                                                    elif value == 'file':
                                                        crk_wrk = os.getcwd()
                                                        file_path = os.path.join(crk_wrk, key)
                                                        page.set_input_files('input[type="file"]', file_path)


                                                    elif value == "file-type-invoice":
                                                        crk_wrk = os.getcwd()
                                                        file_path = os.path.join(crk_wrk, key)
                                                        with page.expect_file_chooser() as fc_info:
                                                            page.locator(f'#{value}').click()
                                                        file_chooser = fc_info.value
                                                        file_chooser.set_files(file_path)

                                                    elif key.startswith('Horizontal_scroll'):
                                                        # page.locator(f"#{value}").scroll_into_view_if_needed()
                                                        page.evaluate("window.scrollBy(300, 600)")
                                                        # page.locator(".table-responsive").evaluate("el => el.scrollLeft = el.scrollWidth")
                                                        page.wait_for_timeout(2000)

                                                    elif key.startswith('Vertical_scroll'):
                                                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                                        page.wait_for_timeout(2000)

                                                    elif isinstance(value, list):
                                                        for idx, item in enumerate(value):
                                                            form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                            placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                            id_locator = page.locator(f'[id="{key}"]')
                                                            if form_locator.count() > 0:
                                                                locator = form_locator.nth(idx)
                                                            elif placeholder_locator.count() > 0:
                                                                locator = placeholder_locator.nth(idx)
                                                            elif id_locator.count() > 0:
                                                                locator = placeholder_locator.nth(idx)
                                                            locator.wait_for(state="attached")
                                                            try:
                                                                tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                                if tag_name == 'mat-select':
                                                                    locator = page.locator(f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(idx)
                                                                    locator.scroll_into_view_if_needed()
                                                                    locator.click(force=True)
                                                                else:
                                                                    locator.click()
                                                                    locator.fill(item)
                                                                options = page.locator("mat-option")
                                                                if options.count() > 0:
                                                                    mat_option = page.locator(f'mat-option >> text="{value}"')
                                                                    if mat_option.count() > 0:
                                                                        mat_option.first.click()
                                                                    else:
                                                                        options.nth(0).click()
                                                            except:
                                                                pass
                                                    elif "date" in key.lower() or "dob" in key.lower():
                                                        try:
                                                            page.keyboard.press("Escape")
                                                            page.wait_for_timeout(200)
                                                            locators = [
                                                                page.locator(f'[formcontrolname="{key}"]'),
                                                                page.locator(f'[id="{key}"]'),
                                                                page.locator(f'[name="{key}"]'),
                                                                page.locator(f'input[placeholder*="{key.split("_")[-1]}"]',
                                                                             has_text=None)
                                                            ]
                                                            locator = None
                                                            for candidate in locators:
                                                                if candidate.count() > 0:
                                                                    locator = candidate.first
                                                                    break

                                                            if not locator:
                                                                print(f"[!] Could not find date input for '{key}' — skipping.")
                                                                continue

                                                            locator.scroll_into_view_if_needed()
                                                            locator.click(force=True)
                                                            page.wait_for_timeout(300)
                                                            date_container = locator.locator("xpath=ancestor::mat-form-field")
                                                            toggle_button = date_container.locator(
                                                                "button[aria-label='Open calendar'], button[title='Open calendar']"
                                                            )

                                                            if toggle_button.count() > 0:
                                                                toggle_button.first.click(force=True)
                                                            else:
                                                                print(
                                                                    f"[!] No datepicker toggle found for {key}, filling manually.")
                                                                locator.fill(value)
                                                                continue

                                                            page.wait_for_timeout(500)

                                                            dt = datetime.strptime(value, "%d-%m-%Y")
                                                            page.locator(".mat-calendar-header").click()
                                                            page.locator(".mat-calendar-body-cell-content",
                                                                         has_text=str(dt.year)).click()
                                                            page.locator(".mat-calendar-body-cell-content",
                                                                         has_text=dt.strftime("%b").upper()).click()
                                                            page.locator(".mat-calendar-body-cell-content",
                                                                         has_text=str(dt.day)).first.click()
                                                            page.wait_for_timeout(300)

                                                            print(f"[+] Selected date for {key}: {value}")

                                                        except Exception as e:
                                                            print(f"[X] Failed to select date for {key}: {e}")

                                                    else:
                                                        form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                        placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                        id_locator = page.locator(f'[id="{key}"]')
                                                        if form_locator.count() > 0:
                                                            locator = form_locator.nth(0)
                                                        elif placeholder_locator.count() > 0:
                                                            locator = placeholder_locator.nth(0)
                                                        elif id_locator.count() > 0:
                                                            locator = id_locator.nth(0)
                                                        locator.wait_for(state="attached")
                                                        try:
                                                            tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                            if tag_name == 'mat-select':
                                                                form_locator = page.locator(f'[formcontrolname="{key}"] .mat-mdc-select-trigger')
                                                                placeholder_locator = page.locator(f'[placeholder="{key}"] .mat-mdc-select-trigger')
                                                                id_locator = page.locator(f'[id="{key}"] .mat-mdc-select-trigger')
                                                                if form_locator.count() > 0:
                                                                    locator = form_locator.nth(0)
                                                                elif placeholder_locator.count() > 0:
                                                                    locator = placeholder_locator.nth(0)
                                                                elif id_locator.count() > 0:
                                                                    locator = id_locator.nth(0)
                                                                locator.scroll_into_view_if_needed()
                                                                locator.click(force=True)
                                                            else:
                                                                if module == 'ECF' and client == 'NF':
                                                                    locator.click()
                                                                    locator.fill(value)

                                                                else:
                                                                    locator.fill(value)
                                                                    page.wait_for_timeout(800)
                                                                    locator.click()
                                                                page.wait_for_timeout(1000)
                                                                locator.click()
                                                            options = page.locator('mat-option')
                                                            if options.count() > 0:
                                                                page.wait_for_timeout(2000)
                                                                mat_option = page.locator(f'mat-option >> text="{value}"')
                                                                # page.keyboard.type(value, delay=20)
                                                                mat_option = page.locator(f'//mat-option[contains(.,"{value}")]')
                                                                if mat_option.count() > 0:
                                                                    mat_option.click()
                                                                else:
                                                                    options.nth(0).click()
                                                                    # page.locator(f'//mat-option[contains(.,"{value}")]')
                                                                    page.locator("mat-option").click()

                                                                success_fields.append(key)
                                                        except:
                                                            locator.click()
                                                            locator.fill(value)
                                                            # page.keyboard.type(value, delay=20)
                                                            # page.locator(f'//mat-option[contains(.,"{value}")]').click()
                                                            page.locator(f'mat-option >> text="{value}"').click()
                                                            success_fields.append(key)

                                                    success_fields.append(key)
                                                except:
                                                    print(
                                                        f"❌ Field '{key}' failed to fill or click properly — stopping scenario execution.")

                                                    # Mark all remaining sections as ✗
                                                    remaining_sections = list(input_data.keys())[
                                                                         list(input_data.keys()).index(
                                                                             section_key) + 1:]
                                                    for rem_sec in remaining_sections:
                                                        if rem_sec != "Testcase_scnarios":
                                                            print(f"{rem_sec} : ✗")
                                                            section_status_dict[rem_sec] = "✗"

                                                    # Stop scenario execution immediately
                                                    raise Exception(
                                                        f"Field '{key}' failed to fill — Scenario '{scenario_name}' stopped.")
                                                    break


                                        status = "✓" if not fail_fields else "✗"
                                        print(f"{section_key} : {status}")
                                        section_status_dict[section_key] = status
                                        scenrios_status_dict[scenario_name]='Processing'
                                        print(f"{section_key} : {status}")

                                print('SUCCESS')
                                page.screenshot(path=path1)
                                print("screenshot taken")
                                code = page.locator('tbody tr').nth(0).locator('td').nth(1).inner_text()
                                print("First row code:", code)

                                if client == 'NF':
                                    page.get_by_text("person").click()
                                    page.locator("a").filter(has_text="Logout").click()
                                    print("Logged out")
                                elif client == 'NAC':
                                    page.get_by_text("logout", exact=True).click()
                                elif client =="KVB":
                                    page.get_by_text("logout", exact=True).click()

                                scenrios_status_dict[scenario_name] = 'Success'

                                def save_result():
                                    print("entrytab")
                                    print("entered")
                                    Testcase_Result.objects.create(
                                        client_name=client,
                                        status='Success',
                                        Testcase_Result='Pass',
                                        created_date=datetime.now(),
                                        inputdata=input_data,
                                        outputdata=input_data,
                                        screenshoot=path1,
                                        code = code,
                                        Module=module,
                                        video_link=video_path,
                                        remarks="All fields completed",
                                        Testcase_code=testcasecode,
                                        test_implement_status=scenrios_status_dict,
                                        Test_scnarios=scenario_name,
                                        scenario_type=scenario_type
                                    )
                                Thread(target=save_result).start()
                                print("DB saved")
                                print("completed"
                                      )


                     except Exception as e:
                                print("Error in ECF creation:", e)
                                status = "x"
                                if fail_fields:
                                    scenrios_status_dict[scenario_name] = 'Failed'
                                    print(f"❌ Failed at section: {section_key}, fields: {fail_fields}")
                                print(f"{section_key} : {status}")
                                page.screenshot(path=path1)
                                print("Screenshot taken on failure")
                                # video_file_path = page.video.path()
                                # print(f"Recorded video path: {video_file_path}")
                                if client == 'NF':
                                    page.get_by_text("person").click()
                                    page.locator("a").filter(has_text="Logout").click()
                                    print("Logged out")
                                elif client == 'NAC':
                                    page.get_by_text("logout", exact=True).click()
                                    print("Logged out")
                                elif client == "KVB":
                                    page.get_by_text("logout", exact=True).click()
                                    print("Logged out")

                                def save_result1():
                                    Testcase_Result.objects.create(
                                        client_name=client,
                                        status='Failed',
                                        Testcase_Result='Fail',
                                        created_date=datetime.now(),
                                        inputdata=input_str,
                                        outputdata=input_data,
                                        Testcase_code=testcasecode,
                                        screenshoot=path1,
                                        Test_scnarios=scenario_name,
                                        Module=module,
                                        remarks=e,
                                        scenario_type=scenario_type,
                                        test_implement_status=scenrios_status_dict
                                    )
                                Thread(target=save_result1).start()
                                print('tb')
                                print("failed")
                                continue



    def nf_vendor_creationtre3(self, testcasecode, client):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        test_result=Testcase_Result.objects.create(client_name=client,Testcase_code=testcasecode)

        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module
            id = run.id

            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)

            video_filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
            file_path1 = os.path.join(settings.MEDIA_ROOT, filename)

            # path = rf"D:\Auomation_Testing\Screenshot\{filename}"
            path = rf"D:\pfffimage\{filename}"
            video_path = rf"D:\plyvid\{video_filename}"
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"], slow_mo=0.5)
            # context = browser.new_context(no_viewport=True)
            context = browser.new_context(
                no_viewport=True,
                record_video_dir=video_path,
                record_video_size={"width": 1280, "height": 720}  # optional
            )

            page = context.new_page()
            # page.goto("http://192.168.5.4:4201/#/login")
            # page.goto("http://13.200.50.27:2000/#/login")
            page.goto("http://3.108.200.134:9089/#login")

            for input_data in test_case['data']:
                scenario_name = input_data.get("Testcase_scnarios", "Unnamed")

                print(f"\nScenario: {scenario_name}")
                percentage = ""
                try:
                    for section_key, section_value in input_data.items():
                        if section_key == "Testcase_scnarios":
                            continue
                        fail_fields = []
                        success_fields = []
                        per = 0
                        merged_steps = section_value if isinstance(section_value, list) else [section_value]

                        for section in merged_steps:
                            for key, value in section.items():
                                try:
                                    per += 10
                                    percen = f"{per}%"

                                    if key.startswith("button"):
                                        try:
                                            page.get_by_role("button", name=value).click()
                                        except:
                                            page.get_by_text(value, exact=True).click()

                                        page.wait_for_timeout(3000)
                                        if value == 'Login' or value == "Sign in":
                                            Module_Selection().select_module(page, module, client)
                                    # elif key=="has_text":
                                    #     page.locator('span', has_text=value).click()
                                    # elif key=="mat-icon":
                                    #     page.locator("mat-icon", has_text=value).click()

                                    elif key == "ecf-inventory-00071":
                                        page.locator('button#ecf-inventory-00071.btn.btn-light').click()
                                    elif key == "ecf-inventory-00135":
                                        page.locator("#ecf-inventory-00135").click()


                                    elif key == "choosetype":
                                        page.locator(f"text={value}").click()

                                    elif key == "radiobutton":
                                        if value == "Yes":
                                            page.locator('mat-radio-button:has-text("Yes")').click()
                                        else:
                                            page.locator('mat-radio-button:has-text("No")').click()
                                    elif key.startswith('tooltip'):
                                        locator = page.locator(f'[mattooltip="{value}"]')
                                        locator.wait_for(state="visible")
                                        locator.click()
                                        success_fields.append(key)
                                        # page.locator(f'span.fa.fa-arrow-up[mattooltip="{key}"]').click()

                                    elif value == 'click':
                                        text_locator = page.get_by_text(f"{key.strip()}", exact=True)
                                        if text_locator.count() > 0:
                                            text_locator.first.click()
                                        else:
                                            form_locator = page.locator(f'[formcontrolname="{key}"]')
                                            placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                            id_locator = page.locator(f'[id="{key}"]')
                                            if form_locator.count() > 0:
                                                form_locator.click()
                                            elif placeholder_locator.count() > 0:
                                                placeholder_locator.click()
                                            elif id_locator.count() > 0:
                                                id_locator.click()

                                    elif value == 'file':
                                        if client == 'NF':
                                            crk_wrk = os.getcwd()
                                            file_path = os.path.join(crk_wrk, key)
                                            page.set_input_files('input[type="file"]', file_path)
                                            per += 10
                                            percen = f"{per}%"

                                        else:
                                            crk_wrk = os.getcwd()
                                            file_path = os.path.join(crk_wrk, key)
                                            # Upload the file using Playwright (click is NOT required)
                                            page.set_input_files('input[type="file"]', file_path)
                                            page.set_input_files('#ecf-inventory-00066', file_path)

                                    elif isinstance(value, list):
                                        for idx, item in enumerate(value):
                                            form_locator = page.locator(f'[formcontrolname="{key}"]')
                                            placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                            id_locator = page.locator(f'[id="{key}"]')
                                            if form_locator.count() > 0:
                                                locator = form_locator.nth(idx)
                                            elif placeholder_locator.count() > 0:
                                                locator = placeholder_locator.nth(idx)
                                            elif id_locator.count() > 0:
                                                locator = placeholder_locator.nth(idx)
                                            locator.wait_for(state="attached")

                                            try:
                                                tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                if tag_name == 'mat-select':
                                                    locator = page.locator(
                                                        f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(idx)
                                                    locator.scroll_into_view_if_needed()
                                                    locator.click(force=True)
                                                else:
                                                    locator.click()
                                                    locator.fill(item)
                                                options = page.locator("mat-option")
                                                if options.count() > 0:
                                                    mat_option = page.locator(f'mat-option >> text="{value}"')
                                                    if mat_option.count() > 0:
                                                        mat_option.first.click()
                                                    else:
                                                        options.nth(0).click()
                                            except:
                                                locator.click()
                                                page.locator(f'mat-option >> text="{item}"').click()
                                    elif key.startswith("scrool"):
                                        if value == "vertical":
                                            page.evaluate("window.scrollBy(0, 100)")
                                        else:
                                            # page.evaluate("window.scrollBy(500, 0)")
                                            locator = page.locator(
                                                'xpath=/html/body/app-root/body/div[1]/div[2]/app-ecf/div[1]/mat-card/div[1]/app-ecf-inventory/div[1]/div/mat-card/div/div[2]/div/form/div/tr/td/button[1]')
                                            locator.scroll_into_view_if_needed()
                                            pixel = page.evaluate("window.pageYOffset")


                                    elif "date" in key.lower() or "dob" in key.lower():

                                        if client == "NAC":
                                            calendar_btn = page.get_by_role("button", name="Open calendar").nth(1)
                                            calendar_btn.wait_for(state="visible")
                                            calendar_btn.click()
                                            page.locator('.mat-calendar-header').click()
                                            dt = datetime.strptime(value, "%d-%m-%Y")
                                            page.locator(".mat-calendar-body-cell-content",
                                                         has_text=str(dt.year)).click()
                                            page.locator(".mat-calendar-body-cell-content",
                                                         has_text=dt.strftime("%b").upper()).click()
                                            page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(
                                                0).click()
                                            per += 10
                                            percen = f"{per}%"

                                        else:
                                            form_locator = page.locator(f'[formcontrolname="{key}"]')
                                            placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                            id_locator = page.locator(f'[id="{key}"]')
                                            if form_locator.count() > 0:
                                                locator = form_locator
                                            elif placeholder_locator.count() > 0:
                                                locator = placeholder_locator
                                            elif id_locator.count() > 0:
                                                locator = id_locator
                                            locator.wait_for(state="attached")  # Wait until it's in the DOM
                                            date_tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                            if date_tag_name == 'mat-datepicker-toggle':
                                                locator.get_by_role("button", name="Open calendar").click()
                                            else:
                                                page.get_by_role("button", name="Open calendar").nth(0).click()
                                            page.locator('.mat-calendar-header').click()
                                            dt = datetime.strptime(value, "%d-%m-%Y")
                                            page.locator(".mat-calendar-body-cell-content",
                                                         has_text=str(dt.year)).click()
                                            page.locator(".mat-calendar-body-cell-content",
                                                         has_text=dt.strftime("%b").upper()).click()
                                            page.locator(".mat-calendar-body-cell-content", has_text=str(dt.day)).nth(
                                                0).click()
                                            per += 10
                                            percen = f"{per}%"
                                    else:
                                        all_locators = page.locator(f'[formcontrolname="{key}"]')
                                        count = all_locators.count()

                                        for i in range(count):
                                            locator = all_locators.nth(i)

                                            locator.wait_for(state="attached", timeout=3000)
                                            if locator.is_visible():
                                                try:
                                                    locator.fill(value)
                                                    locator.click()
                                                    page.wait_for_timeout(2000)
                                                    if page.locator("mat-option").count() > 0:
                                                        page.locator(f'mat-option >> text="{value}"').click()
                                                        success_fields.append(key)
                                                        per += 10
                                                        percen = f"{per}%"
                                                except:
                                                    locator.click()
                                                    page.locator(f'mat-option >> text="{value}"').click()
                                                    page.wait_for_timeout(2000)
                                                    success_fields.append(key)
                                                    per += 10
                                                    percen = f"{per}%"
                                                break  # Stop after successfully filling visible locator
                                        else:
                                            locator = page.locator(f'[formcontrolname="{key}"]').nth(0)
                                            locator.wait_for(state="attached")
                                            try:
                                                locator.fill(value)
                                                locator.click()
                                                page.wait_for_timeout(3000)
                                                if page.locator("mat-option").count() > 0:
                                                    page.locator(f'mat-option >> text="{value}"').click()
                                                    per += 10
                                                    percen = f"{per}%"
                                                    success_fields.append(key)
                                            except:
                                                locator.click()
                                                page.locator(f'mat-option >> text="{value}"').click()
                                                per += 10
                                                percen = f"{per}%"
                                                success_fields.append(key)
                                                page.wait_for_timeout(2000)

                                        success_fields.append(key)
                                except Exception as e:
                                    fail_fields.append(key)

                        status = "✓" if not fail_fields else "✗"
                        print(f"{section_key} : {status}")
                        # if fail_fields:
                        #     print(f"  Failed Fields: {fail_fields}")
                    value = page.locator("span.nf_icon").first.text_content()
                    print(value)
                    print('SUCCESS')
                    video_file_path = page.video.path()
                    print(f"Recorded video path: {video_file_path}")
                    page.screenshot(path=path)
                    print("screenshot taken")
                    # percentage.append(percen)
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()
                        print("Logged out")

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='SUCCESS',
                            Testcase_Result='Pass',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,

                            Module=module,
                            code=value,
                            percentage=percen,
                            video_link=video_file_path
                        )
                    Thread(target=save_result).start()
                    print("DB saved")
                    print("completed")


                except Exception as e:
                    print("Error in ECF creation:", e)
                    status = "x"
                    print(f"{section_key} : {status}")
                    if fail_fields:
                        print(f"  Failed Fields: {fail_fields}")
                    page.screenshot(path=path)
                    print("Screenshot taken on failure")
                    video_file_path = page.video.path()
                    print(f"Recorded video path: {video_file_path}")
                    if client == 'NF':
                        page.get_by_text("person").click()
                        page.locator("a").filter(has_text="Logout").click()

                    def save_result():
                        Testcase_Result.objects.create(
                            client_name=client,
                            status='Failed',
                            Testcase_Result='Fail',
                            created_date=datetime.now(),
                            inputdata=input_str,
                            outputdata=input_data,
                            Testcase_code=testcasecode,
                            screenshoot=path,
                            Test_scnarios=scenario_name,
                            Module=module,
                            remarks=e,
                            percentage=percen,
                            video_link=video_file_path
                        )

                    Thread(target=save_result).start()
                    print('tb')
                continue

























    def process_summary(self,test_id):
            testcase_code = Testcase_Result.objects.get(id=test_id)
            data = {
                'Testcase_code': testcase_code.test_implement_status,
                'status': testcase_code.status,
            }
            return data


    def get_scnario_name(self, request, testcasecode):
        try:
            # 1. First check if entries already exist in Testcase_Result
            existing_results = Testcase_Result.objects.filter(Testcase_code=testcasecode,status='Yet to start')

            if existing_results.exists():
                # Return existing entries
                existing_data = [
                    {
                        "id": result.id,
                        "Testcase_code": result.Testcase_code,
                        "Test_scnarios": result.Test_scnarios,
                        "test_implement_status":result.test_implement_status,
                        "status":result.status
                    }
                    for result in existing_results
                ]
                return {"data": existing_data}

            # 2. If not exist, fetch the testcase from Testcase_Run
            testcase_code_obj = Testcase_Run.objects.filter(Testcase_code=testcasecode).first()

            if not testcase_code_obj:
                return {"error": "Testcase code not found."}

            parsed_data = json.loads(testcase_code_obj.Testcase_template_input)
            scenarios = [item['Testcase_scnarios'] for item in parsed_data.get('data', [])]

            created_entries = []
            for scenario in scenarios:
                result_obj = Testcase_Result.objects.create(
                    Testcase_code=testcasecode,
                    Test_scnarios=scenario,
                    status="Yet to start" ,
                    test_implement_status="Yet to start"# Optional default status
                )
                created_entries.append({
                    "id": result_obj.id,
                    "Testcase_code": result_obj.Testcase_code,
                    "Test_scnarios": result_obj.Test_scnarios,
                    "status":result_obj.status,
                    "test_implement_status":result_obj.test_implement_status

                })

            return {"data": created_entries}

        except Exception as e:
            return {"error": str(e)}

    def dropdown_teastcasecode(self,request, clientname,module,environment):

        code=Testcase_Run.objects.filter(module=module,clientname=clientname,environment=environment)
        testcode=[]

        for i in code:
            case=i.Testcase_code
            testcode.append(case)
        return testcode

    def automation_script2(self, testcasecode, client, testcase_id):
        test_run = Testcase_Run.objects.filter(Testcase_code=testcasecode)
        for run in test_run:
            input_str = run.Testcase_template_input
            module = run.module
            scenario_type = run.scenario_type
            test_case = json.loads(input_str)
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            path1 = os.path.join(settings.MEDIA_ROOT, filename)
            video_filename = f"testing_video{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
            video_path = rf"D:\plyvid\{video_filename}"
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=False, args=["--start-maximized"], slow_mo=900)
            context = browser.new_context(no_viewport=True)
            page = context.new_page()
            page.goto("https://s3.ap-south-1.amazonaws.com/kvb.vsolv.co.in/index.html#/login")

            def handle_dialog(dialog):
                print(f"Dialog message: {dialog.message}")
                dialog.accept()

            def wait_for_screen_to_load(page):
                try:
                    page.wait_for_selector(".loading-text", timeout=2000)
                    try:
                        page.wait_for_selector(".loading-text", state="detached", timeout=3000)
                    except:
                        page.wait_for_selector(".loading-text", state="hidden", timeout=3000)
                except:
                    print("No loading-text found, or it disappeared too quickly.")

            scenrios_status_dict = {}

            test_ids = ast.literal_eval(testcase_id)
            fail_fields = []
            success_fields = []

            for test_id in test_ids:
                    print(f"\n🔁 Running for Testcase ID: {test_id}")
                    try:

                        def status_update(test_id):
                            print(test_ids)
                            Testcase_Result.objects.filter(id=test_id).update(client_name=client, Module=module,
                                                                               status="STARTED")

                        t1 = Thread(target=status_update, args=(test_id,))
                        t1.start()
                        t1.join()

                        for input_data in test_case['data']:
                                    print(input_data)
                                    scenario_name = input_data.get("Testcase_scnarios", "Unnamed")
                                    print(f"\nScenario: {scenario_name}")
                                    section_status_dict = {}
                                    date = datetime.now().strftime('%Y-%m-%d')
                                    safe_module = "".join(c if c.isalnum() or c in " _-" else "_" for c in module)
                                    safe_scenario = "".join(c if c.isalnum() or c in " _-" else "_" for c in scenario_name)
                                    screenshot_paths = []

                                    for section_key, section_value in input_data.items():
                                        if section_key == "Testcase_scnarios":
                                            continue
                                        merged_steps = section_value if isinstance(section_value, list) else [section_value]
                                        for section in merged_steps:
                                            for key, value in section.items():
                                                try:
                                                    scenrios_status_dict[scenario_name] = 'Started'
                                                    if key.startswith("button"):
                                                        page.once("dialog", handle_dialog)
                                                        locator = page.get_by_role("button", name=value)
                                                        if locator.count() > 0:
                                                            btn_type = locator.get_attribute("type")
                                                            if btn_type is None or btn_type == "button" or btn_type == 'submit':
                                                                locator.nth(0).click()
                                                                wait_for_screen_to_load(page)
                                                                if client == 'NF' and (module == 'ECF' or module == 'AP'):
                                                                    wait_for_screen_to_load(page)
                                                        elif locator.count() == 0:
                                                            locator = page.locator(f"#{value}")
                                                            locator.nth(0).click()
                                                            wait_for_screen_to_load(page)
                                                            if client == 'NF' and (module == 'ECF' or module == 'AP'):
                                                                wait_for_screen_to_load(page)
                                                        # page.wait_for_selector(".spinner", state="hidden")
                                                        # page.wait_for_selector(".data-loaded")
                                                        if value == 'Login' or value == 'Sign in' or value == 'login':
                                                            Module_Selection().select_module(page, module, client)
                                                            wait_for_screen_to_load(page)

                                                        toast = page.locator(".toast-top-right.toast-container")
                                                        toast_count = toast.count()
                                                        if toast_count > 0:
                                                            message = toast.inner_text()
                                                            print(f" Toast message: {message}")
                                                            page.screenshot(path=file_path)
                                                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                                                            filename = f"screenshot_{timestamp}.png"
                                                            folder_path = os.path.join(settings.MEDIA_ROOT, date,
                                                                                       client, safe_module,
                                                                                       safe_scenario)
                                                            os.makedirs(folder_path, exist_ok=True)
                                                            file_path = os.path.join(folder_path, filename)
                                                            page.screenshot(path=file_path)
                                                            relative_path = os.path.relpath(file_path,
                                                                                            settings.MEDIA_ROOT).replace(
                                                                "\\", "/")
                                                            screenshot_paths.append(relative_path)
                                                        else:
                                                            message = ""
                                                            print("No toast message visible")

                                                    # elif key=="tab":
                                                    #     if value==" JV Maker Summary ":
                                                    #         page.locator("/html/body/app-root/body/div[1]/div[2]/app-jv/div[1]/mat-card/nav/div/span[1]").click()
                                                    #     else:
                                                    #         page.locator("/html/body/app-root/body/div[1]/div[2]/app-jv/div[1]/mat-card/nav/div/span[2]").click()

                                                    elif key == "tooltip":
                                                        page.locator('span.fa.fa-arrow-up.mat-mdc-tooltip-trigger').click()
                                                    elif value == "product":
                                                        field = page.locator("//input[@formcontrolname='description']")
                                                        field.click()
                                                        field.fill("product")
                                                    elif value == "popup-yes":
                                                        page.locator(
                                                            "xpath=/html/body/app-root/body/div[1]/div[2]/app-ecfap/div[1]/div[2]/app-invoice-detail/section/div[22]/div/div/div[2]/div[2]/button[2]").click()
                                                    elif value=="popup-yes":
                                                        page.locator(
                                                            "xpath=/html/body/app-root/body/div[1]/div[2]/app-ecfap/div[1]/div[2]/app-invoice-detail/section/div[22]/div/div/div[2]/div[2]/button[1]").click()

                                                    elif value == "link":
                                                        page.locator("a", has_text=f"{key}").click()
                                                    elif key == "case":
                                                        page.locator(
                                                            "xpath=/html/body/app-root/body/div[1]/div[2]/app-ecfap/div[1]/div[2]/app-create-ecf/div[8]/div/div/div[3]/button[1]").click()

                                                    elif key == "Add Notes":
                                                        # Click the Add Notes section
                                                        page.locator("//h3[contains(text(), 'Add Notes')]").click()
                                                        page.wait_for_timeout(800)
                                                        # Wait for the note editor to appear
                                                        note_editor = page.locator(".note-editable")
                                                        # Ensure it is visible and interactable
                                                        note_editor.wait_for(state="visible")

                                                        # Click inside and fill the text
                                                        note_editor.click()
                                                        note_editor.fill(value)

                                                    elif value == 'click':
                                                        if client == 'NAC' and module == 'Vendor' and key == 'payment':
                                                            page.get_by_text(f"{key}", exact=True).nth(i).click()
                                                            i += 1
                                                        elif client == 'NF' and module == 'AP' and key == 'invdetail-0016':
                                                            rows = page.locator('#invdetail-0015 tbody tr')
                                                            count = rows.count()
                                                            for i in range(count):
                                                                i += i
                                                                page.locator('tbody tr').locator('label:has-text("OK")').nth(
                                                                    i).click()
                                                        else:
                                                            text_locator = page.get_by_text(f"{key}", exact=True)
                                                            if text_locator.count() > 0:
                                                                text_locator.first.click()
                                                                wait_for_screen_to_load(page)
                                                            else:
                                                                form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                                placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                                id_locator = page.locator(f'[id="{key}"]')
                                                                if form_locator.count() > 0:
                                                                    form_locator.click()
                                                                elif placeholder_locator.count() > 0:
                                                                    placeholder_locator.click()
                                                                elif id_locator.count() > 0:
                                                                    id_locator.click()
                                                    elif value == 'file':
                                                        crk_wrk = os.getcwd()
                                                        file_path = os.path.join(crk_wrk, key)
                                                        page.set_input_files('input[type="file"]', file_path)


                                                    elif value == "file-type-invoice":
                                                        crk_wrk = os.getcwd()
                                                        file_path = os.path.join(crk_wrk, key)
                                                        with page.expect_file_chooser() as fc_info:
                                                            page.locator(f'#{value}').click()
                                                        file_chooser = fc_info.value
                                                        file_chooser.set_files(file_path)

                                                    elif key.startswith('Horizontal_scroll'):
                                                        # page.locator(f"#{value}").scroll_into_view_if_needed()
                                                        page.evaluate("window.scrollBy(300, 600)")
                                                        # page.locator(".table-responsive").evaluate("el => el.scrollLeft = el.scrollWidth")
                                                        page.wait_for_timeout(2000)

                                                    elif key.startswith('Vertical_scroll'):
                                                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                                        page.wait_for_timeout(2000)

                                                    elif isinstance(value, list):
                                                        for idx, item in enumerate(value):
                                                            form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                            placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                            id_locator = page.locator(f'[id="{key}"]')
                                                            if form_locator.count() > 0:
                                                                locator = form_locator.nth(idx)
                                                            elif placeholder_locator.count() > 0:
                                                                locator = placeholder_locator.nth(idx)
                                                            elif id_locator.count() > 0:
                                                                locator = placeholder_locator.nth(idx)
                                                            locator.wait_for(state="attached")
                                                            try:
                                                                tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                                if tag_name == 'mat-select':
                                                                    locator = page.locator(
                                                                        f'[formcontrolname="{key}"] .mat-mdc-select-trigger').nth(
                                                                        idx)
                                                                    locator.scroll_into_view_if_needed()
                                                                    locator.click(force=True)
                                                                else:
                                                                    locator.click()
                                                                    locator.fill(item)
                                                                options = page.locator("mat-option")
                                                                if options.count() > 0:
                                                                    mat_option = page.locator(f'mat-option >> text="{value}"')
                                                                    if mat_option.count() > 0:
                                                                        mat_option.first.click()
                                                                    else:
                                                                        options.nth(0).click()
                                                            except:
                                                                pass
                                                    elif "date" in key.lower() or "dob" in key.lower():
                                                        try:
                                                            page.keyboard.press("Escape")
                                                            page.wait_for_timeout(200)
                                                            locators = [
                                                                page.locator(f'[formcontrolname="{key}"]'),
                                                                page.locator(f'[id="{key}"]'),
                                                                page.locator(f'[name="{key}"]'),
                                                                page.locator(f'input[placeholder*="{key.split("_")[-1]}"]',
                                                                             has_text=None)
                                                            ]
                                                            locator = None
                                                            for candidate in locators:
                                                                if candidate.count() > 0:
                                                                    locator = candidate.first
                                                                    break

                                                            if not locator:
                                                                print(f"[!] Could not find date input for '{key}' — skipping.")
                                                                continue

                                                            locator.scroll_into_view_if_needed()
                                                            locator.click(force=True)
                                                            page.wait_for_timeout(300)
                                                            date_container = locator.locator("xpath=ancestor::mat-form-field")
                                                            toggle_button = date_container.locator(
                                                                "button[aria-label='Open calendar'], button[title='Open calendar']"
                                                            )

                                                            if toggle_button.count() > 0:
                                                                toggle_button.first.click(force=True)
                                                            else:
                                                                print(
                                                                    f"[!] No datepicker toggle found for {key}, filling manually.")
                                                                locator.fill(value)
                                                                continue

                                                            page.wait_for_timeout(500)

                                                            dt = datetime.strptime(value, "%d-%m-%Y")
                                                            page.locator(".mat-calendar-header").click()
                                                            page.locator(".mat-calendar-body-cell-content",
                                                                         has_text=str(dt.year)).click()
                                                            page.locator(".mat-calendar-body-cell-content",
                                                                         has_text=dt.strftime("%b").upper()).click()
                                                            page.locator(".mat-calendar-body-cell-content",
                                                                         has_text=str(dt.day)).first.click()
                                                            page.wait_for_timeout(300)

                                                            print(f"[+] Selected date for {key}: {value}")

                                                        except Exception as e:
                                                            print(f"[X] Failed to select date for {key}: {e}")

                                                    else:
                                                        form_locator = page.locator(f'[formcontrolname="{key}"]')
                                                        placeholder_locator = page.locator(f'[placeholder="{key}"]')
                                                        id_locator = page.locator(f'[id="{key}"]')
                                                        if form_locator.count() > 0:
                                                            locator = form_locator.nth(0)
                                                        elif placeholder_locator.count() > 0:
                                                            locator = placeholder_locator.nth(0)
                                                        elif id_locator.count() > 0:
                                                            locator = id_locator.nth(0)
                                                        locator.wait_for(state="attached")
                                                        try:
                                                            tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                                                            if tag_name == 'mat-select':
                                                                form_locator = page.locator(
                                                                    f'[formcontrolname="{key}"] .mat-mdc-select-trigger')
                                                                placeholder_locator = page.locator(
                                                                    f'[placeholder="{key}"] .mat-mdc-select-trigger')
                                                                id_locator = page.locator(f'[id="{key}"] .mat-mdc-select-trigger')
                                                                if form_locator.count() > 0:
                                                                    locator = form_locator.nth(0)
                                                                elif placeholder_locator.count() > 0:
                                                                    locator = placeholder_locator.nth(0)
                                                                elif id_locator.count() > 0:
                                                                    locator = id_locator.nth(0)
                                                                locator.scroll_into_view_if_needed()
                                                                locator.click(force=True)
                                                            else:
                                                                if module == 'ECF' and client == 'NF':
                                                                    locator.click()
                                                                    locator.fill(value)

                                                                else:
                                                                    locator.fill(value)
                                                                    page.wait_for_timeout(800)
                                                                    locator.click()
                                                                page.wait_for_timeout(1000)
                                                                locator.click()
                                                            options = page.locator('mat-option')
                                                            if options.count() > 0:
                                                                page.wait_for_timeout(2000)
                                                                mat_option = page.locator(f'mat-option >> text="{value}"')
                                                                # page.keyboard.type(value, delay=20)
                                                                mat_option = page.locator(f'//mat-option[contains(.,"{value}")]')
                                                                if mat_option.count() > 0:
                                                                    mat_option.click()
                                                                else:
                                                                    options.nth(0).click()
                                                                    # page.locator(f'//mat-option[contains(.,"{value}")]')
                                                                    page.locator("mat-option").click()

                                                                success_fields.append(key)
                                                        except:
                                                            locator.click()
                                                            locator.fill(value)
                                                            # page.keyboard.type(value, delay=20)
                                                            # page.locator(f'//mat-option[contains(.,"{value}")]').click()
                                                            page.locator(f'mat-option >> text="{value}"').click()
                                                            success_fields.append(key)

                                                    success_fields.append(key)
                                                except:
                                                    fail_fields.append(key)

                                                    print(
                                                        f"❌ Field '{key}' failed to fill or click properly — stopping scenario execution.")

                                                    # Mark all remaining sections as ✗
                                                    remaining_sections = list(input_data.keys())[
                                                                         list(input_data.keys()).index(
                                                                             section_key) + 1:]
                                                    for rem_sec in remaining_sections:
                                                        if rem_sec != "Testcase_scnarios":
                                                            print(f"{rem_sec} : ✗")
                                                            section_status_dict[rem_sec] = "✗"

                                                    # Stop scenario execution immediately
                                                    raise Exception(
                                                        f"Field '{key}' failed to fill — Scenario '{scenario_name}' stopped.")
                                                    break

                                    status = "✓" if not fail_fields else "✗"
                                    print(f"{section_key} : {status}")
                                    section_status_dict[section_key] = status
                                    scenrios_status_dict[scenario_name] = 'Processing'


                        print('SUCCESS')
                        page.screenshot(path=path1)
                        print("screenshot taken")
                        code = page.locator('tbody tr').nth(0).locator('td').nth(1).inner_text()
                        print("First row code:", code)

                        if client == 'NF':
                            page.get_by_text("person").click()
                            page.locator("a").filter(has_text="Logout").click()
                            print("Logged out")
                        elif client == 'NAC':
                            page.get_by_text("logout", exact=True).click()
                        elif client == "KVB":
                            page.get_by_text("logout", exact=True).click()

                        scenrios_status_dict[scenario_name] = 'Success'

                        def save_result():
                            print("sucess")
                            Testcase_Result.objects.filter(id=test_id).update(
                                client_name=client,
                                status='sucess',
                                Testcase_Result='sucess',
                                created_date=datetime.now(),
                                inputdata=input_data,
                                outputdata=input_data,
                                # screenshoot=file_path,
                                # screenshoot=json.dumps(screenshot_paths),
                                screenshoot=path1,
                                Module=module,
                                scenario_type=scenario_name,
                                videolink=video_path
                            )
                            Testcase_Run.objects.filter(Testcase_code=testcasecode).update(
                                test_implement_status=scenrios_status_dict, updated_date=datetime.now())

                        Thread(target=save_result).start()
                        print("db inserted")
                        print('tb')
                        test_case['data'].remove(input_data)


                    except Exception as e:
                            print("Error in ECF creation:", e)
                            error_message = str(e)
                            status = "x"
                            if fail_fields:
                                scenrios_status_dict[scenario_name] = 'Failed'
                                print(f"❌ Failed at section: {section_key}, fields: {fail_fields}")
                            print(f"{section_key} : {status}")
                            page.screenshot(path=path1)
                            print("Screenshot taken on failure")
                            # video_file_path = page.video.path()
                            # print(f"Recorded video path: {video_file_path}")
                            if client == 'NF':
                                page.get_by_text("person").click()
                                page.locator("a").filter(has_text="Logout").click()
                                print("Logged out")
                            elif client == 'NAC':
                                page.get_by_text("logout", exact=True).click()
                                print("Logged out")
                            elif client == "KVB":
                                page.get_by_text("logout", exact=True).click()
                                print("Logged out")

                            def save_result():
                                Testcase_Result.objects.filter(id=test_id).update(
                                    client_name=client,
                                    status='Failed',
                                    Testcase_Result='Fail',
                                    created_date=datetime.now(),
                                    inputdata=input_data,
                                    outputdata=input_data,
                                    # screenshoot=file_path,
                                    # screenshoot=json.dumps(screenshot_paths),
                                    screenshoot=path1,
                                    Module=module,
                                    remarks=error_message,
                                    videolink=video_path
                                )
                                Testcase_Run.objects.filter(Testcase_code=testcasecode).update(test_implement_status=scenrios_status_dict,
                                                                                               updated_date=datetime.now())
                            Thread(target=save_result).start()
                            print('tb')
                            print("tb inserted")
                            test_case['data'].remove(input_data)
                            # continue




class Report:
    from django.template.loader import render_to_string
    from django.http import HttpResponse
    from weasyprint import HTML
    import pandas as pd
    # def test_report_pdf(request, clientnme,fromdate,todate,module):
    #     import base64
    #     # Step 1: Query data
    #     condition = Q()
    #     if clientnme is not None:
    #         condition=Q(client_name=clientnme)
    #     if fromdate is not None:
    #         condition=Q(created_date=fromdate)
    #     if todate is not None:
    #         condition = Q(created_date=todate)
    #     if module is not None:
    #         condition = Q(Module=module)
    #
    #     records = Testcase_Result.objects.filter(condition).values(
    #         'client_name', 'status', 'screenshoot', 'Testcase_Result', 'inputdata', 'outputdata', 'Testcase_code',
    #         'created_date','Test_scnarios',"video_link"
    #     )
    #     data_set = []
    #     for rec in records:
    #         with open(rec['screenshoot'], "rb") as image_file:
    #             rec['base64_image'] = base64.b64encode(image_file.read()).decode('utf-8')
    #             data_set.append(rec)
    #
    #     # Step 2: Render HTML template with data
    #     html = render_to_string('reporttest.html', {
    #         'client_name': clientnme,
    #         'records': data_set,
    #
    #     })
    #
    #     pdf_file = HTML(string=html).write_pdf()
    #     # Step 4: Return PDF as response
    #     response = HttpResponse(pdf_file, content_type='application/pdf')
    #     return response
    #     response['Content-Disposition'] = f'attachment; filename="{clientnme}_test_report.pdf"'

    def test_report_pdf(request, clientnme, fromdate, todate, module,testcasecode):
        # Step 1: Build query condition
        condition = Q()
        if clientnme:
            condition &= Q(client_name=clientnme)
        if fromdate:
            condition &= Q(created_date=fromdate)
        if todate:
            condition &= Q(created_date=todate)
        if module:
            condition &= Q(Module=module)

        if testcasecode:
            condition &=Q(Testcase_code=testcasecode)

        records = Testcase_Result.objects.filter(condition).values(
            'client_name', 'status', 'screenshoot', 'Testcase_Result',
            'inputdata', 'outputdata', 'Testcase_code', 'created_date',
            'Test_scnarios', 'videolink','remarks'
        )

        data_set = []
        for rec in records:
            raw_path = rec.get('screenshoot')

            # ----------- 🎯 FIX STARTS HERE -------------
            # Handle screenshoot path datatype issues
            if isinstance(raw_path, list) and raw_path:
                screenshot_path = raw_path[0]  # extract first item
            elif isinstance(raw_path, str):
                screenshot_path = raw_path
            else:
                screenshot_path = None  # invalid or missing
            # ----------- 🎯 FIX ENDS HERE -------------

            # Validate screenshot path
            if screenshot_path:
                # If path is relative, convert with MEDIA_ROOT
                if not os.path.isabs(screenshot_path):
                    screenshot_path = os.path.join(settings.MEDIA_ROOT, screenshot_path)

                # Check file exists
                if os.path.exists(screenshot_path):
                    try:
                        with open(screenshot_path, "rb") as image_file:
                            base64_img = base64.b64encode(image_file.read()).decode('utf-8')
                        rec['base64_image'] = base64_img
                    except Exception:
                        rec['base64_image'] = None
                else:
                    rec['base64_image'] = None
            else:
                rec['base64_image'] = None

            data_set.append(rec)

            # Step 2: Render HTML template
        html = render_to_string('reporttest.html', {
            'client_name': clientnme,
            'records': data_set,
        })

        # Step 3: Generate PDF
        pdf_file = HTML(string=html).write_pdf()

        # Step 4: Return PDF response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{clientnme}_test_report.pdf"'
        return response

        # for rec in records:
        #     screenshot_path = rec['screenshoot']
        #
        #     # Handle relative path from MEDIA_ROOT
        #     if not os.path.isabs(screenshot_path):
        #         screenshot_path = os.path.join(settings.MEDIA_ROOT, screenshot_path)
        #
        #     if os.path.exists(screenshot_path):
        #         with open(screenshot_path, "rb") as image_file:
        #             rec['base64_image'] = base64.b64encode(image_file.read()).decode('utf-8')
        #     else:
        #         rec['base64_image'] = None  # handle missing image gracefully
        #
        #     data_set.append(rec)
        #
        # # Step 2: Render HTML template
        # html = render_to_string('reporttest.html', {
        #     'client_name': clientnme,
        #     'records': data_set,
        # })
        #
        # # Step 3: Generate PDF
        # # pdf_file = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
        # pdf_file = HTML(string=html).write_pdf()
        #
        # # Step 4: Return PDF as response
        # response = HttpResponse(pdf_file, content_type='application/pdf')
        # response['Content-Disposition'] = f'attachment; filename="{clientnme}_test_report.pdf"'
        # return response