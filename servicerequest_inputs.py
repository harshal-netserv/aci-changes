from __future__ import absolute_import
from mysite.globals import *
import json
import re
from mysite.nlead_library.aci_api_inputs import *
from mysite.nlead_library.aci_api_functions import *
from django.conf import settings

if not settings.configured:
    settings.configure('mysite', DEBUG=True)

try:
    from mysite.models import CustomerDB, CronDB, ACI_Change_Request_DB
    from mysite.models import template_db
    from mysite.models import SetupParameters
    from django.contrib.auth.models import Group,User
    from mysite.models import UserProfile
except ValueError:
    print "Need to figure it out"


def app_inputs():
    with open('./mysite/Json_DATA/application_option.json') as f:
        data = json.load(f)

        return data


def get_template_list(customer="", type="", role=""):

    template_dict = {}
    print "get template list >>>>>>>", type
    entry = template_db.objects.values_list('id', 'template', "ios", "plat", "tech", "name", "customer", "type",
                                            "device_role", "status").all()
    # print entry
    if entry:
        templ_list = []
        tempdict = {}
        tempdict["key"] = ""
        tempdict["value"] = "Select Template"
        tempdict["disabled"] = "no"
        templ_list.append(tempdict)
        for each in entry:
            # if str(each[7]) == "6":
            #     template_dict = {}
            #     template_dict['key'] = each[0]
            #     template_dict['value'] = each[5]
            #     template_dict['disabled'] = "no"
            #     templ_list.append(template_dict)
            if str(each[7]) == type and str(each[7]) == "1":
                template_dict = {}
                if each[6] != "":
                    customer_list = each[6].split(" ")
                else:
                    customer_list = []
                if customer in customer_list or customer == "common":
                    if role != "" and each[8] == role or each[8] == "":
                        template_dict['key'] = each[0]
                        if len(each[5]) > 3:
                            template_dict['value'] = each[5]
                        else:
                            ios = " (" + each[2].upper() + ")"
                            plat = " (" + each[3].upper() + ")"
                            tech = " (" + each[4].upper() + ")"
                            if each[2].upper() == "NA":
                                ios = ""
                            if each[3].upper() == "NA":
                                plat = ""
                            if each[4].upper() == "NA" or each[4].upper() == "ANY":
                                tech = ""

                            template_dict['value'] = each[1] + ios + plat + tech
                    # else:
                    # template_dict['key'] = each[0]
                    # if len(each[5]) > 3:
                    # template_dict['value'] = each[5]
                    # else:
                    # ios =  " (" +each[2].upper() + ")"
                    # plat = " (" +each[3].upper() + ")"
                    # tech = " (" +each[4].upper() + ")"
                    # if each[2].upper() == "NA" :
                    # ios =""
                    # if each[3].upper()  == "NA":
                    # plat = ""
                    # if each[4].upper() == "NA" or each[4].upper() == "ANY":
                    # tech = ""
                    # template_dict['value'] = each[1] + ios + plat + tech
                    if each[9] == 2:
                        template_dict["disabled"] = "yes"
                    else:
                        template_dict["disabled"] = "no"
                templ_list.append(template_dict)
            elif str(each[7]) == type and str(each[7]) == "2":
                print ">>>>>> Here in Type "
                template_dict = {}
                if "," in each[3]:
                    plat_list = each[3].split(",")
                else:
                    plat_list = [each[3]]
                # print plat_list
                if each[6] != "":
                    customer_list = each[6].split(" ")
                    # print customer_list
                else:
                    customer_list = []
                if customer in customer_list or each[6] == "":
                    template_dict['key'] = each[0]
                    # if len(plat_list) > 1:
                    for plat in plat_list:
                        if each[2].upper() == "ACI":
                            template_dict['value'] = each[1] + " (" + each[2].upper() + ")"
                        elif plat.upper() == "NA" or plat.upper() == "ANY":
                            template_dict['value'] = each[1] + " (" + each[2].upper() + ") (" + each[4].upper() + ")"
                        else:
                            plat_indx = plat_list.index(plat)
                            template_dict['key'] = str(each[0]) + "-" + str(plat_indx)
                            template_dict['value'] = each[1] + " (" + each[2].upper() + ") (" + plat.upper() + ") (" + \
                                                     each[4].upper() + ")"
                        if each[9] == 2:
                            template_dict["disabled"] = "yes"
                        else:
                            template_dict["disabled"] = "no"
                        templ_list.append(template_dict.copy())
                else:
                    continue
            elif str(each[7]) == type and str(each[7]) == "ansible":
                template_dict = {}
                if "," in each[3]:
                    plat_list = each[3].split(",")
                else:
                    plat_list = [each[3]]
                # print plat_list
                if each[6] != "":
                    customer_list = each[6].split(" ")
                    # print customer_list
                else:
                    customer_list = []
                if customer in customer_list or each[6] == "":
                    template_dict['key'] = each[0]
                    # if len(plat_list) > 1:
                    for plat in plat_list:
                        if each[2].upper() == "ACI":
                            template_dict['value'] = each[1] + " (" + each[2].upper() + ")"
                        elif plat.upper() == "NA" or plat.upper() == "ANY":
                            template_dict['value'] = each[1] + " (" + each[2].upper() + ") (" + each[4].upper() + ")"
                        else:
                            plat_indx = plat_list.index(plat)
                            template_dict['key'] = str(each[0]) + "-" + str(plat_indx)
                            template_dict['value'] = each[1] + " (" + each[2].upper() + ") (" + plat.upper() + ") (" + \
                                                     each[4].upper() + ")"
                        if each[9] == 2:
                            template_dict["disabled"] = "yes"
                        else:
                            template_dict["disabled"] = "no"
                        templ_list.append(template_dict.copy())
                else:
                    continue

            if str(each[7]) == "3" and type == "1":
                template_dict = {}
                if each[6] != "":
                    customer_list = each[6].split(" ")
                else:
                    customer_list = []
                if customer in customer_list or customer == "common":  # or each[6]==""
                    template_dict['key'] = each[0]
                    template_dict['value'] = each[5]
                    if each[9] == 2:
                        template_dict["disabled"] = "yes"
                    else:
                        template_dict["disabled"] = "no"
                    templ_list.append(template_dict)
                else:
                    continue
            if str(each[7]) == "4" and type == "2":
                template_dict = {}
                if each[6] != "":
                    customer_list = each[6].split(" ")
                    # print customer_list
                else:
                    customer_list = []
                if customer in customer_list or customer == "common":  # or each[6]==""
                    template_dict['key'] = each[0]
                    template_dict['value'] = each[5]
                    if each[9] == 2:
                        template_dict["disabled"] = "yes"
                    else:
                        template_dict["disabled"] = "no"

                else:
                    continue

    templ_list.append(template_dict)
    return templ_list


def get_template_list2(customer=""):
    entry = template_db.objects.values_list('template', "ios", "plat", "tech", "name", "customer", "type",
                                            "status").all()
    if entry:
        templ_list = []
        for each in entry:
            if str(each[6]) == "1":
                if each[5] != "":
                    customer_list = each[5].split(" ")
                else:
                    customer_list = []
                if customer in customer_list or customer == "common":  # or each[5]==""
                    template_dict = {}
                    if each[3].upper() != "NA" or each[3].upper() != "Any":
                        template_dict['label'] = each[0] + " (" + each[1].upper() + ") (" + each[3].upper() + ")"
                        template_dict['value'] = each[0] + " (" + each[1].upper() + ") (" + each[3].upper() + ")"
                    else:
                        template_dict['label'] = each[0] + " (" + each[1].upper() + ")"
                        template_dict['value'] = each[0] + " (" + each[1].upper() + ")"
                    if each[7] == 2:
                        template_dict['disabled'] = "yes"
                    else:
                        template_dict['disabled'] = "no"
                    templ_list.append(template_dict)

    return templ_list


def get_customer_options():
    q1 = CustomerDB.objects.values_list("name").all().filter(status=1)
    customeroptions = [{"label": "Please Select Customer", "value": ""}]
    if q1:
        for entry in q1:
            dict1 = {}
            dict1["label"] = entry[0]
            dict1["value"] = entry[0].lower()
            dict1["send"] = 'yes'
            customeroptions.append(dict1)
    return customeroptions

def get_users_options():
    from django.contrib.auth.models import User
    users = User.objects.all()

    customeroptions = [{"label": "Please Select Customer", "value": ""}]
    if users:
        for entry in users:
            dict1 = {}
            dict1["label"] = entry.username
            dict1["value"] = entry.username
            dict1["send"] = 'no'
            customeroptions.append(dict1)
    return customeroptions

def get_group_options():
    from django.contrib.auth.models import Group
    users = Group.objects.all()

    customeroptions = [{"label": "Please Select Groups", "value": ""}]
    if users:
        for entry in users:
            dict1 = {}
            dict1["label"] = entry.name
            dict1["value"] = entry.name
            dict1["send"] = 'no'
            customeroptions.append(dict1)
    return customeroptions

def getuserdept(request):
    current_user = request.user
    uid = current_user.id
    from mysite.models import UserProfile
    q1 = UserProfile.objects.values_list('department').filter(user=uid).last()
    if q1:
        return q1[0]
    else:
        return ""


def getusersubdept(request):
    current_user = request.user
    uid = current_user.id
    from mysite.models import UserProfile
    q1 = UserProfile.objects.values_list('subdepartment').filter(user=uid).last()
    if q1:
        return q1[0]
    else:
        return ""


class ServiceRequest_InputData:
    '''
    This class loads the inputs to phase 1 using unique value.
	Inputs:  following are default input rendered
    Change request number
    Type: (configuration, Troubleshooting)
    Service: select template for loads inputs and configuration


    '''

    def __init__(self, req_type, response={}):

        # pre_response = response.GET
        pre_response = {}
        for el in response.GET:
            if response.GET.get(el):
                if "[" in el:
                    element_value = response.GET.getlist(el)
                    if element_value:
                        new_el = el.split("[]")[0]
                        pre_response[new_el] = element_value
                else:
                    pre_response[el] = response.GET.get(el)
        from mysite.models import ServiceRequestDB
        para_dict = []
        is_hardcoded = 1
        # pre_response["customer"] = defaultcustomer
        defaultcustomer = ""
        if len(response.user.groups.all()) > 0:
            defaultcustomer = str(response.user.groups.all()[0])
        # New Request
        if req_type == "1":
            print "customer  ==== " , response.session["customer"]
            if response.session.has_key("customer") and response.session["customer"] != "":
                para_dict.append(
                    {"name": "customer", "format": "", "default1": response.session["customer"], "output": "",
                     "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide"})
            else:
                if pre_response.has_key("customer"):
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
                else:
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
            if pre_response.has_key("taskid"):
                para_dict.append(
                    {"name": "taskid", "format": "", "default1": pre_response["taskid"], "output": "", "type": "text",
                     "example": "", "desc": "Change Request Number", "mandatory": "yes",
                     "vmessage": "Please Enter Change Request No."})
            else:
                para_dict.append(
                    {"name": "taskid", "format": "", "default1": "", "output": "", "type": "text", "example": "",
                     "desc": "Change Request Number", "mandatory": "yes", "vmessage": "Please Enter Change Request No."})
            if pre_response.has_key("subtaskid"):
                para_dict.append(
                    {"name": "subtaskid", "format": "", "default1": pre_response["subtaskid"], "output": "",
                     "type": "hidden", "example": "(Optional)", "desc": "Sub-Task ID", "mandatory": "no"})
            else:
                para_dict.append({"name": "subtaskid", "format": "", "default1": "", "output": "", "type": "hidden",
                                  "example": "(Optional)", "desc": "Sub-Task ID", "mandatory": "no"})
            if pre_response.has_key("template_name"):
                para_dict.append({"note": "If Template name is known", "default1": pre_response.get("template_name"),
                                  "name": "template_name", "send": "yes", "type": "hidden", "options": [
                        {"trigger": ["type_ct", "template", "deviceip"], "hide": "hide", "value": "yes",
                         "label": "Yes"},
                        {"trigger": ["scope", "deviceip"], "hide": "hide", "value": "no", "label": "No"}],
                                  "desc": "Do you know Template Name?"})
            else:
                para_dict.append(
                    {"note": "If Template name is known", "default1": "yes", "name": "template_name", "send": "yes",
                     "type": "hidden", "options": [
                        {"trigger": ["type_ct", "template", "deviceip"], "hide": "hide", "value": "yes",
                         "label": "Yes"},
                        {"trigger": ["scope", "deviceip"], "hide": "hide", "value": "no", "label": "No"}],
                     "desc": "Do you know Template Name?"})
            if pre_response.has_key("templateid") and pre_response["templateid"] and str(getuserdept(response)) == "greenwood":
                para_dict.append(
                    {"note": "", "default1": "2", "name": "type_ct", "send": "yes",
                     "type": "radio", "options": [{"value": "1", "label": "Configuration", "hide": "hide"},{"value": "2", "label": "Troubleshooting", "hide": "hide"}, ],
                     "desc": "Type"})
            elif pre_response.has_key("templateid") and pre_response["templateid"] :
                para_dict.append(
                    {"note": "", "default1": "2", "name": "type_ct", "send": "yes",
                     "type": "radio", "options": [{"value": "1", "label": "Configuration", "hide": "hide"},
                                                  {"value": "2", "label": "Troubleshooting", "hide": "hide"}, ],
                     "desc": "Type"})
                #{"value": "ansible", "label": "Ansible", "hide": "hide"}
            else:
                if pre_response.has_key("type_ct"):
                    para_dict.append(
                        {"note": "", "default1": pre_response.get("type_ct"), "name": "type_ct", "send": "yes",
                         "type": "radio", "options": [{"value": "1", "label": "Configuration", "hide": "hide"},
                                                      {"value": "2", "label": "Troubleshooting", "hide": "hide"},
                                                      ],
                         "desc": "Type"})
                    #{"value": "ansible", "label": "Ansible", "hide": "hide"}
                else:
                    para_dict.append({"note": "", "default1": "1", "name": "type_ct", "send": "yes", "type": "radio",
                                      "options": [{"value": "1", "label": "Configuration", "hide": "hide"},
                                                  {"value": "2", "label": "Troubleshooting", "hide": "hide"},
                                                      ],
                                      "desc": "Type"})
                    #{"value": "ansible", "label": "Ansible", "hide": "hide"}
            if pre_response.has_key("type_ct") and pre_response.get("type_ct") == "1":
                if pre_response.has_key("area"):
                    para_dict.append({"name": "area", "format": "", "default1": pre_response.get("area"), "output": "",
                                      "type": "radio", "example": "(Optional)", "desc": "Area", "mandatory": "no",
                                      "hide": "hide", "send": "yes",
                                      "options": [{"label": "Data Center", "value": "datacenter"},
                                                  {"label": "Cloud", "value": "cloud"},
                                                  {"label": "Campus", "value": "campus"},
                                                  {"label": "Branch", "value": "branch"}]})
                else:
                    para_dict.append(
                        {"name": "area", "format": "", "default1": "datacenter", "output": "", "type": "radio",
                         "example": "(Optional)", "desc": "Area", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": [{"label": "Data Center", "value": "datacenter"},
                                     {"label": "Cloud", "value": "cloud"}, {"label": "Campus", "value": "campus"},
                                     {"label": "Branch", "value": "branch"}]})
            elif pre_response.get("type_ct") not in ["2", "ansible"]:
                para_dict.append({"name": "area", "format": "", "default1": "datacenter", "output": "", "type": "radio",
                                  "example": "(Optional)", "desc": "Area", "mandatory": "no", "hide": "hide",
                                  "send": "yes", "options": [{"label": "Data Center", "value": "datacenter"},
                                                             {"label": "Cloud", "value": "cloud"},
                                                             {"label": "Campus", "value": "campus"},
                                                             {"label": "Branch", "value": "branch"}]})
            if pre_response.has_key("template") and pre_response.has_key("customer"):
                print "Here 1"
                options = []
                template_list = get_template_list(pre_response["customer"], pre_response.get("type_ct"),
                                                  pre_response.get("area"))
                for each in template_list:
                    dict1 = {}
                    if each.has_key("value"):
                        dict1["label"] = each["value"]
                        dict1["value"] = each["key"]
                        dict1["disabled"] = each["disabled"]
                        options.append(dict1)
                para_dict.append(
                    {"name": "template", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Service", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": options, "default1": pre_response["template"]})
            elif pre_response.has_key("templateid") and pre_response["templateid"] != "" and pre_response.has_key(
                    "customer"):
                print "Here 2"

                options = []
                template_list = get_template_list(pre_response["customer"], "2", pre_response.get("area"))
                for each in template_list:
                    dict1 = {}
                    if each.has_key("value"):
                        dict1["label"] = each["value"]
                        dict1["value"] = each["key"]
                        dict1["disabled"] = each["disabled"]
                        options.append(dict1)
                para_dict.append(
                    {"name": "template", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Service", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": options, "default1": pre_response["templateid"]})

            else:
                print "Here 3"
                if pre_response.has_key("customer") and pre_response.has_key("type_ct"):
                    options = []
                    template_list = get_template_list(pre_response["customer"], pre_response.get("type_ct"), "datacenter")
                    # print template_list
                    for each in template_list:
                        dict1 = {}
                        if each.has_key("value"):
                            dict1["label"] = each["value"]
                            dict1["value"] = each["key"]
                            dict1["disabled"] = each["disabled"]
                            options.append(dict1)
                else:
                    options = []
                    template_list = get_template_list(pre_response["customer"], type="1" , role="datacenter")
                    for each in template_list:
                        dict1 = {}
                        if each.has_key("value"):
                            dict1["label"] = each["value"]
                            dict1["value"] = each["key"]
                            dict1["disabled"] = each["disabled"]
                            options.append(dict1)
                para_dict.append(
                    {"name": "template", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Service", "mandatory": "no", "send": "yes", "hide": "hide",
                     "options": options})
            if pre_response.has_key("template"):
                if "-" in pre_response["template"]:
                    x = pre_response["template"].split("-")
                    template_id = x[0]
                    plat_index = int(x[1])
                else:
                    template_id = pre_response["template"]
            if pre_response.has_key("template") and pre_response["template"] != "":
                print ">>>>",template_id
                template_name = template_db.objects.values_list("ext_name", "ext_label", "ext_value").filter(
                    id=int(template_id)).last()
                if template_name[0]:
                    et_name = template_name[0]
                    et_lbl = template_name[1].split(",")
                    et_vlu = template_name[2].split(",")
                    et_dict = zip(et_lbl, et_vlu)
                    options22 = []
                    for ele in et_dict:
                        dict1 = {}
                        dict1["label"] = ele[0]
                        dict1["value"] = ele[1].strip()
                        options22.append(dict1)
                    if pre_response.has_key("ext[]"):
                        new_optn = []
                        for opt in options22:
                            tmp_opt = opt
                            if opt.get("value") in pre_response.getlist("ext[]"):
                                tmp_opt["checked"] = "checked"
                            new_optn.append(tmp_opt)
                        para_dict.append(
                            {"name": "ext", "format": "", "default1": "", "output": "",
                             "type": "checkbox", "example": "(Optional)", "desc": et_name, "mandatory": "no",
                             "send": "yes", "hide": "hide", "options": new_optn})
                    elif len(options22) >= 3 and pre_response.has_key("ext"):
                        para_dict.append(
                                {"name": "ext", "format": "", "default1": pre_response.get("ext"), "output": "",
                                 "type": "dropdown", "example": "(Optional)", "desc": et_name, "mandatory": "no",
                                 "send": "yes", "hide": "hide", "options": options22})
                    else:
                        if len(options22) >= 3 and template_id == "1247" :
                            para_dict.append(
                                {"name": "ext", "format": "", "default1": "", "output": "", "type": "checkbox",
                                 "example": "(Optional)", "desc": et_name, "mandatory": "no", "send": "no",
                                 "hide": "hide", "options": options22})
                        elif len(options22) >= 3 :
                            para_dict.append(
                                {"name": "ext", "format": "", "default1": "", "output": "", "type": "dropdown",
                                 "example": "(Optional)", "desc": et_name, "mandatory": "no", "send": "no",
                                 "hide": "hide", "options": options22})
                        else:
                            para_dict.append(
                                {"name": "ext", "format": "", "default1": "", "output": "", "type": "radio",
                                 "example": "(Optional)", "desc": et_name, "mandatory": "no", "send": "no",
                                 "hide": "hide", "options": options22})
            if pre_response.has_key("template") and pre_response["template"] != "":
                q1 = template_db.objects.filter(id=int(template_id), type=1, tag="provisioning_workflow").last()
                if q1:
                    if pre_response.has_key("ext") and (
                            pre_response.get("ext") == "add_vlan" or pre_response.get("ext") == "rem_vlan"):
                        a = 22
                        # para_dict.append({"name": "config_action", "format": "", "default1": "", "output": "",
                        #  "type": "dropdown", "example": "(Optional)", "desc": "Action","mandatory":"no","hide":"hide","options":[{"label":"Reservation","value":"reserve"},{"label":"Provision","value":"provision"},{"label":"Provision and Activation","value":"provision_activation"},{"label":"Activation","value":"activation"},{"label":"De-Provisioning","value":"deprovision"}]})
                    elif 'config_action' in pre_response:
                        para_dict.append(
                            {"name": "config_action", "format": "", "default1": pre_response['config_action'], "output": "", "type": "dropdown",
                             "example": "(Optional)", "desc": "Action", "mandatory": "no", "hide": "hide","send": "yes",
                             "options": [{"label": "Reservation", "value": "reserve"},
                                         {"label": "Provision", "value": "provision"},
                                        # {"label": "Provision and Activation", "value": "provision_activation"},
                                         {"label": "Activation", "value": "activation"},
                                         {"label": "Reservation for De-Provision", "value": "deprovision_reservation"},
                                         {"label": "De-Provision", "value": "deprovision"},
                                         {"label": "Leaf Port Status", "value": "leaf_port_status"}]})
                    else:
                        para_dict.append(
                            {"name": "config_action", "format": "", "default1": "", "output": "", "type": "dropdown",
                             "example": "(Optional)", "desc": "Action", "mandatory": "no", "hide": "hide","send": "yes",
                             "options": [{"label": "Reservation", "value": "reserve"},
                                         {"label": "Provision", "value": "provision"},
                                        # {"label": "Provision and Activation", "value": "provision_activation"},
                                         {"label": "Activation", "value": "activation"},
                                         {"label": "Reservation for De-Provision", "value": "deprovision_reservation"},
                                         {"label": "De-Provision", "value": "deprovision"},
                                         {"label": "Leaf Port Status", "value": "leaf_port_status"}]})

            if pre_response.has_key("scope"):
                para_dict.append({"note": "", "default1": "single_device", "name": "scope", "type": "hidden",
                                  "options": [{"value": "single_device", "label": "Single Device"},
                                              {"value": "controller", "label": "Controller"},
                                              {"value": "network", "label": "Network"}], "desc": "Scope"})
            else:
                para_dict.append({"note": "", "default1": "single_device", "name": "scope", "type": "hidden",
                                  "options": [{"value": "single_device", "label": "Single Device"},
                                              {"value": "controller", "label": "Controller"},
                                              {"value": "network", "label": "Network"}], "desc": "Scope"})
            if pre_response.has_key("template") and pre_response["template"] != "":
                from mysite.models import ApicIpDb
                options1 = []
                entry = ApicIpDb.objects.all()
                if entry:
                    for dict in entry:
                        dict1 = {}
                        dict1["label"] = dict.label
                        dict1["value"] = dict.name
                        options1.append(dict1)
                template_name = template_db.objects.values_list("name", "template").filter(id=int(template_id)).last()
                if template_name and response.session["customer"] == "stanford":
                    options1 = [{"label":"300P", "value":"300P"}, {"label":"500P", "value":"500P"}]
                    para_dict.append(
                        {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "dropdown",
                         "example": "(Optional)", "desc": "Site", "mandatory": "no", "hide": "hide",
                         "options": options1})
                # elif template_name and "ACI" in template_name[0] or "ACI" in template_name[1]:
                #     para_dict.append(
                #         {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "dropdown",
                #          "example": "(Optional)", "desc": "Location", "mandatory": "no", "hide": "hide",
                #          "options": options1})
                #       para_dict.append(
                #           {"name": "existing_sr", "format": "", "default1": "yes", "output": "", "type": "radio",
                #            "example": "(Optional)", "desc": "Existing Service Request", "mandatory": "no", "hide": "hide",
                #            "options":  [{"value": "yes", "label": "Yes "},
                #                           {"value": "no", "label": "No"}]})
                      # para_dict.append(
                      #     {"name": "reservation_duration", "format": "", "default1": "", "output": "", "type": "dropdown",
                      #      "example": "(Optional)", "desc": "Reservation Duration", "mandatory": "no", "hide": "hide",
                      #      "options": [{"value":"permanant","label":"Permanant"},
                      #                  {"value":"1month","label":"1 Month"},
                      #                  {"value": "3month", "label": "3 Month"},
                      #                  {"value": "6month", "label": "6 Month"},
                      #                  {"value": "1year", "label": "1 Year"}]})
                elif template_name and "Provision Cloud" in template_name[0]:
                    inp1 = {}
                    inp1["name"] = 'group'
                    inp1["format"] = 'default1'
                    inp1["desc"] = 'Group'
                    inp1["default1"] = 'application'
                    inp1["type"] = 'radio'
                    inp1["options"] = [{"value": "application", "label": "Application"},
                                       {"value": "it", "label": "IT Infrastructure"}]
                    para_dict.append(inp1)
                    para_dict.append(
                        {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "dropdown",
                         "example": "(Optional)", "desc": "Location", "mandatory": "no", "hide": "hide",
                         "options": options1})


                # elif (pre_response.has_key("type_ct") and pre_response["type_ct"] == "1") or not pre_response.has_key(
                #         "type_ct"):
                #         para_dict.append(
                #             {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "dropdown",
                #              "example": "(Optional)", "desc": "Location", "mandatory": "no", "hide": "hide",
                #              "options": options1})
            # elif (pre_response.has_key("type_ct") and pre_response["type_ct"] == "1") or not pre_response.has_key(
            #         "type_ct"):
            #     from mysite.models import ApicIpDb
            #     options1 = []
            #     entry = ApicIpDb.objects.all()
            #     if entry:
            #         for dict in entry:
            #             dict1 = {}
            #             dict1["label"] = dict.label
            #             dict1["value"] = dict.name
            #             options1.append(dict1)
            #         para_dict.append(
            #             {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "dropdown",
            #              "example": "(Optional)", "desc": "Location", "mandatory": "no", "hide": "hide",
            #              "options": options1})
            if pre_response.has_key("template") and pre_response["template"] != "":
                template_name = template_db.objects.values_list("name", "template").filter(id=int(template_id)).last()
                if template_name:
                    print ">>>>>Template naME", template_name
                if template_name and "Provision Cloud" in template_name[1]:
                    inp1 = {}
                    inp1["name"] = 'cloudserviceprovider'
                    inp1["format"] = 'default1'
                    inp1["desc"] = 'Cloud Provider'
                    inp1["default1"] = 'AWS Direct Connect'
                    inp1["type"] = 'dropdown'
                    inp1["options"] = [{"value": "AWS Direct Connect", "label": "AWS Direct Connect"},
                                       {"value": "Azure ExpressRoute", "label": "Azure ExpressRoute"},
                                       {"value": "Google Dedicated Interconnect",
                                        "label": "Google Dedicated Interconnect"},
                                       {"value": "Google VPC with IPsec VPN", "label": "Google VPC with IPsec VPN"},
                                       {"value": "Oracle FastConnet", "label": "Oracle FastConnet"},
                                       {"value": "vCloud Direct Connect", "label": "vCloud Direct Connect"},
                                       {"value": "Other", "label": "Other"}]
                    para_dict.append(inp1)
                elif template_name and "Verification" in template_name[1]:
                    print "here in Verification "
                    sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue__in=[2,3,4]).distinct()
                    project_options = []
                    t = {}
                    t["value"] = ""
                    t["label"] = "Select Project No."
                    project_options.append(t)
                    if sentry:
                        for entry in sentry:
                            t = {}
                            t["value"] = entry[0]
                            t["label"] = entry[0]
                            project_options.append(t)
                    para_dict.append(
                        {"name": "project_no", "format": "", "default1": "", "output": "",
                         "type": "dropdown-autocomplete",
                         "example": "", "desc": "Project Name", "mandatory": "yes",
                         "vmessage": "Please Select Service Request No.", "options": project_options})
                    if pre_response.has_key("devices"):
                        para_dict.append(
                            {"name": "devices", "format": "", "default1": pre_response.get("devices"), "output": "",
                             "type": "tags-auto", "example": "Please hit enter after each IP/Host",
                             "desc": "Datacenter", "mandatory": "no", "hide": "hide"})
                    else:
                        para_dict.append(
                            {"name": "devices", "format": "", "default1": "", "output": "", "type": "tags-auto",
                             "example": "Please hit enter after each IP/Host", "desc": "Datacenter", "mandatory": "no",
                             "hide": "hide"})
                elif template_name and "Cisco to Cisco Port Migration" in template_name[1] or "Cisco to Cisco Migration 2" in template_name[1]:
                    a =1
                    para_dict.append({"name": "new_platform", "format": "default1", "desc": "New Platform",
                                      "default1": "", "type": "dropdown",
                                      "options": [{"value": "9300", "label": "C9300"},
                                                  {"value": "9300_stack", "label": "C9300 Stack"},
                                                  {"value": "9400", "label": "C9410"},{"value": "4500", "label": "C4500"},{"value": "3850", "label": "C3850"},]})
                    para_dict.append({"name": "upstream_ios", "format": "default1", "desc": "Upstream IOS",
                                      "default1": "", "type": "dropdown",
                                      "options": [{"value": "xr", "label": "XR-OS"},
                                                  {"value": "ios", "label": "IOS"},
                                                  {"value": "nx", "label": "NX-OS"},]})
                    para_dict.append({"name": "no_of_device", "format": "default1", "desc": "Number of Upstream Router",
                                      "default1": "1", "type": "dropdown",
                                      "options": [{"value": "1", "label": "1"},
                                                  {"value": "2", "label": "2"},
                                                  {"value": "3", "label": "3"},{"value": "4", "label": "4"},{"value": "5", "label": "5"},]})
                    para_dict.append({"name": "routing", "format": "default1", "desc": "Routing",
                                      "default1": "OSPF", "type": "radio",
                                      "options": [{"value": "OSPF", "label": "OSPF"},
                                                  {"value": "BGP", "label": "BGP", 'hide':'hide', 'trigger':['local_as_num']},
                                                  {"value": "EIGRP", "label": "EIGRP"},]})

                    para_dict.append(
                        {"name": "local_as_num", "format": "", "default1": "",
                         "type": "text", "example": "",
                         "desc": "Local AS Number", "mandatory": "no", "hide": "hide"})

                    para_dict.append(
                        {"name": "distro_sw_port", "format": "", "default1": "",
                         "type": "text", "example": "",
                         "desc": "Uplink Router Port", "mandatory": "no", "hide": "hide"})
                    para_dict.append(
                        {"name": "sw01_skip_interface", "format": "", "default1": "",
                         "type": "text", "example": "",
                         "desc": "SW01 Skip Interface List", "mandatory": "no", "hide": "hide"})
                    para_dict.append(
                        {"name": "sw02_skip_interface", "format": "", "default1": "",
                         "type": "text", "example": "",
                         "desc": "SW02 Skip Interface List", "mandatory": "no", "hide": "hide"})
                elif template_name and "Consolidation" in template_name[1]:
                    a =1
                    para_dict.append(
                        {"name": "distribution_sw_interface", "format": "", "default1": "",
                         "type": "text", "example": "",
                         "desc": "Distribution Switch Interface", "mandatory": "no", "hide": "hide"})
                    # para_dict.append(
                    #     {"name": "hardware_refresh", "format": "", "default1": "",
                    #      "type": "radio", "example": "",
                    #      "desc": "Hardware Refresh", "mandatory": "no", "hide": "hide",
                    #      "options":[{"value":"Precheck","label":"Precheck","hide":"hide","trigger":["switch_name"]},
                    #                 {"value":"Postcheck","label":"Postcheck"}]})
                    # para_dict.append(
                    #     {"name": "switch_name", "format": "", "default1": "",
                    #      "type": "text", "example": "",
                    #      "desc": "Switch Name and IDF", "mandatory": "no", "hide": "hide"})

                elif template_name and "Migration" in template_name[1]:
                    a =1
                    # Add Inputs for Cisco to Cisco Migration
                    para_dict.append({"name": "new_platform", "format": "default1", "desc": "New Platform",
                                      "default1": "", "type": "dropdown",
                                      "options": [{"value": "9300", "label": "C9300"},
                                                  {"value": "9300-stack", "label": "C9300-stack"},
                                                  {"value": "9410", "label": "C9410"},
                                                  {"value": "9404", "label": "C9404"},
                                                  {"value": "9407", "label": "C9407"}]})
                    para_dict.append({"name": "uplink_modules", "send": "", "format": "default1", "desc": "Uplink Modules",
                                      "default1": "yes", "type": "dropdown",
                                        "options": [{"value": "copper", "label": "Copper"}, {"value": "1G", "label": "1G"},
                                                    {"value": "10G", "label": "10G"}, {"value": "25G", "label": "25G"},
                                                    {"value": "40G", "label": "40G"}]})
                    para_dict.append({"name": "conversion_method", "send": "", "format": "default1", "desc": "Conversion Method",
                                      "default1": "ssh", "type": "radio",
                                        "options": [{"value": "ssh", "label": "SSH","hide":"hide","trigger":["devices"]}, {"value": "upload_file", "label": "Upload File"}]})
                    # para_dict.append({"name": "config_display", "send": "", "format": "default1", "desc": "Type",
                    #                     "default1": "configuration", "type": "radio",
                    #                     "options": [{"value": "configuration", "label": "Configuration"}, {"value": "port_matrix", "label": "Port Matrix"}]})
                    para_dict.append(
                        {"name": "devices", "format": "", "default1":"", "output": "",
                         "type": "tags-auto", "example": "Please hit enter after each IP/Host",
                         "desc": "Datacenter", "mandatory": "no", "hide": "hide"})


                elif template_name and "Access Campus Switch Provisioning - Bulk(NEW)" == template_name[1]:
                    a =1
                    # Add Inputs for Cisco to Cisco Migration
                    para_dict.append({"name": "new_platform", "format": "default1", "desc": "New Platform",
                     "default1": "", "type": "dropdown",
                     "options": [{"value": "9300", "label": "C9300"}, {"value": "9300-stack", "label": "C9300-stack"},
                                 {"value": "9410", "label": "C9410"}, {"value": "9404", "label": "C9404"},
                                 {"value": "9407", "label": "C9407"}]})

                elif template_name and "Bulk" in template_name[1]:
                    a =1
                elif pre_response.has_key("config_action") and pre_response["config_action"]=="leaf_port_status" and "devices" in pre_response:
                    para_dict.append(
                        {"name": "devices", "format": "", "default1": pre_response.get("devices"), "output": "",
                         "type": "tags-auto", "example": "Please hit enter after each IP/Host",
                         "desc": "Datacenter", "mandatory": "no", "hide": "hide"})
                elif pre_response.has_key("devices"):
                    para_dict.append(
                        {"name": "devices", "format": "", "default1": pre_response.get("devices"), "output": "",
                         "type": "tags-auto", "example": "Please hit enter after each IP/Host",
                         "desc": "Datacenter", "mandatory": "no", "hide": "hide"})
                elif pre_response.get("type_ct") != "2":
                    para_dict.append(
                        {"name": "devices", "format": "", "default1": "", "output": "", "type": "tags-auto",
                         "example": "Please hit enter after each IP/Host", "desc": "Datacenter", "mandatory": "no",
                         "hide": "hide"})


            # else:
            #     para_dict.append({"name": "devices", "format": "", "default1": "", "output": "", "type": "tags-auto",
            #                       "example": "Please hit enter after each IP/Host", "desc": "Device IP or Hostname",
            #                       "mandatory": "no", "hide": "hide"})
        #Clone Request
        if req_type == "2":
            para_dict.append(
                {"name": "taskid", "format": "", "default1": "", "output": "", "type": "text", "example": "",
                 "desc": "Existing Service Request No.", "mandatory": "yes"})
            para_dict.append(
                {"name": "taskid_new", "format": "", "default1": "", "output": "", "type": "text", "example": "",
                 "desc": "New Service Request No.", "mandatory": "yes"})
        #Task Without Request Number
        if req_type == "3":
            template_id = 0
            subuser = getusersubdept(response)
            if str(getuserdept(response)) == "provision":
                if subuser == "network" and pre_response.has_key("template"):
                    para_dict.append({"name": "template", "format": "", "output": "", "type": "dropdown", "example": "",'length':'full',
                                      "desc": "Service request", "mandatory": "no", "hide": "hide", "send": "yes",
                                      "default1": pre_response["template"],
                                      "options": [{"label": "TSO Provisioning", "value": "1"},
                                                  {"label": "Bulk TSO Provisioning", "value": "2"},
                                                  {"label": "Provision APs", "value": "8"},
                                                  {"label": "Port Provisioning Based On MAC", "value": "9"},
                                                  {"label": "TSO Deprovisioning", "value": "5"},
                                                  {"label": "Upload Patching Matrix", "value": "6"},
                                                  {"label": "Add VLAN", "value": "3"},
                                                  {"label": "TSO Status", "value": "4"},
                                                  {"label": "Patching Matrix Filter", "value": "7"}
                                                  ]})
                elif subuser == "network":
                    para_dict.append({"name": "template", "format": "", "output": "", "type": "dropdown", "example": "",'length':'full',
                                      "desc": "Service request", "mandatory": "no", "hide": "hide", "send": "yes",
                                      "default1": "",
                                      "options": [{"label": "TSO Provisioning", "value": "1"},
                                                  {"label": "Bulk TSO Provisioning", "value": "2"},
                                                  {"label": "Provision APs", "value": "8"},
                                                  {"label": "Port Provisioning Based On MAC", "value": "9"},
                                                  {"label": "TSO Deprovisioning", "value": "5"},
                                                  {"label": "Upload Patching Matrix", "value": "6"},
                                                  {"label": "Add VLAN", "value": "3"},
                                                  {"label": "TSO Status", "value": "4"},
                                                  {"label": "Patching Matrix Filter", "value": "7"}
                                                  ]})
                elif pre_response.has_key("template"):
                    para_dict.append({"name": "template", "format": "", "output": "", "type": "dropdown", "example": "",'length':'full',
                                      "desc": "Service request", "mandatory": "no", "hide": "hide", "send": "yes",
                                      "default1": pre_response["template"],
                                      "options": [{"label": "TSO Provisioning", "value": "1"},
                                                  {"label": "Bulk TSO Provisioning", "value": "2"},
                                                  {"label": "TSO Deprovisioning", "value": "4"},
                                                  {"label": "TSO Status", "value": "3"},
                                                  ]})

                else:
                    para_dict.append(
                        {"name": "template", "format": "", "default1": "", "output": "", "type": "dropdown",'length':'full',
                         "example": "", "desc": "Service request", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": [{"label": "TSO Provisioning", "value": "1"},
                                     {"label": "Bulk TSO Provisioning", "value": "2"},
                                     {"label": "TSO Deprovisioning", "value": "4"},
                                     {"label": "TSO Status", "value": "3"}, ]})
                if (not pre_response.has_key("template")) or (
                        pre_response.has_key("template") and pre_response["template"] not in ["2", "3", "4", "6", "7", "8","9"]):
                    para_dict.append(
                        {"name": "tsoid", "format": "", "default1": "", "output": "", "type": "text",'length':'full',
                         "note": "You will find this number on the TSO",
                         "desc": "TSO ID", "mandatory": "no", "example": "Ex: L067-02-08-26"})
                    device_opt = []
                    if subuser == "enduser":
                        device_opt = [{"label": "End User", "value": "1", "isdevider": "1"},
                                      {"label": "Desktop", "value": "Desktop"},
                                      {"label": "Printer", "value": "Printer"},
                                      {"label": "VoIP Phone", "value": "voip_phone"}, ]
                    elif subuser == "vendor":
                        device_opt = [{"label": "Vendor", "value": "2", "isdevider": "1"},
                                      {"label": "RTLS", "value": "RTLS"},
                                      {"label": "POS", "value": "POS"},
                                      {"label": "Non-Medical", "value": "Non-Medical"},
                                      {"label": "BMS (SCADA, HVAC)", "value": "Struxware"},
                                      ]
                    elif subuser == "medical":
                        device_opt = [{"label": "Medical", "value": "3", "isdevider": "1"},
                                      {"label": "Philips", "value": "Philips"},
                                      {"label": "Medical", "value": "Medical"}, ]
                    elif subuser == "network":

                        device_opt = [{"label": "Network", "value": "4", "isdevider": "1"},
                                      {"label": "SUMCNet User", "value": "SUMCnet Users"},
                                      {"label": "Access Points", "value": "Access Points"},
                                      {"label": "Internal Infra", "value": "internal infra"},
                                      {"label": "End User", "value": "1", "isdevider": "1"},
                                      {"label": "Desktop", "value": "Desktop"},
                                      {"label": "Printer", "value": "Printer"},
                                      {"label": "VoIP Phone", "value": "voip_phone"},
                                      {"label": "Vendor", "value": "2", "isdevider": "1"},
                                      {"label": "RTLS", "value": "RTLS"},
                                      {"label": "POS", "value": "POS"},
                                      {"label": "Non-Medical", "value": "Non-Medical"},
                                      {"label": "BMS (SCADA, HVAC)", "value": "Struxware"},
                                      {"label": "Medical", "value": "3", "isdevider": "1"},
                                      {"label": "Philips", "value": "Philips"},
                                      {"label": "Medical", "value": "Medical"},
                                      ]

                    para_dict.append(
                        {"name": "devicetype", "format": "", "default1": "", "output": "", "type": "dropdown",'length':'full',
                         "example": "", "desc": "Device Type", "mandatory": "no", "hide": "hide",
                         "options": device_opt})
                    #
                    para_dict.append(
                        {"name": "description", "format": "", "default1": "", "output": "", "type": "text",'length':'full',
                         "example": "optional", "desc": "Description", "mandatory": "no", "hide": "hide"})
                    if subuser == "network":
                        para_dict.append({"note": "DHCP", "type": "radio", "name": "dhcp", "default1": "dhcp",
                                          "desc": "IP Address Type",'length':'full',
                                          "options": [{"label": "DHCP", "value": "dhcp", "hide": "hide"},
                                                      {"label": "DHCP/MAC", "value": "dhcp/mac", "hide": "hide",
                                                       "trigger": ["ip", "mac"]},
                                                      {"label": "Static", "value": "static", "hide": "hide",
                                                       "trigger": ["ip"]}]})
                        para_dict.append({"type": "text", "name": "ip", "desc": "IP", "example": "",'length':'full',
                                          "validate": "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                                          "csend": "", "extraclass": "color-blue", "hide": "hide", "rhide": "hide",
                                          "vmessage": "Enter Valid IP Address", "default1": ""})
                        para_dict.append({"type": "text", "name": "mac", "desc": "MAC", "example": "", "csend": "",'length':'full',
                                          "extraclass": "color-blue", "hide": "hide", "rhide": "hide", "default1": ""})
                        # para_dict.append({"type": "text", "name": "manufacturer", "desc": "Manufacturer", "example": '(Optional)' , "pattern": "",  "csend": "yes", "extraclass": "color-blue", "hide": "hide", "rhide": "hide", "default1": ""})
                        # para_dict.append({"type": "text", "name": "model", "desc": "Model", "example": '(Optional)' , "pattern": "",  "csend": "yes", "extraclass": "color-blue", "hide": "hide", "rhide": "hide", "default1": ""})
                        para_dict.append(
                            {"type": "radio", "name": "overwite", "desc": "Overwrite Configuration", "default1": "no",'length':'full',
                             "options": [{"label": "No", "value": "no"}, {"label": "Yes", "value": "yes"}, ]})
                    para_dict.append(
                        {"type": "radio", "name": "connectivity", "desc": "Test Connectivity", "default1": "no",'length':'full',
                         "options": [{"label": "No", "value": "no"},
                                     {"label": "Yes", "value": "yes", "hide": "hide", "trigger": ["test_ip"]}, ]})
                    para_dict.append(
                        {"type": "text", "name": "test_ip", "desc": "IP Address", "default1": "", })
                if pre_response.has_key("template") and pre_response["template"] == "2":
                    para_dict.append(
                        {"type": "radio", "name": "overwite", "desc": "Overwrite Configuration", "example": '',
                         "pattern": "",
                         "csend": "", "hide": "hide", "default1": "no",
                         "options": [{"label": "No", "value": "no"}, {"label": "Yes", "value": "yes"}, ]})
                elif pre_response.has_key("template") and pre_response["template"] == "4":
                    para_dict.append(
                        {"type": "text", "name": "tso_id", "desc": "TSO ID", "example": '',
                         "pattern": "",
                         "csend": "", "hide": "hide", "default1": ""})
                elif pre_response.has_key("template") and pre_response["template"] == "9":
                    floor_options= [{"label": "1", "value": "1"}, {"label": "2", "value": "2"},
                                   {"label": "3", "value": "3"}, {"label": "4", "value": "4"},
                                   {"label": "5", "value": "5"}, {"label": "6", "value": "6"},
                                   {"label": "7", "value": "7"}, {"label": "8", "value": "8"}]

                    device_opt = [{"label": "Network", "value": "4", "isdevider": "1"},
                                  {"label": "SUMCNet User", "value": "SUMCnet Users"},
                                  {"label": "Access Points", "value": "Access Points"},
                                  {"label": "Internal Infra", "value": "internal infra"},
                                  {"label": "End User", "value": "1", "isdevider": "1"},
                                  {"label": "Desktop", "value": "Desktop"},
                                  {"label": "Printer", "value": "Printer"},
                                  {"label": "VoIP Phone", "value": "voip_phone"},
                                  {"label": "Vendor", "value": "2", "isdevider": "1"},
                                  {"label": "RTLS", "value": "RTLS"},
                                  {"label": "POS", "value": "POS"},
                                  {"label": "Non-Medical", "value": "Non-Medical"},
                                  {"label": "BMS (SCADA, HVAC)", "value": "Struxware"},
                                  {"label": "Medical", "value": "3", "isdevider": "1"},
                                  {"label": "Philips", "value": "Philips"},
                                  {"label": "Medical", "value": "Medical"},
                                  ]

                    para_dict.append(
                        {"name": "device_type", "format": "", "default1": "", "output": "", "type": "dropdown",
                         'length': 'full',
                         "example": "", "desc": "Device Type", "hide": "hide",
                         "options":device_opt })
                    para_dict.append(
                        {"type": "text", "name": "mac_address", "desc": "Mac Address", "example": "", "length": "full",
                         "pattern": "",
                         "csend": "", "hide": "hide", "default1": ""})
                    para_dict.append(
                        {"type": "dropdown", "name": "floor", "desc": "Floor", "example": '',
                         "pattern": "","length": "full",
                         "csend": "", "hide": "hide", "default1": "","options":floor_options})

                elif pre_response.has_key("template") and pre_response["template"] == "3":
                    para_dict.append(
                        {"type": "text", "name": "device_type", "desc": "Device Type", "example": '',
                         "pattern": "",
                         "csend": "", "hide": "hide", "default1": ""})
                    para_dict.append(
                        {"type": "text", "name": "vrf", "desc": "VRF Name", "default1": ""})
                    para_dict.append(
                        {"type": "text", "name": "vlanid", "desc": "Vlan No.", "default1": "", })
                elif pre_response.has_key("template") and pre_response["template"] == "7":
                    options = [{"value": "stationid", "label": "TSO ID"}, {"value": "stanidf", "label": "Stanford IDF"},
                               {"value": "archidf", "label": "Architechture IDF"}, {"value": "rack", "label": "Rack"}]
                    para_dict.append(
                        {"type": "dropdown", "name": "filtername", "desc": "Type", "example": "Example",
                         "condition": "date",
                         "trigger": ["datetime", "abc"], "rcondition": "date",
                         "rtrigger": "value", "hide": "hide", "rhide": "hide", "options": options})
                    para_dict.append(
                        {"newline": "yes", "type": "text", "name": "value", "desc": "Value to Search", "example": "",
                         "pattern": "",
                         "csend": "yes", "extraclass": "color-blue", "hide": "hide", "rhide": "hide", "default1": ""})
                elif pre_response.has_key("template") and pre_response["template"] == "6":
                    idf_options = [{"label": "0C011", "value": "0C011"}, {"label": "0F023", "value": "0F023"},
                                   {"label": "0H010", "value": "0H010"}, {"label": "0G010", "value": "0G010"},
                                   {"label": "1C010", "value": "1C010"}, {"label": "1F011", "value": "1F011"},
                                   {"label": "1F015", "value": "1F015"}, {"label": "1D040", "value": "1D040"},
                                   {"label": "1G010", "value": "1G010"}, {"label": "2B016", "value": "2B016"},
                                   {"label": "2F011", "value": "2F011"}, {"label": "2G026", "value": "2G026"},
                                   {"label": "2F025", "value": "2F025"}, {"label": "2D058", "value": "2D058"},
                                   {"label": "3G022", "value": "3G022"}, {"label": "3F010", "value": "3F010"},
                                   {"label": "3F021", "value": "3F021"}, {"label": "3D013", "value": "3D013"},
                                   {"label": "4H042", "value": "4H042"}, {"label": "4F042", "value": "4F042"},
                                   {"label": "4B042", "value": "4B042"}, {"label": "4D042", "value": "4D042"},
                                   {"label": "5H042", "value": "5H042"}, {"label": "5F042", "value": "5F042"},
                                   {"label": "5D042", "value": "5D042"}, {"label": "5B042", "value": "5B042"},
                                   {"label": "6H042", "value": "6H042"}, {"label": "6F042", "value": "6F042"},
                                   {"label": "6D042", "value": "6D042"}, {"label": "6B042", "value": "6B042"},
                                   {"label": "7H042", "value": "7H042"}, {"label": "7F042", "value": "7F042"},
                                   {"label": "7D042", "value": "7D042"}, {"label": "7B042", "value": "7B042"}]
                    para_dict.append(
                        {"type": "dropdown", "name": "idfno", "desc": "IDF No.", "default1": "",
                         "options": idf_options})
                    para_dict.append(
                        {"type": "radio", "name": "overwrite", "desc": "Overwrite Entries", "example": '',
                         "default1": "no",
                         "options": [{"label": "No", "value": "no"}, {"label": "Yes", "value": "yes"}, ]})

                elif pre_response.has_key("template") and pre_response["template"] == "8":
                    idf_options = [{"label": "0C011", "value": "0C011"}, {"label": "0F023", "value": "0F023"},
                                   {"label": "0H010", "value": "0H010"}, {"label": "0G010", "value": "0G010"},
                                   {"label": "1C010", "value": "1C010"}, {"label": "1F011", "value": "1F011"},
                                   {"label": "1F015", "value": "1F015"}, {"label": "1D040", "value": "1D040"},
                                   {"label": "1G010", "value": "1G010"}, {"label": "2B016", "value": "2B016"},
                                   {"label": "2F011", "value": "2F011"}, {"label": "2G026", "value": "2G026"},
                                   {"label": "2F025", "value": "2F025"}, {"label": "2D058", "value": "2D058"},
                                   {"label": "3G022", "value": "3G022"}, {"label": "3F010", "value": "3F010"},
                                   {"label": "3F021", "value": "3F021"}, {"label": "3D013", "value": "3D013"},
                                   {"label": "4H042", "value": "4H042"}, {"label": "4F042", "value": "4F042"},
                                   {"label": "4B042", "value": "4B042"}, {"label": "4D042", "value": "4D042"},
                                   {"label": "5H042", "value": "5H042"}, {"label": "5F042", "value": "5F042"},
                                   {"label": "5D042", "value": "5D042"}, {"label": "5B042", "value": "5B042"},
                                   {"label": "6H042", "value": "6H042"}, {"label": "6F042", "value": "6F042"},
                                   {"label": "6D042", "value": "6D042"}, {"label": "6B042", "value": "6B042"},
                                   {"label": "7H042", "value": "7H042"}, {"label": "7F042", "value": "7F042"},
                                   {"label": "7D042", "value": "7D042"}, {"label": "7B042", "value": "7B042"}]
                    para_dict.append(
                        {"type": "dropdown", "name": "idfno", "desc": "IDF No.", "default1": "",
                         "options": idf_options})
            else:
                if response.session.has_key("customer") and response.session["customer"] != "":
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": response.session["customer"], "output": "",
                         "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                         "hide": "hide"})
                else:
                    if pre_response.has_key("customer"):
                        para_dict.append({"name": "customer", "format": "", "default1": defaultcustomer, "output": "",
                                          "type": "hidden", "example": "", "desc": "Customer/Department",
                                          "mandatory": "no", "hide": "hide", "send": "yes",
                                          "options": get_customer_options()})
                    else:
                        para_dict.append({"name": "customer", "format": "", "default1": defaultcustomer, "output": "",
                                          "type": "hidden", "example": "", "desc": "Customer/Department",
                                          "mandatory": "no", "hide": "hide", "send": "yes",
                                          "options": get_customer_options()})
                if pre_response.has_key("template_name"):
                    para_dict.append(
                        {"note": "If Template name is known", "default1": pre_response.get("template_name"),
                         "name": "template_name", "send": "yes", "type": "hidden", "options": [
                            {"trigger": ["type_ct", "template", "deviceip"], "hide": "hide", "value": "yes",
                             "label": "Yes"},
                            {"trigger": ["scope", "deviceip"], "hide": "hide", "value": "no", "label": "No"}],
                         "desc": "Do you know Template Name?"})
                else:
                    para_dict.append(
                        {"note": "If Template name is known", "default1": "yes", "name": "template_name", "send": "yes",
                         "type": "hidden", "options": [
                            {"trigger": ["type_ct", "template", "deviceip"], "hide": "hide", "value": "yes",
                             "label": "Yes"},
                            {"trigger": ["scope", "deviceip"], "hide": "hide", "value": "no", "label": "No"}],
                         "desc": "Do you know Template Name?"})
                if pre_response.has_key("type_ct"):
                    para_dict.append(
                        {"note": "", "default1": pre_response.get("type_ct"), "name": "type_ct", "send": "yes",
                         "type": "radio", "options": [{"value": "1", "label": "Configuration"},
                                                      {"value": "2", "label": "Troubleshooting"}], "desc": "Type"})
                else:
                    para_dict.append({"note": "", "default1": "1", "name": "type_ct", "send": "yes", "type": "radio",
                                      "options": [{"value": "1", "label": "Configuration"},
                                                  {"value": "2", "label": "Troubleshooting"}], "desc": "Type"})
                if pre_response.has_key("area"):
                    para_dict.append({"name": "area", "format": "", "default1": pre_response.get("area"), "output": "",
                                      "type": "radio", "example": "(Optional)", "desc": "Area", "mandatory": "no",
                                      "hide": "hide", "send": "yes",
                                      "options": [{"label": "Data Center", "value": "datacenter"},
                                                  {"label": "Cloud", "value": "cloud"},
                                                  {"label": "Campus", "value": "campus"},
                                                  {"label": "Branch", "value": "branch"}]})
                else:
                    para_dict.append(
                        {"name": "area", "format": "", "default1": "datacenter", "output": "", "type": "radio",
                         "example": "(Optional)", "desc": "Area", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": [{"label": "Data Center", "value": "datacenter"},
                                     {"label": "Cloud", "value": "cloud"}, {"label": "Campus", "value": "campus"},
                                     {"label": "Branch", "value": "branch"}]})
                if pre_response.has_key("template"):
                    if pre_response.has_key("customer"):
                        options = []
                        template_list = get_template_list(pre_response["customer"], pre_response.get("type_ct"),
                                                          pre_response.get("area"))
                        for each in template_list:
                            dict1 = {}
                            if each.has_key("value"):
                                dict1["label"] = each["value"]
                                dict1["value"] = each["key"]
                                dict1["disabled"] = each["disabled"]
                                options.append(dict1)
                    para_dict.append(
                        {"name": "template", "format": "", "output": "", "type": "dropdown-autocomplete", "example": "",
                         "desc": "Template", "mandatory": "no", "hide": "hide", "send": "yes", "options": options,
                         "default1": pre_response["template"]})
                else:
                    if pre_response.has_key("customer"):
                        options = []
                        template_list = get_template_list(pre_response["customer"], "1", "datacenter")
                        for each in template_list:
                            dict1 = {}
                            if each.has_key("value"):
                                dict1["label"] = each["value"]
                                dict1["value"] = each["key"]
                                dict1["disabled"] = each["disabled"]
                                options.append(dict1)
                    else:
                        options = []
                        template_list = get_template_list()
                        for each in template_list:
                            dict1 = {}
                            if each.has_key("value"):
                                dict1["label"] = each["value"]
                                dict1["value"] = each["key"]
                                dict1["disabled"] = each["disabled"]
                                options.append(dict1)
                    para_dict.append({"name": "template", "format": "", "default1": "", "output": "",
                                      "type": "dropdown-autocomplete", "example": "", "desc": "Template",
                                      "mandatory": "no", "send": "yes", "hide": "hide", "options": options})
                if pre_response.has_key("template") and pre_response["template"] != "":
                    if "-" in pre_response["template"]:
                        x = pre_response["template"].split("-")
                        template_id = x[0]
                        plat_index = int(x[1])
                    else:
                        template_id = pre_response["template"]
                    print ">>>>>>>", template_id
                    if "-" not in template_id:
                        template_name = template_db.objects.values_list("ext_name", "ext_label", "ext_value",
                                                                        "status").filter(id=int(template_id)).last()
                        if template_name[0]:
                            et_name = template_name[0]
                            et_lbl = template_name[1].split(",")
                            et_vlu = template_name[2].split(",")
                            et_dict = zip(et_lbl, et_vlu)
                            options22 = []
                            for ele in et_dict:
                                dict1 = {}
                                dict1["label"] = ele[0]
                                dict1["value"] = ele[1].strip()
                                options22.append(dict1)
                            if len(options22) >= 3:
                                para_dict.append(
                                    {"name": "ext", "format": "", "default1": "", "output": "", "type": "dropdown",
                                     "example": "(Optional)", "desc": et_name, "mandatory": "no", "hide": "hide",
                                     "options": options22})
                            else:
                                para_dict.append(
                                    {"name": "ext", "format": "", "default1": "", "output": "", "type": "radio",
                                     "example": "(Optional)", "desc": et_name, "mandatory": "no", "hide": "hide",
                                     "options": options22})
                    if "-" not in template_id:
                        print ">>>>>>>", template_id
                        q1 = template_db.objects.filter(id=int(template_id), type=1, tag="provisioning_workflow").last()
                        if q1:
                            para_dict.append({"name": "config_action", "format": "", "default1": "", "output": "",
                                              "type": "dropdown", "example": "(Optional)", "desc": "Action",
                                              "mandatory": "no", "hide": "hide",
                                              "options": [{"label": "Reservation", "value": "reserve"},
                                                          {"label": "Provision", "value": "provision"},
                                                          {"label": "Provision and Activation",
                                                           "value": "provision_activation"},
                                                          {"label": "Activation", "value": "activation"},
                                                          {"label": "De-Provision Reservation ", "value": "deprovision_reservation"},
                                                          {"label": "De-Provisioning", "value": "deprovision"}]})
                    if pre_response.has_key("scope"):
                        para_dict.append({"note": "", "default1": "single_device", "name": "hidden", "type": "hidden",
                                          "options": [{"value": "single_device", "label": "Single Device"},
                                                      {"value": "controller", "label": "Controller"},
                                                      {"value": "network", "label": "Network"}], "desc": "Scope"})
                    else:
                        para_dict.append({"note": "", "default1": "single_device", "name": "scope", "type": "hidden",
                                          "options": [{"value": "single_device", "label": "Single Device"},
                                                      {"value": "controller", "label": "Controller"},
                                                      {"value": "network", "label": "Network"}], "desc": "Scope"})

                    if "-" not in template_id:
                        template_name = template_db.objects.values_list("name").filter(id=int(template_id)).last()
                        if template_name and "ACI" in template_name[0]:
                            from mysite.models import ApicIpDb
                            options1 = []
                            entry = ApicIpDb.objects.all()
                            if entry:
                                for dict in entry:
                                    dict1 = {}
                                    dict1["label"] = dict.label
                                    dict1["value"] = dict.name
                                    options1.append(dict1)
                            para_dict.append(
                                {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "dropdown",
                                 "example": "(Optional)", "desc": "Device IP", "mandatory": "no", "hide": "hide",
                                 "options": options1})
                        if template_name and "ACI" in template_name[0]:
                            from mysite.models import ApicIpDb
                            options1 = []
                            entry = ApicIpDb.objects.all()
                            if entry:
                                for dict in entry:
                                    dict1 = {}
                                    dict1["label"] = dict.label
                                    dict1["value"] = dict.name
                                    options1.append(dict1)
                            para_dict.append(
                                {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "dropdown",
                                 "example": "(Optional)", "desc": "Location", "mandatory": "no", "hide": "hide",
                                 "options": options1})
                        elif template_name and "Provision Cloud" in template_name[0]:
                            from mysite.models import ApicIpDb
                            options1 = []
                            entry = ApicIpDb.objects.all()
                            if entry:
                                for dict in entry:
                                    dict1 = {}
                                    dict1["label"] = dict.label
                                    dict1["value"] = dict.name
                                    options1.append(dict1)
                            para_dict.append(
                                {"name": "area", "format": "", "default1": "datacenter", "output": "", "type": "radio",
                                 "example": "(Optional)", "desc": "Area", "mandatory": "no", "hide": "hide",
                                 "options": [{"label": "Data Center", "value": "datacenter"},
                                             {"label": "Cloud", "value": "cloud"},
                                             {"label": "Campus", "value": "campus"},
                                             {"label": "Branch", "value": "branch"}]})
                            para_dict.append(
                                {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "dropdown",
                                 "example": "(Optional)", "desc": "Location", "mandatory": "no", "hide": "hide",
                                 "options": options1})
                            para_dict.append(
                                {"name": "devices", "format": "", "default1": "", "output": "", "type": "tags-auto",
                                 "example": "Please hit enter after each IP/Host", "desc": "Device IP or Hostname",
                                 "mandatory": "no", "hide": "hide"})
                        elif (pre_response.has_key("type_ct") and pre_response[
                            "type_ct"] == "1") or not pre_response.has_key("type_ct"):
                            from mysite.models import ApicIpDb
                            options1 = []
                            entry = ApicIpDb.objects.all()
                            if entry:
                                for dict in entry:
                                    dict1 = {}
                                    dict1["label"] = dict.label
                                    dict1["value"] = dict.name
                                    options1.append(dict1)
                                para_dict.append({"name": "acilocation", "format": "", "default1": "", "output": "",
                                                  "type": "dropdown", "example": "(Optional)", "desc": "Location",
                                                  "mandatory": "no", "hide": "hide", "options": options1})
                        else:
                            para_dict.append(
                                {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "text",
                                 "example": "(Optional)", "desc": "Device IP", "mandatory": "no", "hide": "hide"})
                elif (pre_response.has_key("type_ct") and pre_response["type_ct"] == "1") or not pre_response.has_key(
                        "type_ct"):
                    from mysite.models import ApicIpDb
                    options1 = []
                    entry = ApicIpDb.objects.all()
                    if entry:
                        for dict in entry:
                            dict1 = {}
                            dict1["label"] = dict.label
                            dict1["value"] = dict.name
                            options1.append(dict1)
                        para_dict.append(
                            {"name": "acilocation", "format": "", "default1": "", "output": "", "type": "dropdown",
                             "example": "(Optional)", "desc": "Location", "mandatory": "no", "hide": "hide",
                             "options": options1})
                else:
                    para_dict.append({"name": "acilocation", "format": "", "default1": "", "output": "", "type": "text",
                                      "example": "(Optional)", "desc": "Device IP", "mandatory": "no", "hide": "hide"})
        #Modify Request, Display Request
        if req_type == "4" or req_type == "5" or req_type == "6":
            sentry = ServiceRequestDB.objects.order_by().values_list('taskid').distinct()
            temp = []
            t = {}
            t["value"] = ""
            t["label"] = "Select Task ID"
            temp.append(t)
            if sentry:
                for entry in sentry:
                    t = {}
                    t["value"] = entry[0]
                    t["label"] = entry[0]
                    temp.append(t)
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})
            para_dict.append(
                {"name": "taskid", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                 "example": "", "desc": "Service Request No.", "mandatory": "yes",
                 "vmessage": "Please Enter Service Request No.", "options": temp})
            para_dict.append({"name": "subtaskid", "format": "", "default1": "", "output": "", "type": "text",
                              "example": "(Optional)", "desc": "Sub-Task ID", "mandatory": "no"})
            para_dict.append(
                {"name": "req_type", "format": "", "default1": req_type, "output": "", "type": "hidden", "example": "",
                 "desc": "Template Name.", "mandatory": "yes", "send": "yes"})
        #Existing Request
        if req_type == "10":
            sentry = ServiceRequestDB.objects.order_by().values_list('taskid').distinct()
            temp = []
            t = {}
            t["value"] = ""
            t["label"] = "Select Task ID"
            temp.append(t)
            if sentry:
                for entry in sentry:
                    t = {}
                    t["value"] = entry[0]
                    t["label"] = entry[0]
                    temp.append(t)
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})
            if pre_response.has_key("taskid"):
                para_dict.append({"name": "taskid", "format": "", "default1": pre_response["taskid"], "output": "",
                                  "type": "dropdown-autocomplete", "example": "", "desc": "Change Request Number",
                                  "mandatory": "yes", "send": "yes", "vmessage": "Please Enter Change Request Number",
                                  "options": temp})
            else:
                para_dict.append(
                    {"name": "taskid", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Change Request Number", "mandatory": "yes", "send": "yes",
                     "vmessage": "Please Enter Change Request Number", "options": temp})
            para_dict.append({"name": "subtaskid", "format": "", "default1": "00", "output": "", "type": "text",
                              "example": "(Optional)", "desc": "Sub-Task ID", "mandatory": "no", "send": "yes"})
            para_dict.append(
                {"name": "req_type", "format": "", "default1": req_type, "output": "", "type": "hidden", "example": "",
                 "desc": "Template Name.", "mandatory": "yes", "send": "yes"})
            if pre_response.has_key("taskid"):
                q1 = CronDB.objects.values_list('cstate').filter(taskid=pre_response["taskid"],
                                                                 subtaskid=pre_response["subtaskid"],
                                                                 customer=pre_response["customer"]).last()
                if q1 and str(q1[0]) != "":
                    print "---->", q1[0]
                    para_dict.append(
                        {"name": "cstatus", "format": "", "default1": str(q1[0]).title(), "output": "", "type": "text",
                         "example": "", "desc": "Current Status ", "mandatory": "no"})
                    para_dict.append(
                        {"name": "existing_apply_action", "format": "", "default1": "reserve", "output": "",
                         "type": "radio", "example": "(Optional)", "desc": "Action", "mandatory": "no", "hide": "hide",
                         "options": [{"label": "Reservation", "value": "reserve"},
                                     {"label": "Provision", "value": "provision"},
                                     {"label": "Activation", "value": "activation"},
                                     {"label": "De-Provision Reservation ", "value": "deprovision_reservation"},
                                     {"label": "De-Provision", "value": "deprovision"}]})
                    if q1[0] == "provision" or q1[0] == "activated":
                        e1 = ServiceRequestDB.objects.values_list("reponsedictionary").filter(
                            taskid=pre_response["taskid"], subtaskid=pre_response["subtaskid"]).last()
                        if e1:
                            data = json.loads(e1[0])
                            if data.has_key("template"):
                                template_name = template_db.objects.values_list("ext_name", "ext_label",
                                                                                "ext_value").filter(
                                    id=int(data.get("template"))).last()
                                if template_name[0]:
                                    et_name = template_name[0]
                                    et_lbl = template_name[1].split(",")
                                    et_vlu = template_name[2].split(",")
                                    et_dict = zip(et_lbl, et_vlu)
                                    options22 = []
                                    for ele in et_dict:
                                        dict1 = {}
                                        dict1["label"] = ele[0]
                                        dict1["value"] = ele[1].strip()
                                        options22.append(dict1)
                                    if len(options22) > 3:
                                        para_dict.append({"name": "ext", "format": "", "default1": "", "output": "",
                                                          "type": "dropdown", "example": "(Optional)", "desc": et_name,
                                                          "mandatory": "no", "hide": "hide", "options": options22})
                                    else:
                                        para_dict.append(
                                            {"name": "ext", "format": "", "default1": "", "output": "", "type": "radio",
                                             "example": "(Optional)", "desc": et_name, "mandatory": "no",
                                             "hide": "hide", "options": options22})
                else:
                    para_dict.append(
                        {"type": "radio", "name": "existing_apply_action", "default1": "", "desc": "Action",
                         "options": [{"label": "Display", "value": "display"},
                                     {"label": "Roll Back Configuration", "value": "rollback"}]})
            else:
                para_dict.append({"type": "radio", "name": "existing_apply_action", "default1": "", "desc": "Action",
                                  "options": [{"label": "Display", "value": "display"},
                                              {"label": "Roll Back Configuration", "value": "rollback"}]})
        #Add
        if req_type == "7":
            if response.session.has_key("customer"):
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide"})
            else:
                if pre_response.has_key("customer"):
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
                else:
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
            para_dict.append(
                {"name": "template", "format": "", "default1": "", "output": "", "type": "text", "example": "",
                 "desc": "Template Name", "mandatory": "yes", "send": "yes"})
            para_dict.append({"note": "", "default1": "", "name": "ios", "type": "dropdown",
                              "options": [{"value": "NA", "label": "--NA--"}, {"value": "nx", "label": "NX IOS"},
                                          {"value": "xr", "label": "XR IOS"}, {"value": "ios", "label": "IOS"},
                                          {"value": "ACI", "label": "ACI"}, {"value": "junos", "label": "JUNOS"},
                                          {"value": "asa", "label": "Cisco ASA"},
                                          {"value": "arista", "label": "ARISTA"},
                                          {"value": "checkpoint", "label": "Checkpoint"},
                                          {"value": "pan", "label": "Palo Alto"}], "desc": "IOS (Optional)"})
        #Modify, Delete
        if req_type == "8" or req_type == "9":
            print " in Modify or delete"

            # else:
            if pre_response.has_key("customer"):
                if response.session.has_key("customer") and response.session["customer"] != "":
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": response.session["customer"], "output": "",
                         "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                         "hide": "hide"})
                else:
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                         "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                         "hide": "hide", "send": "yes", "options": get_customer_options()})
                if pre_response.has_key("template"):
                    para_dict.append(
                        {"name": "template", "format": "", "default1": pre_response["template"], "output": "",
                         "type": "dropdown-autocomplete", "example": "", "desc": "Template", "mandatory": "no",
                         "hide": "hide", "send": "yes", "options": get_template_list2(pre_response["customer"])})
                    if pre_response.has_key("template"):
                        match = re.search(r"(.+)\(.+\)\s+\(.+\)", pre_response["template"])
                        if match:
                            template = match.group(1).strip()
                        template_name = template_db.objects.values_list("template", "ext_name", "ext_label",
                                                                        "ext_value").filter(template=template).last()
                        if template_name:
                            et_name = template_name[1]
                            et_lbl = template_name[2].split(",")
                            et_vlu = template_name[3].split(",")
                            et_dict = zip(et_lbl, et_vlu)
                            options22 = []
                            if et_name != "":
                                for ele in et_dict:
                                    dict1 = {}
                                    dict1["label"] = ele[0]
                                    dict1["value"] = ele[1].strip()
                                    options22.append(dict1)
                                if len(options22) > 3:
                                    para_dict.append(
                                        {"name": "ext", "format": "", "default1": "", "output": "", "type": "dropdown",
                                         "example": "(Optional)", "desc": et_name, "mandatory": "no", "hide": "hide",
                                         "options": options22})
                                else:
                                    para_dict.append(
                                        {"name": "ext", "format": "", "default1": "", "output": "", "type": "radio",
                                         "example": "(Optional)", "desc": et_name, "mandatory": "no", "hide": "hide",
                                         "options": options22})
                        q1 = template_db.objects.filter(template=template, type=1, tag="provisioning_workflow").last()
                        if q1:
                            para_dict.append({"name": "config_action", "format": "", "default1": "", "output": "",
                                              "type": "dropdown", "example": "(Optional)", "desc": "Action",
                                              "mandatory": "no", "hide": "hide",
                                              "options": [{"label": "Reservation", "value": "reserve"},
                                                          {"label": "Provision", "value": "provision"},
                                                          {"label": "Activation", "value": "activation"},
                                                          {"label": "De-Provision Reservation ", "value": "deprovision_reservation"},
                                                          {"label": "De-Provisioning", "value": "deprovision"}]})
                else:
                    para_dict.append({"name": "template", "format": "", "default1": "", "output": "",
                                      "type": "dropdown-autocomplete", "example": "", "desc": "Template",
                                      "mandatory": "no", "hide": "hide", "send": "yes",
                                      "options": get_template_list2(pre_response["customer"])})


            else:
                print " In else condition "
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})
                para_dict.append(
                    {"name": "template", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Template", "mandatory": "no", "hide": "hide",
                     "options": get_template_list2(response.session["customer"])})
        #SD-Access Campus Greenfield
        if req_type == "12":
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                            {"value": "modify","label": "Modify Project"},
                                                                             {"value": "clone", "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"}, {"value": "clone","label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                # print "______________________________"+ str(response.user)
                if str(response.user) in ["admin", "SDA-Access"]:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design-1", "label": "Design-1"},{"value": "Design-2", "label": "Design-2"},
                                     {"value": "Checklist", "label": "Check List"},
                                     {"value": "Discovery", "label": "Discovery"},
                                     {"value": "Implimentation", "label": "Implementation"},
                                     {"value": "validate", "label": "Validate"},
                                     {"value": "Configuration", "label": "Phase-I Configuration "},
                                     {"value": "bulk Configuration", "label": "Bulk Configuration "},
                                     # {"value": "Configuration_Underlay_Automation", "label": "Configuration Underlay Automation"}
                                     ]})
                else:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [
                                     {"value": "validate", "label": "Validate"},
                                     {"value": "Configuration", "label": "Configuration Phase-I"},
                                     {"value": "Configuration_Underlay_Automation", "label": "Configuration Phase-II"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc":"Overwrite Project", "mandatory": "no",
                #      "options": [{'value':'Yes', 'label':'Yes'},{'value':'No', 'label':'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                      "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                      "options": [{"value": "sda", "label": "SDA"},
                                                  {"value": "non_sda", "label": "Non SDA"}]})
        #Zscale
        if req_type == "37":
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                            {"value": "modify","label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"}, {"value": "clone","label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                print "______________________________"+ str(response.user)
                if str(response.user) == "admin":
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                     {"value": "Checklist", "label": "Check List"},
                                     {"value": "Discovery", "label": "Discovery"},
                                     {"value": "Implimentation", "label": "Implementation"},
                                     {"value": "validate", "label": "Validate"},
                                     {"value": "Configuration", "label": "Configuration Phase-I"},
                                     {"value": "Configuration_Underlay_Automation", "label": "Configuration Underlay Automation"}]})
                else:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [
                                     {"value": "validate", "label": "Validate"},
                                     {"value": "Configuration", "label": "Configuration Phase-I"},
                                     {"value": "Configuration_Underlay_Automation", "label": "Configuration Phase-II"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                      "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                      "options": [{"value": "sda", "label": "SDA"},
                                                  {"value": "non_sda", "label": "Non SDA"}]})

        if req_type == "40":
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            opt_type =[{"value": "Partner", "label": "Partner"},
                       {"value": "Vendor",   "label": "Vendor"},
                       {"value": "Customer","label": "Customer"}]

            if pre_response.has_key("Type"):
                for cst in pre_response["Type"]:
                    print cst
                    for opt in opt_type:
                        if opt.get("value") == cst:
                            opt["checked"] = "checked"
                    print opt_type
                para_dict.append({"name": "Type", "format": "", "default1":"",
                                  "type": "checkbox", "example": "", "desc": "Type", "mandatory": "no",
                                  "hide": "hide", "send": "no", "options": opt_type})
            else:
                para_dict.append(
                    {"name": "Type", "format": "", "default1": "Type", "type": "checkbox",
                     "example": "", "desc": "Type", "mandatory": "no", "hide": "hide", "send": "no",
                     "options": opt_type})

            opt_roles =[{"value": "Execative", "label": "Execative"},
                        {"value": "Sales","label": "Sales"},
                        {"value": "Ps", "label": "PS"},
                        {"value": "Engineering","label": "Engineering"},
                        {"value": "Pm","label": "PM"},
                        ]

            if pre_response.has_key("Roles"):
                for cst in pre_response["Roles"]:
                    for opt in opt_roles:
                        if opt.get("value") == cst:
                            opt["selected"] = "yes"
                para_dict.append({"name": "Roles", "format": "", "default1": "", "output": "",
                                  "type": "dropdown-checkbox", "example": "", "desc": "Roles", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": opt_roles})
            else:
                para_dict.append(
                    {"name": "Roles", "format": "", "default1": "", "output": "", "type": "dropdown-checkbox",
                     "example": "", "desc": "Roles", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": opt_roles})


            opt_agenda =[{"value": "Informal", "label": "Informal"},
                        {"value": "Discover", "label": "Discover"},
                        {"value": "Scope","label": "Scope"},
                        {"value": "Kick-Off", "label": "Kick-Off"},
                        {"value": "Followup", "label": "Follow-up"}]
            if pre_response.has_key("Agenda"):
                for cst in pre_response["Agenda"]:
                    for opt in opt_agenda:
                        if opt.get("value") == cst:
                            opt["selected"] = "yes"
                para_dict.append({"name": "Agenda", "format": "", "default1": "", "output": "",
                                  "type": "dropdown-checkbox", "example": "", "desc": "Agenda", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": opt_agenda})
            else:
                para_dict.append(
                    {"name": "Agenda", "format": "", "default1": "", "output": "", "type": "dropdown-checkbox",
                     "example": "", "desc": "Agenda", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": opt_agenda})



            opt_deepdive=[{"value": "msp", "label": "MSP"},
                          {"value": "Campus","label": "Campus"},
                          {"value": "DC", "label": "DC"},
                          {"value": "Cloud","label": "Cloud"},
                          {"value": "Transform","label": "Transform"}]
            if pre_response.has_key("Deepdive"):
                for cst in pre_response["Deepdive"]:
                    for opt in opt_deepdive:
                        if opt.get("value") == cst:
                            opt["selected"] = "yes"
                para_dict.append({"name": "Deepdive", "format": "", "default1": "", "output": "",
                                  "type": "dropdown-checkbox", "example": "", "desc": "DeepDive", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options":opt_deepdive })
            else:
                para_dict.append(
                    {"name": "Deepdive", "format": "", "default1": "", "output": "", "type": "dropdown-checkbox",
                     "example": "", "desc": "DeepDive", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": opt_deepdive})


            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                             {"value": "modify",
                                                                              "label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"},
                                 {"value": "clone", "label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                print "______________________________" + str(response.user)
                if str(response.user) == "admin":
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                     {"value": "Checklist", "label": "Check List"},
                                     {"value": "Discovery", "label": "Discovery"},
                                     {"value": "Implimentation", "label": "Implementation"},
                                     {"value": "validate", "label": "Validate"},
                                     {"value": "Configuration", "label": "Configuration Phase-I"},
                                     {"value": "Configuration_Underlay_Automation",
                                      "label": "Configuration Underlay Automation"}]})
                else:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [
                             {"value": "validate", "label": "Validate"},
                             {"value": "Configuration", "label": "Configuration Phase-I"},
                             {"value": "Configuration_Underlay_Automation", "label": "Configuration Phase-II"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

        if req_type == "47":
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                             {"value": "modify",
                                                                              "label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"},
                                 {"value": "clone", "label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                #Application ! Selected Value = 5
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                print "______________________________" + str(response.user)
                if str(response.user) in ["admin","msp-admin"]:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [{"value": "Plan", "label": "Plan"},
                                     {"value": "Hyphothesis", "label": "Hyphothesis"},]})
                                     # {"value": "Checklist", "label": "Check List"},
                                    # {"value": "Design", "label": "Design"},
                                     # {"value": "Discovery", "label": "Discovery"},
                                     # {"value": "Implimentation", "label": "Implementation"},
                                     # {"value": "validate", "label": "Validate"},
                                     # {"value": "Configuration", "label": "Configuration Phase-I"},
                                     # {"value": "Configuration_Underlay_Automation",
                                     #  "label": "Configuration Underlay Automation"}]})
                else:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [
                             {"value": "validate", "label": "Validate"},
                             {"value": "Configuration", "label": "Configuration Phase-I"},
                             {"value": "Configuration_Underlay_Automation", "label": "Configuration Phase-II"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

        # MSP MultiTAb testing
        if req_type == "60":
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                             {"value": "modify",
                                                                              "label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"},
                                 {"value": "clone", "label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                #Application ! Selected Value = 5
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                print "______________________________" + str(response.user)
                if str(response.user) in ["admin","msp-admin"]:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [{"value": "Plan", "label": "Plan"},
                                     {"value": "Hyphothesis", "label": "Hyphothesis"},]})
                    # {"value": "Checklist", "label": "Check List"},
                    # {"value": "Design", "label": "Design"},
                    # {"value": "Discovery", "label": "Discovery"},
                    # {"value": "Implimentation", "label": "Implementation"},
                    # {"value": "validate", "label": "Validate"},
                    # {"value": "Configuration", "label": "Configuration Phase-I"},
                    # {"value": "Configuration_Underlay_Automation",
                    #  "label": "Configuration Underlay Automation"}]})
                else:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [
                             {"value": "validate", "label": "Validate"},
                             {"value": "Configuration", "label": "Configuration Phase-I"},
                             {"value": "Configuration_Underlay_Automation", "label": "Configuration Phase-II"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

        if req_type == "48":




            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})




            # para_dict.append(
            #     {"type": "text", "name": "applicn_name", "desc": "Application Name", "example": "", "length": "full",
            #      "pattern": "",
            #      "csend": "", "hide": "hide", "default1": ""})
            f = open('./mysite/Json_DATA/application_option.json', )
            data = json.load(f)
            test_list=[]
            for i in data:
                # print(i)
                dict1 = {}
                dict1["label"] = i
                dict1["value"] = i
                # dict1["send"] = "yes"
                test_list.append(dict1)
            new_app = {"label":"New Application Name","value ":"new_app_name"}
            test_list.append(new_app)
            # print test_list,"test>>>>>>>>>>>>>>>"
             #            [{"label": "NaviCare Nurse Call", "value": "NaviCare Nurse Call"},
             # {"label": "Philips Intellivue Patient Monitoring", "value": "Philips Intellivue Patient Monitoring"},
             # {"label": "New Application Name", "value": "New Application Name"}]


            if pre_response.has_key("applic_name"):

                para_dict.append({"name": "applic_name", "format": "", "default1": pre_response["applic_name"], "output": "",
                                  "type": "dropdown", "example": "", "desc": "Application Name", "mandatory": "",
                                  "hide": "hide", "send": "yes", "options": test_list})
            else:
                para_dict.append(
                    {"name": "applic_name", "format": "", "default1": "", "output": "", "type": "dropdown",
                     "example": "", "desc": "Application Name", "mandatory": "", "hide": "hide", "send": "yes",
                     "options": test_list})


            if pre_response.has_key("applic_name") and pre_response.get("applic_name") == "new_app_name":

                para_dict.append(
                    {"name": "application_name", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Application Name", "mandatory": "", "hide": "hide","rhide":"rhide"})

                para_dict.append({"name": "action", "format": "", "default1": "add",
                                  "type": "hidden",  "desc": "Action"})
            elif pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                             {"value": "modify",
                                                                              "label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"},
                                 {"value": "clone", "label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=5).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                print "______________________________" + str(response.user)
                if str(response.user) in ["admin"]:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [{"value": "Plan", "label": "Plan"},
                                     {"value": "Design", "label": "Design"},
                                     {"value": "Implimentation", "label": "Implementation"},
                                     {"value": "Verification", "label": "Verification"},

                                     {"value": "Troubleshooting", "label": "Troubleshooting"},]})
                    # {"value": "Checklist", "label": "Check List"},
                    # {"value": "Design", "label": "Design"},
                    # {"value": "Discovery", "label": "Discovery"},
                    # {"value": "Implimentation", "label": "Implementation"},
                    # {"value": "validate", "label": "Validate"},
                    # {"value": "Configuration", "label": "Configuration Phase-I"},
                    # {"value": "Configuration_Underlay_Automation",
                    #  "label": "Configuration Underlay Automation"}]})
                else:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [
                             {"value": "validate", "label": "Validate"},
                             {"value": "Configuration", "label": "Configuration Phase-I"},
                             {"value": "Configuration_Underlay_Automation", "label": "Configuration Phase-II"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=5).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})




                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            # para_dict.append(
            #     {"name": "new_application_name", "format": "", "default1": "", "output": "", "type": "text",
            #      "example": "", "desc": "New Application Name", "mandatory": "", "hide": "hide", "send": "yes"})

        if req_type == "41":
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                             {"value": "modify",
                                                                              "label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"},
                                 {"value": "clone", "label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                print "______________________________" + str(response.user)
                if str(response.user) == "admin":
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                     {"value": "Checklist", "label": "Check List"},
                                     {"value": "Discovery", "label": "Discovery"},
                                     {"value": "Implimentation", "label": "Implementation"},
                                     {"value": "validate", "label": "Validate"},
                                     {"value": "Configuration", "label": "Configuration Phase-I"},
                                     {"value": "Configuration_Underlay_Automation",
                                      "label": "Configuration Underlay Automation"}]})
                else:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [
                             {"value": "validate", "label": "Validate"},
                             {"value": "Configuration", "label": "Configuration Phase-I"},
                             {"value": "Configuration_Underlay_Automation", "label": "Configuration Phase-II"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

        if req_type == "42":
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            opt_type =[{"value": "Partner", "label": "Partner"},
                       {"value": "Vendor",   "label": "Vendor"},
                       {"value": "Customer","label": "Customer"}]

            if pre_response.has_key("CustomerType"):
                for cst in pre_response["CustomerType"]:
                    for opt in opt_type:
                        if opt.get("value") == cst:
                            opt["checked"] = "checked"
                para_dict.append({"name": "CustomerType", "format": "", "default1":"",
                                  "type": "checkbox", "example": "", "desc": "Type", "mandatory": "no",
                                  "hide": "hide", "send": "no", "options": opt_type})
            else:
                para_dict.append(
                    {"name": "CustomerType", "format": "", "default1": "Type", "type": "checkbox",
                     "example": "", "desc": "Type", "mandatory": "no", "hide": "hide", "send": "no",
                     "options": opt_type})

            opt_roles =[{"value": "Execative", "label": "Execative"},
                        {"value": "Sales","label": "Sales"},
                        {"value": "Project Scope", "label": "Project Scope"},
                        {"value": "Engineering","label": "Engineering"},
                        {"value": "Project Management","label": "Project Management"},
                        {"value": "Marketing","label": "Marketing"},
                        {"value": "CIO","label": "CIO"},
                        {"value": "CTO","label": "CTO"},
                        {"value": "Ops","label": "Ops"},
                        ]

            if pre_response.has_key("Roles"):
                for cst in pre_response["Roles"]:
                    for opt in opt_roles:
                        if opt.get("value") == cst:
                            opt["selected"] = "yes"
                para_dict.append({"name": "Roles", "format": "", "default1": "", "output": "",
                                  "type": "dropdown-checkbox", "example": "", "desc": "Roles", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": opt_roles})
            else:
                para_dict.append(
                    {"name": "Roles", "format": "", "default1": "", "output": "", "type": "dropdown-checkbox",
                     "example": "", "desc": "Roles", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": opt_roles})




            if pre_response.has_key("phase"):
                print pre_response
                para_dict.append({"name": "phase", "format": "", "default1": pre_response["phase"], "output": "",
                                  "type": "radio", "example": "", "desc": "Project Phase", "mandatory": "no",
                                  "hide": "hide", "options": [{"value": "Phase-1", "label": "Phase-1"},
                                                                             {"value": "Phase-2", "label": "Phase-2"},
                                                                             {"value": "Phase-3","label": "Phase-3"},
                                                                             {"value": "Phase-4", "label": "Phase-4"}]})
            else:
                para_dict.append(
                    {"name": "phase", "format": "", "default1": "", "output": "", "type": "radio",
                     "example": "", "desc": "Project Phase", "mandatory": "no", "hide": "hide",
                     "options": [{"value": "Phase-1", "label": "Phase-1"},
                                 {"value": "Phase-2", "label": "Phase-2"},
                                 {"value": "Phase-3","label": "Phase-3"},
                                 {"value": "Phase-4", "label": "Phase-4"}]})







            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                             {"value": "modify",
                                                                              "label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"},
                                 {"value": "clone", "label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                print "______________________________" + str(response.user)
                if str(response.user) == "admin":
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                     {"value": "Checklist", "label": "Check List"},
                                     {"value": "Discovery", "label": "Discovery"},
                                     {"value": "Implimentation", "label": "Implementation"},
                                     {"value": "validate", "label": "Validate"},
                                     {"value": "Configuration", "label": "Configuration Phase-I"},
                                     {"value": "Configuration_Underlay_Automation",
                                      "label": "Configuration Underlay Automation"}]})
                else:
                    para_dict.append(
                        {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                         "example": "", "desc": "Project Phase", "mandatory": "no",
                         "vmessage": "Please Enter Service Request No.",
                         "options": [
                             {"value": "validate", "label": "Validate"},
                             {"value": "Configuration", "label": "Configuration Phase-I"},
                             {"value": "Configuration_Underlay_Automation", "label": "Configuration Phase-II"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"},
                                 {"value": "Configuration", "label": "Configuration"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})
        # Cisco UCM Options
        if req_type == "43":
            if pre_response.get("services"):
                para_dict.append(
                    {"name": "services", "format": "", "default1": pre_response.get("services"), "output": "",
                     "type": "dropdown", "example": "", "desc": "Services", "mandatory": "no",
                     "hide": "hide", "send": "yes", "options": [{"value": "Select Service", "label": "Select Service"},
                                                                {"value": "add_phone", "label": "Add Phone"},
                                                                {"value": "add_user", "label": "Add User"},
                                                                {"value": "add_device_pool",
                                                                 "label": "Add Device Pool"},
                                                                {"value": "add_directory_number",
                                                                 "label": "Add Directory Number"},
                                                                {"value": "view_user", "label": "View Users"},
                                                                {"value": "view_phone", "label": "View Phone details"},
                                                                # {"value": "add_deviceProfile", "label": "Add Device Profile"},
                                                                # {"value": "view_deviceProfile", "label": "View Device Profile"},
                                                                ]})
            else:
                para_dict.append(
                    {"name": "services", "format": "", "default1": "", "output": "",
                     "type": "dropdown", "example": "", "desc": "Services", "mandatory": "no",
                     "hide": "hide", "options": [{"value": "Select Service", "label": "Select Service"},
                                                 {"value": "add_phone", "label": "Add Phone"},
                                                 {"value": "add_user", "label": "Add User"},
                                                 {"value": "add_device_pool", "label": "Add Device Pool"},
                                                 {"value": "add_directory_number", "label": "Add Directory Number"},
                                                 {"value": "view_user", "label": "View Users"},
                                                 {"value": "view_phone", "label": "View Phone details"},
                                                 # {"value": "add_deviceProfile", "label": "Add Device Profile"},
                                                 # {"value": "view_deviceProfile", "label": "View Device Profile"},
                                                 ]})
        # ACI Port Provisioing
        if req_type == "45":
            
            if pre_response.get("apic_services"):
                para_dict.append(
                    {"name": "apic_services", "format": "", "default1": pre_response.get("apic_services"), "output": "",
                     "type": "dropdown", "example": "", "desc": "Services", "mandatory": "no", "send": "yes",
                     "hide": "hide", "options": [{"value": "Select Service", "label": "Select Service"},
                                                 {"value": "Port Configuration", "label": "Port Provision"},
                                                 {"value": "Add Or Modify Tenant", "label": "Add Or Modify Tenant"},
                                                 {"value": "policy_grp", "label": "Add Leaf Port Policy Group"},
                                                 {"value": "port_channel_group", "label": "Add Port Channel Group"},
                                                 {"value": "Available Ports", "label": "Available Ports"},
                                                 {"value": "Leaf Port Status", "label": "Leaf Port Status"},
                                                 ]})
            else:
                para_dict.append(
                    {"name": "apic_services", "format": "", "default1": "", "output": "", "send": "yes",
                     "type": "dropdown", "example": "", "desc": "Services", "mandatory": "no",
                     "hide": "hide", "options": [{"value": "Select Service", "label": "Select Service"},
                                                 {"value": "Port Configuration", "label": "Port Provision"},
                                                 {"value": "Add Or Modify Tenant", "label": "Add Or Modify Tenant"},
                                                 {"value": "policy_grp", "label": "Add Leaf Port Policy Group"},
                                                 {"value": "port_channel_group", "label": "Add Port Channel Group"},
                                                 {"value": "Available Ports", "label": "Available Ports"},
                                                 {"value": "Leaf Port Status", "label": "Leaf Port Status"},
                                                 ]})
                
            
                       
            if pre_response.has_key('apic_services') and 'Port Configuration' in pre_response.get('apic_services'):
                
                if pre_response.get("action"):
                    para_dict.append(
                        {"name": "action", "format": "", "default1": pre_response.get("action"), "output": "",
                         "type": "dropdown", "example": "", "desc": "Action", "mandatory": "no", "send": "yes",
                         "hide": "hide", "options": [{"value": "Reservation", "label": "Reservation"},
                                                     {"value": "Provision", "label": "Provision"},
                                                     # {"value": "Activation", "label": "Activation"},
                                                     # {"value": "Reservation for De-Provision",
                                                     #  "label": "Reservation for De-Provision"},
                                                     {"value": "De-Provision", "label": "De-Provision"},
                                                     ]})
                else:
                    para_dict.append(
                        {"name": "action", "format": "", "default1": pre_response.get("action"), "output": "",
                         "type": "dropdown", "example": "", "desc": "Action", "mandatory": "no", "send": "yes",
                         "hide": "hide", "options": [{"value": "Select Action", "label": "Select Action"},
                                                     {"value": "Reservation", "label": "Reservation"},
                                                     {"value": "Provision", "label": "Provision"},
                                                     # {"value": "Activation", "label": "Activation"},
                                                     # {"value": "Reservation for De-Provision",
                                                     #  "label": "Reservation for De-Provision"},
                                                     {"value": "De-Provision", "label": "De-Provision"},
                                                     
                                                     ]})
                    
                if pre_response.has_key('action') and 'Provision' == pre_response.get('action'):
                    if pre_response.get("port_type"):
                        para_dict.append(
                            {"name": "port_type", "format": "", "default1": pre_response.get("port_type"), "output": "",
                            "type": "dropdown", "example": "", "desc": "Port Type", "mandatory": "no",
                            "hide": "hide", "options": [{"value": "Select Service", "label": "Select Service"},
                                                        {"value": "Physical", "label": "Physical"},
                                                        {"value": "Port-Channel", "label": "Port-Channel"},
                                                        {"value": "Virtual Port-Channel", "label": "Virtual Port-Channel"},
                                                        # {"value": "Uplink Port-Channel ","label": "Uplink Port-Channel",'disabled':'yes'},
                                                        # {"value": "Uplink FEX Ports","label": "Uplink FEX Ports",'disabled':'yes'},
                                                        # {"value": "Adding VLAN/EPG","label": "Adding VLAN/EPG",'disabled':'yes'},
                                                        # {"value": "Removing VLAN/EPG","label": "Removing VLAN/EPG",'disabled':'yes'},
                                                        ]})
                    else:
                        para_dict.append(
                            {"name": "port_type", "format": "", "default1": "", "output": "",
                            "type": "dropdown", "example": "", "desc": "Port Type", "mandatory": "no",
                            "hide": "hide", "options": [{"value": "Select Service", "label": "Select Service"},
                                                        {"value": "Physical", "label": "Physical"},
                                                        {"value": "Port-Channel", "label": "Port-Channel"},
                                                        {"value": "Virtual Port-Channel", "label": "Virtual Port-Channel"},
                                                        # {"value": "Uplink Port-Channel ", "label": "Uplink Port-Channel",'disabled':'yes'},
                                                        # {"value": "Uplink FEX Ports", "label": "Uplink FEX Ports",'disabled':'yes'},
                                                        # {"value": "Adding VLAN/EPG", "label": "Adding VLAN/EPG",'disabled':'yes'},
                                                        # {"value": "Removing VLAN/EPG", "label": "Removing VLAN/EPG",'disabled':'yes'},
                                                        ]})
                    
                                    
            from mysite.models import ApicIpDb
            options1 = []
            entry = ApicIpDb.objects.all()
            if entry:
                for dict in entry:
                    dict1 = {}
                    dict1["label"] = dict.label
                    dict1["value"] = dict.name
                    options1.append(dict1)
            if pre_response.has_key('apic_services') and 'Port Configuration' in pre_response.get(
                    'apic_services') and pre_response.get('action') in ['Reservation',
                                                                        'Provision'] and Service_now_flag:
                para_dict.append(
                    {"name": "service_now_check", "format": "", "default1": "no", "output": "",
                     "type": "radio", "example": "", "desc": "Do you want to fetch from Service Now ?",
                     "mandatory": "no",
                     "hide": "hide", "options": [{'label': 'Yes', 'value': 'yes'}, {'label': 'No', 'value': 'no'}]})

            para_dict.append(
                {"name": "data_center", "format": "", "default1": "", "output": "",
                 "type": "dropdown-autocomplete", "example": "", "desc": "Data Center", "mandatory": "no",
                 "hide": "hide", "options": options1})
            
            if pre_response.has_key('apic_services') and 'Available Ports' in pre_response.get('apic_services'):
                leaf_options = []
                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                leaf_list = apic_auth.get_leaf_list()
                leaf_count = 0
                for ele in leaf_list:
                    leaf_count +=1
                    model_num = apic_auth.get_model_no(ele["name"])
                    dict1 = {'send': "yes"}
                    dict1["label"] = "LCAWDCP-01-01-0" + str(leaf_count) + " [ " + ele["name"] + " ]" + " [ " + model_num + " ]"
                    dict1["value"] = ele["name"]
                    leaf_options.append(dict1)
                if pre_response.get("leaf_id"):
                        para_dict.append(
                            {"name": "leaf_id",  "format": "default1", "desc": "Leaf Switches",
                            "length": "full", 'mandatory': 'yes',
                            "type": "dropdown-checkbox", 'options': leaf_options})
                else:
                    para_dict.append(
                        {"name": "leaf_id", "format": "default1", "desc": "Leaf Switches",
                        "length": "full", 'mandatory': 'yes',
                        "type": "dropdown-checkbox", 'options': leaf_options})
    
        
            if pre_response.has_key('apic_services') and 'Leaf Port Status' in pre_response.get('apic_services'):
                    leaf_options = []
                    apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                    leaf_list = apic_auth.get_leaf_list()
                    leaf_count = 0
                    for ele in leaf_list:
                        leaf_count +=1
                        model_num = apic_auth.get_model_no(ele["name"])
                        dict1 = {'send': "yes"}
                        dict1["label"] = "LCAWDCP-01-01-0" + str(leaf_count) + " [ " + ele["name"] + " ]" + " [ " + model_num + " ]"
                        dict1["value"] = ele["name"]
                        leaf_options.append(dict1)
                        
                    
                    if pre_response.get("rack_row_number"):
                        para_dict.append(
                            {"name": "rack_row_number", "format": "default1", "desc": "Rack Row Number",
                            "length": "full",
                            "default1": "", "type": "hidden",
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
                                        ]})
                    else:
                        para_dict.append(
                            {"name": "rack_row_number", "format": "default1", "desc": "Rack Row Number",
                            "length": "full",
                            "default1": "", "type": "hidden",
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
                                        ]})
                        
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
                    if pre_response.get("rack_row_number"):
                        para_dict.append(
                            {"name": "rack_number",  "format": "default1", "desc": "Rack Number",
                             "length": "full",
                             "default1": "", "type": "hidden", "options": rack_options})
                    else:
                        para_dict.append(
                            {"name": "rack_number", "format": "default1", "desc": "Rack Number",
                             "length": "full",
                             "default1": "", "type": "hidden", "options": rack_options})
                        
                    if pre_response.get("leaf_id"):
                        para_dict.append(
                            {"name": "leaf_id",  "format": "default1", "desc": "Leaf Switches",
                            "length": "full", 'mandatory': 'yes',
                            "type": "dropdown", 'options': leaf_options})
                    else:
                        para_dict.append(
                            {"name": "leaf_id", "format": "default1", "desc": "Leaf Switches",
                            "length": "full", 'mandatory': 'yes',
                            "type": "dropdown", 'options': leaf_options})
                        
                    interaface_options = [{"value": '', 'label': 'Select'}]
                    for num in range(1, 49):
                        port_dict = {}
                        port_dict['value'] = 'eth 1/' + str(num)
                        port_dict['label'] = 'Eth 1/' + str(num)
                        interaface_options.append(port_dict)
                    
                    if pre_response.get("phy_ports"):
                        para_dict.append(
                            {"name": "phy_ports", "format": "default1", "desc": "Physical Port",
                            "length": "full", 'mandatory': 'yes',
                            "type": "dropdown-checkbox", 'options': interaface_options})
                    else:
                        para_dict.append(
                            {"name": "phy_ports", "format": "default1", "desc": "Physical Port",
                            "length": "full", 'mandatory': 'yes',
                            "type": "dropdown-checkbox", 'options': interaface_options})  
        
        # ACI Port Provisioing = Bulk
        if req_type == "46":
            print Service_now_flag
            if pre_response.get("apic_services"):
                para_dict.append(
                    {"name": "apic_services", "format": "", "default1": pre_response.get("apic_services"), "output": "",
                     "type": "dropdown", "example": "", "desc": "Services", "mandatory": "no","send":"yes",
                     "hide": "hide", "send": "yes", "options": [{"value": "", "label": "Select Service"},
                                                                {"value": "Reservation", "label": "Port Reservation"},
                                                                {"value": "Provision", "label": "Port Provision","send":"yes"},
                                                                {"value": "De-Provision", "label": "Port De-Provision"},
                                                                ]})
            else:
                para_dict.append(
                    {"name": "apic_services", "format": "", "default1": "", "output": "",
                     "type": "dropdown", "example": "", "desc": "Services", "mandatory": "no","send":"yes",
                     "hide": "hide", "options": [{"value": "", "label": "Select Service"},
                                                 {"value": "Reservation", "label": "Port Reservation"},
                                                 {"value": "Provision", "label": "Port Provision","send":"yes"},
                                                 {"value": "De-Provision", "label": "Port De-Provision"},
                                                 ]})
            
            if pre_response.has_key('apic_services') and 'Provision' == pre_response.get('apic_services'):
                
                if pre_response.get("port_type"):
                    para_dict.append(
                        {"name": "port_type", "format": "", "default1": pre_response.get("port_type"), "output": "",
                        "type": "dropdown", "example": "", "desc": "Port Type", "mandatory": "no","send":"yes",
                        "hide": "hide", "options": [{"value": "Select Service", "label": "Select Service"},
                                                    {"value": "Physical", "label": "Physical","send":"yes"},
                                                    {"value": "Port-Channel", "label": "Port-Channel","send":"yes"},
                                                    {"value": "Virtual Port-Channel", "label": "Virtual Port-Channel","send":"yes"},
                                                    # {"value": "Uplink Port-Channel ","label": "Uplink Port-Channel",'disabled':'yes'},
                                                    # {"value": "Uplink FEX Ports","label": "Uplink FEX Ports",'disabled':'yes'},
                                                    # {"value": "Adding VLAN/EPG","label": "Adding VLAN/EPG",'disabled':'yes'},
                                                    # {"value": "Removing VLAN/EPG","label": "Removing VLAN/EPG",'disabled':'yes'},
                                                    ]})
                
                else:
                    para_dict.append(
                        {"name": "port_type", "format": "", "default1": "", "output": "","send":"yes",
                        "type": "dropdown", "example": "", "desc": "Port Type", "mandatory": "no",
                        "hide": "hide", "options": [{"value": "Select Service", "label": "Select Service"},
                                                    {"value": "Physical", "label": "Physical","send":"yes"},
                                                    {"value": "Port-Channel", "label": "Port-Channel","send":"yes"},
                                                    {"value": "Virtual Port-Channel", "label": "Virtual Port-Channel","send":"yes"},
                                                    # {"value": "Uplink Port-Channel ", "label": "Uplink Port-Channel",'disabled':'yes'},
                                                    # {"value": "Uplink FEX Ports", "label": "Uplink FEX Ports",'disabled':'yes'},
                                                    # {"value": "Adding VLAN/EPG", "label": "Adding VLAN/EPG",'disabled':'yes'},
                                                    # {"value": "Removing VLAN/EPG", "label": "Removing VLAN/EPG",'disabled':'yes'},
                                                    ]})

                if pre_response.has_key('port_type') and 'Physical' == pre_response.get('port_type'):
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
                                
                    para_dict.append({"note": "", "default1": "", "name": "policy_grp",
                            "type": "dropdown", "desc": "Policy Group", 'options': policy_options})                
                    
                if pre_response.has_key('port_type') and 'Port-Channel' == pre_response.get('port_type'):
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
                    para_dict.append({"note": "", "default1": "", "name": "pc_policy_grp",
                            "type": "dropdown", "desc": "PC Policy Group", 'options': policy_options})

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
                    para_dict.append({"note": "", "default1": "", "name": "profile_grp",
                            "type": "dropdown", "desc": "Profile Group", 'options': policy_options})               
                        
            if Service_now_flag:
                if pre_response.get("service_now_check"):
                    para_dict.append(
                        {"name": "service_now_check", "format": "", "default1": pre_response.get("service_now_check"),
                         "send": "yes",
                         "type": "radio", "example": "", "desc": "Do you want to fetch from Service Now",
                         "mandatory": "no",
                         "hide": "hide", "options": [{'label': 'Yes', 'value': 'yes'}, {'label': 'No', 'value': 'no'}]})
                else:
                    para_dict.append(
                        {"name": "service_now_check", "format": "", "default1": "", "send": "yes",
                         "type": "radio", "example": "", "desc": "Do you want to fetch from Service Now",
                         "mandatory": "no",
                         "hide": "hide", "options": [{'label': 'Yes', 'value': 'yes'}, {'label': 'No', 'value': 'no'}]})
                options1 = []

                if pre_response.get('service_now_check') == "yes":
                    get_data = get_work_order_list("Bulk ACI")
                    print " Here 11223344"
                    options1 = [{'label': "Select Number", 'value': ''}]
                    for d_tct in get_data:
                        dict22 = {}
                        dict22['label'] = d_tct
                        dict22['value'] = d_tct
                        dict22['send'] = "yes"
                        dict22['hide'] = "hide"
                        options1.append(dict22)
                    if pre_response.get("work_order_no"):
                        para_dict.append(
                            {"name": "work_order_no", "send": "yes", "format": "default1", "desc": "Work Order Number",
                             "length": "full",
                             "options": options1, "default1": pre_response.get("work_order_no"), "mandatory": "yes",
                             'example': "Ex: REQ0000001",
                             "type": "dropdown-autocomplete"})
                    else:
                        para_dict.append(
                            {"name": "work_order_no", "send": "yes", "format": "default1", "desc": "Work Order Number",
                             "length": "full", "options": options1, "default1": "", "mandatory": "yes",
                             'example': "Ex: REQ0000001",
                             "type": "dropdown-autocomplete"})

        # Cisco UCM Bulk
        if req_type == "44":

            if pre_response.get("services"):
                para_dict.append(
                    {"name": "services", "format": "", "default1": pre_response.get("services"), "output": "",
                     "type": "dropdown", "example": "", "desc": "Services", "mandatory": "no",
                     "hide": "hide", "send": "yes", "options": [{"value": "Select Service", "label": "Select Service"},
                                                                {"value": "add_phone", "label": "Add Phone"},
                                                                # {"value": "add_user", "label": "Add User"},
                                                                # {"value": "add_deviceProfile", "label": "Add Device Profile"},
                                                                # {"value": "add_device_pool", "label": "Add Device Pool"},
                                                                # {"value": "view_user", "label": "View Users"},
                                                                # {"value": "view_phone", "label": "View Phone details"},
                                                                # {"value": "view_deviceProfile", "label": "View Device Profile"},
                                                                ]})
            else:
                para_dict.append(
                    {"name": "services", "format": "", "default1": "", "output": "",
                     "type": "dropdown", "example": "", "desc": "Services", "mandatory": "no",
                     "hide": "hide", "options": [{"value": "Select Service", "label": "Select Service"},
                                                 {"value": "add_phone", "label": "Add Phone"},
                                                 # {"value": "add_user", "label": "Add User"},
                                                 # {"value": "add_deviceProfile", "label": "Add Device Profile"},
                                                 # {"value": "add_device_pool", "label": "Add Device Pool"},
                                                 # {"value": "view_user", "label": "View Users"},
                                                 # {"value": "view_phone", "label": "View Phone details"},
                                                 # {"value": "view_deviceProfile", "label": "View Device Profile"},
                                                 ]})
        # Cisco ISE
        if req_type == "29":
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                            {"value": "modify","label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"}, {"value": "clone","label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "Discovery", "label": "Discovery"},
                                 {"value": "Checklist", "label": "Check List"},
                                 {"value": "Implimentation", "label": "Implimentation"},
                                 {"value": "validate", "label": "Validate"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"}]})
                para_dict.append({"type": "hidden", "name": "fabric_type", "desc": "Fabric Type",
                                      "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                      "options": [{"value": "sda", "label": "SDA"},
                                                  {"value": "non_sda", "label": "Non SDA"}]})

        #SD-WAN Deployment
        if req_type == "27":
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                            {"value": "modify","label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"}, {"value": "clone","label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=4).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "Checklist", "label": "Check List"},
                                 {"value": "Discovery", "label": "Discovery"},
                                 {"value": "Implementation", "label": "Implementation"},
                                 {"value": "Design_VN", "label": "Design Virtual Network And IP Pool"},
                                 {"value": "validate", "label": "Validate"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append(
                #     {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                #      "example": "", "desc": "Project Phase", "mandatory": "no",
                #      "vmessage": "Please Enter Service Request No.",
                #      "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                #                  {"value": "Checklist", "label": "Check List"},
                #                  {"value": "Implimentation", "label": "Implimentation"},
                #                  # {"value": "Configuration", "label": "Configuration phase 1"},
                #                  {"value": "Design_VN", "label": "Design Virtual Network And IP Pool"},
                #                  {"value": "validate", "label": "Validate"}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})
            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "validation", "label": "Validation"}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Validate", "label": "Validate"}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                       "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                       "options": [{"value": "sda", "label": "SDA"},
                #                                   {"value": "non_sda", "label": "Non SDA"}]})
        #Green Field Campus Design -Bulk Upload
        if req_type == "21":
            if response.session.has_key("customer") and response.session["customer"] != "":
                para_dict.append(
                    {"name": "customer", "format": "", "default1": response.session["customer"], "output": "",
                     "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide"})
            else:
                if pre_response.has_key("customer"):
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
                else:
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
            if pre_response.has_key("action"):
                para_dict.append(
                    {"name": "action", "format": "", "default1": pre_response.get("action"), "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "update", "label": "Update Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "update", "label": "Update Project"}]})
            if pre_response.has_key("project_no") and pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": pre_response.get("project_no"), "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
            elif pre_response.has_key("action") and pre_response.get("action") == "update":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=2).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please select Service Request No.", "options": temp})
            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
        #End-to-End Troubleshooting
        if req_type == "13":
            if response.session.has_key("customer") and response.session["customer"] != "":
                para_dict.append(
                    {"name": "customer", "format": "", "default1": response.session["customer"], "output": "",
                     "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide"})
            else:
                if pre_response.has_key("customer"):
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
                else:
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
            if pre_response.has_key("taskid"):
                para_dict.append(
                    {"name": "taskid", "format": "", "default1": pre_response.get("taskid"), "output": "",
                     "type": "text",
                     "example": "", "desc": "Change No.", "mandatory": "yes", "hide": "hide", "send": "yes"})
            else:
                para_dict.append(
                    {"name": "taskid", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Change No.", "mandatory": "yes", "hide": "hide"})

            if pre_response.has_key("existing_ticket_no"):
                para_dict.append(
                    {"name": "existing_ticket_no", "format": "", "default1": pre_response.get("existing_ticket_no"), "output": "",
                     "type": "radio",
                     "example": "", "desc": "Do you have existing incident ticket number ?","hide": "hide",
                     "options":[{"value":"Yes","label":"Yes"},{"value":"No","label":"No"}]})
            else:
                para_dict.append(
                    {"name": "existing_ticket_no", "format": "", "default1": "", "output": "", "type": "radio",
                     "example": "", "desc": "Do you have existing incident ticket number ?", "hide": "hide",
                     "options":[{"value":"Yes","label":"Yes"},{"value":"No","label":"No"}]})

            if pre_response.has_key("single_service_affected"):
                para_dict.append(
                    {"name": "single_service_affected", "format": "", "default1": pre_response.get("single_service_affected"), "output": "",
                     "type": "radio","send":"yes",
                     "example": "", "desc": "Is single service affected?","hide": "hide",
                     "options":[{"value":"Yes","label":"Yes","send":"yes"},{"value":"No","label":"No"},{"value":"Unknown","label":"Unknown"}]})
            else:
                para_dict.append(
                    {"name": "single_service_affected", "format": "", "default1": "", "output": "", "type": "radio",
                     "example": "", "desc": "Is single service affected?", "hide": "hide","send":"yes",
                     "options":[{"value":"Yes","label":"Yes","send":"yes"},{"value":"No","label":"No"},{"value":"Unknown","label":"Unknown"}]})
            if pre_response.has_key("single_service_affected") and "Yes" in pre_response.get("single_service_affected"):

                tech_options = [
                                {"value": "Select Option", "label": "Select Option"},
                                {"value": "wired", "label": "Wired Connectivity"},
                                {"value": "wireless", "label": "Wireless Connectivity"},
                                {"value": "Existing Application", "label": "Existing Application"},
                                {"value": "New Application", "label": "New Application"},
                                {"value": "Internet", "label": "Internet"},
                                {"value": "cloud", "label": "Cloud", "isdevider": "1"},
                                {"value": "Data Center", "label": "Data Center"}
                                ]
                if pre_response.has_key("tech"):
                    para_dict.append(
                        {"note": "", "default1": pre_response.get("tech"), "name": "tech","send":"yes",
                         "type": "dropdown",
                         "options": tech_options, "desc": "Affected Service"})
                else:

                    para_dict.append(
                        {"note": "", "default1": "", "name": "tech","type": "dropdown","send":"yes",
                         "options": tech_options, "desc": "Affected Service"})


                if pre_response.has_key("tech") and "wireless" in pre_response.get("tech"):
                    para_dict.append(
                        {"note": "", "default1": "Not Reachable", "name": "template", "send": "yes", "type": "hidden",
                         "options": [], "desc": "Problem Symptom"})
                    wired_conn_options = [
                        {"value": "Yes", "label": "Yes"},
                        {"value": "no", "label": "No"},
                        {"value": "Don't Know", "label": "Don't Know"}]
                    if pre_response.has_key("some_device_wired_connection"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("some_device_wired_connection"), "name": "some_device_wired_connection",
                             "type": "radio",
                             "options": wired_conn_options, "desc": "Does same device work on wired connection ?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "some_device_wired_connection",  "type": "radio",
                             "options": wired_conn_options, "desc": "Does same device work on wired connection ?"})

                    working_before = [
                        {"value": "Yes", "label": "Yes"},
                        {"value": "no", "label": "No"},
                        {"value": "Don't Know", "label": "Don't Know"}]



                    if pre_response.has_key("working_befores"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("working_befores"),
                             "name": "some_device_wired_connection",
                             "type": "radio",
                             "options": working_before, "desc": "Was it working before ?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "working_befores",
                             "type": "radio",
                             "options": working_before, "desc": "Was it working before ?"})

                    issue_device = [
                        {"value": "Yes", "label": "Yes"},
                        {"value": "no", "label": "No","hide":"hide","trigger":["device_affected"]},
                        {"value": "Don't Know", "label": "Don't Know"}]

                    if pre_response.has_key("device_having_issue"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("device_having_issue"),
                             "name": " device_having_issue",
                             "type": "radio",
                             "options": issue_device, "desc": "Is single device having the issue ?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "device_having_issue",
                             "type": "radio",
                             "options": issue_device, "desc": " Is single device having the issue ?"})

                    if pre_response.has_key("device_affected"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("single_device_affected"),
                             "name": " device_affected",
                             "type": "text",
                             "desc": "How many devices are affected ?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "device_affected",
                             "type": "text",
                             "desc": " How many devices are affected ?"})

                    Common_affected = [
                        {"value": "Device Type", "label": "Device Type"},
                        {"value": "SSID", "label": "SSID"},
                        {"value": "Access Point", "label": "Access Point"}, {"value": "Network Switch", "label": "Network Switch"},
                        {"value": "Wired Closet", "label": "Wired Closet"},
                        {"value": "Site", "label": "Site"}]

                    if pre_response.has_key("common_devices"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("common_devices"),"name": " common_devices",
                             "type": "checkbox","options": Common_affected, "desc": "What is common among affected devices ?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "common_devices", "type": "checkbox",
                             "options": Common_affected, "desc": "What is common among affected devices ?"})

                    if pre_response.has_key("wireless_ssid_network"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("wireless_ssid_network"),
                             "name": " wireless_ssid_network", "send": "yes",
                             "type": "dropdown",
                             "options": [{"value":"Guest","label":"Guest"},{"value":"Enterprise","label":"Enterprise"},
                                         {"value": "SCH_WLAN", "label": "SCH_WLAN"},
                                         {"value": "LPCH_VOIP", "label": "LPCH_VOIP"},
                                         {"value": "SUMC_Med", "label": "SUMC_Med"},
                                         {"value": "SHCclinA", "label": "SHCclinA"},
                                         {"value": "SHCclinB", "label": "SHCclinB"},
                                         {"value": "SHCMed_WLAN", "label": "SHCMed_WLAN"},
                                         {"value": "SHC_Test", "label": "SHC_Test"},],
                             "desc": "Wireless SSID / Network"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "wireless_ssid_network", "send": "yes",
                             "type": "dropdown",
                             "options": [{"value":"Guest","label":"Guest"},{"value":"Enterprise","label":"Enterprise"},
                                         {"value": "SCH_WLAN", "label": "SCH_WLAN"},
                                         {"value": "LPCH_VOIP", "label": "LPCH_VOIP"},
                                         {"value": "SUMC_Med", "label": "SUMC_Med"},
                                         {"value": "SHCclinA", "label": "SHCclinA"},
                                         {"value": "SHCclinB", "label": "SHCclinB"},
                                         {"value": "SHCMed_WLAN", "label": "SHCMed_WLAN"},
                                         {"value": "SHC_Test", "label": "SHC_Test"},
                                         ], "desc": "Wireless SSID / Network"})
                if pre_response.has_key("tech") and "wired" in pre_response.get("tech"):

                    wired_conn_options = [
                        {"value": "Yes", "label": "Yes"},
                        {"value": "no", "label": "No"},
                        {"value": "Don't Know", "label": "Don't Know"}]
                    if pre_response.has_key("some_device_wired_connection"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("some_device_wired_connection"), "name": "some_device_wireless_connection",
                             "type": "radio",
                             "options": wired_conn_options, "desc": "Does same device work on wireless connection ?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "some_device_wireless_connection", "type": "radio",
                             "options": wired_conn_options, "desc": "Does same device work on wireless connection ?"})

                    working_before = [
                        {"value": "Yes", "label": "Yes"},
                        {"value": "no", "label": "No"},
                        {"value": "Don't Know", "label": "Don't Know"}]



                    if pre_response.has_key("working_befores"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("working_befores"),
                             "name": "some_device_wired_connection",
                             "type": "radio",
                             "options": working_before, "desc": "Was it working before ?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "working_befores",
                             "type": "radio",
                             "options": working_before, "desc": "Was it working before ?"})

                    issue_device = [
                        {"value": "Yes", "label": "Yes"},
                        {"value": "no", "label": "No","hide":"hide","trigger":["device_affected"]},
                        {"value": "Don't Know", "label": "Don't Know"}]

                    if pre_response.has_key("device_having_issue"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("device_having_issue"),
                             "name": " device_having_issue",
                             "type": "radio",
                             "options": issue_device, "desc": "Is single device having the issue ?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "device_having_issue",
                             "type": "radio",
                             "options": issue_device, "desc": " Is single device having the issue ?"})

                    if pre_response.has_key("device_affected"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("single_device_affected"),
                             "name": " device_affected",
                             "type": "text",
                              "desc": "How many devices are affected?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "device_affected",
                             "type": "text",
                              "desc": " How many devices are affected ?"})

                    Common_affected = [
                        {"value": "Device Type", "label": "Device Type"},
                        {"value": "Network Switch", "label": "Network Switch"},
                        {"value": "Wired Closet", "label": "Wired Closet"},
                        {"value": "Site", "label": "Site"}]

                    if pre_response.has_key("common_devices"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("common_devices"),
                             "name": " common_devices",
                             "type": "checkbox",
                             "options": Common_affected, "desc": "What is common among affected devices ?"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "", "name": "common_devices",
                             "type": "checkbox",
                             "options": Common_affected, "desc": " What is common among affected devices ?"})

                    para_dict.append(
                            {"note": "", "default1": "Not Reachable", "name": "template", "send": "yes", "type": "hidden",
                             "options": [], "desc": "Problem Symptom"})

                if pre_response.has_key("tech") and "Existing Application" in pre_response.get("tech"):
                    affected_options = [
                        {"value": "Select Option", "label": "Select Option"},
                        {"value": "pacs", "label": "PACS"},
                        {"value": "citrix", "label": "CITRIX"}, {"value": "dmz", "label": "DMZ"},
                        {"value": "epic", "label": "EPIC"}]

                    if pre_response.has_key("affected_application"):
                        para_dict.append(
                            {"note": "", "default1": pre_response.get("affected_application"), "name": "affected_application", "send": "yes",
                             "type": "dropdown",
                             "options": affected_options, "desc": "Affected Application"})
                    else:
                        para_dict.append(
                            {"note": "", "default1": "datacenter", "name": "affected_application", "send": "yes", "type": "dropdown",
                             "options": affected_options, "desc": "Affected Application"})


                    ct_options = [
                                  {"label": "Not Reachable", "value": "Not Reachable", 'hide':'hide',"send": "yes" },
                                  {"label": "Poor Performance", "value": "Poor Performance", 'hide':'hide',"send": "yes"},
                                  {"label": "Intermittent Connectivity", "value": "Intermittent Connectivity", 'hide':'hide',"send": "yes"}]

                    if pre_response.has_key("affected_application"):
                        if pre_response.has_key("template"):
                            para_dict.append(
                                {"note": "", "default1": pre_response.get("template"), "name": "template", "send": "yes",
                                 "type": "dropdown", "options": ct_options, "desc": "Problem Symptom"})
                        else:
                            para_dict.append(
                                {"note": "", "default1": "", "name": "template", "send": "yes", "type": "dropdown",
                                 "options": ct_options, "desc": "Problem Symptom"})
                    else:
                        para_dict.append({"note": "", "default1": "1", "name": "template", "send": "yes", "type": "dropdown",
                                          "options": ct_options, "desc": "Problem Symptom"})

                if pre_response.has_key("tech") :
                    name = 'device_ip_info'
                    # desc = 'Source IP'
                    desc = 'User device IP information'
                    default1 = ""
                    input_dict4 = {'name': name, 'type': 'radio', 'desc': desc,
                                   'default1': "Device have the IP", 'example': '',
                                   'options':[{"value":"Device have the IP","label":"Device have the IP",'hide':'hide','trigger':['src_ip']},
                                              {"value":"Device don't have the IP","label":"Device don't have the IP",'hide':'hide','trigger':['user_device_mac']},
                                              {"value":"Don't have the info","label":"Don't have the info",'hide':'hide','trigger':['user_device_mac']},
                                              ]}

                    name = 'src_ip'
                    # desc = 'Source IP'
                    desc = 'User device (source) IP'
                    default1 = ""
                    input_dict5 = {'name': name, 'type': 'text', 'desc': desc,"hide":"hide",
                                   'default1': default1, 'example': ''
                                   }

                    name = 'user_device_mac'
                    # desc = 'Source IP'
                    desc = 'User device (source) MAC'
                    default1 = ""
                    input_dict6 = {'name': name, 'type': 'text', 'desc': desc,"hide":"hide",
                                   'default1': default1, 'example': ''
                                   }

                    name = 'user_device_tso_id'
                    # desc = 'Source IP'
                    desc = 'User Device TSO ID (Optional)'
                    default1 = ""
                    input_dict7 = {'name': name, 'type': 'text', 'desc': desc,
                                   'default1': default1, 'example': 'Ex. J150-04-08-11'
                                   }


                    default_desip = ""
                    default_desport = ""
                    with open('/home/ubuntu/prepro/mysite/mysite/data/all/services.json') as f:
                        data = json.load(f)
                        for k, v in data.iteritems():
                            if pre_response.get("affected_application")== k:
                                default_desip = v["service_ip"]
                                default_desport = v["service_port"]

                    # name = 'src_ip'
                    # # desc = 'Source IP'
                    # desc = 'Source IP / User IP'
                    # default1 = ""
                    # input_dict1 = {'name': name, 'type': 'text', 'desc': desc,
                    #                'default1': default1, 'example': ''}

                    name = 'des_ip'
                    desc = 'Destination IP / URL'
                    # desc = 'Destination or Service IP'
                    default1 = default_desip
                    input_dict2 = {'name': name, 'type': 'text', 'desc': desc,
                                   'default1': default1, 'example': ''}

                    name = 'host_port'
                    # desc = 'Destination IP'
                    desc = 'Destination Port Number'
                    default1 = default_desport
                    input_dict3 = {'name': name, 'type': 'text', 'desc': desc,
                                      'default1': default1, 'example': 'Ex. 80 or 443'}


                    # para_dict.append(input_dict1)
                    para_dict.append(input_dict4)
                    para_dict.append(input_dict5)
                    para_dict.append(input_dict6)
                    para_dict.append(input_dict2)
                    para_dict.append(input_dict3)

                    para_dict.append(input_dict7)






            # para_dict.append(
            #     {"name": "devices", "format": "", "default1": "", "output": "", "type": "tags-auto", "example": "",
            #      "desc": "Involved Devices", "mandatory": "no", "hide": "hide"})
        #Enterprise Network T/S Setting
        if req_type == "31":
            if response.session.has_key("customer") and response.session["customer"] != "":
                para_dict.append(
                    {"name": "customer", "format": "", "default1": response.session["customer"], "output": "",
                     "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide"})
            else:
                if pre_response.has_key("customer"):
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
                else:
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
            # if pre_response.has_key("taskid"):
            #     para_dict.append(
            #         {"name": "taskid", "format": "", "default1": pre_response.get("taskid"), "output": "",
            #          "type": "text",
            #          "example": "", "desc": "Change No.", "mandatory": "yes", "hide": "hide", "send": "yes"})
            # else:
            #     para_dict.append(
            #         {"name": "taskid", "format": "", "default1": "", "output": "", "type": "text",
            #          "example": "", "desc": "Change No.", "mandatory": "yes", "hide": "hide", "send": "yes"})

            tech_options = [{"value": "1", "label": "Troubleshooting", "isdevider": "1"},
                            {"value": "user_options", "label": "User Options", "isdevider": "1"},
                            {"value": "Add Service", "label": "Add Service"},
                            {"value": "Modify Service", "label": "Modify Service"},
                            {"value": "Delete Service", "label": "Delete Service"},
                            {"value": "Add Device", "label": "Add Device"},
                            {"value": "Modify Device", "label": "Modify Device"},
                            {"value": "Delete Device", "label": "Delete Device"}
                            ]
            if pre_response.has_key("tech"):
                para_dict.append(
                    {"note": "", "default1": pre_response.get("tech"), "name": "tech", "send": "yes",
                     "type": "dropdown",
                     "options": tech_options, "desc": "Affected Services"})
            else:

                para_dict.append(
                    {"note": "", "default1": "datacenter", "name": "tech", "send": "yes", "type": "dropdown",
                     "options": tech_options, "desc": "Affected Services"})

            ct_options = [
                          {"value": "2", "label": "User Option", "isdevider": "1", 'hide':'hide',"send": "yes"},
                          {"label": "Add Path", "value": "Add Path", 'hide':'hide',"send": "yes"},
                          {"label": "Modify Path", "value": "Modify Path", 'hide':'hide',"send": "yes"},
                          {"label": "Delete Path", "value": "Delete Path", 'hide':'hide',"send": "yes"},
                          ]
            if pre_response.has_key("tech"):

                if pre_response.has_key("template"):
                    para_dict.append(
                        {"note": "", "default1": pre_response.get("template"), "name": "template", "send": "yes",
                         "type": "dropdown", "options": ct_options, "desc": "Type"})
                else:
                    para_dict.append(
                        {"note": "", "default1": "1", "name": "template", "send": "yes", "type": "dropdown",
                         "options": ct_options, "desc": "Type"})
            else:
                para_dict.append({"note": "", "default1": "1", "name": "template", "send": "yes", "type": "dropdown",
                                  "options": ct_options, "desc": "Type"})
        #DNAC
        if req_type == "32":
            para_dict.append(
                {"name": "process_url", "format": "", "default1": "", "output": "",
                 "type": "radio", "desc": "Do You want to proceed the Request ",
                 "options": [{"value":"Yes","label":"Yes","hide":"hide","trigger":["url"]},{"value":"No","label":"No"}], "hide": "hide"})
            para_dict.append(
                {"name": "url", "format": "", "default1": "", "output": "",
                 "type": "text", "example": "Ex:https://10.250.79.250/api/system", "desc": "URL",
                 "mandatory": "no", "hide": "hide"})
        #Security Segmentation
        if req_type == "33":
            para_dict.append(
                {"name": "source_application", "format": "", "default1": "", "output": "",
                 "type": "dropdown", "desc": "Source Application",
                 "options": [{"value": "Other", "label": "Other", "hide": "hide", "trigger": ["source_ip"]},
                             ],})
            para_dict.append(
                {"name": "source_ip", "format": "", "default1": "", "output": "",
                 "type": "text", "example": "", "desc": "Source IP",
                 "mandatory": "no", "hide": "hide"})
            para_dict.append(
                {"name": "destination_application", "format": "", "default1": "", "output": "",
                 "type": "dropdown", "desc": "Destination Application","condition": "destination_ip",
                 "options": [{"value": "data_center", "label": "Data Center", "hide": "hide"},
                             {"value": "other_ip", "label": "Other IP", "hide": "hide", "trigger": ["destination_ip"]}
                             ]})
            para_dict.append(
                {"name": "destination_ip", "format": "", "default1": "", "output": "",
                 "type": "text", "example": "", "desc": "Destination IP",
                 "mandatory": "no", "hide": "hide"})
        #S2
        if req_type == "34":
            pre_response1 = {}

            para_dict.append(
                {"desc": "Device Name", "type": "text", "name": "device_name",
                 "default1":"", 'length': "full", "trigger": [""], "condition": "",
                 "hide": "hide"})

            if pre_response:
                for el in pre_response:
                    if pre_response.get(el):
                        if "[" in el:
                            element_value = pre_response.getlist(el)
                            if element_value:
                                new_el = el.split("[]")[0]
                                pre_response1[new_el] = element_value
                        else:
                            pre_response1[el] = pre_response.get(el)

            options1 = [{"value": "Lutron Electronics Co., Inc", "label": "Lutron Electronics Co., Inc", "send": "yes"},
                        {"value": "Axis Communications AB", "label": "Axis Communications AB", "send": "yes"},
                        {"value": "CRESTRON ELECTRONICS, INC", "label": "CRESTRON ELECTRONICS, INC", "send": "yes"},
                        {"value": "Adder Technology Limited", "label": "Adder Technology Limited", "send": "yes"},
                        {"value": "Translogic Corporation", "label": "Translogic Corporation", "send": "yes"},
                        {"value": "POWER MEASUREMENT LTD", "label": "POWER MEASUREMENT LTD", "send": "yes"},
                        {"value": "BrightSign LLC", "label": "BrightSign LLC", "send": "yes"},
                        {"value": "Super Micro Computer, Inc.", "label": "Super Micro Computer, Inc.", "send": "yes"},
                        {"value": "Aiphone co.,Ltd", "label": "Aiphone co.,Ltd", "send": "yes"},
                        {"value": "STAR MICRONICS CO.,LTD.", "label": "STAR MICRONICS CO.,LTD.", "send": "yes"},
                        {"value": "AEWIN Technologies Co., Ltd.", "label": " AEWIN Technologies Co., Ltd.", "send": "yes"},
                        {"value": "AMERICAN POWER CONVERSION CORP", "label": "AMERICAN POWER CONVERSION CORP", "send": "yes"},
                        {"value": "Lantronix", "label": "Lantronix", "send": "yes"},
                        {"value": "Shany Electronic Co., Ltd.", "label": "Shany Electronic Co., Ltd.", "send": "yes"},
                        {"value": "Uplogix, Inc.", "label": "Uplogix, Inc.", "send": "yes"},
                        {"value": "Wistron Info", "label": "Wistron Info", "send": "yes"},]

            para_dict.append(
                    {"desc": "Device type", "type": "dropdown", "name": "device_type",
                     "default1": pre_response.get("device_type"), 'length': "full", "trigger": [""], "condition": "",
                     "hide": "hide", "send": "yes","options": options1})

            con_option = [{"value": "internet", "label": "Internet","hide":"hide",},
                          {"value": "data center", "label": "Data Center", "hide":"hide","send":"yes","trigger":["dc_need_access","vn_need_access"]},
                          {"value": "inter sites", "label": "Inter Sites", "hide":"hide","send":"yes","trigger":["site_need_access","vn_need_access_site"]},
                          {"value": "inter vlan", "label": "Inter Vlan", "hide":"hide","send":"yes","trigger":["vlan_need_access_site"]},
                          {"value": "intra vlan", "label": "Intra Vlan", "hide":"hide","send":"yes","trigger":["device_need_access"]},
                          {"value": "Other devices", "label": "Other devices with same type"}]


            if pre_response1.has_key("connectivity_req"):
                for cst in pre_response1.get("connectivity_req"):
                    for opt in con_option:
                        if opt.get("value") == cst:
                            opt["selected"] = "yes"
                para_dict.append(
                    {"desc": "Connectivity Requirement", "type": "dropdown-checkbox", "name": "connectivity_req",
                     "default1": "", 'length': "full",  "rhide": "hide","send":"yes",
                     "hide": "hide", "options": con_option})
            else:
                para_dict.append(
                    {"desc": "Connectivity Requirement", "type": "dropdown-checkbox", "name": "connectivity_req",
                     "rhide": "hide","send":"yes",
                     "default1": "", 'length': "full",  "hide": "hide", "options": con_option})

            # if pre_response.has_key("connectivity_req") and "data center" in pre_response.get("connectivity_req"):
            options1 = [{"value": "MTC", "label": "MTC"}, {"value": "STC", "label": "STC"},
                        {"value": "MSP", "label": "MSP"}, ]
            if pre_response1.has_key("connectivity_req") and "data center" in pre_response1.get("connectivity_req"):
                para_dict.append(
                    {"desc": "Which dc need access?",  "type": "checkbox","mandatory": "no",
                     "format": "default1", "name": "dc_need_access",
                     "default1": "", 'length': "full", "options": options1, })
            # else:
            #     para_dict.append(
            #         {"desc": "Which dc need access?","mandatory": "no",
            #          "type": "checkbox", "format": "default1", "name": "dc_need_access",
            #          "default1": "",  'length': "full",
            #          "options": options1, })

            options2 = [{"value": "Grn200", "label": "Grn200"},
                        {"value": "Blu300", "label": "Blu300"}, ]

            if pre_response1.has_key("connectivity_req") and "data center" in pre_response1.get("connectivity_req"):
                para_dict.append(
                    {"desc": "Which vn need access?", "hide": "hide", "rhide": "hide",
                     "type": "checkbox", "format": "default1", "name": "vn_need_access",
                     "default1": "", "condition": "Other", 'length': "full",
                     "options": options2, })
            # else:
            #     para_dict.append(
            #         {"desc": "Which vn need access?", "hide": "hide", "rhide": "hide",
            #          "type": "checkbox", "format": "default1", "name": "vn_need_access",
            #          "default1": "", "condition": "Other", 'length': "full",
            #          "options": options2, })

            options3 = [{"value": "500p", "label": "500p"},
                        {"value": "300p", "label": "300p"}, ]

            if pre_response1.has_key("connectivity_req") and "inter sites" in pre_response1.get("connectivity_req"):

                para_dict.append(
                    {"desc": "Which sites need access?", "hide": "hide",
                     "type": "checkbox", "format": "default1", "name": "site_need_access",
                     "default1": "", "condition": "Other", 'length': "full",
                     "options": options3, })
            # else:
            #     para_dict.append(
            #         {"desc": "Which sites need access?", "hide": "hide",
            #          "type": "checkbox", "format": "default1", "name": "site_need_access",
            #          "default1": "", "condition": "Other", 'length': "full",
            #          "options": options3, })

            options4 = [{"value": "Grn200", "label": "Grn200"},
                        {"value": "Blu300", "label": "Blu300"}, ]

            if pre_response1.has_key("connectivity_req") and "inter sites" in pre_response1.get("connectivity_req"):

                para_dict.append(
                    {"desc": "Which vn need access?", "hide": "hide",
                     "type": "checkbox", "format": "default1", "name": "vn_need_access_site",
                     "default1": "", "condition": "Other", 'length': "full",
                     "options": options4, })
            # else:
            #     para_dict.append(
            #         {"desc": "Which vn need access?", "hide": "hide",
            #          "type": "checkbox", "format": "default1", "name": "vn_need_access_site",
            #          "default1": "", "condition": "Other", 'length': "full",
            #          "options": options4, })

            options5 = [{"value": "200", "label": "200"},
                        {"value": "310", "label": "310"}, {"value": "300", "label": "300"}, ]
            # if old_data.has_key("connectivity_req") and "inter vlan" in old_data.get("connectivity_req"):
            if pre_response1.has_key("connectivity_req") and "inter vlan" in pre_response1.get("connectivity_req"):

                para_dict.append(
                    {"desc": "Which vlan's need access?", "hide": "hide",
                     "type": "checkbox", "format": "default1", "name": "vlan_need_access_site",
                     "default1": "", "condition": "Other", 'length': "full",
                     "options": options5, })
            # else:
            #     para_dict.append(
            #         {"desc": "Which vlan's need access?", "hide": "hide",
            #          "type": "checkbox", "format": "default1", "name": "vlan_need_access_site",
            #          "default1": "", "condition": "Other", 'length': "full",
            #          "options": options5, })

            options7 = [{"value": "200", "label": "200"},
                        {"value": "310", "label": "310"}, {"value": "300", "label": "300"}, ]
            # if old_data.has_key("connectivity_req") and "intra vlan" in old_data.get("connectivity_req"):
            if pre_response1.has_key("connectivity_req") and "inter vlan" in pre_response1.get("connectivity_req"):

                para_dict.append(
                    {"desc": "Which device type need access?", "hide": "hide",
                     "type": "checkbox", "format": "default1", "name": "device_need_access",
                     "default1": "", "condition": "Other", 'length': "full",
                     "options": options7, })
            # else:
            #     para_dict.append(
            #         {"desc": "Which device type need access?", "hide": "hide",
            #          "type": "checkbox", "format": "default1", "name": "device_need_access",
            #          "default1": "", "condition": "Other", 'length': "full",
            #          "options": options7, })

            # options6 = [{"value": "200", "label": "200"},
            #             {"value": "310", "label": "310"}, {"value": "300", "label": "300"}, ]
            #
            # if old_data.has_key("vlan_need_access_site"):
            #
            #     para_dict.append(
            #         {"desc": "Which vlan's need access?", "hide": "hide",
            #          "type": "checkbox", "format": "default1", "name": "vlan_need_access_site",
            #          "default1": "", "condition": "Other", 'length': "full",
            #          "options": options6, })
            # else:
            #     para_dict.append(
            #         {"desc": "Which vlan's need access?", "hide": "hide",
            #          "type": "checkbox", "format": "default1", "name": "vlan_need_access_site",
            #          "default1": "", "condition": "Other", 'length': "full",
            #          "options": options6, })
        #Enterprise Firewall
        if req_type == "14":
            if response.session.has_key("customer") and response.session["customer"] != "":
                para_dict.append(
                    {"name": "customer", "format": "", "default1": response.session["customer"], "output": "",
                     "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide"})
            else:
                if pre_response.has_key("customer"):
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
                else:
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
            options = [{"value": "New Object Groups", "label": "Firewall Rules with New Object Groups"},
                       {"value": "Existing Object Groups", "label": "Firewall Rules with Existing Object Groups"},
                       {"value": "Config_firewall_rule", "label": "Configure Checkpoint Firewall Rule"}]
            if pre_response.has_key("taskid"):
                para_dict.append(
                    {"name": "taskid", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Change No.", "mandatory": "no", "hide": "hide", "send": "yes"})
            else:
                para_dict.append(
                    {"name": "taskid", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Change No.", "mandatory": "no", "hide": "hide", "send": "yes"})
            if pre_response.has_key("service"):
                para_dict.append({"note": "", "default1": pre_response.get("service"), "name": "service", "send": "yes",
                                  "type": "dropdown", "options": options, "desc": "Service"})
            else:
                para_dict.append({"note": "", "default1": "1", "name": "service", "send": "yes", "type": "dropdown",
                                  "options": options, "desc": "Service"})
        #Query
        if req_type == "15":
            if response.session.has_key("customer") and response.session["customer"] != "":
                para_dict.append(
                    {"name": "customer", "format": "", "default1": response.session["customer"], "output": "",
                     "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide"})
            else:
                if pre_response.has_key("customer"):
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
                else:
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
            para_dict.append({"name": "devices", "format": "", "default1": "", "output": "", "type": "tags-auto",
                              "example": "", "desc": "APIC IP",
                              "mandatory": "no", "hide": "hide"})
        #Discovery
        if req_type == "16":
            if response.session.has_key("customer") and response.session["customer"] != "":
                para_dict.append(
                    {"name": "customer", "format": "", "default1": response.session["customer"], "output": "",
                     "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide"})
            else:
                if pre_response.has_key("customer"):
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
                else:
                    para_dict.append(
                        {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                         "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                         "options": get_customer_options()})
            para_dict.append({"name": "devices", "format": "", "default1": "", "output": "", "type": "tags-auto",
                              "example": "", "desc": "APIC IP",
                              "mandatory": "no", "hide": "hide"})
        #Parameters
        if req_type == "11":
            from mysite.models import CommonSetupParameters
            cpar = 0
            if pre_response.has_key("item"):
                cpar = 1
                item = pre_response["item"]
                entry = CommonSetupParameters.objects.filter(parameter=item).first()
                label = entry.label
                variable = entry.variable
                value = entry.value
                regex = entry.regex
                type = entry.type
                regextype = entry.regextype
                location = entry.location
                cond1field = entry.cond1field
                cond1val = entry.cond1val
                paramter = pre_response["item"]

            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            from mysite.models import ApicIpDb
            options1 = []
            dict1 = {}
            dict1["label"] = "Global"
            dict1["value"] = "all"
            options1.append(dict1)
            entry = ApicIpDb.objects.all()
            if entry:
                for dict in entry:
                    dict1 = {}
                    dict1["label"] = dict.label
                    dict1["value"] = dict.name
                    options1.append(dict1)
            if pre_response.has_key("location"):
                para_dict.append({"name": "location", "format": "", "default1": pre_response["location"], "output": "",
                                  "type": "dropdown", "example": "", "send": "yes", "desc": "Site",
                                  "mandatory": "no", "hide": "hide", "options": options1})
            elif cpar and location:
                para_dict.append(
                    {"name": "location", "format": "", "default1": location, "output": "", "type": "dropdown",
                     "example": "", "send": "yes", "desc": "Site", "mandatory": "no", "hide": "hide",
                     "options": options1})
            else:
                para_dict.append(
                    {"name": "location", "format": "", "default1": "", "output": "", "type": "dropdown", "example": "",
                     "send": "yes", "desc": "Site", "mandatory": "no", "hideyp": "hide", "options": options1})
            if pre_response.has_key("actionsr"):
                para_dict.append({"name": "actionsr", "format": "", "default1": pre_response["actionsr"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no", "hide": "hide",
                                  "options": [{"label": "Add", "value": "1"}, {"label": "Update", "value": "2"},
                                              {"label": "Delete", "value": "3"}], "send": "yes"})
            else:
                para_dict.append(
                    {"name": "actionsr", "format": "", "default1": "1", "output": "", "type": "radio", "example": "",
                     "desc": "Action", "mandatory": "no", "hide": "hide",
                     "options": [{"label": "Add", "value": "1"}, {"label": "Update", "value": "2"},
                                 {"label": "Delete", "value": "3"}], "send": "yes"})
            if (pre_response.has_key("actionsr") and pre_response["actionsr"] == "1") or not pre_response.has_key(
                    "actionsr"):
                if pre_response.has_key("paratype"):
                    para_dict.append(
                        {"name": "paratype", "format": "", "default1": pre_response["paratype"], "output": "",
                         "type": "text", "example": "", "desc": "Parameter Name", "mandatory": "no", "hide": "hide",
                         "send": "yes"})
                elif cpar and paramter:
                    para_dict.append(
                        {"name": "paratype", "format": "", "default1": paramter, "output": "", "type": "text",
                         "example": "", "desc": "Parameter Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                else:
                    para_dict.append(
                        {"name": "paratype", "format": "", "default1": "", "output": "", "type": "text", "example": "",
                         "desc": "Parameter Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                if pre_response.has_key("variablesr"):
                    para_dict.append(
                        {"name": "variablesr", "format": "", "default1": pre_response["variablesr"], "output": "",
                         "type": "text", "example": "", "desc": "Variable", "mandatory": "no", "hide": "hide"})
                elif cpar and variable:
                    para_dict.append(
                        {"name": "variablesr", "format": "", "default1": variable, "output": "", "type": "text",
                         "example": "", "desc": "Variable", "mandatory": "no", "hide": "hide"})
                else:
                    para_dict.append({"name": "variablesr", "format": "", "default1": "", "output": "", "type": "text",
                                      "example": "", "desc": "Variable", "mandatory": "no", "hide": "hide"})
                # if pre_response.has_key("vtypesr"):
                # para_dict.append({"name": "vtypesr", "format": "", "default1":pre_response["vtypesr"], "output": "", "type": "radio", "example": "", "desc": "Is it fixed value ?","mandatory":"no","hide":"hide","options":[{"label":"Yes","value":"3"},{"label":"No","value":"0"}]})
                # elif  cpar and type:
                # para_dict.append({"name": "vtypesr", "format": "", "default1":type, "output": "", "type": "radio", "example": "", "desc": "Is it fixed value ?","mandatory":"no","hide":"hide","options":[{"label":"Yes","value":"3"},{"label":"No","value":"0"}]})
                # else:
                # para_dict.append({"name": "vtypesr", "format": "", "default1":"3", "output": "", "type": "radio", "example": "", "desc": "Is it fixed value ?","mandatory":"no","hide":"hide","options":[{"label":"Yes","value":"3"},{"label":"No","value":"0"}]})
                if pre_response.has_key("vtypesr"):
                    para_dict.append(
                        {"name": "vtypesr", "format": "", "default1": pre_response["vtypesr"], "output": "",
                         "type": "dropdown", "example": "", "desc": "Input Type", "mandatory": "no", "hide": "hide",
                         "options": [{"label": "Textbox", "value": "0"},
                                     {"label": "Radio", "value": "1", "hide": "hide", "trigger": ["labelsr"]},
                                     {"label": "Dropdown", "value": "2", "hide": "hide", "trigger": ["labelsr"]},
                                     {"label": "Fixed", "value": "3"}]})
                elif cpar and type:
                    para_dict.append({"name": "vtypesr", "format": "", "default1": type, "output": "", "type": "radio",
                                      "example": "", "desc": "Input Type ?", "mandatory": "no", "hide": "hide",
                                      "options": [{"label": "Textbox", "value": "0"},
                                                  {"label": "Radio", "value": "1", "hide": "hide",
                                                   "trigger": ["labelsr"]},
                                                  {"label": "Dropdown", "value": "2", "hide": "hide",
                                                   "trigger": ["labelsr"]}, {"label": "Fixed", "value": "3"}]})
                else:
                    para_dict.append(
                        {"name": "vtypesr", "format": "", "default1": "0", "output": "", "type": "radio", "example": "",
                         "desc": "Input Type", "mandatory": "no", "hide": "hide",
                         "options": [{"label": "Textbox", "value": "0"},
                                     {"label": "Radio", "value": "1", "hide": "hide", "trigger": ["labelsr"]},
                                     {"label": "Dropdown", "value": "2", "hide": "hide", "trigger": ["labelsr"]},
                                     {"label": "Fixed", "value": "3"}]})
                if pre_response.has_key("regexsr"):
                    para_dict.append(
                        {"name": "regexsr", "format": "", "default1": pre_response["regexsr"], "output": "",
                         "type": "radio", "example": "", "desc": "Regex", "mandatory": "no", "hide": "hide",
                         "options": [{"label": "No Regex", "value": "1"},
                                     {"label": "Built-In Regex", "value": "2", "hide": "hide",
                                      "trigger": ["builtinsr"]},
                                     {"label": "Customize", "value": "3", "hide": "hide", "trigger": ["customizesr"]}]})
                elif cpar and regextype:
                    para_dict.append(
                        {"name": "regexsr", "format": "", "default1": regextype, "output": "", "type": "radio",
                         "example": "", "desc": "Regex", "mandatory": "no", "hide": "hide",
                         "options": [{"label": "No Regex", "value": "1"},
                                     {"label": "Built-In Regex", "value": "2", "hide": "hide",
                                      "trigger": ["builtinsr"]},
                                     {"label": "Customize", "value": "3", "hide": "hide", "trigger": ["customizesr"]}]})
                else:
                    para_dict.append(
                        {"name": "regexsr", "format": "", "default1": "1", "output": "", "type": "radio", "example": "",
                         "desc": "Regex", "mandatory": "no", "hide": "hide",
                         "options": [{"label": "No Regex", "value": "1"},
                                     {"label": "Built-In Regex", "value": "2", "hide": "hide",
                                      "trigger": ["builtinsr"]},
                                     {"label": "Customize", "value": "3", "hide": "hide", "trigger": ["customizesr"]}]})
                if pre_response.has_key("builtinsr"):
                    para_dict.append(
                        {"name": "builtinsr", "format": "", "default1": pre_response["builtinsr"], "output": "",
                         "type": "radio", "example": "", "desc": "Built-In Regex", "mandatory": "no", "hide": "hide",
                         "options": [{"label": "IPV4", "value": "1"}, {"label": "IPV6", "value": "2"},
                                     {"label": "IPV4 Multicast", "value": "3"}, {"label": "Digit", "value": "4"}]})
                elif cpar and regextype == "2":
                    para_dict.append(
                        {"name": "builtinsr", "format": "", "default1": regex, "output": "", "type": "radio",
                         "example": "", "desc": "Built-In Regex", "mandatory": "no", "hide": "hide",
                         "options": [{"label": "IPV4", "value": "1"}, {"label": "IPV6", "value": "2"},
                                     {"label": "IPV4 Multicast", "value": "3"}, {"label": "Digit", "value": "4"}]})
                else:
                    para_dict.append({"name": "builtinsr", "format": "", "default1": "1", "output": "", "type": "radio",
                                      "example": "", "desc": "Built-In Regex", "mandatory": "no", "hide": "hide",
                                      "options": [{"label": "IPV4", "value": "1"}, {"label": "IPV6", "value": "2"},
                                                  {"label": "IPV4 Multicast", "value": "3"},
                                                  {"label": "Digit", "value": "4"}]})
                if pre_response.has_key("customizesr"):
                    para_dict.append(
                        {"name": "customizesr", "format": "", "default1": pre_response["customizesr"], "output": "",
                         "type": "text", "example": "", "desc": "Custom Regex", "mandatory": "no", "hide": "hide"})
                elif cpar and regextype == "3":
                    para_dict.append(
                        {"name": "customizesr", "format": "", "default1": regex, "output": "", "type": "text",
                         "example": "", "desc": "Custom Regex", "mandatory": "no", "hide": "hide"})
                else:
                    para_dict.append({"name": "customizesr", "format": "", "default1": "", "output": "", "type": "text",
                                      "example": "", "desc": "Custom Regex", "mandatory": "no", "hide": "hide"})

                if pre_response.has_key("valuesr"):
                    para_dict.append(
                        {"name": "valuesr", "format": "", "default1": pre_response["valuesr"], "output": "",
                         "type": "text", "example": "", "desc": "Value", "mandatory": "no", "hide": "hide"})
                elif cpar and value:
                    para_dict.append({"name": "valuesr", "format": "", "default1": value, "output": "", "type": "text",
                                      "example": "", "desc": "Value", "mandatory": "no", "hide": "hide"})
                else:
                    para_dict.append(
                        {"name": "valuesr", "format": "", "default1": "", "output": "", "type": "text", "example": "",
                         "desc": "Value", "mandatory": "no", "hide": "hide"})
                if pre_response.has_key("labelsr"):
                    para_dict.append(
                        {"name": "labelsr", "format": "", "default1": pre_response["labelsr"], "output": "",
                         "type": "text", "example": "", "desc": "Label", "mandatory": "no", "hide": "hide"})
                # elif cpar and type == "1" or type == "2":
                # para_dict.append({"name": "labelsr", "format": "", "default1":label, "output": "", "type": "text", "example": "", "desc": "Label","mandatory":"no","hide":"hide"})
                else:
                    para_dict.append(
                        {"name": "labelsr", "format": "", "default1": "", "output": "", "type": "text", "example": "",
                         "desc": "Label", "mandatory": "no", "hide": "hide"})
                if pre_response.has_key("customcondsr"):
                    para_dict.append(
                        {"name": "customcondsr", "format": "", "default1": pre_response["customcondsr"], "output": "",
                         "type": "hidden", "example": "", "desc": "Conditional Parameter 1", "mandatory": "no",
                         "hide": "hide",
                         "options": [{"label": "Prod1", "value": "Prod1"}, {"label": "Prod2", "value": "Prod2"}]})
                else:
                    para_dict.append(
                        {"name": "customcondsr", "format": "", "default1": "", "output": "", "type": "hidden",
                         "example": "", "desc": "Conditional Parameter 1", "mandatory": "no", "hide": "hide",
                         "options": [{"label": "Prod1", "value": "Prod1"}, {"label": "Prod2", "value": "Prod2"}]})
                if pre_response.has_key("customcondvalsr"):
                    para_dict.append(
                        {"name": "customcondvalsr", "format": "", "default1": pre_response["customcondvalsr"],
                         "output": "", "type": "hidden", "example": "", "desc": "Value", "mandatory": "no",
                         "hide": "hide"})
                else:
                    para_dict.append({"name": "customcondvalsr", "format": "", "default1": "EPG,PROD", "output": "",
                                      "type": "hidden", "example": "", "desc": "Value", "mandatory": "no",
                                      "hide": "hide"})

            if pre_response.has_key("actionsr") and pre_response["actionsr"] == "2":
                # from mysite.models import ApicIpDb
                # options1 = []
                # dict1 = {}
                # dict1["label"] = "Global"
                # dict1["value"] ="all"
                # options1.append(dict1) 
                # entry  = ApicIpDb.objects.all()
                # if entry:
                # for dict in entry:
                # dict1 = {}
                # dict1["label"] = dict.label
                # dict1["value"] =dict.name
                # options1.append(dict1)
                # if pre_response.has_key("location"):
                # para_dict.append({"name": "location", "format": "", "default1":pre_response["location"], "output": "", "type": "dropdown", "example": "", "desc": "Location","mandatory":"no","hide":"hide","send":"yes","options":options1})
                # # elif cpar and location:
                # # para_dict.append({"name": "location", "format": "", "default1":location, "output": "", "type": "dropdown", "example": "", "desc": "Location","mandatory":"no","hide":"hide","options":options1})
                # else:
                # para_dict.append({"name": "location", "format": "", "default1":"", "output": "", "type": "dropdown", "example": "", "desc": "Location","mandatory":"no","hide":"hide","send":"yes","options":options1})
                if pre_response.has_key("location"):
                    e1 = SetupParameters.objects.filter(location=pre_response.get("location"), customer=defaultcustomer).all()
                    options3 = []
                    if e1:
                        for ele in e1:
                            dict1 = {}
                            dict1["label"] = ele.parameter
                            dict1["value"] = ele.parameter
                            options3.append(dict1)
                    print options3
                    if pre_response.has_key("paratype"):
                        para_dict.append(
                            {"name": "paratype", "format": "", "default1": pre_response["paratype"], "output": "",
                             "type": "dropdown-autocomplete", "example": "", "desc": "Parameter Name",
                             "mandatory": "no", "hide": "hide", "send": "yes", "options": options3})
                    else:
                        para_dict.append({"name": "paratype", "format": "", "default1": "", "output": "",
                                          "type": "dropdown-autocomplete", "example": "", "desc": "Parameter Name",
                                          "mandatory": "no", "hide": "hide", "send": "yes", "options": options3})
                    if pre_response.has_key("paratype") and pre_response.has_key("location"):
                        print pre_response.get("paratype")
                        print pre_response.get("location")
                        e2 = SetupParameters.objects.filter(parameter=pre_response.get("paratype"), customer=defaultcustomer,
                                                                  location=pre_response.get("location")).first()
                        print e2
                        if e2:
                            para_dict.append({"name": "variablesr", "format": "", "default1": e2.variable, "output": "",
                                              "type": "text", "example": "", "desc": "Variable", "mandatory": "no",
                                              "hide": "hide"})
                            if pre_response.has_key("vtypesr"):
                                para_dict.append({"name": "vtypesr", "format": "", "default1": e2.type, "output": "",
                                                  "type": "radio", "example": "", "desc": "Input Type",
                                                  "mandatory": "no", "hide": "hide",
                                                  "options": [{"label": "Textbox", "value": "0"},
                                                              {"label": "Radio", "value": "1", "hide": "hide",
                                                               "trigger": ["labelsr"]},
                                                              {"label": "Dropdown", "value": "2", "hide": "hide",
                                                               "trigger": ["labelsr"]},
                                                              {"label": "Fixed", "value": "3"}]})
                            elif cpar and type:
                                para_dict.append(
                                    {"name": "vtypesr", "format": "", "default1": type, "output": "", "type": "radio",
                                     "example": "", "desc": "Input Type ?", "mandatory": "no", "hide": "hide",
                                     "options": [{"label": "Textbox", "value": "0"},
                                                 {"label": "Radio", "value": "1", "hide": "hide",
                                                  "trigger": ["labelsr"]},
                                                 {"label": "Dropdown", "value": "2", "hide": "hide",
                                                  "trigger": ["labelsr"]}, {"label": "Fixed", "value": "3"}]})
                            else:
                                para_dict.append({"name": "vtypesr", "format": "", "default1": e2.type, "output": "",
                                                  "type": "radio", "example": "", "desc": "Input Type",
                                                  "mandatory": "no", "hide": "hide",
                                                  "options": [{"label": "Textbox", "value": "0"},
                                                              {"label": "Radio", "value": "1", "hide": "hide",
                                                               "trigger": ["labelsr"]},
                                                              {"label": "Dropdown", "value": "2", "hide": "hide",
                                                               "trigger": ["labelsr"]},
                                                              {"label": "Fixed", "value": "3"}]})
                            if pre_response.has_key("regexsr"):
                                para_dict.append(
                                    {"name": "regexsr", "format": "", "default1": e2.regextype, "output": "",
                                     "type": "radio", "example": "", "desc": "Regex", "mandatory": "no", "hide": "hide",
                                     "options": [{"label": "No Regex", "value": "1"},
                                                 {"label": "Built-In Regex", "value": "2", "hide": "hide",
                                                  "trigger": ["builtinsr"]},
                                                 {"label": "Customize", "value": "3", "hide": "hide",
                                                  "trigger": ["customizesr"]}]})
                            elif cpar and regextype:
                                para_dict.append({"name": "regexsr", "format": "", "default1": regextype, "output": "",
                                                  "type": "radio", "example": "", "desc": "Regex", "mandatory": "no",
                                                  "hide": "hide", "options": [{"label": "No Regex", "value": "1"},
                                                                              {"label": "Built-In Regex", "value": "2",
                                                                               "hide": "hide",
                                                                               "trigger": ["builtinsr"]},
                                                                              {"label": "Customize", "value": "3",
                                                                               "hide": "hide",
                                                                               "trigger": ["customizesr"]}]})
                            else:
                                para_dict.append(
                                    {"name": "regexsr", "format": "", "default1": e2.regextype, "output": "",
                                     "type": "radio", "example": "", "desc": "Regex", "mandatory": "no", "hide": "hide",
                                     "options": [{"label": "No Regex", "value": "1"},
                                                 {"label": "Built-In Regex", "value": "2", "hide": "hide",
                                                  "trigger": ["builtinsr"]},
                                                 {"label": "Customize", "value": "3", "hide": "hide",
                                                  "trigger": ["customizesr"]}]})
                            if pre_response.has_key("builtinsr"):
                                para_dict.append({"name": "builtinsr", "format": "", "default1": e2.regex, "output": "",
                                                  "type": "radio", "example": "", "desc": "Built-In Regex",
                                                  "mandatory": "no", "hide": "hide",
                                                  "options": [{"label": "IPV4", "value": "1"},
                                                              {"label": "IPV6", "value": "2"},
                                                              {"label": "IPV4 Multicast", "value": "3"},
                                                              {"label": "Digit", "value": "4"}]})
                            elif cpar and regextype == "2":
                                para_dict.append({"name": "builtinsr", "format": "", "default1": regex, "output": "",
                                                  "type": "radio", "example": "", "desc": "Built-In Regex",
                                                  "mandatory": "no", "hide": "hide",
                                                  "options": [{"label": "IPV4", "value": "1"},
                                                              {"label": "IPV6", "value": "2"},
                                                              {"label": "IPV4 Multicast", "value": "3"},
                                                              {"label": "Digit", "value": "4"}]})
                            else:
                                para_dict.append({"name": "builtinsr", "format": "", "default1": e2.regex, "output": "",
                                                  "type": "radio", "example": "", "desc": "Built-In Regex",
                                                  "mandatory": "no", "hide": "hide",
                                                  "options": [{"label": "IPV4", "value": "1"},
                                                              {"label": "IPV6", "value": "2"},
                                                              {"label": "IPV4 Multicast", "value": "3"},
                                                              {"label": "Digit", "value": "4"}]})
                            if pre_response.has_key("customizesr"):
                                para_dict.append(
                                    {"name": "customizesr", "format": "", "default1": e2.regex, "output": "",
                                     "type": "text", "example": "", "desc": "Custom Regex", "mandatory": "no",
                                     "hide": "hide"})
                            elif cpar and regextype == "3":
                                para_dict.append({"name": "customizesr", "format": "", "default1": regex, "output": "",
                                                  "type": "text", "example": "", "desc": "Custom Regex",
                                                  "mandatory": "no", "hide": "hide"})
                            else:
                                para_dict.append(
                                    {"name": "customizesr", "format": "", "default1": e2.regex, "output": "",
                                     "type": "text", "example": "", "desc": "Custom Regex", "mandatory": "no",
                                     "hide": "hide"})

                            # if pre_response.has_key("valuesr"):
                            # para_dict.append({"name": "valuesr", "format": "", "default1":pre_response["valuesr"], "output": "", "type": "text", "example": "", "desc": "Value","mandatory":"no","hide":"hide"})
                            # elif cpar and value:
                            # para_dict.append({"name": "valuesr", "format": "", "default1":value, "output": "", "type": "text", "example": "", "desc": "Value","mandatory":"no","hide":"hide"})
                            # else:
                            para_dict.append(
                                {"name": "valuesr", "format": "", "default1": e2.value, "output": "", "type": "text",
                                 "example": "", "desc": "Value", "mandatory": "no", "hide": "hide"})
                            if pre_response.has_key("labelsr"):
                                para_dict.append(
                                    {"name": "labelsr", "format": "", "default1": pre_response["labelsr"], "output": "",
                                     "type": "text", "example": "", "desc": "Label", "mandatory": "no", "hide": "hide"})
                            elif cpar and label:
                                para_dict.append(
                                    {"name": "labelsr", "format": "", "default1": label, "output": "", "type": "text",
                                     "example": "", "desc": "Label", "mandatory": "no", "hide": "hide"})
                            else:
                                para_dict.append({"name": "labelsr", "format": "", "default1": e2.label, "output": "",
                                                  "type": "text", "example": "", "desc": "Label", "mandatory": "no",
                                                  "hide": "hide"})
                            if pre_response.has_key("customcondsr"):
                                para_dict.append(
                                    {"name": "customcondsr", "format": "", "default1": pre_response["customcondsr"],
                                     "output": "", "type": "hidden", "example": "", "desc": "Conditional Parameter 1",
                                     "mandatory": "no", "hide": "hide",
                                     "options": [{"label": "Prod1", "value": "Prod1"},
                                                 {"label": "Prod2", "value": "Prod2"}]})
                            else:
                                para_dict.append(
                                    {"name": "customcondsr", "format": "", "default1": e2.cond1field, "output": "",
                                     "type": "hidden", "example": "", "desc": "Conditional Parameter 1",
                                     "mandatory": "no", "hide": "hide",
                                     "options": [{"label": "Prod1", "value": "Prod1"},
                                                 {"label": "Prod2", "value": "Prod2"}]})
                            if pre_response.has_key("customcondvalsr"):
                                para_dict.append({"name": "customcondvalsr", "format": "",
                                                  "default1": pre_response["customcondvalsr"], "output": "",
                                                  "type": "hidden", "example": "", "desc": "Value", "mandatory": "no",
                                                  "hide": "hide"})
                            else:
                                para_dict.append(
                                    {"name": "customcondvalsr", "format": "", "default1": e2.cond1val, "output": "",
                                     "type": "hidden", "example": "", "desc": "Value", "mandatory": "no",
                                     "hide": "hide"})
            if pre_response.has_key("actionsr") and pre_response["actionsr"] == "3":
                # from mysite.models import ApicIpDb
                # options1 = []
                # dict1 = {}
                # dict1["label"] = "Global"
                # dict1["value"] ="all"
                # options1.append(dict1) 
                # entry  = ApicIpDb.objects.all()
                # if entry:
                # for dict in entry:
                # dict1 = {}
                # dict1["label"] = dict.label
                # dict1["value"] =dict.name
                # options1.append(dict1)
                # if pre_response.has_key("location"):
                # para_dict.append({"name": "location", "format": "", "default1":pre_response["location"], "output": "", "type": "dropdown", "example": "", "desc": "Location","mandatory":"no","hide":"hide","send":"yes","options":options1})
                # elif cpar and location:
                # para_dict.append({"name": "location", "format": "", "default1":location, "output": "", "type": "dropdown", "example": "", "desc": "Location","mandatory":"no","hide":"hide","options":options1})
                # else:
                # para_dict.append({"name": "location", "format": "", "default1":options1[0]["value"], "output": "", "type": "dropdown", "example": "", "desc": "Location","mandatory":"no","hide":"hide","send":"yes","options":options1})
                if pre_response.has_key("location"):
                    e1 = CommonSetupParameters.objects.filter(location=pre_response.get("location")).all()
                    options3 = []
                    if entry:
                        for ele in e1:
                            dict1 = {}
                            dict1["label"] = ele.parameter
                            dict1["value"] = ele.parameter
                            options3.append(dict1)
                    if pre_response.has_key("paratype"):
                        para_dict.append(
                            {"name": "paratype", "format": "", "default1": pre_response["paratype"], "output": "",
                             "type": "dropdown-autocomplete", "example": "", "desc": "Parameter Name",
                             "mandatory": "no", "hide": "hide", "options": options3})
                    else:
                        para_dict.append({"name": "paratype", "format": "", "default1": "", "output": "",
                                          "type": "dropdown-autocomplete", "example": "", "desc": "Parameter Name",
                                          "mandatory": "no", "hide": "hide", "options": options3})
        #Network Connections
        if req_type == '20':
            para_dict.append({"name": "network_connections", "format": "", "default1": "network_connections", "output": "",
                              "type": "hidden", "example": "", "send": "yes", "desc": "Network Connection",
                              "mandatory": "no", "hide": "hide"})
        #Parameters- Bulk
        if req_type == '19':
            from mysite.models import ApicIpDb
            options1 = []
            dict1 = {}
            dict1["label"] = "Global"
            dict1["value"] = "all"
            options1.append(dict1)
            entry = ApicIpDb.objects.all()
            if entry:
                for dict in entry:
                    dict1 = {}
                    dict1["label"] = dict.label
                    dict1["value"] = dict.name
                    options1.append(dict1)
            if pre_response.has_key("location"):
                para_dict.append({"name": "location", "format": "", "default1": pre_response["location"], "output": "",
                                  "type": "dropdown", "example": "", "send": "yes", "desc": "Site",
                                  "mandatory": "no", "hide": "hide", "options": options1})
            else:
                para_dict.append(
                    {"name": "location", "format": "", "default1": "", "output": "", "type": "dropdown", "example": "",
                     "send": "yes", "desc": "Site", "mandatory": "no", "hide": "hide", "options": options1})
            if pre_response.has_key("actionsr"):
                para_dict.append({"name": "actionsr", "format": "", "default1": pre_response["actionsr"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no", "hide": "hide",
                                  "options": [{"label": "Add", "value": "add"}, {"label": "Update", "value": "update"},
                                              {"label": "Delete", "value": "delete"}], "send": "yes"})
            else:
                para_dict.append(
                    {"name": "actionsr", "format": "", "default1": "1", "output": "", "type": "radio", "example": "",
                     "desc": "Action", "mandatory": "no", "hide": "hide",
                     "options": [{"label": "Add", "value": "add"}, {"label": "Update", "value": "update"},
                                 {"label": "Delete", "value": "delete"}], "send": "yes"})
        #SD Access Campus Brownfield
        if req_type == "17":
            # BrownFiled Campus Design
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                             {"value": "modify",
                                                                              "label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify "},
                                 {"value": "clone", "label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=3).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Enter Service Request No.", "options": temp})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                     "example": "", "desc": "Project Phase", "mandatory": "no",#'length':'full',
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"},
                                 {"value": "Discovery", "label": "Discovery"},
                                 {"value": "Design", "label": "Design"},
                                 {"value": "Checklist", "label": "Check List"},
                                 {"value": "Implement", "label": "Implement"},
                                 {"value": "Verification", "label": "Verification"}]})

                # para_dict.append(
                #     {"name": "overwrite_project", "format": "", "default1": "", "output": "", "type": "radio",
                #      "example": "", "desc": "Overwrite Project", "mandatory": "no",
                #      "options": [{'value': 'Yes', 'label': 'Yes'}, {'value': 'No', 'label': 'No'}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=3).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})

            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Discovery", "label": "Discovery"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Operation", "label": "Operation"}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Operation", "label": "Operation"}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})

        if req_type == "50":
            # BrownFiled Campus Design
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": "", "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})
            if pre_response.has_key("affected_app"):
                para_dict.append(
                    {"name": "affected_app", "format": "", "default1": pre_response.get("affected_app"), "output": "", "type": "text",
                      "desc": "App Name/URL or IP", "mandatory": "no", "hide": "hide","example":"Ex:10.1.1.1 or google.com or hillroom"})
            else:
                para_dict.append(
                    {"name": "affected_app", "format": "", "default1": "", "output": "", "type": "text",
                      "desc": "App Name/URL or IP", "mandatory": "no", "hide": "hide","example":"Ex:10.1.1.1 or google.com or hillroom"})

            if pre_response.has_key("client_info_available"):
                para_dict.append({"name": "client_info_available", "format": "",
                                  "default1": pre_response.get('client_info_available'), "output": "",
                                  "type": "radio", "desc": " What Client Info Available ?",
                                  "hide": "hide", "send": "yes", "options": [
                        {"value": "MAC", "label": "MAC", "trigger": [""], "hide": "hide", },
                        {"value": "IP","label": "IP", "trigger": [""], "hide": "hide"},
                        {"value": "Username", "label": "Username", "trigger": [""], "hide": "hide"},
                        {"value": "Location", "label": "Location", "trigger": [""], "hide": "hide"},
                        {"value": "None", "label": "None", "trigger": [""], "hide": "hide"},
                    ]})
            else:
                para_dict.append(
                    {"name": "client_info_available", "format": "", "default1": "", "output": "", "type": "radio",
                     "example": "", "desc": " What Client Info Available ?", "mandatory": "", "hide": "hide",
                     "send": "yes",
                     "options": [{"value": "MAC", "label": "MAC", "trigger": [""], "hide": "hide", },
                        {"value": "IP","label": "IP", "trigger": [""], "hide": "hide"},
                        {"value": "Username", "label": "Username", "trigger": [""], "hide": "hide"},
                        {"value": "Location", "label": "Location", "trigger": [""], "hide": "hide"},
                        {"value": "None", "label": "None", "trigger": [""], "hide": "hide"}]})
            if pre_response.has_key("client_info_available") and pre_response["client_info_available"] == "MAC":
                if pre_response.has_key("User_Mac"):
                    para_dict.append(
                        {"name": "User_Mac", "format": "", "default1": pre_response.get('User_Mac'), "output": "", "type": "text",
                         "example": "", "desc": "User MAC", "mandatory": "", "hide": "hide",
                         })
                else:
                    para_dict.append(
                        {"name": "User_Mac", "format": "", "default1":"", "output": "",
                         "type": "text",
                         "example": "", "desc": "User MAC", "mandatory": "", "hide": "hide",
                         })
            if pre_response.has_key("client_info_available") and pre_response["client_info_available"] == "IP":
                if pre_response.has_key("User_ip"):
                    para_dict.append(
                        {"name": "User_ip", "format": "", "default1": pre_response.get('User_ip'), "output": "", "type": "text",
                         "example": "", "desc": "User IP Address", "mandatory": "", "hide": "hide",
                         })
                else:
                    para_dict.append(
                        {"name": "User_ip", "format": "", "default1":"", "output": "",
                         "type": "text",
                         "example": "", "desc": "User IP Address", "mandatory": "", "hide": "hide",
                         })
            if pre_response.has_key("client_info_available") and pre_response["client_info_available"] == "Username":
                if pre_response.has_key("user_name"):
                    para_dict.append(
                        {"name": "user_name", "format": "", "default1": pre_response.get('user_name'), "output": "", "type": "text",
                         "example": "", "desc": "User Name", "mandatory": "", "hide": "hide"
                         })
                else:
                    para_dict.append(
                        {"name": "user_name", "format": "", "default1": "", "output": "",
                         "type": "text","example": "", "desc": "User Name", "mandatory": "", "hide": "hide"
                         })
            if pre_response.has_key("client_info_available") and pre_response["client_info_available"] == "Location":

                if pre_response.has_key("User_location"):
                    para_dict.append(
                        {"name": "User_location", "format": "", "default1": pre_response.get('User_location'), "output": "", "type": "dropdown",
                         "example": "", "desc": "User Location", "mandatory": "", "hide": "hide",
                         "send": "yes",
                         "options": [{"value": "Campus Wireless", "label": "Campus Wireless", "trigger": [""], "hide": "hide", },
                                     {"value": "Campus Wired", "label": "Campus Wired", "trigger": [""], "hide": "hide"},
                                     {"value": "Branch Wireless", "label": "Branch Wireless", "trigger": [""], "hide": "hide"},
                                     {"value": "Branch Wired", "label": "Branch Wired", "trigger": [""], "hide": "hide"},
                                     ]})

                else:
                    para_dict.append(
                        {"name": "User_location", "format": "", "default1": "", "output": "",
                         "type": "dropdown",
                         "example": "", "desc": "User Location", "mandatory": "", "hide": "hide",
                         "send": "yes",
                         "options": [
                             {"value": "Campus Wireless", "label": "Campus Wireless", "trigger": [""], "hide": "hide", },
                             {"value": "Campus Wired", "label": "Campus Wired", "trigger": [""], "hide": "hide"},
                             {"value": "Branch Wireless", "label": "Branch Wireless", "trigger": [""], "hide": "hide"},
                             {"value": "Branch Wired", "label": "Branch Wired", "trigger": [""], "hide": "hide"},
                             ]})

                if pre_response.has_key("vpn_user"):
                    para_dict.append(
                        {"name": "vpn_user", "format": "", "default1": pre_response.get('vpn_user'), "output": "",
                         "type": "text",
                         "example": "", "desc": "VPN User", "mandatory": "", "hide": "hide"
                         })
                else:
                    para_dict.append(
                        {"name": "vpn_user", "format": "", "default1": "", "output": "",
                         "type": "text", "example": "", "desc": "VPN User", "mandatory": "", "hide": "hide"
                         })
            if pre_response.has_key("user_ip_type"):
                para_dict.append(
                    {"name": "user_ip_type", "format": "", "default1": pre_response.get('user_ip_type'),
                     "output": "", "type": "dropdown",
                     "example": "", "desc": "User IP Type", "mandatory": "", "hide": "hide",
                     "send": "yes",
                     "options": [{"value": "Campus Wireless", "label": "Campus Wireless", "trigger": [""],
                                  "hide": "hide", },
                                 {"value": "Campus Wired", "label": "Campus Wired", "trigger": [""],
                                  "hide": "hide"},
                                 {"value": "Branch Wireless", "label": "Branch Wireless", "trigger": [""],
                                  "hide": "hide"},
                                 {"value": "Branch Wired", "label": "Branch Wired", "trigger": [""],
                                  "hide": "hide"},
                                 ]})

            else:
                para_dict.append(
                    {"name": "user_ip_type", "format": "", "default1": "", "output": "",
                     "type": "dropdown",
                     "example": "", "desc": "User IP Type", "mandatory": "", "hide": "hide",
                     "send": "yes",
                     "options": [
                         {"value": "Campus Wireless", "label": "Campus Wireless", "trigger": [""],
                          "hide": "hide", },
                         {"value": "Campus Wired", "label": "Campus Wired", "trigger": [""], "hide": "hide"},
                         {"value": "Branch Wireless", "label": "Branch Wireless", "trigger": [""],
                          "hide": "hide"},
                         {"value": "Branch Wired", "label": "Branch Wired", "trigger": [""], "hide": "hide"},
                     ]})

            if pre_response.has_key("vpn_user1"):
                para_dict.append(
                    {"name": "vpn_user1", "format": "", "default1": pre_response.get('vpn_user1'), "output": "",
                     "type": "text",
                     "example": "", "desc": "VPN User", "mandatory": "", "hide": "hide"
                     })
            else:
                para_dict.append(
                    {"name": "vpn_user1", "format": "", "default1": "", "output": "",
                     "type": "text", "example": "", "desc": "VPN User", "mandatory": "", "hide": "hide"
                     })
                                # if pre_response.has_key("available_ip_or_mac"):
            #     para_dict.append({"name": "available_ip_or_mac", "format": "", "default1": pre_response.get('available_ip_or_mac'), "output": "",
            #                       "type": "radio","desc": " Client IP or MAC Available?",
            #                       "hide": "hide", "send": "yes", "options": [{"value": "Yes", "label": "Yes","trigger":["affected_user_ip_mac"],"hide": "hide",},
            #                                                                  {"value": "no",
            #                                                                   "label": "No","trigger":[""],"hide": "hide"}]})
            # else:
            #     para_dict.append(
            #         {"name": "available_ip_or_mac", "format": "", "default1": "Yes", "output": "", "type": "radio",
            #          "example": "", "desc": " Client IP or MAC Available?", "mandatory": "", "hide": "hide", "send": "yes",
            #          "options": [{"value": "Yes", "label": "Yes"},
            #                      {"value": "No","label": "No"}]})

            # if pre_response.has_key("IP_or_MAC_available_of_affected_user"):
            # if pre_response.has_key("IP_or_MAC_available_of_affected_user") and pre_response["IP_or_MAC_available_of_affected_user"] == "no":
            # para_dict.append(
            #     {"name": "affected_user", "format": "", "default1": "", "output": "", "type": "text",
            #      "example": "Ex:10.1.1.1 or mac", "desc": "User IP or Mac", "mandatory": "", "hide": "hide",
            #      "send": "yes",
            #      "options": ""})



            if pre_response.has_key("available_ip_or_mac") and pre_response["available_ip_or_mac"] == "no":
                para_dict.append(
                    {"name": "affected_source", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "Ex:10.1.1.1 or Switch name", "desc": "User, Location, Access Switch Name ", "mandatory": "", "hide": "hide",
                     "send": "yes",
                     "options": ""})


                f = open('./mysite/Json_DATA/device_baseline.json', )

                data = json.load(f)
                test_list = []
                for k in data.keys():
                    # print(i)
                    dict1 = {}
                    dict1["label"] = k
                    dict1["value"] = k
                    test_list.append(dict1)
                para_dict.append(
                    {"name": "device_type ", "format": "", "default1": "", "output": "", "type": "dropdown",
                     "example": "", "desc": "Device Type", "mandatory": "", "hide": "hide",
                     "send": "no",
                     "options": test_list})

            para_dict.append(
                {"name": "other_info", "format": "", "default1": "", "output": "", "type": "dropdown-checkbox",
                 "example": "", "desc": "Other Info", "mandatory": "",   'length':'full',
                 "vmessage": "Please Enter Service Request No.",
                 "options": [{"value": "Existing Ticket", "label": "Existing Ticket"},
                             {"value": "Single Service Affected", "label": "Single Service Affected"},
                             {"value": "Single User Affected", "label": "Single User Affected"},
                             {"value": "Regression", "label": "Regression"},
                             {"value": "Multiple Services Affected", "label": "Multiple Services Affected"},
                             {"value": "Multiple User Affected", "label": "Multiple User Affected"}]})
        # Application Connectivity Setting
        if req_type == "51":

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                            {"value": "modify","label": "Modify Project"},
                                                                             {"value": "Delete", "label": "Delete"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify Project"},
                                 {"value": "Delete", "label": "Delete"}]})

            if pre_response.get("action") == "modify":
                f = open('./mysite/Json_DATA/Application_baseline.json', )
                data = json.load(f)
                print data
                test_list = []
                for k,v in data.iteritems():
                    # print(i)
                    dict1 = {}
                    dict1["label"] = k
                    dict1["value"] = k
                    # dict1["send"] = "yes"
                    test_list.append(dict1)
                para_dict.append(
                    {"name": "select_app_name", "format": "", "default1": "", "output": "", "type": "dropdown",
                     "example": "", "desc": "Application Name", "mandatory": "no", "hide": "hide",'options':test_list})

            elif pre_response.get("action") == "Delete":
                f = open('./mysite/Json_DATA/Application_baseline.json', )
                data = json.load(f)
                print data
                test_list = []
                for k,v in data.iteritems():
                    # print(i)
                    dict1 = {}
                    dict1["label"] = k
                    dict1["value"] = k
                    # dict1["send"] = "yes"
                    test_list.append(dict1)
                para_dict.append(
                    {"name": "select_app_name", "format": "", "default1": "", "output": "", "type": "dropdown",
                     "example": "", "desc": "Application Name", "mandatory": "no", "hide": "hide",'options':test_list})

            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "app_name", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Application Name", "mandatory": "no", "hide": "hide"})

        #Hardware Refresh
        if req_type == "30":
            # Hardware Refresh
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                             {"value": "modify",
                                                                              "label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify "},
                                 {"value": "clone", "label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=3).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Enter Service Request No.", "options": temp})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                     "example": "", "desc": "Project Phase", "mandatory": "no",#'length':'full',
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"},
                                 {"value": "Discovery", "label": "Discovery"},

                                 {"value": "Design", "label": "Design"},
                                 {"value": "Checklist", "label": "Check List"},
                                 {"value": "Implement", "label": "Implement"},
                                 {"value": "Verification", "label": "Verification"}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=3).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})

            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Discovery", "label": "Discovery"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Operation", "label": "Operation"}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Operation", "label": "Operation"}]})
                # para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                #                   "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                #                   "options": [{"value": "sda", "label": "SDA"},
                #                               {"value": "non_sda", "label": "Non SDA"}]})
        #Config based on Mac
        if req_type == "35":
            # code added for "config based on mac" by harshal
            if pre_response.has_key("config_scope"):
                para_dict.append({"name": "config_scope", "format": "", "default1": pre_response["config_scope"], "output": "",
                                  "type": "dropdown", "example": "", "desc": "Configuration Scope","hide": "hide","send":"yes",
                                  "options": [{"value":"Site","label":"Site"},
                                              {"value":"Floor","label":"Floor"},
                                              {"value":"Switch","label":"Switch"}]})
            else:
                para_dict.append(
                    {"name": "config_scope", "format": "", "default1": "", "output": "", "type": "dropdown",
                     "example": "", "desc": "Configuration Scope", "hide": "hide","send":"yes",
                     "options": [{"value":"","label":"Select",},{"value":"Site","label":"Site",},
                                 {"value":"Floor","label":"Floor"},
                                 {"value":"Switch","label":"Switch"}]})

            if pre_response.has_key("config_scope") and "Site" in pre_response.get("config_scope"):
                if pre_response.has_key("site_type"):
                    para_dict.append({"name": "site_type", "format": "", "default1": pre_response["site_type"], "output": "",
                                      "type": "dropdown", "example": "", "desc": "Site Type","hide": "hide",
                                      "options": [{"value":"500p","label":"500p"},
                                                  {"value":"Garage","label":"Garage"}]})
                else:
                    para_dict.append(
                        {"name": "site_type", "format": "", "default1": "", "output": "", "type": "dropdown",
                         "example": "", "desc": "Site Type", "hide": "hide",
                         "options":[{"value":"500p","label":"500p"},
                                    {"value":"Garage","label":"Garage"}]})
            if pre_response.has_key("config_scope") and "Floor" in pre_response.get("config_scope"):
                floor_options = []
                for i in range(0, 8):
                    dict1 = {}
                    dict1["label"] = str(i)
                    dict1["value"] = str(i)
                    floor_options.append(dict1)
                floor_lst = ["Radio", "Garage1", "Garage2", "Garage3"]
                for i2 in floor_lst:
                    dict1 = {}
                    dict1["label"] = i2
                    dict1["value"] = i2
                    floor_options.append(dict1)
                if pre_response.has_key("floor_no"):
                    para_dict.append({"name": "floor_no", "format": "", "default1": pre_response["floor_no"], "output": "",
                                      "type": "dropdown-checkbox", "example": "", "desc": "Floor No","hide": "hide",
                                      "options": floor_options})
                else:
                    para_dict.append(
                        {"name": "floor_no", "format": "", "default1": "", "output": "", "type": "dropdown-checkbox",
                         "example": "", "desc": "Floor No", "hide": "hide","options":floor_options})
            if pre_response.has_key("config_scope") and "Switch" in pre_response.get("config_scope"):
                switch_options = []
                switch_lst = ["STNNSH-001-SA01", "STNNSH-001-SA02", "STNNSH-101-SA01", "STNNSH-101-SA02",
                              "STNNSH-102-SA01","STNNSH-102-SA02","STNNSH-504-SA03","STNNSH-201-SA04",
                              "STNNSH-201-SA01","STNNSH-105-SA02","STNNSH-602-SA04","STNNSH-602-SA02",
                              "STNNSH-501-SA04","STNNSH-501-SA02",]
                for i2 in switch_lst:
                    dict1 = {}
                    dict1["label"] = i2
                    dict1["value"] = i2
                    switch_options.append(dict1)
                if pre_response.has_key("switch_name"):
                    para_dict.append({"name": "switch_name", "format": "", "default1": pre_response["switch_name"], "output": "",
                                      "type": "text", "example": "", "desc": "Switch Name","hide": "hide",
                                      "options":switch_options})
                else:
                    para_dict.append(
                        {"name": "switch_name", "format": "", "default1": "", "output": "", "type": "dropdown-checkbox",
                         "example": "", "desc": "Switch Name", "hide": "hide","options":switch_options})
        #Access switch HW Request
        if req_type == "36":
            para_dict.append({"type": "dropdown", "name": "service", "desc": "Service",
                              "extraclass": "color-black", "hide": "hide", "rhide": "hide",
                              "default1": pre_response.get("service"), "send": "yes",
                              "options": [{"value": "select", "label": "Select Service"},
                                          {"value": "Precheck", "label": "Precheck"},
                                          {"value": "Postcheck", "label": "Postcheck"}]})

            if pre_response.has_key("service") and "Postcheck" in pre_response.get("service"):
                para_dict.append({"type": "radio", "name": "conn_type", "desc": "Connection Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "Upload",
                                  "options": [{"value": "Upload", "label": "Upload", "hide": "hide",
                                               "trigger": ["precheck_switch"]},
                                              {"value": "SSH", "label": "SSH"}, ]})
                # para_dict.append({"name": "precheck_switch", "format": "", "default1": "", "type": "text",
                #                   "desc": "Precheck Switch", })

            if pre_response.has_key("service") and "Precheck" in pre_response.get("service"):
                para_dict.append({"type": "radio", "name": "conn_type", "desc": "Connection Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "Upload",
                                  "options": [{"value": "Upload", "label": "Upload"},
                                              {"value": "SSH", "label": "SSH"}]})

                para_dict.append({"name": "precheck_sw", "format": "", "default1": "", "type": "text",
                                  "desc": "Hostname or IP", })

        #Network Assurance
        if req_type == "24":
            # BrownFiled Campus Design
            if pre_response.has_key("customer"):
                para_dict.append({"name": "customer", "format": "", "default1": pre_response["customer"], "output": "",
                                  "type": "hidden", "example": "", "desc": "Customer/Department", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": get_customer_options()})
            else:
                para_dict.append(
                    {"name": "customer", "format": "", "default1": defaultcustomer, "output": "", "type": "hidden",
                     "example": "", "desc": "Customer/Department", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": get_customer_options()})

            if pre_response.has_key("action"):
                para_dict.append({"name": "action", "format": "", "default1": pre_response["action"], "output": "",
                                  "type": "radio", "example": "", "desc": "Action", "mandatory": "no",
                                  "hide": "hide", "send": "yes", "options": [{"value": "add", "label": "Add Project"},
                                                                             {"value": "modify",
                                                                              "label": "Modify Project"},
                                                                             {"value": "clone",
                                                                              "label": "Clone Project"}]})
            else:
                para_dict.append(
                    {"name": "action", "format": "", "default1": "add", "output": "", "type": "radio",
                     "example": "", "desc": "Action", "mandatory": "no", "hide": "hide", "send": "yes",
                     "options": [{"value": "add", "label": "Add Project"},
                                 {"value": "modify", "label": "Modify "},
                                 {"value": "clone", "label": "Clone Project"}]})

            if pre_response.get("action") == "modify":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=3).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Enter Service Request No.", "options": temp})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "dropdown",
                     "example": "", "desc": "Project Phase", "mandatory": "no",#'length':'full',
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"},{"value": "Discovery", "label": "Discovery"}, {"value": "Design", "label": "Design"},
                                 {"value": "Implement", "label": "Implement"},
                                 {"value": "Verification", "label": "Verification"}]})
                para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})
            elif pre_response.get("action") == "clone":
                sentry = ServiceRequestDB.objects.order_by().values_list('taskid').filter(selectedvalue=3).distinct()
                temp = []
                t = {}
                t["value"] = ""
                t["label"] = "Select Project No."
                temp.append(t)
                if sentry:
                    for entry in sentry:
                        t = {}
                        t["value"] = entry[0]
                        t["label"] = entry[0]
                        temp.append(t)
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Project Name", "mandatory": "yes",
                     "vmessage": "Please Select Project Name", "options": temp})
                para_dict.append(
                    {"name": "new_project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "New Project Name", "mandatory": "yes",
                     "vmessage": "Please Select New Project Name"})

            elif pre_response.get("action") == "add":
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project Name", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Discovery", "label": "Discovery"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Operation", "label": "Operation"}]})
                para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})

            else:
                para_dict.append(
                    {"name": "project_no", "format": "", "default1": "", "output": "", "type": "text",
                     "example": "", "desc": "Project No.", "mandatory": "no", "hide": "hide", "send": "yes"})
                para_dict.append(
                    {"name": "project_phase", "format": "", "default1": "Plan", "output": "", "type": "hidden",
                     "example": "", "desc": "Project Phase", "mandatory": "no",
                     "vmessage": "Please Enter Service Request No.",
                     "options": [{"value": "Plan", "label": "Plan"}, {"value": "Design", "label": "Design"},
                                 {"value": "implement", "label": "implement"},
                                 {"value": "Operation", "label": "Operation"}]})
                para_dict.append({"type": "radio", "name": "fabric_type", "desc": "Fabric Type",
                                  "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "sda",
                                  "options": [{"value": "sda", "label": "SDA"},
                                              {"value": "non_sda", "label": "Non SDA"}]})
        if req_type == "22":
            # Option to add existing user added 08-10-2018 By PS
            para_dict.append(
                {"name": "username", "format": "",  "output": "","default1": "", "type": "text",
                 "example": "Username", "desc": "Username", "mandatory": "yes",
                 "vmessage": "Please Enter Unique username"})
            para_dict.append(
                {"name": "email", "format": "", "output": "", "default1": "", "type": "text",
                 "example": "Email", "desc": "Email", "mandatory": "no",
                 "vmessage": "Please Enter Email"})
            para_dict.append(
                {"name": "password", "format": "",  "output": "","default1": "", "type": "text",
                 "example": "Password", "desc": "Password", "mandatory": "yes",
                 "vmessage": "Please Enter password"})
            para_dict.append(
                {"name": "fname", "format": "",  "output": "","default1": "", "type": "text",
                 "example": "First Name", "desc": "First Name", "mandatory": "no",
                 "vmessage": "Please Enter First Name"})
            para_dict.append(
                {"name": "lname", "format": "",  "output": "","default1": "", "type": "text",
                 "example": "Last Name", "desc": "Last Name", "mandatory": "no",
                 "vmessage": "Please Enter Last Name"})
            para_dict.append(
                {"name": "department", "format": "",  "output": "","default1": "", "type": "text",
                 "example": "Department", "desc": "Department", "mandatory": "no",
                 "vmessage": "Please Enter Department"})
            para_dict.append(
                {"name": "subdepartment", "format": "",  "output": "","default1": "", "type": "text",
                 "example": "Sub Department", "desc": "Sub Department", "mandatory": "no",
                 "vmessage": "Please Enter Sub Department"})
            options = get_group_options()
            para_dict.append(
                {"name": "groups", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                 "example": "Groups", "desc": "Groups", "mandatory": "yes", "hide": "hide", "send": "no",
                 "options": options})
        if req_type == "23":
            print " loading this EDIT"
            # Option to edit existing user added 08-10-2018 By PS
            options = get_users_options()
            if pre_response.has_key("username"):
                para_dict.append(
                    {"name": "username", "format": "", "default1": pre_response.get("username"), "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Username", "mandatory": "yes", "hide": "hide", "send": "yes",
                     "options": options})
            else:
                para_dict.append(
                    {"name": "username", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "", "desc": "Username", "mandatory": "yes", "hide": "hide", "send": "yes",
                     "options": options})

            if pre_response.has_key("username"):
                print " loading this"
                user = User.objects.filter(username=pre_response.get("username")).all()[0]
                print user
                para_dict.append(
                    {"name": "email", "format": "", "output": "", "default1": user.email, "type": "text",
                     "example": "Email", "desc": "Email", "mandatory": "no",
                     "vmessage": "Please Enter Email"})
                para_dict.append(
                    {"name": "password", "format": "", "output": "", "default1": user.password, "type": "text",
                     "example": "Password", "desc": "Password", "mandatory": "yes",
                     "vmessage": "Please Enter password"})
                para_dict.append(
                    {"name": "fname", "format": "", "output": "", "default1": user.first_name, "type": "text",
                     "example": "First Name", "desc": "First Name", "mandatory": "no",
                     "vmessage": "Please Enter First Name"})
                para_dict.append(
                    {"name": "lname", "format": "", "output": "", "default1": user.last_name, "type": "text",
                     "example": "Last Name", "desc": "Last Name", "mandatory": "no",
                     "vmessage": "Please Enter Last Name"})
                if UserProfile.objects.filter(user=user):
                    user_profile = User.objects.filter(user=pre_response.get("username")).all()
                    dept = user.department
                    sub_dept =  "subdepartment"
                else:
                    dept = ""
                    sub_dept = ""

                para_dict.append(
                    {"name": "department", "format": "", "output": "", "default1": dept, "type": "text",
                     "example": "Department", "desc": "Department", "mandatory": "no",
                     "vmessage": "Please Enter Department"})
                para_dict.append(
                    {"name": "subdepartment", "format": "", "output": "", "default1": sub_dept, "type": "text",
                     "example": "Sub Department", "desc": "Sub Department", "mandatory": "no",
                     "vmessage": "Please Enter Sub Department"})
                options = get_group_options()
                para_dict.append(
                    {"name": "groups", "format": "", "default1": "", "output": "", "type": "dropdown-autocomplete",
                     "example": "Groups", "desc": "Groups", "mandatory": "yes", "hide": "hide", "send": "no",
                     "options": options})
        #Campus Dashboard
        if req_type == "25":
            para_dict.append({"type": "radio", "name": "device", "desc": "Scope",
                              "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "",
                              "options": [{"value": "device", "label": "Device","hide":"hide","trigger":["devices"]},
                                          {"value": "site", "label": "Site","hide":"hide","trigger":["site_id"]}]})
            para_dict.append(
                {"name": "device_ip", "default1": "", "type": "text",
                 "example": "Ex: 100.201.0.1", "desc": "Devices", "mandatory": "", "hide": "hide",
                 "options":"" })
           # para_dict.append({"name": "devices", "format": "", "default1": "", "output": "", "type": "tags-auto",
            #                  "example": "", "desc": "APIC IP",
             #                 "mandatory": "no", "hide": "hide"})

            para_dict.append(
                {"name": "site_id", "format": "", "default1": "", "output": "", "type": "dropdown",
                  "desc": "Site ID", "mandatory": "", "hide": "hide", "send": "",
                 "options":[{"value": "500p", "label": "500p"},{"value": "NC", "label": "NC"}] })
        #Campus Dashboard2
        if req_type =="26":
            para_dict.append({"type": "radio", "name": "device", "desc": "Scope",
                              "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "",
                              "options": [
                                  {"value": "device", "label": "Device(single device)"}]})

            para_dict.append({"type": "radio", "name": "connection_type", "desc": "Connection Type",
                              "extraclass": "color-black", "hide": "hide", "rhide": "hide", "default1": "",
                              "options": [{"value": "ssh", "label": "SSH",'hide':'hide','trigger':['device_ip1']},
                                          {"value": "upload", "label": "Upload"}]})

            para_dict.append(
                {"name": "device_ip1", "default1": "", "type": "text",
                 "example": "Ex: 100.201.0.1", "desc": "Devices", "mandatory": "", "hide": "hide",
                 "options": ""})

        self.para_dict = {"column": "12", "newline": "yes", "inputs": para_dict}

    def get_response_data(self):
        return self.para_dict
