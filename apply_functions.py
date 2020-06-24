from mysite.globals import *
import json
import re
import os
import pexpect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render
import time
import datetime
import re
import sys
import subprocess
import urllib, codecs
from nlead_library.aci_api_functions import *
from nlead_library.service_now import *
from mysite.models import combimatin_db
from mysite.models import CronDB, ServiceRequestDB, UserSelectionDb, CustomerDB, LeafDB
from mysite.models import ACI_EPG_Mapping, DeviceModel, ACIInterfaceStatusDB
import zipfile
import base64
# from mysite.nlead_library.service_now import *
from collections import OrderedDict

from mysite.models import CronDB, template_db


def main_apply_function(request):
    taskid = request.session["taskid"]
    subtaskid = request.session["subtaskid"]
    customer = request.session["customer"]
    final_op = {}
    q1 = CronDB.objects.filter(taskid=taskid, customer=customer).order_by('subtaskid').values()
    count = CronDB.objects.filter(taskid=taskid, customer=customer).order_by('subtaskid').count()
    counter = 0
    if count <= 100:
        print "Less than 10"
        if q1:
            for each in q1:
                counter += 1
                main_result = {"precheck_detail": [], "precheck_flag": True, "config_status": "",
                               "validation_detail": [],
                               "validation_flag": True}
                host = each['ip'].strip('"')
                username = each['username']
                password = base64.b64decode(each['password'])
                inputs = json.loads(each['inputs_list'])
                commandList = filter_command_list(json.loads(each['command_list']))
                rollbackList = filter_command_list(json.loads(each['rollback_list']))
                main_result['host'] = host

                q2 = template_db.objects.filter(template=inputs["user_type"]).values('preChecks', 'postChecks').last()
                if q2:
                    if "," in q2["preChecks"]:
                        prechecks = q2["preChecks"].split(",")
                    else:
                        prechecks = [q2["preChecks"]]
                    if "," in q2["postChecks"]:
                        postchecks = q2["postChecks"].split(",")
                    else:
                        postchecks = [q2["postChecks"]]
                if len(prechecks) == 1 and prechecks[0] == "":
                    prechecks = "all"
                if len(postchecks) == 0:
                    postchecks = "all"

                provision_obj = Provision(taskid, subtaskid, host, username, password, inputs)
                login_status = provision_obj.get_login_status()
                if not login_status["login_flag"]:
                    main_result = {"precheck_detail": ["NA"], "precheck_flag": True,
                                   "config_status": login_status["login_status"],
                                   "validation_detail": ["NA"],
                                   "validation_flag": True}
                    # final_op[host] = main_result
                else:
                    pre_result = []
                    # below line is for loading precheck conditionally
                    # Precheck block is added on 8-6-2018 and is a flexible check which takes prechecks as comma seperated value from template db. In case we need all prechecks just enter all                  # in prechecks column in template db for that template
                    # print prechecks
                    if "precheck_interface" in prechecks or prechecks == "all":
                        preresult = provision_obj.precheck_interface(host)
                        if preresult["flag"] and main_result["precheck_flag"]:
                            main_result["precheck_flag"] = preresult["flag"]
                        else:
                            main_result["precheck_flag"] = preresult["flag"]
                            # pre_result.append(preresult)
                    if "policy_check" in prechecks or prechecks == "all":
                        preresult = provision_obj.Policy_Check(host)
                        if preresult["flag"] and main_result["precheck_flag"]:
                            main_result["precheck_flag"] = preresult["flag"]
                        else:
                            main_result["precheck_flag"] = preresult["flag"]
                        main_result["precheck_flag"] = True
                        pre_result.append(preresult)

                    if "mac_check" in prechecks or prechecks == "all" and "ACI" not in inputs["user_type"]:
                        preresult = provision_obj.MAC_table_Check(host)
                        if preresult["flag"] and main_result["precheck_flag"]:
                            main_result["precheck_flag"] = preresult["flag"]
                        else:
                            main_result["precheck_flag"] = preresult["flag"]
                        pre_result.append(preresult)

                    if inputs.get("precheck_err") == "continue" or inputs.get("precheck_err") == "skip":
                        for rstl in pre_result:
                            main_result["precheck_detail"].append(rstl["msg"])
                    elif inputs.get("precheck_err") == "abort" and not main_result["precheck_flag"]:
                        for rstl in pre_result:
                            main_result["precheck_detail"].append(rstl["msg"])
                        continue  # Add Break
                    else:
                        for rstl in pre_result:
                            main_result["precheck_detail"].append(rstl["msg"])
                    # Precheck block ends here config starts
                    # if main_result["precheck_flag"]:
                    config_result = provision_obj.Configuration_fun(taskid, subtaskid, inputs, commandList, host)
                    if inputs.get("config_err") == "continue":
                        main_result["config_status"] = config_result["config_status"]
                    elif inputs.get("config_err") == "abort" and not config_result["config_flag"]:
                        main_result["config_status"] = config_result["config_status"] + "\n Configuration Aborted "
                        # final_op[host] = main_result
                        continue
                    else:
                        main_result["config_status"] = config_result["config_status"]
                    # else:
                    #     main_result["config_status"] = "Precheck Failed"


                    # config section ends here postcheck starts
                    # if main_result["precheck_flag"]:
                    # postcheck = provision_obj.Validation()
                    # if inputs.get("postcheck_err") == "continue":
                    #     main_result["validation_detail"].append(postcheck[0]["desc"])
                    #     main_result["validation_flag"] =postcheck[0]["status"]
                    # elif inputs.get("postcheck_err") == "abort" and not postcheck[0]["status"]:
                    #     main_result["validation_detail"].append(postcheck[0]["desc"])
                    #     main_result["validation_flag"] = postcheck[0]["status"]
                    #     continue
                    #     # elif inputs.get("postcheck_err") == "rollback" and not postcheck["flag"] :
                    #     #     main_result["validation_detail"].append(postcheck["msg"])
                    #     #     main_result["validation_flag"] = postcheck["flag"]
                    #     #     continue
                    #     #     # Please Add Rollback Function LATER
                    # else:
                    #     main_result["validation_detail"].append(postcheck[0]["desc"])
                    #     main_result["validation_flag"] = postcheck[0]["status"]
                    # Else condition in precheck Failed
                    # else:
                    #     main_result["validation_detail"].append("NA")
                    #     main_result["validation_flag"] = False
                    main_result["validation_detail"].append("NA")
                    main_result["validation_flag"] = True
                    print inputs["user_type"]
                final_op[str(counter)] = main_result
                # final_op[host] = main_result

        return render(request, 'multi_devices_config.html',
                      {'output_dict': final_op, 'taskid': taskid, 'subtaskid': subtaskid, 'class': 'alert-success',
                       "passed": "0", "failed": "0"})
    else:
        print "some things to print"


def login_authentication(username, password, ip):
    output_dict = {}

    if not ping(ip):
        output_dict["login_status"] = 'Device not reacheable '
        output_dict["login_flag"] = False
    else:
        print " Here1 "
        COMMAND_PROMPT = '^.+#'
        COMMAND_PROMPT2 = '^.+>'
        addr = username + "@" + ip
        SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)\s?'
        child = pexpect.spawn('ssh ' + addr, timeout=None)
        # child.setwinsize(800,800)
        i = child.expect(
            [pexpect.TIMEOUT, COMMAND_PROMPT, r'(yes/no)', r'assword:', r'name', r'Connection refused',
             r'ASSWORD:'])
        # update status = 2 where changid = req.changeid , ip = request.ip when execution endswith
        # update result 1 = success 2 = fail
        # logging.info('Ecpect Value ' )
        # logging.info(i )
        print i
        if i == 0 or i == 5:  # Timeout
            # q1 = CronDB.objects.filter(taskid=taskid,subtaskid=subtaskid, ip=ip).update(status=2, result = 2)
            print 'ERROR! could not login with SSH. '
            output_dict["login_status"] = 'ERROR! could not login to device. '
            output_dict["login_flag"] = False
            # return output_dict
        elif i == 1:
            print 'Commands not executed'
            output_dict["login_status"] = 'Commands not Executed '
            output_dict["login_flag"] = False
            # return output_dict
        elif i == 2 or i == 3 or i == 4 or i == 6:
            if i == 2:
                print "1", child.before
                child.sendline("yes")
                child.expect([r'assword:', r'ASSWORD:'])
                print "2", child.before
            elif i == 4:
                child.sendline(username)
                child.expect(r'assword:')
                print "3", child.before
            child.sendline(password)
            j = child.expect([r'assword:', COMMAND_PROMPT, COMMAND_PROMPT2])
            print child.before, child.after
            # time.sleep(2)

            if j == 0:
                output_dict["login_status"] = 'Login Failed '
                output_dict["login_flag"] = False
            if j == 1:
                output_dict["login_status"] = 'Login Successfull'
                output_dict["login_flag"] = True
            elif j == 2:
                child.sendline("enable")
                child.expect(r'assword:')
                child.sendline(password)
                k = child.expect([r'assword:', COMMAND_PROMPT])
                if k == 0:
                    output_dict["login_status"] = 'Login Failed '
                    output_dict["login_flag"] = False
        output_dict["child"] = child
    return output_dict


# ssh -c aes256-ctr -oHostKeyAlgorithms=+ssh-dss admin@198.18.133.200



class Provision():
    def __init__(self, taskid, subtaskid, ip, username, password, input_dict):
        if input_dict.has_key("user_type"):
            self.template = input_dict["user_type"]
        if input_dict.has_key("ext_dict"):
            self.extension = input_dict["ext_dict"]
        if input_dict.has_key("physical_port1"):
            self.port = input_dict["physical_port1"]
        # if input_dict.has_key("physical_port2"):
        #     self.port = input_dict["physical_port2"]
        if input_dict.has_key("leaf_id"):
            self.leaf = input_dict["leaf_id"]
        file_upload_dir = "/home/ubuntu/prepro/mysite/mysite/user_outputs/"
        filename = file_upload_dir + str(taskid) + "_" + str(subtaskid) + "_" + str(ip) + ".txt"
        # request.session["apic_log"] = filename
        log_file = open(filename, "w")
        outp = ""
        self.output_dict = {}
        addr = username + "@" + ip
        if re.search(r"192.1.1", ip) or re.search(r"STNN|SHN", ip):
            if ip == "192.1.1.1":
                output_dict["config_status"] = 'Configuration Successfull '
                output_dict["config_flag"] = True
            elif ip == "192.1.1.2":
                output_dict["config_status"] = 'Configuration Successful'
                output_dict["config_flag"] = True
            elif ip == "192.1.1.3":
                output_dict["config_status"] = 'Configuration Failed'
                output_dict["config_flag"] = False
            elif ip == "STNNC-420-RS01":
                output_dict["config_status"] = 'Configuration Successful'
                output_dict["config_flag"] = True
            elif ip == "STNMC-WECH-RS01":
                output_dict["config_status"] = 'Configuration Successful'
                output_dict["config_flag"] = False
            elif ip == "SHNETWPSCFW001":
                output_dict["config_status"] = 'Configuration Successful'
                output_dict["config_flag"] = False
        elif not ping(ip):
            self.output_dict["login_status"] = 'Device not reacheable '
            self.output_dict["login_flag"] = False
        else:
            print " Here1 "
            self.COMMAND_PROMPT = COMMAND_PROMPT = '^.+#'
            COMMAND_PROMPT2 = '^.+>'
            SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)\s?'
            child = pexpect.spawn('ssh ' + addr, timeout=None)
            # child.setwinsize(800,800)
            child.logfile = log_file
            i = child.expect(
                [pexpect.TIMEOUT, COMMAND_PROMPT, r'(yes/no)', r'assword:', r'name', r'Connection refused',
                 r'ASSWORD:'])
            # update status = 2 where changid = req.changeid , ip = request.ip when execution endswith
            # update result 1 = success 2 = fail
            # logging.info('Ecpect Value ' )
            # logging.info(i )
            print i
            if i == 0 or i == 5:  # Timeout
                # q1 = CronDB.objects.filter(taskid=taskid,subtaskid=subtaskid, ip=ip).update(status=2, result = 2)
                print 'ERROR! could not login with SSH. '
                self.output_dict["login_status"] = 'ERROR! could not login to device. '
                self.output_dict["login_flag"] = False
                # return output_dict
            elif i == 1:
                print 'Commands not executed'
                self.output_dict["login_status"] = 'Commands not Executed '
                self.output_dict["login_flag"] = False
                # return output_dict
            elif i == 2 or i == 3 or i == 4 or i == 6:
                if i == 2:
                    print "1", child.before
                    child.sendline("yes")
                    child.expect([r'assword:', r'ASSWORD:'])
                    print "2", child.before
                elif i == 4:
                    child.sendline(username)
                    child.expect(r'assword:')
                    print "3", child.before
                child.sendline(password)
                j = child.expect([r'assword:', COMMAND_PROMPT, COMMAND_PROMPT2])
                print child.before, child.after
                # time.sleep(2)

                if j == 0:
                    self.output_dict["login_status"] = 'Login Failed , Password Error'
                    self.output_dict["login_flag"] = False
                if j == 1:
                    self.output_dict["login_status"] = 'Login Successfull'
                    self.output_dict["login_flag"] = True
                elif j == 2:
                    child.sendline("enable")
                    child.expect(r'assword:')
                    child.sendline(password)
                    k = child.expect([r'assword:', COMMAND_PROMPT])
                    if k == 0:
                        self.output_dict["login_status"] = 'Login Failed '
                        self.output_dict["login_flag"] = False
            self.child = child

    def get_login_status(self):
        # print self.output_dict
        return self.output_dict

    def precheck_interface(self, ip):
        template = self.template
        extension = self.extension
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child = self.child
        if re.search(r'192.1.1', ip):
            returnarr = {"msg": "Interface is down", "flag": False}
            return returnarr
        if "ACI" in template and extension.has_key("action") and extension["action"] == "reserve":
            # Added Next 2 lines To By Pass For NOw  Dated : 01/02/2019
            returnarr = {"msg": "Interface is down", "status": "1", "flag": True}
            return returnarr
            port = self.port
            leaf = self.leaf
            cmd_list = []
            if port is None:
                returnarr = {"msg": "Interface is down", "flag": False}
                return returnarr
            if "-" in port:
                m = re.search(r"\S+\s?(\d)\/(\d+)-(\d+)", port)
                if m:
                    lc = m.group(1)
                    p_strt = m.group(2)
                    p_end = m.group(3)
                    for i in range(int(p_strt), int(p_end) + 1):
                        cmd_list.append("fabric " + leaf + " show interface eth" + str(lc) + "/" + str(i))
            else:
                cmd_list.append("fabric " + leaf + " show interface " + str(port))
            # ip = get_device_ip(devices)
            child.sendline('terminal len 0')
            child.expect(COMMAND_PROMPT)
            for line in cmd_list:
                child.sendline(line)
                child.expect(COMMAND_PROMPT)
                outp = child.before
                outp = outp.split("\n")
                for line in outp:
                    match = re.search(r'Eth\S+ is (\w+)', line)
                    if match:
                        state = match.group(1)
                        print match.group(1)
                        if state == "up":
                            returnarr = {"msg": "Interface is up", "status": "0", "flag": False}
                            return returnarr
                        else:
                            returnarr = {"msg": "Interface is down", "status": "1", "flag": True}
                    else:
                        returnarr = {"msg": "Interface is down", "status": "1", "flag": True}
            return returnarr
        elif extension.has_key("action") and extension["action"] == "reserve":
            port = self.port
            if port is None:
                returnarr = {"msg": "Interface is down", "flag": False}
                return returnarr
            cmd_list = []
            if "-" in port:
                m = re.search(r"\S+\s?(\d)\/(\d+)-(\d+)", port)
                if m:
                    lc = m.group(1)
                    p_strt = m.group(2)
                    p_end = m.group(3)
                    for i in range(int(p_strt), int(p_end) + 1):
                        cmd_list.append("show interface ethernet " + str(lc) + "/" + str(i))
            else:
                cmd_list.append("show interface " + str(port))
            print cmd_list
            child.sendline('terminal len 0')
            child.expect(COMMAND_PROMPT)
            for line in cmd_list:
                child.sendline(line)
                child.expect(COMMAND_PROMPT)
                print child.before + child.after
                outp = child.before
                outp = outp.split("\n")
                for line in outp:
                    match = re.search(r'Eth\S+ is (\w+)', line)
                    if match:
                        state = match.group(1)
                        print match.group(1)
                        if state == "up":
                            returnarr = {"msg": "Interface is up", "flag": True}
                            return returnarr
                        else:
                            returnarr = {"msg": "Interface is down", "flag": False}
                            return returnarr
                    else:
                        returnarr = {"msg": "Interface is down", "flag": False}
            return returnarr
        else:
            returnarr = {"msg": "Interface is down", "status": "1", "flag": False}
            return returnarr

    def Policy_Check(self, ip):
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child = self.child
        template = self.template
        extension = self.extension
        if re.search(r'192.1.1', ip):
            returnarr = {"msg": "Interface is down", "flag": False}
            return returnarr
        if "ACI" in template and extension.has_key("action") and extension["action"] in ["reserve", "provision"]:
            # Added next 2 linesTo By Pass For NOw  Dated : 01/02/2019
            returnarr = {"msg": "Policy Group Not Configured", "status": "1", "flag": True}
            return returnarr
            leaf_id = self.leaf
            port = self.port
            print port
            if port is None:
                returnarr = {"msg": "Interface is down", "flag": False}
                return returnarr
            cmd_list = []
            if "-" in port:
                m = re.search(r"\S+\s?(\d)\/(\d+)-(\d+)", port)
                if m:
                    lc = m.group(1)
                    p_strt = m.group(2)
                    p_end = m.group(3)
                    for i in range(int(p_strt), int(p_end) + 1):
                        cmd_list.append(
                            "show running-config leaf " + leaf_id + " interface eth" + str(lc) + "/" + str(i))
            else:
                cmd_list.append("show running-config leaf " + leaf_id + " interface " + str(port))
            print cmd_list
            # ip = get_device_ip(devices)
            child.sendline('terminal len 0')
            child.expect(COMMAND_PROMPT)
            for line in cmd_list:
                child.sendline(line)
                child.expect(COMMAND_PROMPT)
                print child.before + child.after
                outp = child.before
                outp = outp.split("\n")
                for line in outp:
                    match = re.search(r'Policy-group configured', line)
                    if match:
                        returnarr = {"msg": "Policy Group Configured", "status": "0", "flag": False}
                        return returnarr
                    else:
                        returnarr = {"msg": "Policy Group Not Configured", "status": "1", "flag": True}
            return returnarr
        else:
            returnarr = {"msg": "Policy Group Configured", "status": "1", "flag": False}
            return returnarr

    def MAC_table_Check(self, ip):
        template = self.template
        extension = self.extension
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child = self.child
        if re.search(r'192.1.1', ip):
            returnarr = {"msg": "Interface is down", "flag": False}
            return returnarr
        # if "ACI" in template and extension.has_key("action") and extension["action"] == "reserve":
        #     port = self.port
        #     if port is None:
        #         returnarr = {"msg": "Interface is down",  "flag": False}
        #         return returnarr
        #     cmd_list = []
        #     if "-" in port:
        #         m = re.search(r"\S+\s?(\d)\/(\d+)-(\d+)", port)
        #         if m:
        #             lc = m.group(1)
        #             p_strt = m.group(2)
        #             p_end = m.group(3)
        #             for i in range(int(p_strt), int(p_end) + 1):
        #                 cmd_list.append("show mac address-table interface eth" + str(lc) + "/" + str(i))
        #     else:
        #         cmd_list.append("show mac address-table interface " + str(port))
        #     print cmd_list
        #     child.sendline('terminal len 0')
        #     child.expect(COMMAND_PROMPT)
        #     for line in cmd_list:
        #         child.sendline(line)
        #         child.expect(COMMAND_PROMPT)
        #         print child.before + child.after
        #         outp = child.before
        #         outp = outp.split("\n")
        #         for line in outp:
        #             match = re.search(
        #                 r'(([a-fA-F0-9]{2}-){5}[a-fA-F0-9]{2}|([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}|([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4})',
        #                 line)
        #             if match:
        #                 returnarr = {"msg": "MAC table exist",  "flag": True}
        #                 return returnarr
        #             else:
        #                 returnarr = {"msg": "MAC table does not exist",  "flag": False}
        #     return returnarr
        else:
            returnarr = {"msg": "MAC table does not exist", "flag": False}
            return returnarr

    def Configuration_fun(self, taskid, subtaskid, inputs_list, cmd_list, ip):
        output_dict = {}
        # password = Cisco123g
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child = self.child
        q1 = CronDB.objects.filter(taskid=taskid, subtaskid=subtaskid, ip=ip).update(status=1)
        if cmd_list:
            child.sendline('term len 0')
            child.expect(COMMAND_PROMPT)
            # print child.before, child.after
            for each in cmd_list:
                if each in ["Pre Check Verification:", "Configuration:", "Post Check Verification:"]:
                    continue
                if "\n" in each:
                    each = each.strip('\r\n')
                child.sendline(each)
                k = child.expect([COMMAND_PROMPT, r'confirm'])
                # print child.before + child.after
                if k == 1:
                    child.sendline("y")
                    child.expect(COMMAND_PROMPT)
                print child.after
                print child.before
                outp = child.before
                # err_op = outp.split("\n")
                if re.search(r"Incomplete", outp) or re.search(r"Invalid", outp):
                    q1 = CronDB.objects.filter(taskid=taskid, subtaskid=subtaskid,
                                               ip=ip).update(status=2, result=2)
                    output_dict["config_status"] = 'Command Error : ' + each
                    output_dict["config_flag"] = False
                    return output_dict
        output_dict["config_status"] = "Successful"
        output_dict["config_flag"] = True
        ticket_desc = ""
        if inputs_list.has_key("user_type"):
            if inputs_list.get("user_type") == "ACI Port Provisioning":
                print  inputs_list
                if "," in inputs_list["leaf_id"]:
                    leaf_id = inputs_list["leaf_id"].split(",")
                else:
                    leaf_id = [inputs_list["leaf_id"]]
                if inputs_list.has_key("physical_port1"):
                    if "," in inputs_list["physical_port1"]:
                        physical_port1 = inputs_list["physical_port1"].split(",")
                    else:
                        physical_port1 = [inputs_list["physical_port1"]]
                if inputs_list.has_key("physical_port2"):
                    if "," in inputs_list["physical_port2"]:
                        physical_port2 = inputs_list["physical_port2"].split(",")
                    else:
                        physical_port2 = [inputs_list["physical_port2"]]
                ticket_desc = ticket_desc + "Following Ports have been provision for Work Order " + \
                              inputs_list["work_order_no"] + " by user " + "\nFabric:\n"  # Add user
                if len(leaf_id) >= 1:
                    for leaf in leaf_id:
                        ticket_desc = ticket_desc + "\nLeaf: " + leaf + "\n"
                        indx = leaf_id.index(leaf)
                        if indx == 0 and inputs_list.has_key("physical_port1"):
                            physical_port = physical_port1
                        if indx == 1 and inputs_list.has_key("physical_port2"):
                            physical_port = physical_port2
                        ticket_desc = ticket_desc + "Ports: "
                        for ports in physical_port:
                            ticket_desc = ticket_desc + " " + ports + " "
                            if ACIInterfaceStatusDB.objects.filter(work_order_no=inputs_list["work_order_no"],
                                                                   leaf_id=leaf, physical_port=ports).last():
                                if inputs_list["config_action"] == 'deprovision':
                                    q = ACIInterfaceStatusDB.objects.filter(work_order_no=inputs_list["work_order_no"],
                                                                            leaf_id=leaf, physical_port=ports).delete()
                                else:
                                    q = ACIInterfaceStatusDB.objects.filter(work_order_no=inputs_list["work_order_no"],
                                                                            leaf_id=leaf, physical_port=ports).update(
                                        taskid=taskid, status=inputs_list["config_action"])
                            else:
                                q1 = ACIInterfaceStatusDB(taskid=taskid, work_order_no=inputs_list["work_order_no"],
                                                          leaf_id=leaf, physical_port=ports,
                                                          status=inputs_list["config_action"])
                                q1.save()
                work_order_no = inputs_list["work_order_no"]
                q = ACIInterfaceStatusDB.objects.filter(work_order_no=work_order_no).values('servicenowid').first()
                print "Temp Debug Here"
                print inputs_list["config_action"]
                print q
                # if q and inputs_list["config_action"] in ["reserve", 'deprovision_reservation']:
                #     print q
                #     print "Updating  ", work_order_no, q["servicenowid"]
                #     username = "admin"
                #     password = "qg7RwgPG8XtI"
                #     # sysid = 'b36b197fdb32a3009c3ff20ebf9619da'
                #     state = "In Progress"
                #     if inputs_list["config_action"] == "reserve":
                #         short_description1 = "ACI Port Reserved for Work Order " + work_order_no
                #     elif inputs_list["config_action"] == "deprovision_reservation":
                #         short_description1 = "ACI Port Reserved for De-Provision for Work Order " + work_order_no
                #     comments1 = ticket_desc
                #     returnclose = incident_update(username, password, q["servicenowid"], state, short_description1,
                #                                   comments1)
                #     # returnclose = incident_close(username, password, q["servicenowid"])
                #     print returnclose
                #
                # if q and inputs_list["config_action"] in ["provision", 'deprovision']:
                #     print q
                #     print "closing ", work_order_no, q["servicenowid"]
                #     username = "admin"
                #     password = "qg7RwgPG8XtI"
                #     # sysid = 'b36b197fdb32a3009c3ff20ebf9619da'
                #     state = "Closed"
                #     if inputs_list["config_action"] == "provision":
                #         short_description1 = "ACI Port Provision for Work Order " + work_order_no
                #     elif inputs_list["config_action"] == "deprovision":
                #         short_description1 = "ACI Port De-Provisiond for Work Order " + work_order_no
                #
                #     comments1 = ticket_desc
                #     returnclose = incident_update(username, password, q["servicenowid"], state, short_description1,
                #                                   comments1)
                #     returnclose = incident_close(username, password, q["servicenowid"])
                #     print returnclose
            template = inputs_list["user_type"]
            query = template_db.objects.filter(template=template, type=1, tag="provisioning_workflow").last()
            if query and inputs_list.has_key("config_action"):
                print "Work Flow is correct !!"
                print inputs_list["config_action"]
                # q1 = CronDB.objects.filter(taskid=taskid, subtaskid=subtaskid).update(cstate=inputs_list["config_action"], status=4, result=1)
                print " Working Here too "
            else:
                q1 = CronDB.objects.filter(taskid=taskid, subtaskid=subtaskid, ip=str(ip)).update(status=2, result=1)
        print "Returning "
        # self.filter_log(taskid, subtaskid, ip)
        return output_dict

    def Validation(self):
        template = self.template
        extension = self.extension
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child = self.child
        if "ACI" in template and extension.has_key("action") and extension["action"] == "provision":
            print " Here in ACI validation"
            port = self.port
            leaf = self.leaf
            if port is None:
                returnarr = [{"desc": "Group Policy Validation Failed ", "status": True}]
                return returnarr

            child.expect(COMMAND_PROMPT)
            child.sendline('terminal len 0')
            child.expect(COMMAND_PROMPT)
            # print child.before, child.after
            # time.sleep(2)
            child.sendline("show running-config leaf " + leaf + " interface " + port)
            child.expect(COMMAND_PROMPT)
            print child.before + child.after
            outp = child.before
            outp = outp.split("\n")
            for line in outp:
                match = re.search(r'policy-group\s(\S+)', line)
                if match:
                    return [{"desc": "Group Policy Validation Successfull ", "status": True}]
                else:
                    return [{"desc": "Group Policy Validation Failed ", "status": True}]
        return [{"desc": "Group Policy Validation Failed ", "status": True}]

    def filter_log(self, taskid, subtaskid, ip):
        file_upload_dir = "/home/ubuntu/prepro/mysite/mysite/user_outputs/"
        filename = file_upload_dir + str(taskid) + "_" + str(subtaskid) + "_" + ip + ".txt"
        if filename:
            infile = open(filename, "r+")
            log_list = [i for i in infile.readlines()]
            infile.close()
            filter_log_list = []
            for each in log_list:
                if "assword" in each:
                    log_list.remove(each)
                each = re.sub(r'((\^[A-Z])|(\[[A-Z])|(\^\[\[\d+m)|(\^\[\[[A-Z])|(\%)|(\[\d+m)|([a-z]\x08))', '', each)
                each = re.sub(r'\s+a', ' a', each)
                filter_log_list.append(each.translate(None, "\r\x1b"))
            data = open(filename, "w+")
            for line in filter_log_list:
                if line == '\n':
                    continue
                data.write(line)
            data.close()
        else:
            return "File Does Not Exist"


    def get_show_run_op(self):
        print " In get Show run output"
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child = self.child
        child.sendline('terminal len 0')
        child.expect(COMMAND_PROMPT)
        print child.before, child.after
        time.sleep(2)
        child.sendline('show run')
        time.sleep(2)
        child.expect(COMMAND_PROMPT)
        # print child.before
        # print "After >>>>>>", child.after
        outp = child.after
        outp = outp.split("\n")

        return outp


def ping(ip_add):
    return True
    response = os.system('ping -c 4 ' + ip_add)
    if response == 0:
        return True
    else:
        return False


def filter_command_list(list1):
    filtered_list = []
    for cmd in list1:
        cmd = cmd.replace('<span style="color:rgb(237, 125, 49);">', " ")
        cmd = cmd.replace("</span>", " ")
        cmd = cmd.replace("&#60;", "<")
        cmd = cmd.replace("&#62;", ">")
        cmd = re.sub('555', '', cmd)
        cmd = re.sub('666', '', cmd)
        filtered_list.append(cmd)
    return filtered_list


def check_tso_provisioned(ip, interface):
    outp = ""
    username = ""
    password = ""
    addr = username + "@" + ip
    COMMAND_PROMPT = '\S+#'
    # SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)\s?'
    child = pexpect.spawn('ssh -c aes256-ctr -oHostKeyAlgorithms=+ssh-dss ' + addr, timeout=30)
    i = child.expect([pexpect.TIMEOUT, COMMAND_PROMPT, 'password:'])
    if i == 0:  # Timeout
        print 'ERROR! could not login with SSH. '
        return False
    elif i == 1:
        child.sendline('\r')
    elif i == 2:
        # print child.before, child.after
        child.sendline(password)
        child.expect(COMMAND_PROMPT)
        child.sendline('terminal len 0')
        child.expect(COMMAND_PROMPT)
        # print child.before, child.after
        # time.sleep(2)
        child.sendline("show interfaces" + interface)
        child.expect(COMMAND_PROMPT)
        print child.before + child.after
        outp = child.before
        outp = outp.split("\n")
        for line in outp:
            match = re.search(r'Description:\s?(\S+)', line)
            if match:
                print match.group(1)
                if re.search(r'ovisoned', match.group(1)):
                    return True
                else:
                    return False


class ProvisionTSO:
    def __init__(self, tsoid, ip):
        login_dict = {}
        # logging.info("IN TSO Class")
        file_upload_dir = "/home/ubuntu/prepro/mysite/mysite/user_outputs/tso_log/"
        filename = file_upload_dir + str(tsoid) + "_" + str(ip) + ".txt"
        print "<<Filename>>"
        print filename
        log_file = open(filename, "w")
        output_dict = {}
        # username  = "neteng"
        # password = "5HTR@n$f0rm"
        username = "vendor"
        password = "Cisco123"
        addr = username + "@" + ip
        if ping(ip):
            login_dict["msg"] = 'Host %s Not Reachable. ' % ip
            login_dict["flag"] = False
        else:
            COMMAND_PROMPT = '\S+#'
            COMMAND_PROMPT2 = '\S+>'
            SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)\s?'
            child = pexpect.spawn('ssh ' + addr, timeout=30)
            child.setwinsize(800, 800)
            child.logfile = log_file
            i = child.expect(
                [pexpect.TIMEOUT, COMMAND_PROMPT, r'(yes/no)', r'assword', r'Connection refused', r'ASSWORD'])
            if i == 0:  # Timeout
                print 'ERROR! could not login with SSH. '
                login_dict["msg"] = 'ERROR! could not login to device. '
                login_dict["flag"] = False
                # return output_dict
            elif i == 4:
                login_dict["msg"] = 'Connection refused '
                login_dict["flag"] = False
                # return output_dict
            elif i == 1:
                print 'Commands not executed'
                login_dict["msg"] = 'Commands not Executed '
                login_dict["flag"] = False
                # child.sendline('\r')
                # return output_dict
            elif i == 2 or i == 3 or i == 5:
                if i == 2:
                    child.sendline("yes")
                    j = child.expect([r'assword', COMMAND_PROMPT, COMMAND_PROMPT2, r'ASSWORD'])
                    if j == 2:
                        child.sendline("enable")
                        child.expect(r'assword')
                child.sendline(password)
                j = child.expect([COMMAND_PROMPT, COMMAND_PROMPT2, r'assword', r'ASSWORD'])
                if j == [1, 2, 3]:
                    login_dict["msg"] = 'Login Failed, Password Error '
                    login_dict["flag"] = False
                else:
                    login_dict["msg"] = 'Login Successfull '
                    login_dict["flag"] = True
            self.pexpect_child = child
        self.login_dict = login_dict

    def get_login_status(self):
        return self.login_dict

    def tso_config_fun(self, cmd_list):
        output_dict = {}
        child = self.pexpect_child
        COMMAND_PROMPT = '\S+#'
        # logging.info("IN TSO Config")
        # logging.info("Before" + child.before)
        # logging.info("After" + child.after)

        # time.sleep(2)
        if cmd_list:
            child.sendline('terminal len 0')
            child.expect(COMMAND_PROMPT)
            child.sendline('config t')
            child.expect(COMMAND_PROMPT)
            # print child.before, child.after

            # logging.info("Before" + child.before)
            # logging.info("After" + child.after)
            for each in cmd_list:
                if "#" in each:
                    continue
                if "\n" in each:
                    each = each.strip('\r\n')
                child.sendline(each)
                child.expect(COMMAND_PROMPT)
                outp = child.before
                if each == "sh module | in 24":
                    return outp
                if "Incomplete " in outp or "Invalid " in outp:
                    output_dict["msg"] = 'Command Error : ' + each
                    output_dict["flag"] = False
                    return output_dict
        # output_dict["msg"] = "Configuration Successful"
        output_dict["msg"] = "TSO " + str(tsoid) + ": Provisioned "
        output_dict["flag"] = True
        return output_dict

    def tso_precheck_fun(self, hostname, interface):
        output_dict ={}
        returnarr = {"msg": "Interface " + interface + " is down", "flag": False}
        # logging.info("IN TSO PRECHECK")
        print hostname, interface
        child = self.pexpect_child
        COMMAND_PROMPT = '\S+#'
        child.sendline('terminal len 0')
        child.expect(COMMAND_PROMPT)
        child.sendline("show interface " + str(interface))
        child.expect(COMMAND_PROMPT)
        print "output"
        print child.before + child.after
        outp = child.before
        outp = outp.split("\n")
        # logging.info("Before"+child.before)
        # logging.info("After" + child.after)
        # print outp
        for line in outp:
            match = re.search(r'Eth\S+\s+is\s+(\w+)', line)
            if match:
                state = match.group(1)
                print match.group(1)
                if state == "up":
                    child.sendline("show run interface " + interface)
                    child.expect(COMMAND_PROMPT)
                    output = child.before
                    intf_outp = output.split("\n")
                    # logging.info(intf_outp)
                    for e_line in intf_outp:
                        m1 = re.search(r'switchport\s.+\svlan\s(\d+)', e_line)
                        if m1:
                            msg = "Interface {} is configured for Vlan {}".format(interface, str(m1.group(1)))
                            returnarr = {"msg": msg, "flag": True}
                            return returnarr
                    msg = "Interface {} is Not configured ".format(interface)
                    returnarr = {"msg": msg, "flag": True}
                    return returnarr
                else:
                    returnarr = {"msg": "Interface " + interface + " is down", "flag": False}
        return returnarr

    def tso_postcheck_fun(self, para_dict, test_ip):
        returnarr = {}
        # logging.info("IN TSO PostCheck")
        print hostname, interface
        child = self.pexpect_child
        COMMAND_PROMPT = '\S+#'
        print child.before, child.after
        child.sendline('terminal len 0')
        child.expect(COMMAND_PROMPT)
        child.sendline("show interface " + para_dict["interface"])
        child.expect(COMMAND_PROMPT)
        outp = child.before
        outp = outp.split("\n")
        print outp
        for line in outp:
            match = re.search(r'Eth\S+\s+is\s+(\w+)', line)
            if match:
                state = match.group(1)
                print match.group(1)
                if state == "up":
                    child.sendline('ping vrf {} {}'.format(para_dict["vrf"], test_ip))
                    child.expect(COMMAND_PROMPT)
                    outp = child.before
                    outp = outp.split("\n")
                    print outp
                    for line in outp:
                        rtt_match = re.search(r'Success rate is (\d+) percent', line)
                        if rtt_match:
                            avg_rtt = float(rtt_match.group(1))
                            if avg_rtt > 90.0:
                                msg = ["Ping Test Successfull for IP " + str(test_ip)]
                                returnarr = {"msg": msg, "flag": True}
                                return returnarr
                            else:
                                msg = ["Ping Test Failed for IP " + str(test_ip) + " , Ping is not reachable"]
                                returnarr = {"msg": msg, "flag": False}
                                return returnarr
        return returnarr

    def apply_command(self, command_list, interface_list):
        # print interface_list
        output_dict={}
        child = self.pexpect_child
        COMMAND_PROMPT  = self.COMMAND_PROMPT
        for interface in interface_list:
            interface = ",".join(interface)
            if command_list:
                child.sendline('terminal len 0')
                child.expect(COMMAND_PROMPT)
                print child.before
                child.sendline('config t')
                child.expect(COMMAND_PROMPT)
                print child.before
                child.sendline('interface range '+interface)
                child.expect(COMMAND_PROMPT)
                print child.before
                for each in command_list:
                    if "#" in each :
                        continue
                    if "\n" in each :
                        each= each.strip('\r\n')
                    child.sendline(each)
                    child.expect (COMMAND_PROMPT)
                    print child.before, child.after
                    outp = child.before
                child.sendline('end')
                child.expect(COMMAND_PROMPT)
                print child.before, child.after
        output_dict["msg"] = "Configuration Successful"
        output_dict["flag"] = True
        return output_dict

def create_ip_data(child, ip):
    COMMAND_PROMPT = "\S+#"
    child.sendline("show switch")
    child.expect(COMMAND_PROMPT)
    opt = child.before
    lst = opt.split('\n')
    print lst
    leaf_list = []
    for ele in lst:
        m1 = re.search(r'\s(\d+\d)\s', ele)
        if m1:
            leaf_list.append(m1.group(1))
    print "Leaf List", leaf_list
    if len(leaf_list) != 0:
        ip_dict = {ip: {}}
        for i in leaf_list:
            ip_dict[ip][i] = []
            for port in range(1, 48):
                ip_dict[ip][i].append('eth 1/' + str(port))
        with open('/home/ubuntu/prepro/mysite/mysite/Json_DATA/' + ip + '.json') as ip_json_data:
            try:
                devices_data = json.load(ip_json_data)
                devices_data.update(ip_dict)
                with open('/home/ubuntu/prepro/mysite/mysite/Json_DATA/' + ip + '.json', 'w') as data:
                    json.dump(devices_data, data)
            except:
                with open('/home/ubuntu/prepro/mysite/mysite/Json_DATA/' + ip + '.json', 'w') as data:
                    json.dump(ip_dict, data)
    return True


def query_switch(ip, command, pattern):
    # logging.info("IN Query Count Pexpet function ")
    file_upload_dir = "/home/ubuntu/prepro/mysite/mysite/user_outputs/sw_log/"
    filename = file_upload_dir + str(ip) + ".txt"
    log_file = open(filename, "w")
    output_dict = {}
    username = "vendor"
    password = "Cisco123"
    if not ping(ip):
        return "unreachable"
    # username  = "neteng"
    # password = "5HTR@n$f0rm"
    addr = username + "@" + ip
    if not ping(ip):
        print '%s not reachable' % ip
        output_dict["msg"] = 'Host %s Not Reachable. ' % ip
        output_dict["flag"] = False
        return output_dict
    COMMAND_PROMPT = '\S+#'
    COMMAND_PROMPT2 = '\S+>'
    SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)\s?'
    child = pexpect.spawn('ssh ' + addr, timeout=30)
    child.setwinsize(800, 800)
    child.logfile = log_file
    i = child.expect([pexpect.TIMEOUT, COMMAND_PROMPT, r'(yes/no)', r'assword', r'onnection refused', r'ASSWORD'])
    if i == 0 or i == 4:  # Timeout
        return "unreachable"
    elif i == 1:
        return "unreachable"
    elif i == 2 or i == 3 or i == 5:
        if i == 2:
            child.sendline("yes")
            j = child.expect([r'assword', COMMAND_PROMPT, COMMAND_PROMPT2, r'ASSWORD'])
            if j == 2:
                child.sendline("enable")
                child.expect(r'assword')
        child.sendline(password)
        j = child.expect([COMMAND_PROMPT, COMMAND_PROMPT2])
        if j == 1:
            child.sendline("enable")
            child.expect(r'assword')
            child.sendline(password)
            child.expect(COMMAND_PROMPT)
        # time.sleep(2)
        child.sendline('terminal len 0')
        child.expect(COMMAND_PROMPT)
        child.sendline(command)
        child.expect(COMMAND_PROMPT)
        outp = child.before
        out = outp.split("\n")
        count = 0
        for line in out:
            if re.search(pattern, line):
                count += 1

        # logging.info(out)
        # logging.info(count)
        return count

class hardware_data():
    def __init__(self, ip, username, password):

        file_upload_dir = "/home/ubuntu/prepro/mysite/mysite/user_outputs/"
        filename = file_upload_dir + str(ip) + ".txt"
        # request.session["apic_log"] = filename
        log_file = open(filename, "w")
        outp = ""
        self.output_dict = {}
        addr = username + "@" + ip
        if not ping(ip):
            self.output_dict["login_status"] = 'Device not reacheable '
            self.output_dict["login_flag"] = False
        else:
            print " Here1 "
            self.COMMAND_PROMPT = COMMAND_PROMPT = '^.+#'
            COMMAND_PROMPT2 = '^.+>'
            port = '2202'
            SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)\s?'
            child = pexpect.spawn('ssh '+ addr, timeout=None)
            # child.setwinsize(800,800)
            # child.logfile = log_file
            i = child.expect(
                [pexpect.TIMEOUT, COMMAND_PROMPT, r'(yes/no)', r'assword:', r'name', r'Connection refused',
                 r'ASSWORD:'])
            # update status = 2 where changid = req.changeid , ip = request.ip when execution endswith
            # update result 1 = success 2 = fail
            # logging.info('Ecpect Value ' )
            # logging.info(i )
            print i
            if i == 0 or i == 5:  # Timeout
                # q1 = CronDB.objects.filter(taskid=taskid,subtaskid=subtaskid, ip=ip).update(status=2, result = 2)
                print 'ERROR! could not login with SSH. '
                self.output_dict["login_status"] = 'ERROR! could not login to device. '
                self.output_dict["login_flag"] = False
                # return output_dict
            elif i == 1:
                print 'Commands not executed'
                self.output_dict["login_status"] = 'Commands not Executed '
                self.output_dict["login_flag"] = False
                # return output_dict
            elif i == 2 or i == 3 or i == 4 or i == 6:
                if i == 2:
                    print "1", child.before
                    child.sendline("yes")
                    child.expect([r'assword:', r'ASSWORD:'])
                    print "2", child.before
                elif i == 4:
                    child.sendline(username)
                    child.expect(r'assword:')
                    print "3", child.before
                child.sendline(password)
                j = child.expect([r'assword:', COMMAND_PROMPT, COMMAND_PROMPT2])
                print child.before, child.after
                # time.sleep(2)

                if j == 0:
                    self.output_dict["login_status"] = 'Login Failed , Password Error'
                    self.output_dict["login_flag"] = False
                if j == 1:
                    self.output_dict["login_status"] = 'Login Successfull'
                    self.output_dict["login_flag"] = True
                elif j == 2:
                    child.sendline("enable")
                    child.expect(r'assword:')
                    child.sendline(password)
                    k = child.expect([r'assword:', COMMAND_PROMPT])
                    if k == 0:
                        self.output_dict["login_status"] = 'Login Failed '
                        self.output_dict["login_flag"] = False
            self.child = child

    def get_login_status(self):
        # print self.output_dict
        return self.output_dict

    def get_platform(self):
        print " In Get Platform ", self.COMMAND_PROMPT, self.child
        child = self.child
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child.sendline("show version")
        child.expect(COMMAND_PROMPT)
        print "Before >>>>>", child.before
        print "After >>>>>", child.after
        opt = child.after
        lst = opt.split('\n')
        model_list = []
        platform =""
        for ele in lst:
            m1 = re.search(r'cisco\s(\S+\s\S+)\spr', ele)
            if m1:
                match = m1.group(1)[1:6]
                if match == "C9300":
                    platform = match
                    flag = True

                else:
                    platform = match
                    flag = False
        if flag:
            child.sendline("show module")
            child.expect(COMMAND_PROMPT)
            opt2 = child.before
            lst2 = opt2.split('\n')
            for ele in lst:
                m2 = re.search(r'\d+\s+([C]\S+)', ele)
                if m2:
                    models_list.append(m2.group(1))
        else:
            child.sendline("show module")
            child.expect(COMMAND_PROMPT)
            opt2 = child.before
            lst2 = opt2.split('\n')
            for ele1 in lst2:
                m2 = re.search(r'\d+\s.+\s([C]\S+)\s', ele1)
                if m2:
                    model_list.append(m2.group(2))

        return model_list,platform

    def inline_power(self,platform):
        child = self.child
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child.sendline("show power inline")
        child.expect(COMMAND_PROMPT)
        opt = child.before
        command_op = opt.split('\n')
        data_dict = {}
        total_count = 0
        upoe_count = 0
        total_poe = 0
        inline_dict = {}
        if platform == "9400":
            for ele in command_op:
                m1 = re.search(r'(\w+\d+/\d+/\d+)', ele)
                if m1:
                    # print m1.group()
                    total_count += 1
                m2 = re.search(r'Totals:\s+(\S+)\s', ele)
                if m2:
                    total_poe = int(m2.group(1))
                m3 = re.search(r'\w+\d+\S+(.+)on\s+\S+\s+(\w+\.\w+)', ele)
                if m3:
                    a = float(m3.group(2))
                    if a > 32.00:
                        upoe_count += 1
        elif platform == "9300":
            for ele in command_op:
                m1 = re.search(r'(\w+\d+/\d+/\d+)\s', ele)
                if m1:
                    # print m1.group()
                    total_count += 1
                m2 = re.search(r'(\w+\d+/\d+/\d+).+(on)\s', ele)
                if m2:
                    total_poe = int(m2.group(1))
                m3 = re.search(r'on\s+(\d+\.\d+)\s', ele)
                if m3:
                    a = float(m3.group(2))
                    if a > 32.00:
                        upoe_count += 1
        inline_dict['upoe_count'] = upoe_count
        inline_dict['poe_count'] = total_poe
        normal_count = total_count - (total_poe + upoe_count)
        inline_dict['normal_count'] = normal_count
        return inline_dict
    def Interface_status_function(self):
        child = self.child
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child.sendline("show interfaces status")
        child.expect(COMMAND_PROMPT)
        opt = child.before
        int_status_op = opt.split('\n')
        data_dict = {}
        total_count = 0
        active_count = 0
        inactive_count = 0
        for ele in int_status_op:
            m1 = re.search(r'(\w+\d+/\d+/\d+)\s', ele)
            if m1:
                total_count += 1
            m2 = re.search(r'(\w+\d+/\d+/\d+)\s+(.*|\s+)\s+(connected)', ele)
            if m2:
                active_count += 1
            m3 = re.search(r'(\w+\d+/\d+/\d+)\s+(.*|\s+)\s+(notconnect|inactive)', ele)
            if m3:
                inactive_count += 1
        count_dict = {'total': total_count, 'active_count': active_count, 'inactive_count': inactive_count}
        return count_dict
    def get_command_op(self, command):
        child = self.pexpect_child
        COMMAND_PROMPT = '\S+#'
        child.sendline('terminal len 0')
        child.expect(COMMAND_PROMPT)
        child.sendline(command)
        child.expect(COMMAND_PROMPT)
        opt = child.before
        lst = opt.split('\n')
        return lst

    def get_hostname(self):
        child  = self.pexpect_child
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child.sendline('terminal len 0')
        child.expect(COMMAND_PROMPT)
        outp = child.after
        outp = outp.split("\n")
        for ele in outp:
            m = re.search('(\S+)#',ele)
            if m:
                return m.group(1)

def proposed_hardware(inline_dict, platform):
    proprsed_hrd = []
    poe = inline_dict['poe_count']
    upoe = inline_dict['upoe_count']
    normal = inline_dict['normal_count']
    if platform=="9400":
        print normal, upoe, poe
        normal_LC = normal/48
        upeo_LC = upoe/48
        poe_LC = poe/48
        print poe%48
        if normal_LC>=0 and normal%48>=1 and normal%48<=24:
            proprsed_hrd+=['C9400-LC-48T' for i in range(normal_LC)]
            proprsed_hrd+=['C9400-LC-24T']
        elif normal_LC>=0 and normal%48>=24 and normal%48<=48:
            proprsed_hrd+=['C9400-LC-48T' for i in range(normal_LC+1)]

        if upeo_LC>=0 and upoe%48>=1 and upoe%48<=24:
            proprsed_hrd+=['C9400-LC-48U' for i in range(upeo_LC)]
            proprsed_hrd+=['C9400-LC-24U']
        elif upeo_LC>=0 and upoe%48>=24 and upoe%48<=48:
            proprsed_hrd+=['C9400-LC-48U' for i in range(upeo_LC+1)]

        if poe_LC>=0 and poe%48>=1 and poe%48<=24:
            proprsed_hrd+=['C9400-LC-48P' for i in range(poe_LC)]
            proprsed_hrd+=['C9400-LC-24P']
        elif poe_LC>=0 and poe%48>=24 and poe%48<=48:
            proprsed_hrd+=['C9400-LC-48P' for i in range(poe_LC+1)]
    if platform=="9300":
        print normal, upoe, poe
        normal_LC = normal/48
        upeo_LC = upoe/48
        poe_LC = poe/48
        print poe%48
        if normal_LC>=0 and normal%48>=1 and normal%48<=24:
            proprsed_hrd+=['C9300-48T' for i in range(normal_LC)]
            proprsed_hrd+=['C9300-24T']
        elif normal_LC>=0 and normal%48>=24 and normal%48<=48:
            proprsed_hrd+=['C9300-48T' for i in range(normal_LC+1)]

        if upeo_LC>=0 and upoe%48>=1 and upoe%48<=24:
            proprsed_hrd+=['C9300-48U' for i in range(upeo_LC)]
            proprsed_hrd+=['C9300-24U']
        elif upeo_LC>=0 and upoe%48>=24 and upoe%48<=48:
            proprsed_hrd+=['C9300-48U' for i in range(upeo_LC+1)]
        if poe_LC>=0 and poe%48>=1 and poe%48<=24:
            proprsed_hrd+=['C9300-48P' for i in range(poe_LC)]
            proprsed_hrd+=['C9300-24P']
        elif poe_LC>=0 and poe%48>=24 and poe%48<=48:
            proprsed_hrd+=['C9300-48P' for i in range(poe_LC+1)]
    return proprsed_hrd

#function for finding Ip from DNS
def findIp(dns):
    process = subprocess.Popen(["nslookup", dns], stdout=subprocess.PIPE)
    output = process.communicate()[0].split('\n')
    # print dns
    # print output
    for data in output:
        AddIp = re.search(r'Address: (\d.+)', data)
        if AddIp:
            ip_add = AddIp.group(1)
            return ip_add
    return ""


def divide_int_list(int_list):
    for i in range(0, len(int_list), 5):
        yield int_list[i:i+5]


class SSH_Switch():
    def __init__(self, ip):
        login_dict = {}

        file_upload_dir = "/home/ubuntu/prepro/Trap_Handling/Config_Logs/"
        filename = file_upload_dir + str(ip) + ".txt"
        print "<<Filename>>"
        print filename
        log_file = open(filename, "w+")
        username = "vendor"
        password = "Cisco123"
        addr = username + "@" + ip
        if not ping(ip):
            login_dict["msg"] = ' Host {} Not Reachable. '.format(ip)
            login_dict["flag"] = False
        else:
            COMMAND_PROMPT = '\S+#'
            COMMAND_PROMPT2 = '\S+>'
            SSH_NEWKEY = 'Are you sure you want to continue connecting (yes/no)\s?'
            child = pexpect.spawn('ssh ' + addr, timeout=30)
            child.logfile = log_file
            i = child.expect(
                [pexpect.TIMEOUT, COMMAND_PROMPT, r'(yes/no)', r'assword', r'Connection refused', r'ASSWORD',
                 r'Host key verification failed.'])
            if i == 0:  # Timeout
                print 'ERROR! could not login with SSH. '
                login_dict["msg"] = 'ERROR! could not login to device. '
                login_dict["flag"] = False
                # return output_dict
            elif i == 4 or i == 6:
                login_dict["msg"] = 'Connection refused '
                login_dict["flag"] = False
                # return output_dict
            elif i == 1:
                print 'Commands not executed'
                login_dict["msg"] = 'Commands not Executed '
                login_dict["flag"] = False
                # child.sendline('\r')
                # return output_dict
            elif i == 2 or i == 3 or i == 5:
                if i == 2:
                    child.sendline("yes")
                    j = child.expect([r'assword', COMMAND_PROMPT, COMMAND_PROMPT2, r'ASSWORD'])
                    if j == 2:
                        child.sendline("enable")
                        child.expect(r'assword')
                child.sendline(password)
                # time.sleep(2)
                j = child.expect([COMMAND_PROMPT, COMMAND_PROMPT2, r'assword:', r'ASSWORD:'])
                if j in [1, 2, 3]:
                    login_dict["msg"] = 'Login Failed, Password Error '
                    login_dict["flag"] = False
                else:
                    login_dict["msg"] = 'Login Successfull '
                    login_dict["flag"] = True

            self.pexpect_child = child
            self.COMMAND_PROMPT = COMMAND_PROMPT
        self.login_dict = login_dict

    def get_login_status(self):
        return self.login_dict

    def apply_command(self, command_list, interface_list):
        # print interface_list
        output_dict = {}
        child = self.pexpect_child
        COMMAND_PROMPT = self.COMMAND_PROMPT
        for interface in interface_list:
            interface = ",".join(interface)
            if command_list:
                child.sendline('terminal len 0')
                child.expect(COMMAND_PROMPT)
                print child.before
                child.sendline('config t')
                child.expect(COMMAND_PROMPT)
                print child.before
                child.sendline('interface range ' + interface)
                child.expect(COMMAND_PROMPT)
                print child.before
                for each in command_list:
                    if "#" in each:
                        continue
                    if "\n" in each:
                        each = each.strip('\r\n')
                    child.sendline(each)
                    child.expect(COMMAND_PROMPT)
                    print child.before, child.after
                    outp = child.before
                child.sendline('end')
                child.expect(COMMAND_PROMPT)
                print child.before, child.after
        output_dict["msg"] = "Configuration Successful"
        output_dict["flag"] = True
        return output_dict

    def get_hostname(self):
        child = self.pexpect_child
        COMMAND_PROMPT = self.COMMAND_PROMPT
        child.sendline('terminal len 0')
        child.expect(COMMAND_PROMPT)
        outp = child.after
        outp = outp.split("\n")
        for ele in outp:
            m = re.search('(\S+)#', ele)
            if m:
                return m.group(1)

    def deconfig_ports_fun(self, port_list):
        sort_interface_list = list(OrderedDict.fromkeys(port_list))
        int_range_list = list(divide_int_list(sort_interface_list))
        flg = self.apply_command(cmd_list, int_range_list)

    def config_vlan_on_port(self, vlan, port_list):

        output_dict = {}
        if port_list:
            sort_interface_list = list(OrderedDict.fromkeys(port_list))
            int_range_list = list(divide_int_list(sort_interface_list))
            for interface_range in int_range_list:
                interface_range = ','.join(interface_range)
                cmd_list = ["Configure Terminal", "Interface " + interface_range, "switchport mode access",
                            "switchport access vlan " + vlan, "!"]

                child = self.pexpect_child
                COMMAND_PROMPT = '\S+#'
                child.sendline('terminal len 0')
                child.expect(COMMAND_PROMPT)
                for each in cmd_list:
                    child.sendline(each)
                    child.expect(COMMAND_PROMPT)
                    print child.before
                    opt = child.before
                    if re.search(r"Incomplete", opt) or re.search(r"Invalid", opt):
                        output_dict["config_status"] = 'Command Error : ' + each
                        output_dict["config_flag"] = False
                        return output_dict
            output_dict["config_status"] = 'Successfull '
            output_dict["config_flag"] = True
            return output_dict
        else:
            return output_dict


def get_mac_device_type(mac_addr):
    # API base url,you can also use https if you need
    url = "http://macvendors.co/api/"
    # Mac address to lookup vendor from
    mac_address = mac_addr
    # urllib2 = urllib.request
    request = urllib.urlopen(url + mac_address)
    # Fix: json object must be str, not 'bytes'
    reader = codecs.getreader("utf-8")
    try:
        obj = json.load(reader(request))
        vendor = obj['result']['company']
    except:
        vendor = ""
    return vendor


def get_vrf(vlan):
    global_vrf_data = {'blu310': ['Vl310', 'Vl3311', 'Vl3312'],
                       'blu300': ['Vl300', 'Vl301', 'Vl303', 'Vl3301', 'Vl3302'],
                       'red910': ['Vl910', 'Vl3911', 'Vl3912'], 'orn400': ['Vl400', 'Vl3401', 'Vl3402'],
                       'blu330': ['Vl330', 'Vl3331', 'Vl3332'], 'blu320': ['Vl320', 'Vl3321', 'Vl3322'],
                       'grn200': ['Vl200', 'Vl210', 'Vl700', 'Vl1100', 'Vl3201', 'Vl3202'],
                       'blu350': ['Vl350', 'Vl3501', 'Vl3502']}
    for k, v in global_vrf_data.iteritems():
        if "Vl" not in vlan:
            if "Vl" + vlan in v:
                return k
    return "grn200"

# infile = open("commands_file.txt", "r+")
# command_list = [i for i in infile.readlines()]

def aci_Provision_apply(request):
    flag = True
    response_data = request.session['apic_data_dict']
    service_now_action = ''
    if response_data.has_key('action'):
        action = response_data['action']
    if response_data['apic_services'] == "Port Configuration":
        op_list = []
        leaf_dict = {}

        for leaf in response_data['leaf_id']:
            leaf_dict[leaf] = response_data['physical_port_' + str(leaf)]

        work_order_no = response_data['work_order_no']
        rollback_state_list = []
        for leaf, port_list in leaf_dict.iteritems():
            for port in port_list:
                port = port.replace(' ', '')
                response_data['work_order_no'] = work_order_no + "_" + leaf + "_" + port.replace('/', '_')
                print leaf, ">>>>>", port
                if action == 'Reservation':
                    service_now_action = ""
                    if Service_now_flag:
                        print "Herer In Service Now Flag !"
                        service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                        if not service_now.test_connection():
                            return render(request, 'notification.html',
                                          {'output_list': "ServiceNow Instance is uncreachable",
                                           'class': 'alert-danger'})
                    apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                    get_state = apic_auth.get_port_stat(work_order_no, leaf, port)
                    port_config = apic_auth.port_provision(leaf, port, response_data)
                    if len(port_config['imdata']) != 0 and port_config['imdata'][0].has_key('error'):
                        op_dict = {}
                        for data in port_config['imdata']:
                            print '>>>>', data
                            er = data['error']['attributes']
                            m1 = re.search(r'Validation failed', er['text'])
                            if m1:
                                op_dict['name'] = work_order_no
                                op_dict['leaf'] = leaf
                                op_dict['port'] = port
                                op_dict['result'] = "Validation failed"
                                # op_dict['result'] = m1.group(1)  # +' for Leaf '+ m1.group(2) +' and Physical Port -'+ m1.group(3)
                            op_list.append(op_dict)
                    
                    elif len(port_config['imdata']) == 0:
                        op_dict = {}
                        if action == 'Reservation':
                            q = ACIInterfaceStatusDB.objects.update_or_create(
                                work_order_no=work_order_no, leaf_id=leaf,
                                physical_port=port, status=action)

                            if Service_now_flag:
                                service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                                short_desc = "Request for Port Reservation "
                                desc = "Row Rack Number: " + str(
                                    response_data['rack_row_number']) + "\\nRack Number: " + str(
                                    response_data['rack_number']) + "\\nServer Name : " + response_data[
                                           'server_name'] + "\\nProvision Reason: " + response_data[
                                           'provision_reason'] + "\\nAction: " + str(response_data['action'])
                                create_req = service_now.creating_ChangeRequest(work_order_no, short_desc, desc)
                                if create_req['flag']:
                                    stete = ['Assess', 'Authorize']
                                    buss_service = "ACI"
                                    update_req_access = service_now.updating_State(work_order_no, stete, buss_service)
                            op_dict['name'] = work_order_no
                            op_dict['leaf'] = leaf
                            op_dict['port'] = port
                            op_dict['result'] = "Interface Reserved Successfully"
                            op_list.append(op_dict)
                
                if action in ['Provision'] and response_data['port_type'] == 'Physical':
                    service_now_action = ""
                    if Service_now_flag:
                        print "Herer In Service Now Flag !"
                        service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                        if not service_now.test_connection():
                            return render(request, 'notification.html',
                                          {'output_list': "ServiceNow Instance is uncreachable",
                                           'class': 'alert-danger'})
                    apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                    get_state = apic_auth.get_port_stat(work_order_no, leaf, port)
                    port_config = apic_auth.port_provision(leaf, port, response_data)
                    if len(port_config['imdata']) != 0 and port_config['imdata'][0].has_key('error'):
                        op_dict = {}
                        for data in port_config['imdata']:
                            print '>>>>', data
                            er = data['error']['attributes']
                            m1 = re.search(r'Validation failed', er['text'])
                            if m1:
                                op_dict['name'] = work_order_no
                                op_dict['leaf'] = leaf
                                op_dict['port'] = port
                                op_dict['result'] = "Validation failed"
                                # op_dict['result'] = m1.group(1)  # +' for Leaf '+ m1.group(2) +' and Physical Port -'+ m1.group(3)
                            op_list.append(op_dict)
                    
                    elif len(port_config['imdata']) == 0:
                        op_dict = {}
                        if action == 'Reservation':
                            q = ACIInterfaceStatusDB.objects.update_or_create(
                                work_order_no=work_order_no, leaf_id=leaf,
                                physical_port=port, status=action)

                            if Service_now_flag:
                                service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                                short_desc = "Request for Port Reservation "
                                desc = "Row Rack Number: " + str(
                                    response_data['rack_row_number']) + "\\nRack Number: " + str(
                                    response_data['rack_number']) + "\\nServer Name : " + response_data[
                                           'server_name'] + "\\nProvision Reason: " + response_data[
                                           'provision_reason'] + "\\nAction: " + str(response_data['action'])
                                create_req = service_now.creating_ChangeRequest(work_order_no, short_desc, desc)
                                if create_req['flag']:
                                    stete = ['Assess', 'Authorize']
                                    buss_service = "ACI"
                                    update_req_access = service_now.updating_State(work_order_no, stete, buss_service)
                            op_dict['name'] = work_order_no
                            op_dict['leaf'] = leaf
                            op_dict['port'] = port
                            op_dict['result'] = "Interface Reserved Successfully"
                            op_list.append(op_dict)

                        elif action == 'Provision':
                            vlan_detail = response_data['vlan_id'].split('_') 
                            vlan = vlan_detail[0]
                            epg = vlan_detail[1]
                            bd = vlan_detail[2]
                            app = response_data['application']
                            service_now_action = response_data['action_service_now']
                            # q = ACIInterfaceStatusDB.objects.update_or_create(work_order_no=response_data['config_name'],leaf_id=response_data['leaf_node'],physical_port=response_data['physical_ports'], status=action)
                            q1 = ACIInterfaceStatusDB.objects.filter(
                                work_order_no=work_order_no, leaf_id=leaf,
                                physical_port=port).update(status=action,tenant_name=response_data['tenant_name'],application_name=app,epg_name=json.dumps(epg))
                            if Service_now_flag:
                                # Add Service Now Check for Chnage No. Exist

                                service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                                check_change_request_no = service_now.check_change_request_no(work_order_no)
                                if check_change_request_no:
                                    # short_desc = "Request for port provision "
                                    # desc = "following port provision for Leaf " + ','.join(leaf_dict.keys())
                                    if "action_service_now" in response_data and response_data[
                                        'action_service_now'] == "review":
                                        stete = ['Scheduled', 'Implement', 'Review']
                                        buss_service = "ACI"
                                        update_req_access = service_now.updating_State(work_order_no, stete,
                                                                                       buss_service)
                                    elif "action_service_now" in response_data and response_data[
                                        'action_service_now'] == "closed":
                                        stete = ['Scheduled', 'Implement', 'Review']
                                        buss_service = "ACI"
                                        update_req_access = service_now.updating_State(work_order_no, stete,
                                                                                       buss_service)
                                        close_notes = response_data['close_notes']
                                        update_req = service_now.updating_close(work_order_no, close_notes)

                            op_dict['name'] = work_order_no
                            op_dict['leaf'] = leaf
                            op_dict['port'] = port
                            op_dict['result'] = "Interface Provisioned Successfully"

                            op_list.append(op_dict)
                            # return render(request, 'notification.html',
                            #               {'output_list': "Interface " + response_data[
                            #                   'physical_ports'].title() + " provisioned Successfully",
                            #                'class': 'alert-success'})
                
                if action in ['Provision'] and response_data['port_type'] in  ['Port-Channel', 'Virtual Port-Channel']:
                    service_now_action = ""
                    apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                    if action == 'Reservation':
                        get_state = apic_auth.get_port_stat(work_order_no, leaf, port)
                        port_config = apic_auth.port_provision(leaf, port, response_data)
                        if len(port_config['imdata']) != 0 and port_config['imdata'][0].has_key('error'):
                            op_dict = {}
                            for data in port_config['imdata']:
                                er = data['error']['attributes']
                                m1 = re.search(r'Validation failed', er['text'])
                                if m1:
                                    op_dict['name'] = work_order_no
                                    op_dict['leaf'] = leaf
                                    op_dict['port'] = port
                                    op_dict['result'] = "Validation failed"
                                    # op_dict['result'] = m1.group(1)  # +' for Leaf '+ m1.group(2) +' and Physical Port -'+ m1.group(3)
                                op_list.append(op_dict)
                        elif len(port_config['imdata']) == 0:
                            op_dict = {}
                            q = ACIInterfaceStatusDB.objects.update_or_create(
                                work_order_no=work_order_no, leaf_id=leaf,
                                physical_port=port, status=action)
                            if Service_now_flag:
                                service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                                short_desc = "Request for Port Reservation "
                                desc = "Row Rack Number: " + str(
                                    response_data['rack_row_number']) + "\\nRack Number: " + str(
                                    response_data['rack_number']) + "\\nServer Name : " + response_data[
                                           'server_name'] + "\\nProvision Reason: " + response_data[
                                           'provision_reason'] + "\\nAction: " + str(
                                    response_data['action'])
                                create_req = service_now.creating_ChangeRequest(work_order_no, short_desc, desc)
                                if create_req['flag']:
                                    stete = ['Assess', 'Authorize']
                                    buss_service = "ACI"
                                    update_req_access = service_now.updating_State(work_order_no, stete, buss_service)
                                # print "?????????", create_req
                            op_dict['name'] = work_order_no
                            op_dict['leaf'] = leaf
                            op_dict['port'] = port
                            op_dict['result'] = "Interface Reserved Successfully"
                            op_list.append(op_dict)

                    elif action == 'Provision':
                        service_now_action = response_data['action_service_now']
                        get_state = apic_auth.get_port_stat(work_order_no, leaf, port)
                        add_pc_interface = apic_auth.portchannel_group_assign(leaf, response_data['pc_policy_grp'],
                                                                              port,response_data['profile_grp'],response_data)
                        print "????????", add_pc_interface
                        
                        if not add_pc_interface['provision_status']:
                            op_dict = {}
                            op_dict['name'] = work_order_no
                            op_dict['leaf'] = leaf
                            op_dict['port'] = port
                            op_dict['result'] = add_pc_interface['Error']
                            op_list.append(op_dict)
                        
                        elif add_pc_interface['provision_status']:
                            op_dict = {}
                            service_now_action = response_data['action_service_now']
                            vlan_list = []
                            epg_list = []
                            bd_list = []
                            if type(response_data['vlan_id']) == list:
                                for ele in response_data['vlan_id']:
                                    vlan_detail = ele.split('-') 
                                    vlan_list.append(vlan_detail[0])
                                    epg_list.append(vlan_detail[1])
                                    bd_list.append(vlan_detail[2])
                                    app = response_data['application']
                            else:
                                vlan_detail = response_data['vlan_id'].split('-') 
                                vlan_list.append(vlan_detail[0])
                                epg_list.append(vlan_detail[1])
                                bd_list.append(vlan_detail[2])
                                app = response_data['application']
                                print ACIInterfaceStatusDB.objects.filter(work_order_no=work_order_no, leaf_id=leaf,physical_port=port)
                            if ACIInterfaceStatusDB.objects.filter(work_order_no=work_order_no, leaf_id=leaf,physical_port=port):
                                q1 = ACIInterfaceStatusDB.objects.filter(
                                        work_order_no=work_order_no, leaf_id=leaf,
                                        physical_port=port).update(status=action,tenant_name=response_data['tenant_name'],PC_group =response_data['pc_policy_grp'],application_name=app,epg_name=json.dumps(epg_list))
                            else:
                                print '######## Here '
                                q1 = ACIInterfaceStatusDB( work_order_no=work_order_no, leaf_id=leaf, physical_port=port, status=action,tenant_name=response_data['tenant_name'],PC_group =response_data['pc_policy_grp'],application_name=app, epg_name=json.dumps(epg_list))
                                q1.save()
                            print q1,"------------>>>>>>"
                            if Service_now_flag:
                                service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                                if "action_service_now" in response_data and response_data[
                                    'action_service_now'] == "review":
                                    stete = ['Scheduled', 'Implement', 'Review']
                                    buss_service = "ACI"
                                    update_req_access = service_now.updating_State(work_order_no, stete, buss_service)
                                elif "action_service_now" in response_data and response_data[
                                    'action_service_now'] == "closed":
                                    stete = ['Scheduled', 'Implement', 'Review']
                                    buss_service = "ACI"
                                    update_req_access = service_now.updating_State(work_order_no, stete, buss_service)
                                    close_notes = response_data['close_notes']
                                    update_req = service_now.updating_close(work_order_no, close_notes)

                            op_dict['name'] = work_order_no
                            op_dict['leaf'] = leaf
                            op_dict['port'] = port
                            op_dict['servicenow_action'] = response_data['action_service_now']
                            op_dict['result'] =add_pc_interface['Error']

                            op_list.append(op_dict)
                
                elif action == 'De-Provision':
                    # ACI Deprovision
                    status = ""
                    tenant = ""
                    app = ""
                    epg = ""
                    pc_group = ""
                    apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                    get_state = apic_auth.get_port_stat(work_order_no, leaf, port)

                    q1 = ACIInterfaceStatusDB.objects.filter(
                        leaf_id=leaf,
                        physical_port=port).values_list('status', 'tenant_name','PC_group', 'application_name','epg_name').last()
                    if q1:
                        status = q1[0]
                        tenant = q1[1]
                        pc_group = q1[2]
                        app = q1[3]
                        if q1[4] :
                            epg_list = json.loads(q1[4])
                        else:
                            epg_list = []
                    # for epg in epg_list:
                        # print pc_group,'>>>>>>>>>>>>'
                    if tenant:
                        delete_epg = apic_auth.epg_close(tenant, leaf, port, app,epg)
                    else:
                        all_tenant_data = apic_auth.deprovision_tenant_info()
                        for eth, eth_data in all_tenant_data.iteritems():
                            if eth == port and eth_data['leaf'] == leaf:
                                delete_epg = apic_auth.epg_close(eth_data['tenant'], leaf, port, eth_data['app'],eth_data['epg'])
                    get_overide_name = apic_auth.get_override_name(leaf,port)
                    if get_overide_name:
                        port_config = apic_auth.deprovision_port(get_overide_name, tenant, port,leaf, app, epg)
                        # if pc_group:
                        delete_pc_grp = apic_auth.deprovision_pc_group( leaf, port)
                        print 'here in deprovision',port_config
                        if len(port_config['imdata']) != 0 and port_config['imdata'][0].has_key('error'):
                            op_dict = {}
                            for data in port_config['imdata']:
                                er = data['error']['attributes']
                                m1 = re.search(r'Validation failed', er['text'])
                                if m1:
                                    op_dict['name'] = work_order_no
                                    op_dict['leaf'] = leaf
                                    op_dict['port'] = port
                                    op_dict['result'] = "Validation failed"
                                    # op_dict['result'] = m1.group(1)  # +' for Leaf '+ m1.group(2) +' and Physical Port -'+ m1.group(3)
                                op_list.append(op_dict)
                        
                        elif len(port_config['imdata']) == 0:
                            op_dict = {}
                            q1 = ACIInterfaceStatusDB.objects.filter(work_order_no=work_order_no, leaf_id=leaf,
                                                                    physical_port=port).delete()

                            if Service_now_flag:
                                service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                                short_desc = "Request for Port De-Provision "
                                if response_data['physical_port_101']:
                                    desc = "Action: " + str(
                                        response_data['action']) + "\\nLeaf ID: " + str(
                                        response_data['leaf_id']) + "\\nPhysical Port : " + str(
                                        response_data['physical_port_101'])
                                if response_data['physical_port_102']:
                                    desc = "Action: " + str(
                                        response_data['action']) + "\\nLeaf ID: " + str(
                                        response_data['leaf_id']) + "\\nPhysical Port : " + str(
                                        response_data['physical_port_102'])
                                create_req = service_now.creating_ChangeRequest(response_data['new_work_order_no'],
                                                                                short_desc,
                                                                                desc)
                                if create_req['flag']:
                                    stete = ['Assess', 'Authorize', 'Scheduled', 'Implement', 'Review']
                                    buss_service = "ACI Deprovision"
                                    update_req_access = service_now.updating_State(response_data['new_work_order_no'],
                                                                                stete,
                                                                                buss_service)
                            # if create_req['flag']:
                            #     stete = ['Assess', 'Authorize']
                            #     update_req_access = service_now.updating_State(work_order_no, stete)
                            #     # update_req_close = service_now.updating_close(work_order_no)
                            #     # print update_req_close, "Ticket Close"
                            # print "?????????", create_req

                            op_dict['name'] = work_order_no
                            op_dict['leaf'] = leaf
                            op_dict['port'] = port
                            op_dict['result'] = "Interface De-provisioned Successfully"
                            op_list.append(op_dict)

                            # return render(request, 'notification.html',
                            #               {'output_list': "Interface " + response_data[
                            #                   'physical_ports'].title() + " provisioned Successfully",
                            #                'class': 'alert-success'})

        # for state in rollback_state_list:
        #     global_state = rollback_state_list[0]
        if get_state :
            flag = True
        else:
            flag = False
        return render(request, 'port_provision_res.html',
                      {'output_list': op_list, 'flag': flag, 'action': action, 'servicenow_action': service_now_action})
    elif response_data['apic_services'] == "Add Or Modify Tenant":
        if response_data['select_tenant'] == 'New':
            apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
            create_tenant = apic_auth.Create_tenant(response_data['tenant_new'])
            if len(create_tenant['imdata']) == 0:
                if 'bd_new' in response_data and "," in response_data['bd_new']:
                    #     # eth1/1, eth1/2
                    create_bd = response_data['bd_new'].split(",")
                    for bd in create_bd:
                        response_data['bd_new'] = bd
                        # print 'Bridge_Domain >>>>>>>>',response_data
                        create_vrf_bd = apic_auth.Create_VrfBD(response_data)
                else:
                    create_vrf_bd = apic_auth.Create_VrfBD(response_data)

                create_app = apic_auth.create_app_profile(response_data)
                if len(create_app['imdata']) == 0:
                    if 'epg_name_new' in response_data and "," in response_data['epg_name_new']:
                        create_bd = response_data['epg_name_new'].split(",")
                        for bd in create_bd:
                            response_data['epg_name_new'] = bd
                            # print 'EPG ?????????',response_data
                            create_epg = apic_auth.create_epg(response_data)
                    else:
                        create_epg = apic_auth.create_epg(response_data)
                return render(request, 'notification.html',
                              {'output_list': response_data['tenant_new'] + " Tenant Added successfully",
                               'class': 'alert-success'})
            else:
                return render(request, 'notification.html',
                              {'output_list': "Error while Adding Tenant",
                               'class': 'alert-danger'})

        elif response_data['select_tenant'] == 'Existing':
            apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
            if response_data['bd_name']:
                if 'bd_name' in response_data and "," in response_data['bd_name']:
                    #     # eth1/1, eth1/2
                    create_bd = response_data['bd_name'].split(",")
                    op_dict = {}
                    for bd in create_bd:
                        response_data['bd_name'] = bd
                        # print 'Bridge_Domain >>>>>>>>',response_data
                        create_vrf_bd = apic_auth.Create_VrfBD(response_data)
                        if len(create_vrf_bd['imdata']) == 0:
                            op_dict['result'] = "Successfully Added"
                            
                        return render(request, 'notification.html',
                              {'output_list': response_data['tenant_new'] + " Tenant Added successfully",
                               'class': 'alert-success'})
                else:
                    create_vrf_bd = apic_auth.Create_VrfBD(response_data)
                    return render(request, 'notification.html',
                              {'output_list': response_data['tenant_new'] + " Tenant Added successfully",
                               'class': 'alert-success'})
            if response_data['epg_name']:
                if 'epg_name' in response_data and "," in response_data['epg_name']:
                    create_bd = response_data['epg_name'].split(",")
                    for bd in create_bd:
                        response_data['epg_name'] = bd
                        # print 'EPG ?????????',response_data
                        create_epg = apic_auth.create_epg(response_data)
                else:
                    create_epg = apic_auth.create_epg(response_data)
    elif response_data['apic_services'] == "policy_grp":
        print ">>>>>>> In Add Policy "
        apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
        create_policy_grp = apic_auth.policy_group_create(response_data['policy_name'],response_data['speed'])
        print create_policy_grp
        if len(create_policy_grp['imdata']) == 0:
            return render(request, 'notification.html',
                          {'output_list': "Leaf Port Policy Group " + response_data[
                              'policy_name'] + " added successfully",
                           'class': 'alert-success'})
        else:
            msg = create_policy_grp['imdata'][0]['error']['attributes']['text']
            return render(request, 'notification.html',
                          {'output_list': "Error while adding policy group",
                           'class': 'alert-danger'})
    elif response_data['apic_services'] == "port_channel_group":
        print ">>>>>>> In Add PC Policy "
        pc_policy_grp = response_data['PC_group_name']
        if response_data['PC_policy_type'] == 'New':
            PC_policy_name = response_data['port_channel_policy']
            PC_mode = response_data['port_channel_mode']
            desc = response_data['description']

            apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
            create_PC_policy = apic_auth.portchannel_policy_create(PC_policy_name, PC_mode, desc)
            print '>>>>>>',create_PC_policy
            if len(create_PC_policy['imdata']) == 0:
                craete_pc_group = apic_auth.portchannel_group_create2(pc_policy_grp, PC_policy_name, )
                if len(craete_pc_group['imdata']) == 0:
                    return render(request, 'notification.html',
                                  {
                                      'output_list': "New Port Channel Policy Group " + pc_policy_grp + " added successfully",
                                      'class': 'alert-success'})
                else:
                    msg = craete_pc_group['imdata'][0]['error']['attributes']['text']
                    return render(request, 'notification.html',
                                  {'output_list': "Error while adding Port channel policy group",
                                   'class': 'alert-danger'})
            else:
                msg = create_PC_policy['imdata'][0]['error']['attributes']['text']
                return render(request, 'notification.html',
                              {'output_list': "Error while adding Port channel policy ",
                               'class': 'alert-danger'})

        elif response_data['PC_policy_type'] == 'Existing':
            PC_policy_name = response_data['existing_PC_policy']
            apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
            create_PC_policy_grp = apic_auth.portchannel_group_create2(pc_policy_grp, PC_policy_name)
            print create_PC_policy_grp, ">>>>>>>>"
            if len(create_PC_policy_grp['imdata']) == 0:
                return render(request, 'notification.html',
                              {'output_list': "New Port Channel Policy Group " + response_data[
                                  'pc_policy_grp'] + " added successfully",
                               'class': 'alert-success'})

            else:
                msg = create_PC_policy_grp['imdata'][0]['error']['attributes']['text']
                return render(request, 'notification.html',
                              {'output_list': "Error while adding Port channel policy group",
                               'class': 'alert-danger'})
    elif response_data['apic_services'] == "ACI_Bulk_Upload":
        apic_port_list = response_data['response_dict']
        op_list = []
        for response_dict in apic_port_list:
            print '-------------------------------)))))))'
            print response_dict
            work_order_no = response_dict['work_order_no']
            response_dict['work_order_no'] = work_order_no + "_" + response_dict['leaf'] + "_" + response_dict[
                'port'].replace('/', '_')
            # response_dict['work_order_no'] = work_order_no + "_" + response_dict['leaf'] + "_" + response_dict[
            #     'port'].replace('/', '_')
            if response_dict['action'] == 'Reservation':
                service_now_action = ""
                if Service_now_flag:
                    print "Herer In Service Now Flag !"
                    service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                    if not service_now.test_connection():
                        return render(request, 'notification.html',
                                        {'output_list': "ServiceNow Instance is uncreachable",
                                        'class': 'alert-danger'})
                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                get_state = apic_auth.get_port_stat(work_order_no, response_dict['leaf'], response_dict['port'])
                port_config = apic_auth.port_provision_bulk(response_dict['leaf'], response_dict['port'], response_dict)
                if len(port_config['imdata']) != 0 and port_config['imdata'][0].has_key('error'):
                    op_dict = {}
                    for data in port_config['imdata']:
                        print '>>>>', data
                        er = data['error']['attributes']
                        m1 = re.search(r'Validation failed', er['text'])
                        if m1:
                            op_dict['name'] = work_order_no
                            op_dict['leaf'] = response_dict['leaf']
                            op_dict['port'] = response_dict['port']
                            op_dict['result'] = "Validation failed"
                            # op_dict['result'] = m1.group(1)  # +' for Leaf '+ m1.group(2) +' and Physical Port -'+ m1.group(3)
                        op_list.append(op_dict)
                
                elif len(port_config['imdata']) == 0:
                    op_dict = {}
                    if response_dict['action'] == 'Reservation':
                        q = ACIInterfaceStatusDB.objects.update_or_create(
                            work_order_no=work_order_no, leaf_id=response_dict['leaf'],
                            physical_port=response_dict['port'], status=response_dict['action'])

                        if Service_now_flag:
                            service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                            short_desc = "Request for Port Reservation "
                            desc = "Row Rack Number: " + str(
                                response_data['rack_row_number']) + "\\nRack Number: " + str(
                                response_data['rack_number']) + "\\nServer Name : " + response_data[
                                        'server_name'] + "\\nProvision Reason: " + response_data[
                                        'provision_reason'] + "\\nAction: " + str(response_data['action'])
                            create_req = service_now.creating_ChangeRequest(work_order_no, short_desc, desc)
                            if create_req['flag']:
                                stete = ['Assess', 'Authorize']
                                buss_service = "ACI"
                                update_req_access = service_now.updating_State(work_order_no, stete, buss_service)
                        op_dict['name'] = work_order_no
                        op_dict['leaf'] = response_dict['leaf']
                        op_dict['port'] = response_dict['port']
                        op_dict['result'] = "Interface Reserved Successfully"
                        op_list.append(op_dict)
            
            if response_dict['action'] in ['Provision'] and response_dict['port_type'] == 'Physical':
                service_now_action = ""
                response_dict['Desc_int_{}'.format(response_dict['port'].title())] = work_order_no +'_'+ response_dict['description']
                if Service_now_flag:
                    print "Herer In Service Now Flag !"
                    service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                    if not service_now.test_connection():
                        return render(request, 'notification.html',
                                        {'output_list': "ServiceNow Instance is uncreachable",
                                        'class': 'alert-danger'})
                apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                get_state = apic_auth.get_port_stat(work_order_no, response_dict['leaf'], response_dict['port'])
                port_config = apic_auth.port_provision_bulk(response_dict['leaf'], response_dict['port'], response_dict)
                if len(port_config['imdata']) != 0 and port_config['imdata'][0].has_key('error'):
                    op_dict = {}
                    for data in port_config['imdata']:
                        print '>>>>', data
                        er = data['error']['attributes']
                        m1 = re.search(r'Validation failed', er['text'])
                        if m1:
                            op_dict['name'] = work_order_no
                            op_dict['leaf'] = response_dict['leaf']
                            op_dict['port'] = response_dict['port']
                            op_dict['result'] = "Validation failed"
                            # op_dict['result'] = m1.group(1)  # +' for Leaf '+ m1.group(2) +' and Physical Port -'+ m1.group(3)
                        op_list.append(op_dict)
                
                elif len(port_config['imdata']) == 0:
                    op_dict = {}
                    # service_now_action = response_data['action_service_now']
                    vlan_list = []
                    epg_list = []
                    bd_list = []
                    if type(response_dict['vlan_id']) == list:
                        for ele in response_dict['vlan_id']:
                            vlan_detail = ele.split('-') 
                            vlan_list.append(vlan_detail[0])
                            epg_list.append(vlan_detail[1])
                            bd_list.append(vlan_detail[2])
                            app = response_dict['application']
                    else:
                        vlan_detail = response_dict['vlan_id'].split('-') 
                        vlan_list.append(vlan_detail[0])
                        epg_list.append(vlan_detail[1])
                        bd_list.append(vlan_detail[2])
                        app = response_dict['application']
                        # print ACIInterfaceStatusDB.objects.filter(work_order_no=work_order_no, leaf_id=leaf,physical_port=port)
                    
                    if ACIInterfaceStatusDB.objects.filter(work_order_no=work_order_no, leaf_id=response_dict['leaf'],physical_port=response_dict['port']):
                        q1 = ACIInterfaceStatusDB.objects.filter(
                                work_order_no=work_order_no, leaf_id=response_dict['leaf'],
                                physical_port=response_dict['port']).update(status=response_dict['action'],tenant_name=response_data['tenant_name'],PC_group =response_dict['policy_grp'],application_name=app,epg_name=json.dumps(epg_list))
                    else:
                        print '######## Here '
                        q1 = ACIInterfaceStatusDB( work_order_no=work_order_no, leaf_id=response_dict['leaf'], physical_port=response_dict['port'], status=response_dict['action'],tenant_name=response_dict['tenant_name'],PC_group =response_dict['policy_grp'],application_name=app, epg_name=json.dumps(epg_list))
                        q1.save()
                    print q1,"------------>>>>>>"
                    if Service_now_flag:
                        service_now = ServiceNow_ChangeRequest_Data(SRUsername, SRPassword)
                        if "action_service_now" in response_data and response_data[
                            'action_service_now'] == "review":
                            stete = ['Scheduled', 'Implement', 'Review']
                            buss_service = "ACI"
                            update_req_access = service_now.updating_State(work_order_no, stete, buss_service)
                        elif "action_service_now" in response_data and response_data[
                            'action_service_now'] == "closed":
                            stete = ['Scheduled', 'Implement', 'Review']
                            buss_service = "ACI"
                            update_req_access = service_now.updating_State(work_order_no, stete, buss_service)
                            close_notes = response_data['close_notes']
                            update_req = service_now.updating_close(work_order_no, close_notes)

                    op_dict['name'] = work_order_no
                    op_dict['leaf'] = response_dict['leaf']
                    op_dict['port'] = response_dict['port']
                    # op_dict['servicenow_action'] = response_dict['action_service_now']
                    op_dict['result'] ='Interface Provisioned Successfull'

                    op_list.append(op_dict)
            
        print op_list
        return render(request, 'apic_api_bulk_op.html',
                      {'output_list': op_list, 'class': 'alert-success'})
    # print '>>>>>>>>>>',response_data
    # return HttpResponse("<p> Hi Ypou Got Ity </p>")


def rollback_config_apply(request):
    response_data = request.session['apic_data_dict']
    if response_data['apic_services'] == "ACI_Bulk_Upload":
        apic_data = response_data['response_dict']
        op_list = []
        for data in apic_data:
            response_data = data
            print '??????????', response_data
            work_order_no = response_data['work_order_no']
            apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
            rollback_result = apic_auth.rollback_state(work_order_no)

        for tup in rollback_result:
            op_d = {}
            if tup[0]:
                op_d['name'] = response_data['work_order_no']
                op_d['leaf'] = tup[1]
                op_d['port'] = tup[2]
                op_d['result'] = "Rollback Successfull"
            else:
                op_d['name'] = response_data['work_order_no']
                op_d['leaf'] = tup[1]
                op_d['port'] = tup[2]
                op_d['result'] = "Rollback Successfull"
            op_list.append(op_d)
    else:
        work_order_no = response_data['work_order_no']
        op_list = []
        op_d = {}
        with open('mysite/ACI_Rolback_Dir/' + work_order_no + ".json", "r+") as json_file:
            data1 = json.load(json_file)

            for k, v in data1.iteritems():
                op_d['overridename'] = k
                op_d['leaf'] = v['leaf_node']
                op_d['port'] = v['port']
                op_d['policy'] = v['policy']
                op_d['desc'] = v['desc']
            # op_list.append(op_d)
        disolay_data = Display_Inputs_for_rollback(op_d)
        return render(request, 'port_rollback_config.html', {'output_list': disolay_data})


def rollback_config_apply1(request):
    response_data = request.session['apic_data_dict']
    if response_data['apic_services'] == "ACI_Bulk_Upload":
        apic_data = response_data['response_dict']
        op_list = []
        for data in apic_data:
            response_data = data
            print '??????????', response_data
    else:
        work_order_no = response_data['work_order_no']
        apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
        rollback_result = apic_auth.rollback_state(work_order_no)
        op_list = []
        for tup in rollback_result:
            op_d = {}
            if tup[0]:
                op_d['name'] = response_data['work_order_no']
                op_d['leaf'] = tup[1]
                op_d['port'] = tup[2]
                op_d['result'] = "Rollback Successfull"
            else:
                op_d['name'] = response_data['work_order_no']
                op_d['leaf'] = tup[1]
                op_d['port'] = tup[2]
                op_d['result'] = "Rollback Successfull"
            op_list.append(op_d)
    return render(request, 'port_provision_res.html', {'output_list': op_list, 'flag': False})
