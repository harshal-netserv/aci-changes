from __future__ import absolute_import
from mysite.globals import *
import subprocess
import requests
import re, json
import os
from django.conf import settings
from django.db.models import Q
from mysite.nlead_library.service_now import *
from django.utils import timezone

if not settings.configured:
    settings.configure('mysite', DEBUG=True)

try:
    from mysite.models import CustomerDB, CronDB, ACIInterfaceStatusDB, ACI_Change_Request_DB
    from mysite.models import template_db
    from mysite.models import SetupParameters
    from django.contrib.auth.models import Group, User
    from mysite.models import UserProfile
    from mysite.nlead_library.aci_api_functions import *
except ValueError:
    print "Need to figure it out"


def get_work_order_list(service):
    change_req_list = []
    # one_h_ago = timezone.now() - timezone.timedelta(hours=6)
    query = ACI_Change_Request_DB.objects.filter(state='Authorised', services=service).values(
        'change_request_no').all()
    if query:
        print query
        for req_no in query:
            change_req_list.append(req_no['change_request_no'])
    return change_req_list

class ACI_Inputs:

    def __init__(self, service, port_type, action, pre_response={}):
        servicenow = ServiceNowRequest('admin', 'vqfQxF3KqB7X')
        response_data = []
        response_data.append(
            {"default1": service, "name": "apic_services", "type": "hidden", "desc": "Service"})
        response_data.append(
            {"default1": action, "name": "action", "type": "hidden", "desc": "Action"})
        response_data.append(
            {"default1": port_type, "name": "port_type", "type": "hidden", "desc": "Port Type"})
        if service == 'Port Configuration':
                                                                    # ]})
            prereserved_ports = ['Eth 1/45', 'Eth 1/46', 'Eth 1/47', 'Eth 1/48']
            leaf_options = []
            port_options = []
            # /home/netserv/Webapp/Netserv/mysite/Json_DATA/198.18.133.200.json
            apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
            leaf_list = apic_auth.get_leaf_list()
            leaf_count = 0
            for ele in leaf_list:
                leaf_count +=1
                model_num = apic_auth.get_model_no(ele["name"])
                print model_num
                dict1 = {'send': "yes"}
                dict1["label"] = "LCAWDCP-01-01-0" + str(leaf_count) + " [ " + ele["name"] + " ]" + " [ " + model_num + " ]"
                dict1["value"] = ele["name"]
                leaf_options.append(dict1)
            # with open('/home/netserv/Webapp_Latest/netserv/mysite/Json_DATA/' + '198.18.133.200' + '.json') as ip_json_data:
            #     ip_data = json.load(ip_json_data)
            #     # print ip_data
            #     # l_opt = sorted(ip_data.items(), key=lambda kv: kv[1])
            #     for k, v in ip_data.iteritems():
            #         dict1 = {'send': "yes"}
            #         dict1["label"] = "LCAWDCP-01-01-" + k + " [ " + v["id"] + "-" + v["type"] + " ]"
            #         dict1["value"] = v["id"]
            #         leaf_options.append(dict1)
            if action == "Reservation" :
                # inp1 = {}
                # # inp1["type"] = 'line'
                # # inp1["label"] = 'Actions Required :'
                # # response_data["inputs"].append(inp1)
                # inp1 = {"name": "template", "send": "yes", "format": "default1", "desc": "template_id",
                #         "default1": pre_response.get("template"), "type": "hidden"}
                # response_data.append(inp1)

                inp1 = {"name": "work_order_no", "send": "yes", "format": "default1", "desc": "Work Order Number",
                        "length": "full",
                        "default1": "", "mandatory": "yes", 'example': "Ex: CHG0000001", "type": "text", }
                if pre_response.has_key("work_order_no"):
                    inp1['default1'] = pre_response.get("work_order_no")
                    response_data.append(inp1)
                else:
                    print " Here 112233", pre_response.get('service_now_check')
                    if pre_response.get('service_now_check') == "yes":
                        get_data = get_work_order_list("ACI")
                        print " Here 11223344"
                        options1 = [{'label': "Select Number", 'value': ''}]
                        for d_tct in get_data:
                            dict22 = {}
                            dict22['label'] = d_tct
                            dict22['value'] = d_tct
                            dict22['send'] = "yes"
                            dict22['hide'] = "hide"
                            options1.append(dict22)
                        inp1 = {"name": "work_order_no", "send": "yes", "format": "default1",
                                "desc": "Work Order Number", "length": "full", "options": options1,
                                "default1": "", "mandatory": "yes", 'example': "Ex: CHG0000001",
                                "type": "dropdown-autocomplete"}
                        response_data.append(inp1)
                        inp1 = {"name": "service_now_check", "desc": "Work Order Number",
                                "length": "full", "default1": pre_response.get('service_now_check'), "type": "hidden"}
                        response_data.append(inp1)
                    else:
                        response_data.append(inp1)
                # response_data.append(inp1)

                

                inp1 = {"name": "provision_reason", "format": "default1", "desc": "Provision Reason",
                        "length": "full",  # "condition": "other",#"trigger": ["other_reservation_reason"]
                        "default1": "Add New Database Server", "type": "hidden",  # "hide": "hide",
                        'options': [{"value": "Add New Dtabase server", "label": "Add New Dtabase server"},
                                    {"value": "Add New server", "label": "Add New server"},
                                    {"value": "Port change", "label": "Port change"},
                                    {"value": "other", "label": "Other"}]}

                if pre_response['service_now_check'] == 'no':
                    inp1['type'] = "dropdown"
                if pre_response.has_key("provision_reason"):
                    inp1['default1'] = pre_response.get("provision_reason")
                    response_data.append(inp1)
                else:
                    response_data.append(inp1)

                inp1 = {"name": "other_reservation_reason", "send": "", "format": "default1", "desc": "Other Reason",
                        "length": "full", "hide": "hide",
                        "default1": "", "type": "text", }
                # if pre_response.has_key("other_reservation_reason"):
                #     inp1['default1'] = pre_response.get("other_reservation_reason")
                #     response_data.append(inp1)
                # else:
                #     response_data.append(inp1)

                inp1 = {"name": "rack_row_number", "send": "yes", "format": "default1", "desc": "Rack Row Number",
                        "length": "full",
                        "default1": "01", "type": "hidden",
                        "options": [{"value": "01", 'send': 'yes', "label": "R-01 "},
                                    {"value": "02", 'send': 'yes', "label": "R-02", },
                                    {"value": "03", 'send': 'yes', "label": "R-03"},
                                    {"value": "04", 'send': 'yes', "label": "R-04 "},
                                    {"value": "05", 'send': 'yes', "label": "R-05", },
                                    {"value": "06", 'send': 'yes', "label": "R-06"},
                                    {"value": "07", 'send': 'yes', "label": "R-07 "},
                                    {"value": "08", 'send': 'yes', "label": "R-08", },
                                    {"value": "09", 'send': 'yes', "label": "R-09"},
                                    {"value": "10", 'send': 'yes', "label": "R-10 "},
                                    {"value": "11", 'send': 'yes', "label": "R-11", },
                                    {"value": "12", 'send': 'yes', "label": "R-12"}
                                    ]}
                if pre_response.has_key("rack_row_number"):
                    inp1['default1'] = pre_response.get("rack_row_number")
                    response_data.append(inp1)
                else:
                    response_data.append(inp1)
                rack_options = [{'value': u'R-01-01', 'send': 'yes', 'label': u'R-01-01'},
                                {'value': u'R-01-02', 'send': 'yes', 'label': u'R-01-02'},
                                {'value': u'R-01-03', 'send': 'yes', 'label': u'R-01-03'},
                                {'value': u'R-01-06', 'send': 'yes', 'label': u'R-01-06'},
                                {'value': u'R-01-07', 'send': 'yes', 'label': u'R-01-07'},
                                {'value': u'R-01-04', 'send': 'yes', 'label': u'R-01-04'},
                                {'value': u'R-01-05', 'send': 'yes', 'label': u'R-01-05'},
                                {'value': u'R-01-08', 'send': 'yes', 'label': u'R-01-08'},
                                {'value': u'R-01-09', 'send': 'yes', 'label': u'R-01-09'},
                                {'value': u'R-01-10', 'send': 'yes', 'label': u'R-01-10'},
                                {'value': u'R-01-11', 'send': 'yes', 'label': u'R-01-11'},
                                {'value': u'R-01-12', 'send': 'yes', 'label': u'R-01-12'}, ]
                inp1 = {"name": "rack_number", "send": "yes", "format": "default1", "desc": "Rack Number",
                        "length": "full",
                        "default1": "R-01-01", "type": "hidden", "options": rack_options}
                if pre_response.has_key("rack_number"):
                    inp1['default1'] = pre_response.get("rack_number")
                    response_data.append(inp1)
                else:
                    response_data.append(inp1)

                inp1 = {"name": "leaf_id", "send": "yes", "format": "default1", "desc": "Leaf Switches",
                        "length": "full", 'mandatory': 'yes',
                        "type": "dropdown-checkbox", 'options': leaf_options}
                if pre_response.has_key("leaf_id"):
                    inp1['default1'] = pre_response.get("leaf_id")
                    response_data.append(inp1)
                else:
                    response_data.append(inp1)

                # inp1 = {"name": "physical_port", "send": "yes", "format": "default1", "desc": "Leaf-1 Physical Port",
                #         "default1": "", "type": "dropdown-checkbox", 'options': port_options}
                # response_data["inputs"].append(inp1)

                # inp1 = {"name": "leaf_2_interface", "send": "yes", "format": "default1", "desc": "Leaf-2 Interface",
                #         "default1": "", "type": "dropdown", 'options': "", }
                # response_data["inputs"].append(inp1)

                # inp1 = {"name": "physical_port", "send": "yes", "format": "default1", "desc": "Physical Port",
                #         "default1": "", "type": "text",}
                # response_data["inputs"].append(inp1)
                if pre_response.has_key('description'):
                    
                    inp1 = {"name": "description", "send": "yes", "format": "default1", "desc": "Description (Optional)",
                            "length": "full",
                            "default1": "", "mandatory": "no", 'example': "", "type": "text", }
                    if pre_response.has_key("work_order_no"):
                        inp1['default1'] = pre_response.get("description")
                        response_data.append(inp1)
                    else:
                        response_data.append(inp1)
                else:
                    inp1 = {"name": "description", "send": "yes", "format": "default1", "desc": "Description",
                            "length": "full",
                            "default1": "", "mandatory": "no", 'example': "", "type": "text", }
                    if pre_response.has_key("work_order_no"):
                        inp1['default1'] = ""
                        response_data.append(inp1)
                    else:
                        response_data.append(inp1)
                
                server_options = [{'value': u'S-01-01-01', 'send': 'yes', 'label': u'S-01-01-01'},
                                  {'value': u'S-01-01-02', 'send': 'yes', 'label': u'S-01-01-02'},
                                  {'value': u'S-01-01-03', 'send': 'yes', 'label': u'S-01-01-03'},
                                  {'value': u'S-01-01-04', 'send': 'yes', 'label': u'S-01-01-04'},
                                  {'value': u'S-01-01-05', 'send': 'yes', 'label': u'S-01-01-05'},
                                  {'value': u'S-01-01-06', 'send': 'yes', 'label': u'S-01-01-06'},
                                  {'value': u'S-01-01-07', 'send': 'yes', 'label': u'S-01-01-07'},
                                  {'value': u'S-01-01-08', 'send': 'yes', 'label': u'S-01-01-08'},
                                  {'value': u'S-01-01-09', 'send': 'yes', 'label': u'S-01-01-09'},
                                  {'value': u'S-01-01-10', 'send': 'yes', 'label': u'S-01-01-10'},
                                  {'value': u'S-01-01-11', 'send': 'yes', 'label': u'S-01-01-11'},
                                  {'value': u'S-01-01-12', 'send': 'yes', 'label': u'S-01-01-12'}, ]
                inp1 = {"name": "server_name", "send": "", "format": "default1", "desc": "Server Name (Optional)",
                        "length": "full",
                        "default1": "S-01-01-01", "type": "hidden", "options": server_options}
                if pre_response['service_now_check'] == 'no':
                    inp1['type'] = "dropdown"
                if pre_response.has_key("server_name"):
                    inp1['default1'] = pre_response.get("server_name")
                    response_data.append(inp1)
                else:
                    response_data.append(inp1)

                inp1 = {"name": "temporary_port_reservation", "format": "default1",
                        "desc": "Temporary port reservation ?",
                        "length": "full",
                        "default1": "yes", "type": "hidden", 'options': [
                        {"value": "yes", "label": "Yes", "hide": "hide", "trigger": ["reservation_duration"]},
                        {"value": "no", "label": "No", }]}

                response_data.append(inp1)

                inp1 = {"name": "reservation_duration", "format": "", "default1": "", "output": "", "type": "hidden",
                        "example": "(Optional)", "desc": "Reservation Duration", "length": "full", "mandatory": "no",
                        "hide": "hide",
                        "options": [{"value": "1month", "label": "1 Month"},
                                    {"value": "3month", "label": "3 Month"},
                                    {"value": "6month", "label": "6 Month"},
                                    {"value": "1year", "label": "1 Year"}]}

                response_data.append(inp1)

                # apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                # policy_list = apic_auth.list_policygroups()
                # print policy_list
                # policy_options = []
                # if policy_list:
                #     for i in policy_list:
                #         if i:
                #             dict1 = {}
                #             dict1["label"] = i
                #             dict1["value"] = i
                #             policy_options.append(dict1)
                inp1 = {"note": "", "default1": "", "name": "policy_grp",
                        "type": "hidden", "desc": "Policy Group", 'options': []}

                response_data.append(inp1)

                inp1 = {"name": "admin_state", "send": "yes", "format": "default1", "desc": "Admin Status",
                        "length": "full",
                        "default1": "disable", "type": "radio", 'options': [{"value": "disable", "label": "Shutdown"},
                                                                            {"value": "enable",
                                                                             "label": "No Shutdown", }]}
                response_data.append(inp1)
                # request.session['input_response_data'] = response_data
                # return HttpResponse(json.dumps(response_data), content_type="application/json")

            elif action == 'Provision' and port_type == 'Physical':
                print " In Provision !.... "
                work_order_list = []
                query = ACIInterfaceStatusDB.objects.filter(status__in=["Reservation", "reserve"]).values(
                    'work_order_no').all()
                if query:
                    print query
                    for dct in query:
                        if dct["work_order_no"] not in work_order_list:
                            work_order_list.append(dct["work_order_no"])
                wo_options = []
                for each in work_order_list:
                    dict1 = {"send": "yes", "hide": "hide"}
                    dict1["label"] = each
                    dict1["value"] = each
                    wo_options.append(dict1)
                inp1 = {"name": "work_order_no", "send": "yes", "format": "default1", "desc": "Work Order Number",
                        "length": "full",
                        "default1": "", "type": "text", 'options': ""}
                response_data.append(inp1)
                

                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                tenant_list = apic_auth.get_all_tenant()
                # print tenant_list
                tenant_options = []
                if tenant_list:
                    for i in tenant_list:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            tenant_options.append(dict1)
                response_data.append({"type": 'line', "label": 'ACI Options', 'border': 'yes'})

                inp1 = {"name": "tenant_name", "format": "default1", "desc": "Tenant Name",
                        "length": "full", "send": "yes",
                        "default1": "", "type": "dropdown",
                        "options": tenant_options}
                response_data.append(inp1)
                # inp1 = {"name": "port_media_type", "send": "yes", "format": "default1", "desc": "Port Type","length":"full",
                #         "default1": "fibre", "type": "radio", 'options': [{"value": "fibre", "label": "Fibre"},
                #                                                              {"value": "coper","label": "Coper", }]}
                # response_data["inputs"].append(inp1)
                db_leaf_list = []
                db_ports_list = []
                # try:
                query2 = ACIInterfaceStatusDB.objects.filter(status__in=["Reservation", "reserve"],
                                                             work_order_no=work_order_list).values('leaf_id',
                                                                                                   'physical_port').all()
                # except:
                #     return render(request, 'notification.html',
                #                   {'output_list': "No leaf and ports reserved for provision", "count": "1",
                #                    'class': 'alert-danger'})

                if query2:
                    # print query2
                    for dct in query2:
                        if dct["leaf_id"] not in db_leaf_list:
                            db_leaf_list.append(dct["leaf_id"])
                        if dct["physical_port"] not in db_ports_list:
                            db_ports_list.append(dct["physical_port"])

                for cst in db_leaf_list:
                    for opt in leaf_options:
                        if opt.get("value") == cst:
                            opt["selected"] = "yes"
                inp1 = {"name": "leaf_id", "send": "yes", "format": "default1", "desc": "Leaf Names", "length": "full",
                        "default1": "", "type": "dropdown-checkbox", 'options': leaf_options}
                if pre_response.has_key("leaf_id"):
                    inp1['default1'] = pre_response.get("leaf_id")
                    response_data.append(inp1)
                else:
                    response_data.append(inp1)
                
                
                count = 1
                # db_ports_list=[db_ports_list[0]]
                for cst in db_leaf_list:
                    port_options = []
                    for each in db_ports_list:
                        dict1 = {}
                        dict1["label"] = each.title()
                        dict1["value"] = each
                        port_options.append(dict1)
                    inp1 = {"name": "physical_port" + str(count), "send": "yes", "length": "full",
                            "desc": "Leaf " + cst + " Physical Port", "type": "dropdown-checkbox",
                            'options': port_options}
                    count += 1
                    response_data.append(inp1)

                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                policy_list = apic_auth.list_policygroups()
                # print policy_list
                policy_options = []
                if policy_list:
                    for i in policy_list:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            policy_options.append(dict1)
                inp1 = {"note": "", "default1": "", "name": "policy_grp",
                        "type": "dropdown", "desc": "Policy Group", 'options': policy_options}

                response_data.append(inp1)

                inp1 = {"name": "port_mode", "format": "default1", "desc": "Port Mode",
                        "length": "full", "default1": "access", "type": "radio","send":"yes",
                        'options': [{"value": "untagged", "label": "Access", 'send': 'yes'},
                                    {"value": "regular", "label": "Trunk", 'send': 'yes'}]}
                response_data.append(inp1)
                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                app = apic_auth.apps_profile(tenant_list[0])
                print 'application ',app
                epg_bd = apic_auth.get_epg_bd(tenant_list[0],app[0])
                print epg_bd            
                epg_list = epg_bd['epg']
                bd_list = epg_bd['bd']
                vlan_options = []
                count = 1
                for i in range(len(epg_bd['epg'])):
                    dict1 = {}
                    dict1['value'] = "12"+str(count)+"-"+epg_list[i]+"-"+bd_list[i]
                    dict1['label'] = "12"+str(count)+" [EPG: "+epg_list[i]+", BD: "+bd_list[i]+"]"
                    vlan_options.append(dict1)
                inp1 = {"name": "vlan_id", "send": "yes", "format": "default1", "desc": "VLAN ID",
                        "length": "full", "default1": "", "type": "dropdown",
                        'options':vlan_options }
                response_data.append(inp1)
                
                inp1 = {"name": "application", "send": "yes", "format": "default1", "desc": "VLAN ID",
                        "length": "full", "default1": app[0], "type": "hidden",}
                            # [
                            # {"value": "101", "label": "101 [EPG: Prod-EPG-1, BD: Prod-BD-1]"},
                            # {"value": "102", "label": "102 [EPG: Prod-EPG-2, BD: Prod-BD-2]"}]}
                response_data.append(inp1)

                inp1 = {"name": "speed", "send": "yes", "format": "default1", "desc": "Physical Port Speed",
                        "length": "full", "default1": "inherit", "type": "hidden",
                        'options': [{"value": "inherit", "label": "Auto"}, {"value": "10G", "label": "10G"},
                                    {"value": "1G", "label": "1G"}]}
                response_data.append(inp1)

                # inp1 = {"name": "discovery_protocol", "send": "", "format": "default1", "desc": "Discovery Protocol",
                #         "length": "full", "default1": "LLPD", "type": "radio",
                #         'options': [{"value": "LLDP", "label": "LLDP"},
                #                     {"value": "CDP", "label": "CDP"}, {"value": "None", "label": "None"},]}

                # response_data.append(inp1)

                inp1 = {"name": "admin_state", "send": "yes", "format": "default1", "desc": "Admin Status",
                        "length": "full", "default1": "disable", "type": "radio",
                        'options': [{"value": "disable", "label": "Shutdown"},
                                    {"value": "enable", "label": "No Shutdown", }]}
                response_data.append(inp1)

                response_data.append({"type": 'line', "label": 'Service Now', 'border': 'yes'})
                inp1 = {"name": "action_service_now", "format": "default1", "desc": "Action From Service Now",
                        "length": "full", "default1": "review", "type": "radio",
                        'options': [{"value": "review", "label": "Review"},
                                    {"value": "closed", "label": "Closed", "hide": "hide", "trigger": ["close_notes"]}]}

                # if pre_response.has_key('Review'):

                # response_data.append(inp1)
                # inp1={"type": "text", "name": "Review", "desc": "Review",
                #      'length': "full",
                #      "hide": "hide", "rhide": "hide", "default1":"", 'example': ""}
                response_data.append(inp1)

                inp1 = {"type": "textarea", "name": "close_notes", "desc": "Close Notes",
                        'length': "full", "hide": "hide", "rhide": "hide", "default1": "", 'example': ""}

                response_data.append(inp1)
           
            elif action == 'Provision' and port_type == 'Port-Channel':
                print " In Provision !.... "
                work_order_list = []
                query = ACIInterfaceStatusDB.objects.filter(status__in=["Reservation", "reserve"]).values(
                    'work_order_no').all()
                if query:
                    print query
                    for dct in query:
                        if dct["work_order_no"] not in work_order_list:
                            work_order_list.append(dct["work_order_no"])
                wo_options = []
                for each in work_order_list:
                    dict1 = {"send": "yes", "hide": "hide"}
                    dict1["label"] = each
                    dict1["value"] = each
                    wo_options.append(dict1)
                inp1 = {"name": "work_order_no", "send": "yes", "format": "default1", "desc": "Work Order Number",
                        "length": "full",
                        "default1": "", "type": "text", 'options': ""}
                response_data.append(inp1)
                
                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                tenant_list = apic_auth.get_all_tenant()
                # print tenant_list
                tenant_options = []
                if tenant_list:
                    for i in tenant_list:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            tenant_options.append(dict1)
                response_data.append({"type": 'line', "label": 'ACI Options', 'border': 'yes'})
                inp1 = {"name": "tenant_name", "send": "yes", "format": "default1", "desc": "Tenant Name",
                        "length": "full",
                        "default1": "", "type": "dropdown",
                        "options": tenant_options}
                response_data.append(inp1)

                db_leaf_list = []
                db_ports_list = []
                # try:
                query2 = ACIInterfaceStatusDB.objects.filter(status__in=["Reservation", "reserve"],
                                                             work_order_no=work_order_list).values('leaf_id',
                                                                                                   'physical_port').all()

                if query2:
                    # print query2
                    for dct in query2:
                        if dct["leaf_id"] not in db_leaf_list:
                            db_leaf_list.append(dct["leaf_id"])
                        if dct["physical_port"] not in db_ports_list:
                            db_ports_list.append(dct["physical_port"])

                for cst in db_leaf_list:
                    for opt in leaf_options:
                        if opt.get("value") == cst:
                            opt["selected"] = "yes"
                inp1 = {"name": "leaf_id", "send": "yes", "format": "default1", "desc": "Leaf Names", "length": "full",
                        "default1": "", "type": "dropdown-checkbox", 'options': leaf_options}
                response_data.append(inp1)
                
                count = 1
                print db_ports_list
                # db_ports_list=[db_ports_list[0]]
                for cst in db_leaf_list:
                    port_options = []
                    for each in db_ports_list:
                        dict1 = {}
                        dict1["label"] = each.title()
                        dict1["value"] = each
                        port_options.append(dict1)
                    print db_ports_list, port_options
                    inp1 = {"name": "physical_port" + str(count), "send": "yes", "length": "full",
                            "desc": "Leaf " + cst + " Physical Port", "type": "dropdown-checkbox",
                            'options': port_options}
                    count += 1
                    response_data.append(inp1)

                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                policy_list = apic_auth.list_PortChannel_policygroups()
                print policy_list
                policy_options = []
                if policy_list:
                    for i in policy_list:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            policy_options.append(dict1)
                inp1 = {"note": "", "default1": "", "name": "pc_policy_grp",
                        "type": "dropdown", "desc": "PC Policy Group", 'options': policy_options}

                response_data.append(inp1)

                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                profile_list = apic_auth.get_interface_profile()
                # policy_list = apic_auth.list_policygroups()
                # print policy_list
                policy_options = []
                if profile_list:
                    for i in profile_list:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            policy_options.append(dict1)
                inp1 = {"note": "", "default1": "", "name": "profile_grp",
                        "type": "dropdown", "desc": "Profile Group", 'options': policy_options}

                response_data.append(inp1)
            
                inp1 = {"name": "port_mode", "format": "default1", "desc": "Port Mode",
                        "length": "full", "default1": "access", "type": "radio","send":"yes",
                        'options': [{"value": "untagged", "label": "Access", 'send': 'yes'},
                                    {"value": "regular", "label": "Trunk", 'send': 'yes'}]}
                response_data.append(inp1)
                # inp1 = {"name": "physical_port1", "send": "yes", "format": "default1", "desc": "Leaf Physical Port","length":"full",
                #         "default1": "", "type": "dropdown-checkbox", 'options': port_options }
                # response_data["inputs"].append(inp1)

                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                app = apic_auth.apps_profile(tenant_list[0])
                print 'application ',app
                epg_bd = apic_auth.get_epg_bd(tenant_list[0],app[0])
                print epg_bd            
                epg_list = epg_bd['epg']
                bd_list = epg_bd['bd']
                vlan_options = []
                count = 1
                for i in range(len(epg_bd['epg'])):
                    dict1 = {}
                    dict1['value'] = "10"+str(count)+"-"+epg_list[i]+"-"+bd_list[i]
                    dict1['label'] = "10"+str(count)+" [EPG: "+epg_list[i]+", BD: "+bd_list[i]+"]"
                    vlan_options.append(dict1)
                
                inp1 = {"name": "vlan_id", "send": "yes", "format": "default1", "desc": "VLAN ID",
                        "length": "full", "default1": "", "type": "dropdown",
                        'options':vlan_options }
                response_data.append(inp1)
                
                inp1 = {"name": "application", "send": "yes", "format": "default1", "desc": "VLAN ID",
                        "length": "full", "default1": app[0], "type": "hidden",}
                            # [
                            # {"value": "101", "label": "101 [EPG: Prod-EPG-1, BD: Prod-BD-1]"},
                            # {"value": "102", "label": "102 [EPG: Prod-EPG-2, BD: Prod-BD-2]"}]}
                response_data.append(inp1)

                inp1 = {"name": "admin_state", "send": "yes", "format": "default1", "desc": "Admin Status",
                        "length": "full", "default1": "disable", "type": "radio",
                        'options': [{"value": "disable", "label": "Shutdown"},
                                    {"value": "enable", "label": "No Shutdown", }]}
                response_data.append(inp1)

                response_data.append({"type": 'line', "label": 'Service Now', 'border': 'yes'})
                inp1 = {"name": "action_service_now", "format": "default1", "desc": "Action From Service Now",
                        "length": "full", "default1": "review", "type": "radio",
                        'options': [
                            {"value": "review", "label": "Review"},
                            {"value": "closed", "label": "Closed", "hide": "hide", "trigger": ["close_notes"]}]}

                response_data.append(inp1)

                inp1 = {"type": "textarea", "name": "close_notes", "desc": "Close Notes",
                        'length': "full", "hide": "hide", "rhide": "hide", "default1": "", 'example': ""}

                response_data.append(inp1)
            
            elif action == 'Provision' and port_type == 'Virtual Port-Channel':
                print " In Provision !.... "
                work_order_list = []
                query = ACIInterfaceStatusDB.objects.filter(status__in=["Reservation", "reserve"]).values(
                    'work_order_no').all()
                if query:
                    print query
                    for dct in query:
                        if dct["work_order_no"] not in work_order_list:
                            work_order_list.append(dct["work_order_no"])
                wo_options = []
                for each in work_order_list:
                    dict1 = {"send": "yes", "hide": "hide"}
                    dict1["label"] = each
                    dict1["value"] = each
                    wo_options.append(dict1)
                inp1 = {"name": "work_order_no", "send": "no", "format": "default1", "desc": "Work Order Number",
                        "length": "full",
                        "default1": "", "type": "text", 'options': wo_options}
                response_data.append(inp1)
                
                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                tenant_list = apic_auth.get_all_tenant()
                # print tenant_list
                tenant_options = []
                if tenant_list:
                    for i in tenant_list:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            tenant_options.append(dict1)
                response_data.append({"type": 'line', "label": 'ACI Options', 'border': 'yes'})
                inp1 = {"name": "tenant_name", "send": "yes", "format": "default1", "desc": "Tenant Name",
                        "length": "full",
                        "default1": "", "type": "dropdown",
                        "options": tenant_options}
                response_data.append(inp1)

                db_leaf_list = []
                db_ports_list = []
                # try:
                query2 = ACIInterfaceStatusDB.objects.filter(status__in=["Reservation", "reserve"],
                                                             work_order_no=work_order_list).values('leaf_id',
                                                                                                   'physical_port').all()

                if query2:
                    # print query2
                    for dct in query2:
                        if dct["leaf_id"] not in db_leaf_list:
                            db_leaf_list.append(dct["leaf_id"])
                        if dct["physical_port"] not in db_ports_list:
                            db_ports_list.append(dct["physical_port"])

                for cst in db_leaf_list:
                    for opt in leaf_options:
                        if opt.get("value") == cst:
                            opt["selected"] = "yes"
                inp1 = {"name": "leaf_id", "send": "yes", "format": "default1", "desc": "Leaf Names", "length": "full",
                        "default1": "", "type": "dropdown-checkbox", 'options': leaf_options}
                response_data.append(inp1)
                
                count = 1
                print db_ports_list
                # db_ports_list=[db_ports_list[0]]
                for cst in db_leaf_list:
                    port_options = []
                    for each in db_ports_list:
                        dict1 = {}
                        dict1["label"] = each.title()
                        dict1["value"] = each
                        port_options.append(dict1)
                    print db_ports_list, port_options
                    inp1 = {"name": "physical_port" + str(count), "send": "yes", "length": "full",
                            "desc": "Leaf " + cst + " Physical Port", "type": "dropdown-checkbox",
                            'options': port_options}
                    count += 1
                    response_data.append(inp1)

                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                policy_list = apic_auth.list_PortChannel_policygroups()
                print policy_list
                policy_options = []
                if policy_list:
                    for i in policy_list:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            policy_options.append(dict1)
                inp1 = {"note": "", "default1": "", "name": "pc_policy_grp",
                        "type": "dropdown", "desc": "PC Policy Group", 'options': policy_options}

                response_data.append(inp1)

                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                policy_list = apic_auth.get_interface_profile()
                print policy_list
                policy_options = []
                if policy_list:
                    for i in policy_list:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            policy_options.append(dict1)
                inp1 = {"note": "", "default1": "", "name": "profile_grp",
                        "type": "dropdown", "desc": "Policy Group", 'options': policy_options}

                response_data.append(inp1)
            
                inp1 = {"name": "port_mode", "format": "default1", "desc": "Port Mode",
                        "length": "full", "default1": "regular", "type": "radio",
                        'options': [{"value": "untagged", "label": "Access","send":"yes"},
                                    {"value": "regular", "label": "Trunk","send":"yes"}]}
                response_data.append(inp1)
                # inp1 = {"name": "physical_port1", "send": "yes", "format": "default1", "desc": "Leaf Physical Port","length":"full",
                #         "default1": "", "type": "dropdown-checkbox", 'options': port_options }
                # response_data["inputs"].append(inp1)

                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                app = apic_auth.apps_profile(tenant_list[0])
                print 'application ',app
                epg_bd = apic_auth.get_epg_bd(tenant_list[0],app[0])
                print epg_bd            
                epg_list = epg_bd['epg']
                bd_list = epg_bd['bd']
                vlan_options = []
                count = 1
                for i in range(len(epg_bd['epg'])):
                    dict1 = {}
                    dict1['value'] = "10"+str(count)+"_"+epg_list[i]+"_"+bd_list[i]
                    dict1['label'] = "10"+str(count)+" [EPG: "+epg_list[i]+", BD: "+bd_list[i]+"]"
                    vlan_options.append(dict1)
                
                inp1 = {"name": "vlan_id", "send": "yes", "format": "default1", "desc": "VLAN ID",
                        "length": "full", "default1": "", "type": "dropdown-checkbox",
                        'options':vlan_options }
                response_data.append(inp1)
                
                inp1 = {"name": "application", "send": "yes", "format": "default1", "desc": "VLAN ID",
                        "length": "full", "default1": app[0], "type": "hidden",}
                            # [
                            # {"value": "101", "label": "101 [EPG: Prod-EPG-1, BD: Prod-BD-1]"},
                            # {"value": "102", "label": "102 [EPG: Prod-EPG-2, BD: Prod-BD-2]"}]}
                response_data.append(inp1)

                inp1 = {"name": "admin_state", "send": "yes", "format": "default1", "desc": "Admin Status",
                        "length": "full", "default1": "disable", "type": "radio",
                        'options': [{"value": "disable", "label": "Shutdown"},
                                    {"value": "enable", "label": "No Shutdown", }]}
                response_data.append(inp1)

                response_data.append({"type": 'line', "label": 'Service Now', 'border': 'yes'})
                inp1 = {"name": "action_service_now", "format": "default1", "desc": "Action From Service Now",
                        "length": "full", "default1": "review", "type": "radio",
                        'options': [
                            {"value": "review", "label": "Review"},
                            {"value": "closed", "label": "Closed", "hide": "hide", "trigger": ["close_notes"]}]}

                response_data.append(inp1)

                inp1 = {"type": "textarea", "name": "close_notes", "desc": "Close Notes",
                        'length': "full", "hide": "hide", "rhide": "hide", "default1": "", 'example': ""}

                response_data.append(inp1)

            elif action == "De-Provision":
                work_order_options = [{'value': 'Select', 'label': 'Select'}]
                q = ACIInterfaceStatusDB.objects.filter(Q(status="Reservation") | Q(status="Provision")).values_list(
                    'work_order_no')
                wo_num = []
                if q:
                    for ele in q:
                        if ele[0] not in wo_num:
                            wo_num.append(ele[0])
                    for num in wo_num:
                        dict1 = {}
                        dict1['value'] = num
                        dict1['label'] = num
                        dict1['send'] = 'yes'
                        dict1['hide'] = 'hide'
                        work_order_options.append(dict1)
                if pre_response.has_key('work_order_no'):
                    
                    response_data.append(
                        {"note": "", "default1": pre_response.get('work_order_no'), "name": "work_order_no",
                         'send': 'yes',
                         "type": "text", "desc": "Work Order No.", 'options': work_order_options})
                else:
                    
                    response_data.append(
                        {"note": "", "default1": "", "name": "work_order_no", 'send': 'yes',
                         "type": "text", "desc": "Work Order No.", 'options': work_order_options})

                # if pre_response.has_key('work_order_no'):
                   
                if Service_now_flag:
                    if pre_response.has_key('new_work_order_no'):
                        response_data.append(
                            {"note": "", "default1": pre_response.get('new_work_order_no'), "name": "new_work_order_no",
                                "type": "text", "desc": "New Work Order No. for ServiceNow"})
                    else:
                        response_data.append(
                            {"note": "", "default1": "", "name": "new_work_order_no", "type": "text",
                                "desc": "New Work Order No. for ServiceNow"})

                q1 = ACIInterfaceStatusDB.objects.filter(
                    work_order_no=pre_response.get('work_order_no')).values_list('leaf_id')
                leaf_id_list = []
                if q1:
                    for ele in q1:
                        if ele[0] not in leaf_id_list:
                            leaf_id_list.append(ele[0])
                leaf_id_options = []
                leaf_count = 0
                for ele in leaf_list:
                    leaf_count +=1
                    model_num = apic_auth.get_model_no(ele["name"])
                    print " ele['name'] ", ele['name'] 
                    if str(ele['name']) in leaf_id_list:
                        dict1 = {'send': "yes"}
                        dict1["label"] = "LCAWDCP-01-01-0" + str(leaf_count) + " [ " + ele["name"] + " ]" + " [ " + model_num + " ]"
                        dict1["value"] = ele["name"]
                        dict1['selected'] = 'no'
                        leaf_id_options.append(dict1)
               

                if pre_response.has_key('leaf_id'):
                    for opt_sel in pre_response.get('leaf_id'):
                        for opt in leaf_options:
                            if opt_sel == opt['value']:
                                opt['selected'] = 'yes'
                    response_data.append(
                        {"note": "", "default1": pre_response.get('leaf_id'), "name": "leaf_id", 'send': 'yes',
                            "type": "dropdown-checkbox", "desc": "Leaf ID", 'options': leaf_options})
                else:
                    print ">>>>>>>>>>"
                    response_data.append(
                        {"note": "", "default1": "", "name": "leaf_id", 'send': 'yes',
                            "type": "dropdown-checkbox", "desc": "Leaf ID", 'options': leaf_options})

                if pre_response.has_key('leaf_id'):
                    for opt_sel in pre_response.get('leaf_id'):
                        apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                        prereserved_ports = ['Eth 1/45', 'Eth 1/46', 'Eth 1/47', 'Eth 1/48']
                        port_options = []
                        reserved_ports = []
                        query = ACIInterfaceStatusDB.objects.filter(leaf_id=opt_sel).values('physical_port').all()
                        if query:
                            for dct in query:
                                if dct["physical_port"] not in reserved_ports:
                                    reserved_ports.append(dct["physical_port"])
                                    
                        
                        port_details = apic_auth.get_port_details(opt_sel)
                        for each in range(1, 49):
                            get_port_details = ""
                            dict1 = {}
                            each = "Eth 1/" + str(each) 
                            # if request.session["ext_dict"]["action"] in ["Provision"]:
                            port = each.lower().replace(" ","")
                            
                            if port in port_details and port_details[port]['oper_state'] != 'up' and each not in prereserved_ports and each.lower().replace(" ", "") not in reserved_ports:
                                
                                dict1["label"] = each
                                dict1["value"] = each.lower()
                                dict1["send"] = "yes"
                                dict1["disabled"] =  "no"
                                port_options.append(dict1)
                            
                            if port in port_details and port_details[port]['oper_state'] == 'up'  and each not in prereserved_ports and each.lower().replace(" ", "") not in reserved_ports:
                                
                                dict1["label"] = each
                                dict1["value"] = each.lower()
                                dict1["disabled"] =  "yes"
                                port_options.append(dict1)
                            
                            # if port in port_details and port_details[port]['oper_state'] != 'up' and each not in prereserved_ports and each.lower().replace(" ", "") in reserved_ports:
                                
                            #     dict1["label"] = each
                            #     dict1["value"] = each.lower()
                            #     dict1["disabled"] =  "yes"
                            #     port_options.append(dict1)
                            
                            # if port in port_details and port_details[port]['oper_state'] != 'up'  and each not in prereserved_ports and each.lower().replace(" ", "") not in reserved_ports:
                                
                            #     dict1["label"] = each
                            #     dict1["value"] = each.lower()
                            #     dict1["disabled"] =  "yes"
                            #     port_options.append(dict1)
                                
                        all_port_details = apic_auth.get_port_details(opt_sel)
                        q2 = ACIInterfaceStatusDB.objects.filter(leaf_id=opt_sel,
                                                                 work_order_no=pre_response.get(
                                                                     'work_order_no')).values_list('physical_port')
                        port_list = []
                        physical_port = []
                        
                        if q2:
                            print q2
                            for ele in q2:
                                if ele[0] not in port_list:
                                    port_list.append(ele[0])
                            for port in port_list:
                                if port in all_port_details and all_port_details[port]['oper_state'] != 'up' and  all_port_details[port]['policy'] and pre_response.get('work_order_no') in all_port_details[port]['description']:
                                    dict1 = {}
                                    dict1['value'] = port
                                    dict1['label'] = port.title()
                                    dict1['hide'] = 'hide'
                                    physical_port.append(dict1)
                                elif port in all_port_details and all_port_details[port]['policy'] and all_port_details[port]['oper_state'] == 'up' or pre_response.get('work_order_no') not in all_port_details[port]['description']:
                                    dict1 = {}
                                    dict1['value'] = port
                                    dict1['label'] = port.title()
                                    dict1['hide'] = 'hide'
                                    dict1['disabled'] = 'yes'
                                    physical_port.append(dict1)
                        if pre_response.has_key("physical_port_" + opt_sel):
                            print "Here in Physical Port !", pre_response.get("physical_port_" + opt_sel)
                            for prt in pre_response.get("physical_port_" + opt_sel):
                                for opt in port_options:
                                    if opt.get("value") == prt:
                                        opt["selected"] = "yes"
                        response_data.append(
                            {"note": "", "default1": "", "name": "physical_port_" + opt_sel,
                             "type": "dropdown-checkbox", "desc": "Leaf {} Physical Ports".format(opt_sel),
                             'options': port_options})
                #
                # response_data.append(
                #     {"note": "", "default1": "", "name": "admin_state",
                #      "type": "radio", "desc": "Admin State", 'options': [{'value': 'enable', 'label': 'No Shutdown'},
                #                                                          {'value': 'disable', 'label': 'Shutdown'}
                #                                                          ]})

            elif action == "Leaf Port Status":
                if pre_response.has_key('leaf_node'):
                    response_data.append(
                        {"note": "", "default1": pre_response.get('leaf_node'), "name": "leaf_node",
                         "type": "dropdown", "desc": "Leaf", 'options': leaf_options})
                else:
                    response_data.append(
                        {"note": "", "default1": "", "name": "leaf_node",

                         "type": "dropdown", "desc": "Leaf", 'options': leaf_options})
                interaface_options = [{"value": '', 'label': 'Select'}]
                for num in range(1, 45):
                    port_dict = {}
                    port_dict['value'] = 'eth 1/' + str(num)
                    port_dict['label'] = 'Eth 1/' + str(num)
                    interaface_options.append(port_dict)
                if pre_response.has_key('phy_port'):
                    response_data.append(
                        {"note": "", "default1": pre_response.get('phy_port'), "name": "phy_port",
                         "type": "dropdown", "desc": "Physical Port", 'options': interaface_options})
                else:
                    response_data.append(
                        {"note": "", "default1": "", "name": "phy_port",
                         "type": "dropdown", "desc": "Physical Port", 'options': interaface_options})

        if service == 'Add Or Modify Tenant':
            print ">>>>>>>>>>", pre_response
            if pre_response.has_key('select_tenant'):
                response_data.append(
                    {"note": "", "default1": pre_response.get('select_tenant'), "name": "select_tenant", "send": "yes",
                     "type": "radio", "desc": "Tenant",
                     "options": [{"value": "Existing", "label": "Existing", "hide": "hide",
                                  "trigger": ["tenant_name", "app_name", "bd_name", "vrf_name", "epg_name"]},
                                 {"value": "New", "label": "New", "hide": "hide",
                                  "trigger": ["tenant_new", "app_name_new", "epg_name_new", "vrf_new", "bd_new"]}]})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "select_tenant", "send": "yes",
                     "type": "radio", "desc": "Tenant",
                     "options": [{"value": "Existing", "label": "Existing", "hide": "hide",
                                  "trigger": ["tenant_name", "app_name", "bd_name", "vrf_name", "epg_name"]},
                                 {"value": "New", "label": "New", "hide": "hide",
                                  "trigger": ["tenant_new", "app_name_new", "epg_name_new", "vrf_new", "bd_new"]}]})

            apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
            get_tenant = apic_auth.get_all_tenant()
            print pre_response
            tenant_list = [{'value': '', 'label': 'Select'}]
            if get_tenant:
                for i in get_tenant:
                    if i:
                        dict1 = {}
                        dict1["label"] = i
                        dict1["value"] = i
                        dict1["send"] = 'yes'
                        tenant_list.append(dict1)
            if pre_response.has_key('tenant_name'):
                response_data.append(
                    {"note": "", "default1": pre_response.get('tenant_name'), "name": "tenant_name", "hide": "hide",
                     'send': 'yes',
                     "type": "dropdown", "desc": "Tenants", "options": tenant_list})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "tenant_name", "hide": "hide", 'send': 'yes',
                     "type": "dropdown", "desc": "Tenants", "options": tenant_list})

            if pre_response.has_key('tenant_new'):
                response_data.append(
                    {"note": "", "default1": pre_response.get('tenant_new'), "name": "tenant_new", "hide": "hide",
                     "type": "text", "desc": "Tenant Name"})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "tenant_new", "hide": "hide",
                     "type": "text", "desc": "Tenant Name"})

            if pre_response.has_key('vrf_new'):
                response_data.append(
                    {"note": "", "default1": pre_response.get('vrf_new'), "name": "vrf_new", "hide": "hide",
                     "type": "text", "desc": "VRF Name"})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "vrf_new", "hide": "hide",
                     "type": "text", "desc": "VRF Name"})

            if pre_response.has_key('bd_new'):
                response_data.append(
                    {"note": "", "default1": pre_response.get('bd_new'), "name": "bd_new", "hide": "hide",
                     "type": "text", "desc": "Bridge Domain Name"})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "bd_new", "hide": "hide",
                     "type": "text", "desc": "Bridge Domain Name"})
            app_profile_list = []
            if pre_response.has_key('tenant_name'):
                get_app_profile = apic_auth.apps_profile(pre_response.get('tenant_name'))
                print get_app_profile
                if get_tenant:
                    for i in get_app_profile:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            app_profile_list.append(dict1)

                response_data.append(
                    {"note": "", "default1": "", "name": "app_name", "hide": "hide",
                     "type": "dropdown", "desc": "Application Name", "options": app_profile_list})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "app_name_new", "hide": "hide",
                     "type": "text", "desc": "Application Name"})

            if pre_response.has_key('bd_name'):
                print ">>>>>>11"
                response_data.append(
                    {"default1": pre_response.get('bd_name'), "name": "bd_name",
                     "type": "text", "desc": "Bridge Domain Name"})
            else:
                print ">>>>>>22"
                response_data.append(
                    {"default1": "", "name": "bd_name", "type": "text", "desc": "Bridge Domain Name"})

            if pre_response.has_key('vrf_name'):
                response_data.append(
                    {"note": "", "default1": pre_response.get('vrf_name'), "name": "vrf_name", "hide": "hide",
                     "type": "text", "desc": "VRF Name", "example": "VRF"})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "vrf_name", "hide": "hide",
                     "type": "text", "desc": "VRF Name", "example": "VRF"})

            if pre_response.has_key('epg_name'):
                response_data.append(
                    {"note": "", "default1": pre_response.get('epg_name'), "name": "epg_name",
                     "type": "text", "desc": "EPG Name", "options": []})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "epg_name",
                     "type": "text", "desc": "EPG Name", "options": []})
            if pre_response.has_key('epg_name_new'):
                response_data.append(
                    {"note": "", "default1": pre_response.get('epg_name_new'), "name": "epg_name_new", "hide": "hide",
                     "type": "text", "desc": "EPG Name"})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "epg_name_new", "hide": "hide",
                     "type": "text", "desc": "EPG Name"})

        if service == 'policy_grp':
            response_data.append(
                {"note": "", "default1": "", "name": "policy_name",
                 "type": "text", "desc": "Policy Name"})
            
            response_data.append(
                {"note": "", "default1": "", "name": "speed",
                 "type": "radio", "desc": "Speed",
                 "options": [{'value': 'inherit', 'label': 'Auto'},
                             {'value': '1G', 'label': '1G'},
                             {'value': '10G', 'label': '10G'},
                             {'value': '25G', 'label': '25G'},
                             {'value': '100G', 'label': '100G'}]})

        if service == 'port_channel_group':
            if pre_response.has_key('PC_group_name'):
                response_data.append(
                    {"note": "", "default1": pre_response.get('PC_group_name'), "name": "PC_group_name", "hide": "hide",
                     "type": "text", "desc": "Port Channel Group Name"})
            else:
                response_data.append(
                    {"note": "", "default1": "", "name": "PC_group_name", "hide": "hide",
                     "type": "text", "desc": "Port Channel Group Name"})

            if pre_response.has_key('PC_policy_type'):
                print " 1"
                response_data.append(
                    {"note": "", "default1": pre_response.get('PC_policy_type'), "name": "PC_policy_type",
                     "send": "yes",
                     "type": "radio", "hide": "hide", "desc": "Select Port Channel Policy",
                     "options": [{'value': 'Existing', 'label': 'Existing', "send": "yes", "hide": "hide"},
                                 {'value': 'New', 'label': 'New', "send": "yes", "hide": "hide"}]})
            else:
                print "2"
                response_data.append(
                    {"note": "", "default1": "", "name": "PC_policy_type", "send": "yes", "hide": "hide",
                     "type": "radio", "desc": "Select Port Channel Policy",
                     "options": [{'value': 'Existing', 'label': 'Existing', "send": "yes", "hide": "hide"},
                                 {'value': 'New', 'label': 'New', "send": "yes", "hide": "hide"}]})

            if pre_response.has_key('PC_policy_type') and 'New' in pre_response.get('PC_policy_type'):
                response_data.append(
                    {"note": "", "default1": "", "name": "port_channel_policy",
                     "type": "text", "desc": "Port Channel Policy Name"})

                if pre_response.has_key('port_channel_mode'):
                    response_data.append(
                        {"note": "", "default1": pre_response.get('port_channel_mode'), "name": "port_channel_mode",
                         "type": "radio", "desc": "Select Port Channel Policy",
                         "options": [{'value': 'active', 'label': 'LACP Active'},
                                     {'value': 'passive', 'label': 'LACP Passive'},
                                     {'value': 'off', 'label': 'Static-Mode On'}]})
                else:
                    response_data.append(
                        {"note": "", "default1": "", "name": "port_channel_mode",
                         "type": "radio", "desc": "Select Port Channel Policy",
                         "options": [{'value': 'active', 'label': 'LACP Active'},
                                     {'value': 'passive', 'label': 'LACP Passive'},
                                     {'value': 'off', 'label': 'Static-Mode On'}]})

                response_data.append(
                    {"note": "", "default1": "", "name": "description", "type": "text",
                     "desc": "Description"})

            if pre_response.has_key('PC_policy_type') and 'Existing' in pre_response.get('PC_policy_type'):
                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                pc_policy_list = apic_auth.port_channe_group()
                pc_policy_options = [{'value': 'Select Policy', 'label': 'Select Port Channel Policy'}]
                if pc_policy_list:
                    for i in pc_policy_list:
                        if i:
                            dict1 = {}
                            dict1["label"] = i
                            dict1["value"] = i
                            pc_policy_options.append(dict1)
                if pre_response.has_key('existing_PC_policy'):
                    response_data.append(
                        {"note": "", "default1": pre_response.get('existing_PC_policy'), "name": "existing_PC_policy",
                         "type": "dropdown-autocomplete", "hide": "hide", "desc": "Select Port Channel Policy",
                         "options": pc_policy_options})
                else:
                    response_data.append(
                        {"note": "", "default1": "", "name": "existing_PC_policy", "hide": "hide",
                         "type": "dropdown-autocomplete", "desc": "Select Port Channel Policy",
                         "options": pc_policy_options})
        self.para_dict = {"column": "12", "newline": "yes", "inputs": response_data}

    def get_response_data(self):
        return self.para_dict
