from __future__ import absolute_import
from mysite.globals import *
import json
import re
import os
import requests
import urllib3
import collections
urllib3.disable_warnings()


def ping(ip_add):
    response = os.system('ping -c 1 ' + ip_add)
    if response == 0:
        return True
    else:
        return False


class ACIconfig_by_API:
    def __init__(self, ip_address, user, pwd):
        self.user_name = user
        self.password = pwd
        self.ip_addr = ip_address
        if self.test_connection():
            self.get_token()

    def test_connection(self):
        if ping(self.ip_addr):
            return True
        else:
            return False

    def get_token(self):
        
        r = requests.post('https://' + self.ip_addr + '/api/aaaLogin.json',
                          json={'aaaUser': {"attributes": {
                              'name': self.user_name, 'pwd': self.password}}},
                          verify=False)
        r_json = r.json()
        self.token = r_json["imdata"][0]["aaaLogin"]["attributes"]["token"]
        # return self.token
        # print self.token

    # Get Details 
    
    def get_model_no(self,leaf):
        path1 = 'https://198.18.133.200/api/node/mo/topology/pod-1/node-'+leaf+'.json'

        token = self.token
        
        cookie = {'APIC-cookie': token}
        r = requests.get(path1, cookies=cookie, verify=False)
        opt = r.json()
        for data in opt['imdata']:
            # leaf_data = {}
            for k,v in  data["fabricNode"]["attributes"].iteritems():
                if 'model' in k:
                    return v
 
    def get_leaf_list(self):
        
        leaf_data_list = []
        
        path1 = 'http://198.18.133.200/api/node/class/topology/pod-1/topSystem.json?query-target-filter=eq(topSystem.role,"leaf")&rsp-subtree-include=health,required'

        # path = 'http://198.18.133.200/api/node/class/topology/pod-1/topSystem.json?query-target-filter=eq(topSystem.role,"spine")&rsp-subtree-include=health,required'

        token = self.token
        cookie = {'APIC-cookie': token}
        # r1 = requests.get(path, cookies=cookie, verify=False)
        r = requests.get(path1, cookies=cookie, verify=False)
        opt = r.json()
        # opt1=r1.json()
        for data in opt['imdata']:
            leaf_data = {}
            for k,v in  data["topSystem"]["attributes"].iteritems():
                # print k,'>>>>',v
                if "id" in k:
                    leaf_data["name"]= v
                if "serial" in k:
                    leaf_data["serial"]= v
            leaf_data_list.append(leaf_data)     
        return leaf_data_list
            # print ele       
    
    def get_all_tenant(self):
        # getting of all tenant
        # token=""
        tenant_lst = []
        token = self.token
        # print token, ">>>token"
        cookie = {'APIC-cookie': token}
        url = "https://" + self.ip_addr + "/api/class/fvTenant.json"
        # print ("\nExecuting GET '%s'\n" % url)
        # The request and response of "GET" request
        resp = requests.get(url, cookies=cookie, verify=False)
        data = resp.json()
        for i in data["imdata"]:
            tenant_lst.append(i["fvTenant"]["attributes"]["name"])
        return tenant_lst

    def get_epg_bd(self,tenant, app):
        path1 = 'https://198.18.133.200/api/node/mo/uni/tn-'+tenant+'/ap-'+app+'.json?query-target=subtree&target-subtree-class=fvAEPg&query-target-filter=and(not(wcard(fvAEPg.dn,"__ui_")),eq(fvAEPg.isAttrBasedEPg,"false"))&rsp-subtree=children&rsp-subtree-class=fvRsBd'

        token = self.token
        cookie = {'APIC-cookie': token}

        r = requests.get(path1, cookies=cookie, verify=False)
        opt = r.json()
        data = opt['imdata']
        epg_list = []
        bd_list = []
        for i in data:
            EPG = i['fvAEPg']['attributes']['name']
            BD = i['fvAEPg']['children'][0]['fvRsBd']['attributes']['tnFvBDName']
            epg_list.append(EPG)
            bd_list.append(BD)
        return {'epg':epg_list, 'bd':bd_list}
    
    def get_port_details(self,leaf):
        port_details_dict = {}
        token = self.token
        cookie = {'APIC-cookie': token}
        
        url = "http://"+self.ip_addr+"/api/node/class/topology/pod-1/node-"+str(leaf)+"/l1PhysIf.json"
        
        print ("\nExecuting GET '%s'\n" % url)
        count = 0
        resp = requests.get(url, cookies=cookie, verify=False)
        data = resp.json()
        for ele in data['imdata']:
            details_dict = {}
            count += 1
            for k, v in ele["l1PhysIf"]["attributes"].iteritems():
                if "id" in k:
                    details_dict['port'] = v
                    oper_state = self.oper_status(leaf,v)
                    policy = self.get_policy_get(leaf,v)
                    details_dict['policy'] = oper_state
                    details_dict['oper_state'] = oper_state
                    port_details_dict[details_dict['port']] = {}
                if "adminSt" in k:
                    details_dict['admin_state'] = v
                if "descr" in k:
                    details_dict['description'] = v
                if 'port' in  details_dict and details_dict['port'] in port_details_dict:
                    port_details_dict[details_dict['port']] = details_dict
            # port_details_list.append(details_dict)  
        # print count
        return port_details_dict
    
    def get_policy_get(self,leaf,port):
        path='http://'+self.ip_addr+'/api/node/class/infraHPathS.json?&rsp-subtree=full&query-target=subtree&query-target-filter=and(eq(infraRsHPathAtt.tDn,%22topology/pod-1/paths-'+leaf+'/pathep-['+port+']%22))'
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.get(path, cookies=cookie, verify=False)
        opt = r.json()
        policy = ""
        for data in opt['imdata']:
            port_details = data['infraRsHPathAtt']
            for k, v in port_details['attributes'].iteritems():
                if 'dn' in k:
                    m1 = re.search(r'hpaths\S(\S.+)/rsHPathAtt', v)
                    if m1:
                        unitno = m1.group(1)
                    path1='http://'+self.ip_addr+'/api/node/mo/uni/infra/hpaths-'+unitno+'/rspathToAccBaseGrp.json'
                    r1= requests.get(path1, cookies=cookie, verify=False)
                    opt1 = r1.json()
                    for data in opt1['imdata']:
                        port_details = data['infraRsPathToAccBaseGrp']
                        for k, v in port_details['attributes'].iteritems():
                            if 'tDn' in k:
                                m1 = re.search(r'accportgrp\S(\S.+)', v)
                                if m1:
                                    policy = m1.group(1)
                                    return policy
        return policy
    
    def get_port_stat(self, name, leaf, port):
        state_dict = {}
        overide_name = name + "_" + leaf + "_" + port.replace("/", "_")
        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/hpaths-' + overide_name + '.json'
        token = self.token
        cookie = {'APIC-cookie': token}

        r = requests.get(path, cookies=cookie, verify=False)
        # print r.json()

        for elem in r.json()['imdata']:
            overide_name = elem['infraHPathS']['attributes']['name']
            descr = elem['infraHPathS']['attributes']['descr']
            state_dict[overide_name] = {
                'desc': descr, 'leaf_node': leaf, 'port': port}
            break
        path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/hpaths-' + \
            overide_name + '/rspathToAccBaseGrp.json'

        r = requests.get(path, cookies=cookie, verify=False)
        for elem in r.json()['imdata']:
            policy_grp = elem['infraRsPathToAccBaseGrp']['attributes']['tDn']
            m2 = re.search(r'uni/infra/funcprof/accportgrp-(\S.+)', policy_grp)
            if m2:
                policy = m2.group(1)
                state_dict[overide_name]['policy'] = policy
        # c.update(s)
        # js =
        try:
            with open('mysite/ACI_Rolback_Dir/' + name + ".json", 'r+') as json_file:
                data1 = json.load(json_file)
                print data1, ">>>>>>"
                data1.update(state_dict)
                with open('mysite/ACI_Rolback_Dir/' + name + ".json", 'w+') as data:
                    json.dump(data1, data)
        except:
            with open('mysite/ACI_Rolback_Dir/' + name + ".json", 'w+') as data:
                json.dump(state_dict, data)
        if len(state_dict.keys()) == 0:
            return False
        else:
            return True

    def apps_profile(self, tenant_name):

        app_list = []
        # path = 'http://'+self.ip_addr+'/api/node/api/node/class/pod-1/l1PhysIf.json'
        path = 'http://' + self.ip_addr + '/api/node/mo/uni/tn-' + tenant_name + \
            '.json?order-by=fvAp.name|asc&query-target=subtree&target-subtree-class=fvAp'
        
        token = self.token
        cookie = {'APIC-cookie': token}

        r = requests.get(path, cookies=cookie, verify=False)
        # print r
        data = r.json()
        for i in data["imdata"]:
            app_list.append(i["fvAp"]["attributes"]["name"])
        return app_list

    def leaf_status_details(self, leaf_node, phy_port):
        # leaf_node = response_dict['leaf_node']
        # phy_port = response_dict['phy_port']
        # print "Physial Port==============================>", phy_port
        path = 'http://' + self.ip_addr + '/api/node/mo/topology/pod-1/node-' + leaf_node + '/sys/phys-[' + phy_port + '].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg'

        token = self.token
        cookie = {'APIC-cookie': token}
        rsp = requests.get(path, cookies=cookie, verify=False)
        op = rsp.json()
        for each in op['imdata']:
            # print "--------))))))", each
            if "l1PhysIf" in each:
                get_data = each['l1PhysIf']['attributes']
                # print get_data
                return get_data
        else:
            return {}
    
    def get_override_name(self, leaf_node, phy_port):
        
        overide_name = ''
        path = 'https://'+self.ip_addr+'/api/node/class/infraHPathS.json?&rsp-subtree=full&query-target=subtree&query-target-filter=and(eq(infraRsHPathAtt.tDn,%22topology/pod-1/paths-'+leaf_node+'/pathep-['+phy_port+']%22))'

        token = self.token
        cookie = {'APIC-cookie': token}
        rsp = requests.get(path, cookies=cookie, verify=False)
        op = rsp.json()
        for each in op['imdata']:
            # print "--------))))))", each
            if "infraRsHPathAtt" in each:
                get_data = each['infraRsHPathAtt']['attributes']['dn']
                match_data = re.search(r'hpaths-(\S+)/rs',get_data )
                if match_data:
                    overide_name = match_data.group(1)
        return overide_name

    # Create On APIC
    
    def Create_tenant(self, tenant_name):
        # function to create tenant using json
        token = self.token
        r_json = {
            "fvTenant": {
                "attributes": {
                    "name": tenant_name}}}

        cookie = {'APIC-cookie': token}
        post_url = "https://" + self.ip_addr + "/api/mo/uni.json"
        headers = {'content-type': 'application/json'}
        r = requests.post(post_url, data=json.dumps(
            r_json), cookies=cookie, verify=False)
        r1 = r.json()
        return r1

    def Create_VrfBD(self, data_dict):
        if data_dict['select_tenant'] == 'New':
            tenant_name = data_dict['tenant_new']
            get_vrf = data_dict['vrf_new']
            get_bd = data_dict['bd_new']
        else:
            tenant_name = data_dict['tenant_name']
            get_vrf = data_dict['vrf_name']
            get_bd = data_dict['bd_name']

        r_json = '<fvTenant name="' + tenant_name + '"><fvCtx name="' + get_vrf + '"/> <fvBD name="' + get_bd + '"> <fvRsCtx tnFvCtxName="' + get_vrf + '"/> ' \
                                                                                                                                                        '<fvSubnet ip="10.10.100.1/24"/> </fvBD></fvTenant>'
        token = self.token
        cookie = {'APIC-cookie': token}
        # The url for the post ticket API reques
        post_url = "https://" + self.ip_addr + \
            "/api/node/mo/uni/tn-" + tenant_name + ".xml"
        headers = {'content-type': 'application/xml'}
        r = requests.post(post_url, data=r_json, cookies=cookie, verify=False)
        # print ">>>>>>>", r.text
        return r

    def create_app_profile(self, data_dict):
        if data_dict['select_tenant'] == 'New':
            tenant_name = data_dict['tenant_new']
            app_name = data_dict['app_name_new']
        else:
            tenant_name = data_dict['tenant_name']
            app_name = data_dict['app_name']

        path = 'http://' + self.ip_addr + '/api/node/mo/uni/tn-' + \
            tenant_name + '/ap-' + app_name + '.json'
        payload = '{"fvAp":{"attributes":{"dn":"uni/tn-' + tenant_name + '/ap-' + app_name + \
            '","name":"' + app_name + '","rn":"ap-' + \
            app_name + '","status":"created"},"children":[]}}'
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.post(path, cookies=cookie, data=payload, verify=False)
        # print r
        return r.json()

    def create_epg(self, data_dict):
        if data_dict['select_tenant'] == 'New':
            tenant_name = data_dict['tenant_new']
            app_name = data_dict['app_name_new']
            epg_name = data_dict['epg_name_new']
            bd_name = data_dict['bd_new']
        else:
            tenant_name = data_dict['tenant_name']
            app_name = data_dict['app_name']
            epg_name = data_dict['epg_name']
            bd_name = data_dict['bd_name']
        # path = 'http://'+self.ip_addr+'/api/node/api/node/class/pod-1/l1PhysIf.json'
        path = 'http://' + self.ip_addr + '/api/node/mo/uni/tn-' + \
            tenant_name + '/ap-' + app_name + '/epg-' + epg_name + '.json'
        payload = '{"fvAEPg": {"attributes": {"dn": "uni/tn-' + tenant_name + '/ap-' + app_name + '/epg-' + epg_name + '", "name": "' + epg_name + '", "rn": "epg-' + epg_name + '","status": "created"}, ' \
                                                                                                                                                                                 '"children": [{"fvRsBd": {"attributes": {"tnFvBDName": "' + \
            bd_name + '", "status": "created,modified"}, "children": []}}]}}'

        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.post(path, cookies=cookie, data=payload, verify=False)
        # print r
        print r.json()

    def create_policy_group(self, response_dict):
        grp_name = response_dict['policy_name']
        description = response_dict['description']
        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/funcprof/accportgrp-' + grp_name + '.json'
        data = '{"infraAccPortGrp":{"attributes":{"dn":"uni/infra/funcprof/accportgrp-' + grp_name + '","name":"' + \
            grp_name + '","descr":' + description + ',"rn":"accportgrp-' + \
            grp_name + '","status":"created"},"children":[]}}'
        token = self.token
        cookie = {'APIC-cookie': token}

        r = requests.post(path, data=data, cookies=cookie, verify=False)
        return r.json()

    def policy_group_create(self, name,speed):
        llp2 = name + "_llp1280"
        interface_prority_folw = name + "_interface_pfy20"
        interface_fc_policy = "_interface_fc_policy2"
        slow_drain = "_slow_drain"
        cdp1 = name + "_cdp1"
        mcp1 = name + "_mcp1"
        lldp1 = name + "_lldp1"
        stp_policy = name + "_stp_policy"
        storm_control_policy = name + "_storm_control_policy"
        L2_inter = name + "_L2_inter"
        port_securit = name + "_port_securit"
        Access_entity_profile = name + "_attached-entity"

        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/funcprof/accportgrp-' + name + '.json'

        r_json = '{"infraAccPortGrp":{"attributes":{"dn":"uni/infra/funcprof/accportgrp-' + name + '","name":"' + name + '","rn":"accportgrp-' + name + '","status":"created"},' \
                                                                                                                                                        '"children":[{"infraRsHIfPol":{"attributes":{"tnFabricHIfPolName":"' + llp2 + '","status":"created,modified"},"children":[]}},' \
                                                                                                                                                                                                                                      '{"infraRsQosPfcIfPol":{"attributes":{"tnQosPfcIfPolName":"' + interface_prority_folw + '","status":"created,modified"},"children":[]}},' \
                                                                                                                                                                                                                                                                                                                              '{"infraRsFcIfPol":{"attributes":{"tnFcIfPolName":"' + interface_fc_policy + '","status":"created,modified"},"children":[]}},' \
                                                                                                                                                                                                                                                                                                                                                                                                           '{"infraRsQosSdIfPol":{"attributes":{"tnQosSdIfPolName":"' + slow_drain + '","status":"created,modified"},"children":[]}},' \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     '{"infraRsCdpIfPol":{"attributes":{"tnCdpIfPolName":"' + cdp1 + '","status":"created,modified"},"children":[]}},' \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     '{"infraRsMcpIfPol":{"attributes":{"tnMcpIfPolName":"' + mcp1 + '","status":"created,modified"},"children":[]}},' \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     '{"infraRsLldpIfPol":{"attributes":{"tnLldpIfPolName":"' + lldp1 + '","status":"created,modified"},"children":[]}},' \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        '{"infraRsAttEntP":{"attributes":{"tDn":"uni/infra/attentp-' + Access_entity_profile + '","status":"created,modified"},"children":[]}},' \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               '{"infraRsStpIfPol":{"attributes":{"tnStpIfPolName":"' + stp_policy + '","status":"created,modified"},"children":[]}},' \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     '{"infraRsStormctrlIfPol":{"attributes":{"tnStormctrlIfPolName":"' + storm_control_policy + '","status":"created,modified"},"children":[]}},' \
            '{"infraRsL2IfPol":{"attributes":{"tnL2IfPolName":"' + L2_inter + '","status":"created,modified"},"children":[]}},' \
            '{"infraRsL2PortSecurityPol":{"attributes":{"tnL2PortSecurityPolName":"' + \
            port_securit + '","status":"created,modified"},"children":[]}}]}}'

        token = self.token
        cookie = {'APIC-cookie': token}

        r_policy = requests.post(
            path, data=r_json, cookies=cookie, verify=False)
        # print '>>>>>>>>---------', r.json()
        # return r.json()

        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/hintfpol-' + llp2 + '.json'

        data = '{"fabricHIfPol":{"attributes":{"dn":"uni/infra/hintfpol-' + \
            llp2 + '","descr":"any","autoNeg":"on","speed":"'+speed+'"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)

        print r.json()

        path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/pfc-' + \
            interface_prority_folw + '.json'

        data = '{"qosPfcIfPol":{"attributes":{"dn":"uni/infra/pfc-' + interface_prority_folw + '","name":"' + \
            interface_prority_folw + '","rn":"pfc-' + \
            interface_prority_folw + '","status":"created"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)

        print r.json()

        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/fcIfPol-' + interface_fc_policy + '.json'

        data = '{"fcIfPol":{"attributes":{"dn":"uni/infra/fcIfPol-' + interface_fc_policy + \
            '","portMode":"f","trunkMode":"trunk-off","automaxspeed":"32G"},"children":[]}}'
        r = requests.post(path, data=data, cookies=cookie, verify=False)

        print r.json()

        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/qossdpol-' + slow_drain + '.json'

        data = '{"qosSdIfPol":{"attributes":{"dn":"uni/infra/qossdpol-' + slow_drain + '","flushAdminSt":"disabled","name":"' + \
            slow_drain + '","rn":"qossdpol-' + slow_drain + \
            '","status":"created,modified"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)

        print r.json()

        path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/cdpIfP-' + cdp1 + '.json'

        data = '{"cdpIfPol":{"attributes":{"dn":"uni/infra/cdpIfP-' + \
            cdp1 + '"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)

        print r.json()

        path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/mcpIfP-' + mcp1 + '.json'

        data = '{"mcpIfPol":{"attributes":{"dn":"uni/infra/mcpIfP-' + \
            mcp1 + '","adminSt":"disabled"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)

        print r.json()

        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/lldpIfP-' + lldp1 + '.json'

        data = '{"lldpIfPol":{"attributes":{"dn":"uni/infra/lldpIfP-' + lldp1 + \
            '","descr":"test","adminRxSt":"enabled","adminTxSt":"enabled"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)
        print r.json()

        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/ifPol-' + stp_policy + '.json'

        data = '{"stpIfPol":{"attributes":{"dn":"uni/infra/ifPol-' + \
            stp_policy + '","descr":"test"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)
        print r.json()

        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/stormctrlifp-' + storm_control_policy + '.json'

        data = '{"stormctrlIfPol":{"attributes":{"dn":"uni/infra/stormctrlifp-' + storm_control_policy + \
            '","rate":"100.000000","burstRate":"100.000000","isUcMcBcStormPktCfgValid":"Invalid"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)
        print r.json()

        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/l2IfP-' + L2_inter + '.json'

        data = '{"l2IfPol":{"attributes":{"dn":"uni/infra/l2IfP-' + L2_inter + \
            '","vlanScope":"portlocal","vepa":"disabled"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)

        print r.json()

        # path = 'http://'+self.ip_addr+'/api/node/mo/uni/infra/portsecurityP-' + port_securit + '.json'
        #
        # data = '{"l2PortSecurityPol":{"attributes":{"timeout":"60","descr":"sssdddd","name":' + port_securit + '},"children":[]}}'

        path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/funcprof/accportgrp-' + \
            name + '/rsl2PortSecurityPol.json'

        data = '{"infraRsL2PortSecurityPol":{"attributes":{"tnL2PortSecurityPolName":"port_security_policy"},"children":[]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)
        print r.json()

        path = 'http://198.18.133.200/api/node/mo/uni/infra/attentp-' + \
            Access_entity_profile + '.json'

        data = '{"infraAttEntityP":{"attributes":{"dn":"uni/infra/attentp-' + Access_entity_profile + '","name":"' + Access_entity_profile + '",' \
                                                                                                                                             '"rn":"attentp-' + Access_entity_profile + '","status":"created"},' \
                                                                                                                                                                                        '"children":[{"infraProvAcc":{"attributes":{"dn":"uni/infra/attentp-' + Access_entity_profile + '/provacc","status":"created"},' \
                                                                                                                                                                                                                                                                                        '"children":[]}},{"infraRsDomP":{"attributes":{"tDn":"uni/phys-vlan_domain_1","status":"created"},"children":[]}}]}}'

        r = requests.post(path, data=data, cookies=cookie, verify=False)

        print r.json()
        return r_policy.json()

    # Physical Provision
    
    def Deploy_EPG(self, data_dict):
        token = self.token
        tenant_name = data_dict['tenant']
        vrf_name = data_dict['vrf']
        bd_name = data_dict['bd']
        app_name = data_dict['app']
        epg_name = data_dict['epg']
        leaf_id = data_dict['leaf_id']
        phy_port = data_dict['port']
        mode = data_dict['mode']
        vlan = data_dict['vlan']
        # regular ---> Trunk
        # untagged ---> Access
        req_xml = '<fvTenant name="' + tenant_name + '" dn="uni/tn-' + tenant_name + '" > <fvCtx name="' + vrf_name + '" pcEnfPref="enforced" knwMcastAct="permit"/><fvBD name="' + bd_name + '" unkMcastAct="flood" ><fvRsCtx tnFvCtxName="' + vrf_name + '"/></fvBD><fvAp name="' + app_name + '" > <fvAEPg name="' + epg_name + '" ><fvRsPathAtt tDn="topology/pod-1/paths-' + leaf_id + '/pathep-[' + phy_port + ']" mode="' + mode + '" instrImedcy="immediate" encap="vlan-' + vlan + '"/></fvAEPg></fvAp></fvTenant>'

        cookie = {'APIC-cookie': token}
        # The url for the post ticket API reques
        post_url = 'https://' + self.ip_addr + \
            '/api/node/mo/uni/tn-' + tenant_name + '.xml'
        headers = {'content-type': 'application/xml'}
        r = requests.post(post_url, data=req_xml, cookies=cookie, verify=False)
        return r

    def oper_status(self,leaf,port):
        path = 'https://198.18.133.200/api/node/mo/topology/pod-1/node-'+leaf+'/sys/phys-['+port+'].json?query-target=children&target-subtree-class=ethpmPhysIf'

        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.get(path, cookies=cookie, verify=False)
        opt = r.json()
        port_data = []
        for data in opt['imdata']:
            # print ">>>>>>", data
            if 'ethpmPhysIf' in data:
                port_details = data['ethpmPhysIf']['attributes']
                return port_details['operSt']  
            else:
                return {}
                        
    def enable_disable_switch_port(self, port, leaf_id, action):
        print "am here"
        path = 'https://' + self.ip_addr + '/api/node/mo/uni/fabric/outofsvc.json'
        if action == 'disable':
            data = '{"fabricRsOosPath":{"attributes":{"dn":"uni/fabric/outofsvc/rsoosPath-[topology/pod-1/paths-' + \
                leaf_id + '/pathep-[' + port + \
                ']]","lc":"blacklist"},"children":[]}}'

        elif action == 'enable':
            data = '{"fabricRsOosPath":{"attributes":{"dn":"uni/fabric/outofsvc/rsoosPath-[topology/pod-1/paths-%s/pathep-[%s]]","status":"deleted"},"children":[]}}' % (
                leaf_id, port)
        # print data
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.post(path, data=data, cookies=cookie, verify=False)
        # req = self.post(path,data)
        return r

    def port_provision(self, leaf, interface, response_data):
        # print " In Port Provision "
        print leaf, interface, response_data
        name = response_data['work_order_no']
        # dsc = response_data['action'] + \
        #     " for Work Order No. " + name.split('_')[0]
            
        # dsc = name.split('_')[0] +'_'+ response_data['Desc_int_{}'.format(interface.title())]
        if 'description' in response_data and len(response_data['description'])!=0:
            dsc = name.split('_')[0]+"_"+response_data['action']+"_"+response_data['description']
        else:
            dsc = name.split('_')[0]+"_"+response_data['action']
            
        policy_grp = response_data['policy_grp']
        leaf_node = leaf
        port = interface
        state = response_data['admin_state']
        port_status = self.leaf_status_details(leaf, interface)
        oper_status = self.oper_status(leaf, interface)
        policy_status = self.get_policy_get(leaf, interface)
        path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/hpaths-' + name + '.json'
        token = self.token
        # Enable / Disable
        cookie = {'APIC-cookie': token}
        # rsp = requests.post(path, cookies=cookie, data=data, verify=False)
        # Enable / Disable
        port_state = self.enable_disable_switch_port(port, leaf_node, state)
        print oper_status !="up"
        if oper_status !="up" :
            if response_data['action'] == "Reservation" and not policy_status:
                data = '{"infraHPathS":{"attributes":{"dn":"uni/infra/hpaths-' + name + '","name":"' + name + '","status":"created,modified","descr":"' + dsc + '","rn":"hpaths-' + name + \
                    '"},"children":[{"infraRsHPathAtt":{"attributes":{"tDn":"topology/pod-1/paths-' + leaf_node + '/pathep-[' + port + \
                    ']"},"children":[]}}],"children":[{"infraRsPathToAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accportgrp-' + \
                    policy_grp + '","status":"created,modified"}}}]}}'
                rsp = requests.post(path, cookies=cookie, data=data, verify=False)
                print rsp
                return rsp.json()
            elif response_data['action'] == "Provision" and not policy_status:
                desc_port = 'Eth1/'+interface.split('/')[1]
                print desc_port
                if name.split('_')[0] not in response_data['Desc_int_{}'.format(desc_port.title())].split("_")[0]:
                    dsc = name.split('_')[0] +'_'+ response_data['Desc_int_{}'.format(desc_port.title())]
                else:
                    dsc = response_data['Desc_int_{}'.format(desc_port.title())]
                # policy_gen = self.policy_group_create(response_data['policy_grp'], response_data['speed'])

                data = '{"infraHPathS":{"attributes":{"dn":"uni/infra/hpaths-' + name + '","name":"' + name + '","status":"created,modified","descr":"' + dsc + '","rn":"hpaths-' + name + \
                    '"},"children":[{"infraRsHPathAtt":{"attributes":{"tDn":"topology/pod-1/paths-' + leaf_node + '/pathep-[' + port + \
                    ']"},"children":[]}}],"children":[{"infraRsPathToAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accportgrp-' + \
                    policy_grp + '","status":"created,modified"}}}]}}'
                    
                rsp = requests.post(path, cookies=cookie, data=data, verify=False)
                print '>>>>>>>',rsp
                if type(response_data['vlan_id']) == list:
                    for ele in response_data['vlan_id']:
                        vlan_detail = ele.split('-') 
                        vlan = vlan_detail[0]
                        epg = vlan_detail[1]
                        bd = vlan_detail[2]
                        app = response_data['application']
                            
                        
                        # Deploy EPG API call
                        data_dict = {'tenant': response_data['tenant_name'], 'app': app, 'bd': bd,
                                    'mode': response_data['port_mode'], 'vlan': vlan,
                                    'vrf': 'Prod-VRF-1',
                                    'port': interface, 'leaf_id': leaf, 'epg': epg}
                        deploy_epg = self.Deploy_EPG(data_dict)
                        print '>>>>>>>----------', deploy_epg
                else:
                    vlan_detail = response_data['vlan_id'].split('-') 
                    vlan = vlan_detail[0]
                    epg = vlan_detail[1]
                    bd = vlan_detail[2]
                    # app = response_data['application']
                    app = 'new_app'
                        
                    
                    # Deploy EPG API call
                    data_dict = {'tenant': response_data['tenant_name'], 'app': app, 'bd': bd,
                                'mode': response_data['port_mode'], 'vlan': vlan,
                                'vrf': 'Prod-VRF-1',
                                'port': interface, 'leaf_id': leaf, 'epg': epg}
                    deploy_epg = self.Deploy_EPG(data_dict)
                    print '>>>>>>>----------', deploy_epg
                return rsp.json()

            else:
               return {'imdata':[{'error':{"attributes":{'text':"Validation failed : Alredy Have Policy "}}}]} 
        else:
            return {'imdata':[{'error':{"attributes":{'text':"Validation failed : Port is UP and Having description "}}}]}
    
    def port_provision_bulk(self, leaf, interface, response_data):
        # print " In Port Provision "
        print leaf, interface, response_data
        name = response_data['work_order_no']
        # dsc = response_data['action'] + \
        #     " for Work Order No. " + name.split('_')[0]
            
        # dsc = name.split('_')[0] +'_'+ response_data['Desc_int_{}'.format(interface.title())]
        if 'description' in response_data and len(response_data['description'])!=0:
            dsc = name.split('_')[0]+"_"+response_data['action']+"_"+response_data['description']
        else:
            dsc = name.split('_')[0]+"_"+response_data['action']
            
        policy_grp = response_data['policy_grp']
        leaf_node = leaf
        port = interface
        state = response_data['admin_state']
        port_status = self.leaf_status_details(leaf, interface)
        oper_status = self.oper_status(leaf, interface)
        policy_status = self.get_policy_get(leaf, interface)
        path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/hpaths-' + name + '.json'
        token = self.token
        # Enable / Disable
        cookie = {'APIC-cookie': token}
        # rsp = requests.post(path, cookies=cookie, data=data, verify=False)
        # Enable / Disable
        port_state = self.enable_disable_switch_port(port, leaf_node, state)
        print oper_status !="up"
        if oper_status !="up" :
            if response_data['action'] == "Reservation" and not policy_status:
                data = '{"infraHPathS":{"attributes":{"dn":"uni/infra/hpaths-' + name + '","name":"' + name + '","status":"created,modified","descr":"' + dsc + '","rn":"hpaths-' + name + \
                    '"},"children":[{"infraRsHPathAtt":{"attributes":{"tDn":"topology/pod-1/paths-' + leaf_node + '/pathep-[' + port + \
                    ']"},"children":[]}}],"children":[{"infraRsPathToAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accportgrp-' + \
                    policy_grp + '","status":"created,modified"}}}]}}'
                rsp = requests.post(path, cookies=cookie, data=data, verify=False)
                print rsp
                return rsp.json()
            elif response_data['action'] == "Provision" and not policy_status:
                desc_port = 'Eth1/'+interface.split('/')[1]
                print desc_port
                if name.split('_')[0] not in response_data['Desc_int_{}'.format(desc_port.title())].split("_")[0]:
                    dsc = name.split('_')[0] +'_'+ response_data['Desc_int_{}'.format(desc_port.title())]
                else:
                    dsc = response_data['Desc_int_{}'.format(desc_port.title())]
                # policy_gen = self.policy_group_create(response_data['policy_grp'], response_data['speed'])

                data = '{"infraHPathS":{"attributes":{"dn":"uni/infra/hpaths-' + name + '","name":"' + name + '","status":"created,modified","descr":"' + dsc + '","rn":"hpaths-' + name + \
                    '"},"children":[{"infraRsHPathAtt":{"attributes":{"tDn":"topology/pod-1/paths-' + leaf_node + '/pathep-[' + port + \
                    ']"},"children":[]}}],"children":[{"infraRsPathToAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accportgrp-' + \
                    policy_grp + '","status":"created,modified"}}}]}}'
                    
                rsp = requests.post(path, cookies=cookie, data=data, verify=False)
                print '>>>>>>>',rsp
                if type(response_data['vlan_id']) == list:
                    for ele in response_data['vlan_id']:
                        vlan_detail = ele.split('-') 
                        vlan = vlan_detail[0]
                        epg = vlan_detail[1]
                        bd = vlan_detail[2]
                        app = response_data['application']
                            
                        
                        # Deploy EPG API call
                        data_dict = {'tenant': response_data['tenant_name'], 'app': app, 'bd': bd,
                                    'mode': response_data['port_mode'], 'vlan': vlan,
                                    'vrf': 'Prod-VRF-1',
                                    'port': interface, 'leaf_id': leaf, 'epg': epg}
                        deploy_epg = self.Deploy_EPG(data_dict)
                        print '>>>>>>>----------', deploy_epg
                else:
                    vlan_detail = response_data['vlan_id'].split('-') 
                    vlan = vlan_detail[0]
                    epg = vlan_detail[1]
                    bd = vlan_detail[2]
                    app = response_data['application']
                    # app = 'new_app'
                        
                    
                    # Deploy EPG API call
                    data_dict = {'tenant': response_data['tenant_name'], 'app': app, 'bd': bd,
                                'mode': response_data['port_mode'], 'vlan': vlan,
                                'vrf': 'Prod-VRF-1',
                                'port': interface, 'leaf_id': leaf, 'epg': epg}
                    deploy_epg = self.Deploy_EPG(data_dict)
                    print '>>>>>>>----------', deploy_epg
                return rsp.json()

            else:
               return {'imdata':[{'error':{"attributes":{'text':"Validation failed : Alredy Have Policy "}}}]} 
        else:
            return {'imdata':[{'error':{"attributes":{'text':"Validation failed : Port is UP and Having description "}}}]}

    
    
    def list_policygroups(self):
        policy_grps = []
        path = 'http://' + self.ip_addr + '/api/node/class/infraAccPortGrp.json'
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.get(path, cookies=cookie, verify=False)
        # req = self.post(path,data)
        print r
        for elem in r.json()['imdata']:
            # print ">>>>>", elem
            for k, v in elem.iteritems():
                policy_grps.append(v['attributes']['name'])

        return policy_grps

    def list_PortChannel_policygroups(self):
        policy_grps = []
        path = 'http://' + self.ip_addr + '/api/node/class/infraAccBndlGrp.json'
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.get(path, cookies=cookie, verify=False)
        # req = self.post(path,data)
        print r
        for elem in r.json()['imdata']:
            for k, v in elem.iteritems():
                policy_grps.append(v['attributes']['name'])

        return policy_grps

   
    def deprovision_port_bulk(self, response_dict):
        print '>>>>>>', response_dict
        name = response_dict['config_name']
        # port = response_dict['physical_ports']
        # leaf_node = response_dict['leaf_id_deprovision']
        # # action = response_dict['admin_state']
        # action = "disable"
        path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/hpaths-' + name + '.json'
        data = '{"infraHPathS":{"attributes":{"dn":"uni/infra/hpaths-' + \
            name + '","status":"deleted"},"children":[]}}'
        print data, "???>>>>>>>>"
        token = self.token
        cookie = {'APIC-cookie': token}

        r = requests.post(path, data=data, cookies=cookie, verify=False)
        # port_state = self.enable_disable_switch_port(action)
        # print r
        return r.json()
   
    # Rollback Functions
    
    def rollback_state(self, name):
        token = self.token
        cookie = {'APIC-cookie': token}
        # name = "REQ0000020"
        op_list = []
        with open('mysite/ACI_Rolback_Dir/' + name + ".json", "r+") as json_file:
            data1 = json.load(json_file)
            for k, v in data1.iteritems():
                overridename = k
                leaf = v['leaf_node']
                port = v['port']
                policy = v['policy']
                desc = v['desc']

                path = 'http://' + self.ip_addr + \
                    '/api/node/mo/uni/infra/hpaths-' + overridename + '.json'

                data = '{"infraHPathS":{"attributes":{"dn":"uni/infra/hpaths-' + overridename + '","name":"' + overridename + '","status":"created,modified","descr":"' + desc + '","rn":"hpaths-' + overridename + \
                    '"},"children":[{"infraRsHPathAtt":{"attributes":{"tDn":"topology/pod-1/paths-' + leaf + '/pathep-[' + port + \
                    ']"},"children":[]}}],"children":[{"infraRsPathToAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accportgrp-' + \
                    policy + '","status":"created,modified"}}}]}}'

                r = requests.post(path, cookies=cookie,
                                  data=data, verify=False)
                # req = self.post(path,data)
                print r.json()
                if len(r.json()['imdata']) == 0:
                    op_list.append((True, leaf, port))
                else:
                    op_list.append((False, leaf, port))
        return op_list
    
    # Port-Channel Functions
    
    def PC_VPC_port_provision(self,leaf, port, response_data):
        
        profile_name = response_data['profile_grp']
        
        vpc = response_data['pc_policy_grp']
        
        
        phy_port = port.replace(' ', '')
        
        port1 = port.split('/')[1]
        
        name = profile_name + '_' + phy_port.replace('/', '_')
        
        description = profile_name + '_' + phy_port.replace('/', '_')
        
        print profile_name,vpc,name,description
        
        path = ' http://'+self.ip_addr+'/api/node/mo/uni/infra/accportprof-'+profile_name+'.json'
        
        data = '{"infraAccPortP":{"attributes":{"dn":"uni/infra/accportprof-'+profile_name+'","name":' \
        '"'+profile_name+'","descr":"ss","rn":"accportprof-'+profile_name+'","status":"created,modified"}' \
        ',"children":[{"infraHPortS":{"attributes":{"dn":"uni/infra/accportprof-'+profile_name+'' \
        '/hports-'+name+'-typ-range","name":"'+name+'","descr":"ttt","rn":"hports-'+name+'-typ-range",' \
        '"status":"created,modified"},"children":[{"infraPortBlk":{"attributes":{"dn":"uni/infra/' \
        'accportprof-'+profile_name+'/hports-'+name+'-typ-range/portblk-block3","fromPort":"'+port1+'","toPort":"'+port1+'",' \
        '"name":"block3","rn":"portblk-block3","status":"created,modified"},"children":[]}},' \
        '{"infraRsAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accbundle-'+vpc+'","status":' \
        '"created,modified"},"children":[]}}]}}]}}'
        

        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.post(path, data=data, cookies=cookie, verify=False)
        print r.json(),"group"
        
        #     path = ' http://198.18.133.200/api/node/mo/uni/infra/accportprof-'+policy_name+'.json'
            
        # data = '{"infraAccPortP":{"attributes":{"dn":"uni/infra/accportprof-'+policy_name+'","name":' \
        #     '"'+policy_name+'","descr":"ss","rn":"accportprof-'+policy_name+'","status":"created,modified"}' \
        #     ',"children":[{"infraHPortS":{"attributes":{"dn":"uni/infra/accportprof-'+policy_name+'' \
        #     '/hports-'+name+'-typ-range","name":"'+name+'","descr":"ttt","rn":"hports-'+name+'-typ-range",' \
        #     '"status":"created,modified"},"children":[{"infraPortBlk":{"attributes":{"dn":"uni/infra/' \
        #     'accportprof-'+policy_name+'/hports-'+name+'-typ-range/portblk-block2","fromPort":"'+fromPort+'","toPort":"'+toPort+'",' \
        #     '"name":"block2","rn":"portblk-block2","status":"created,modified"},"children":[]}},' \
        #     '{"infraRsAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accbundle-'+vpc+'","status":' \
        #     '"created,modified"},"children":[]}}]}}]}}'

        # token = get_auth_token()
        # cookie = {'APIC-cookie': token}
        # r = requests.post(path, data=data, cookies=cookie, verify=False)
        # print r.json(),"group"
        # path = ' http://198.18.133.200/api/node/mo/uni/infra/funcprof/accbundle-'+vpc+'.json'

        # data='{"infraAccBndlGrp":{"attributes":{"dn":"uni/infra/funcprof/accbundle-'+vpc+'","lagT":"node","name":"'+vpc+'","descr":"vpc",' \
        #     '"rn":"accbundle-'+vpc+'","status":"created,modifed"},"children":[]}}]}}'
        # token = get_auth_token()
        # cookie = {'APIC-cookie': token}
        # r = requests.post(path, data=data, cookies=cookie, verify=False)
        # print r.json(),"policy"
        
        # path = ' http://198.18.133.200/api/node/mo/uni/infra/funcprof/accbundle-'+vpc+'.json'

        # data='{"infraAccBndlGrp":{"attributes":{"dn":"uni/infra/funcprof/accbundle-'+vpc+'","lagT":"node","name":"'+vpc+'","descr":"vpc",' \
        #     '"rn":"accbundle-'+vpc+'","status":"created,modifed"},"children":[]}}]}}'
        
        # token = self.token
        # cookie = {'APIC-cookie': token}
        # r = requests.post(path, data=data, cookies=cookie, verify=False)
        return r.json()
    
    def portchannel_group_create2(self, pc_group_name, PC_policy_name):
        path = ' http://' + self.ip_addr + '/api/node/mo/uni/infra.json'
        data = '{"infraAccBndlGrp":{"attributes":{"dn":"uni/infra/funcprof/accbundle-' + pc_group_name + '",' '"name":"' + pc_group_name + '","descr":"testing port channel","rn":"accbundle-' + pc_group_name + '",' '"status":"created"},"children":[{"infraRsLacpPol":{"attributes":{"tnLacpLagPolName":"' + PC_policy_name + '",''"status":"created,modified"},"children":[]}}]}}'
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.post(path, data=data, cookies=cookie, verify=False)
        return r.json()

    def portchannel_policy_create(self, policy_name, PC_mode, desc):
        path = 'http://' + self.ip_addr + \
            '/api/node/mo/uni/infra/lacplagp-' + policy_name + '.json'
        data = '{"lacpLagPol":{"attributes":{"dn":"uni/infra/lacplagp-' + policy_name + '","name":"' + policy_name + '",' \
                                                                                                                     '"descr":"' + desc + ' ","mode":"' + PC_mode + '","rn":"lacplagp-' + \
            policy_name + '","status":"created"},"children":[]}}'
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.post(path, data=data, cookies=cookie, verify=False)
        return r.json()

    def portchannel_group_assign(self, leaf, pc_policy_grp, port,profile_name, response_data):
        
        op_dict = {'provision_status':'', 'Error': ''}
        
        Provision_flag = False
        
        port_status = self.leaf_status_details(leaf, port)
        oper_status = self.oper_status(leaf, port)
        policy_status = self.get_policy_get(leaf, port)
        
        # phy_port = port.replace(' ', '')
        
        # port1 = port.split('/')[1]
        
        # name = profile_name + '_' + phy_port.replace('/', '_')
        
        description = profile_name + '_' + port.replace('/', '_')
        if oper_status !="up" :
            if response_data['action'] == "Provision":
                port1 = port.split('/')
                path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra.json'
                data = '{"infraInfra":{"attributes":{"dn":"uni/infra","status":"modified"},"children":[{"infraAccPortP":{"attributes":' \
                    '{"dn":"uni/infra/accportprof-'+profile_name+'","name":"'+profile_name+'",' \
                        '"descr":"'+description+'","status":"created,modified"},"children":[' \
                        '{"infraHPortS":{"attributes":{"dn":"uni/infra/accportprof-'+profile_name+'/hports-leaf-' + leaf + '_1-ports-' + \
                    port1[1] + '-typ-range","name":"leaf-' + leaf + '_1-ports-' + port1[1] + '","type":"range",' \
                    '"status":"created,modified"},"children":[{"infraPortBlk":{"attributes":' \
                        '{"dn":"uni/infra/accportprof-'+profile_name+'/hports-leaf-' + leaf + '_1-ports-' + \
                    port1[1] + '-typ-range/portblk-block1","fromPort":"' + port1[1] + '","toPort":"' + port1[
                        1] + '","name":"block1",' \
                        '"status":"created,modified","rn":"portblk-block1"},"children":[]}},' \
                        '{"infraRsAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accbundle-' + pc_policy_grp + '","status":"created,modified"},' \
                        '"children":[]}}]}}]}},{"infraNodeP":{"attributes":{"dn":"uni/infra/nprof-leaf-' + leaf + '_Profile1","name":"leaf-' + leaf + '_Profile1",' \
                        '"descr":"'+description+'","status":"created,modified"},"children":[{"infraLeafS":' \
                        '{"attributes":{"dn":"uni/infra/nprof-leaf-' + leaf + '_Profile1/leaves-leaf-' + leaf + '_Profile1_selector_' + leaf + '-typ-range",' \
                        '"name":"leaf-' + leaf + '_Profile1_selector_' + leaf + '","type":"range","status":"created,modified"},"children":[{"infraNodeBlk":' \
                        '{"attributes":{"dn":"uni/infra/nprof-leaf-' + leaf + '_Profile1/leaves-leaf-' + leaf + '_Profile1_selector_' + leaf + '-typ-range/nodeblk-single0",' \
                        '"status":"created,modified","from_":"' + leaf + '","to_":"' + leaf + '","name":"single0","rn":"nodeblk-single0"},"children":[]}}]}},' \
                        '{"infraRsAccPortP":{"attributes":{"tDn":"uni/infra/accportprof-'+profile_name+'","status":"created,modified"},' \
                        '"children":[]}}]}}]}}'
                token = self.token
                cookie = {'APIC-cookie': token}
                post_data = requests.post(path, data=data, cookies=cookie, verify=False)
                pc_op = post_data.json()
                # print pc_op
                if len(pc_op['imdata']) == 0:
                    name = response_data['work_order_no']
                    # policy_grp = response_data['policy_grp']
                    policy_grp = ""
                    leaf_node = leaf
                    port2 = 'Eth 1/'+ port.split('/')[1]
                    if name.split('_')[0] not in response_data['Desc_int_{}'.format(port2.title())].split("_")[0]:
                        dsc = name.split('_')[0] +'_'+response_data['action']+'_'+ response_data['Desc_int_{}'.format(port2.title())]
                    else:
                        dsc = name.split('_')[0] +'_'+response_data['action']
                    state = response_data['admin_state']
                    
                    
                    provision_path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/hpaths-' + name + '.json'
                    
                    token = self.token
                    # Enable / Disable
                    cookie = {'APIC-cookie': token}
                    # print response_data['action'] == "Provision" and  port_status.has_key('descr')
                    
                            
                    provision_data = '{"infraHPathS":{"attributes":{"dn":"uni/infra/hpaths-' + name + '","name":"' + name + '","status":"created,modified","descr":"' + dsc + '","rn":"hpaths-' + name + \
                        '"},"children":[{"infraRsHPathAtt":{"attributes":{"tDn":"topology/pod-1/paths-' + leaf_node + '/pathep-[' + port + \
                        ']"},"children":[]}}],"children":[{"infraRsPathToAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accportgrp-' + \
                        policy_grp + '","status":"created,modified"}}}]}}'
                        
                    rsp = requests.post(provision_path, cookies=cookie, data=provision_data, verify=False)
                    
                    int_prov_op = rsp.json()
                            
                    if len(int_prov_op['imdata']) == 0:
                        if type(response_data['vlan_id']) == list:
                            for ele in response_data['vlan_id']:
                                vlan_detail = ele.split('-') 
                                vlan = vlan_detail[0]
                                epg = vlan_detail[1]
                                bd = vlan_detail[2]
                                app = response_data['application']
                                    
                                
                                # Deploy EPG API call
                                data_dict = {'tenant': response_data['tenant_name'], 'app': app, 'bd': bd,
                                            'mode': response_data['port_mode'], 'vlan': vlan,
                                            'vrf': 'Prod-VRF-1',
                                            'port': port, 'leaf_id': leaf, 'epg': epg}
                                deploy_epg = self.Deploy_EPG(data_dict)
                                print '>>>>>>>----------', deploy_epg
                                op_dict['provision_status'] = True
                                op_dict['Error'] = 'Interface Provisioned Successfully'
                        else:
                            vlan_detail = response_data['vlan_id'].split('-') 
                            vlan = vlan_detail[0]
                            epg = vlan_detail[1]
                            bd = vlan_detail[2]
                            app = response_data['application']
                            
                            print vlan_detail,vlan,epg,bd,app
                                
                            
                            # Deploy EPG API call
                            data_dict = {'tenant': response_data['tenant_name'], 'app': app, 'bd': bd,
                                        'mode': response_data['port_mode'], 'vlan': vlan,
                                        'vrf': 'Prod-VRF-1',
                                        'port': port, 'leaf_id': leaf, 'epg': epg}
                            deploy_epg = self.Deploy_EPG(data_dict)
                            print '>>>>>>>----------', deploy_epg
                            op_dict['provision_status'] = True
                            op_dict['Error'] = 'Interface Provisioned Successfully'

                   
                else:
                    op_dict['provision_status'] = False
                    op_dict['Error'] = 'Overlapping Interface'
                   
            else:
                op_dict['provision_status'] = False
                op_dict['Error'] = 'Alredy Have Description'
                        
        else:
            op_dict['provision_status'] = False
            op_dict['Error'] = 'Operation State is UP'
                # return pc_op
        return op_dict
    
    def get_interface_profile(self):
        profile_list = []
        path = 'http://'+self.ip_addr+'/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=infraAccPortP&query-target-filter=not(wcard(infraAccPortP.dn,"__ui_"))&target-subtree-class=infraFexP,infraHPortS,infraPortBlk,infraSubPortBlk&query-target=subtree'
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.get(path, cookies=cookie, verify=False)
        data = r.json()
        for elem in data['imdata']:
            if "infraAccPortP" in elem:
                profile_list.append(elem["infraAccPortP"]["attributes"]["name"])
        
        return profile_list

    def leafprofile_details(self):
        path = 'http://'+self.ip_addr+'/api/node/mo/uni/infra.json?query-target=subtree&target-subtree-class=infraAccPortP&query-target-filter=not(wcard(infraAccPortP.dn,"__ui_"))&target-subtree-class=infraFexP,infraHPortS,infraPortBlk,infraSubPortBlk&query-target=subtree'
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.get(path, cookies=cookie, verify=False)
        data = r.json()
        for elem in data['imdata']:
            if "infraAccPortP" in elem:
                leafprofile = elem["infraAccPortP"]["attributes"]["name"]
                path = 'http://'+self.ip_addr+'/api/node/mo/uni/infra/accportprof-'+leafprofile+'.json?query-target=subtree&target-subtree-class=infraHPortS&query-target-filter=not(wcard(infraHPortS.dn,"__ui_"))&target-subtree-class=infraPortBlk,infraSubPortBlk,infraRsAccBaseGrp&query-target=subtree'
                token = self.token
                cookie = {'APIC-cookie': token}
                r = requests.get(path, cookies=cookie, verify=False)
                data = r.json()
                lst = []
                data1 = {}
                for elem in data['imdata']:
                    if "infraHPortS" in  elem:
                        dn =elem["infraHPortS"]["attributes"]["dn"]
                        path = 'http://'+self.ip_addr+'/api/node/mo/'+dn+'.json?rsp-subtree-include=full-deployment&target-path=HPortSToEthIf'
                        token = self.token
                        cookie = {'APIC-cookie': token}
                        r = requests.get(path, cookies=cookie, verify=False)
                        data = r.json()
                        nodeid = []
                        for elem in data['imdata']:
                            for child in elem["infraHPortS"]["children"]:
                                nodeid.append(child["pconsNodeDeployCtx"]["attributes"]["nodeId"])

                        data1["node"]=nodeid

                    if "infraRsAccBaseGrp" in elem:
                        data1["tdn"] =elem["infraRsAccBaseGrp"]["attributes"]["tDn"]
                    if "infraPortBlk" in elem:
                        data1["name"]= elem["infraPortBlk"]["attributes"]["name"]
                        data1["fromPort"]= elem["infraPortBlk"]["attributes"]["fromPort"]
                        data1["toPort"]= elem["infraPortBlk"]["attributes"]["toPort"]
                print data1

    # De-privision Functions
    
    def deprovision_port(self, name, tenant, port, leaf_node,app, epg):
        
        port_status = self.leaf_status_details(leaf_node, port)
        oper_status = self.oper_status(leaf_node, port)
        policy_status = self.get_policy_get(leaf_node, port)
        if oper_status !="up" and  port_status.has_key('descr') and name.split('_')[0] in port_status.get('descr'):
            # action = response_dict['admin_state']
            action = "disable"
            path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/hpaths-' + name + '.json'
            data = '{"infraHPathS":{"attributes":{"dn":"uni/infra/hpaths-' + name + '","status":"deleted"},"children":[]}}'
            token = self.token
            cookie = {'APIC-cookie': token}
            r = requests.post(path, data=data, cookies=cookie, verify=False)
            port_state = self.enable_disable_switch_port(port, leaf_node, action)
                
            # if tenant:
            #     path1 = 'http://198.18.133.200/api/node/mo/uni/tn-'+tenant+'/ap-'+app+'/epg-'+epg+'/rspathAtt-[topology/pod-1/paths-'+leaf_node+'/pathep-['+port+']].json'
                
            #     data1 = '{"fvRsPathAtt":{"attributes":{"dn":"uni/tn-'+tenant+'/ap-'+app+'/epg-'+epg+'/rspathAtt-[topology/pod-1/paths-'+leaf_node+'/pathep-['+port+']]","status":"deleted"},"children":[]}}'
                
            #     cookie1 = {'APIC-cookie': token}
            #     r1 = requests.post(path, data=data, cookies=cookie, verify=False)
                
            # print r
            return r.json()
        else:
            return {'imdata':[{'error':{"attributes":{'text':"Validation failed : Port is UP and Having description "}}}]}

    def deprovision_pc_group(self, leaf, port):
        port1 = port.split('/')
        path = 'http://' + self.ip_addr + '/api/node/mo/uni/infra/accportprof-NS_leaf102_PC/' \
                                                                                              'hports-leaf-' + leaf + '_1-ports-' + \
               port1[1] + '-typ-range.json'

        data = '{"infraHPortS": {"attributes": {"dn":"uni/infra/accportprof-NS_leaf102_PC/' \
                                                                                            'hports-leaf-' + leaf + '_1-ports-' + \
               port1[1] + '-typ-range","status": "deleted"}, "children": []}}'

        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.post(path, data=data, cookies=cookie, verify=False)
        return r.json()
  
    def epg_close(self, tenant, leaf, port , app, epg):
        print 'here in epg_close ###########################',tenant,app, epg
        if tenant:
            print "##################"
            path = 'http://'+self.ip_addr+'/api/node/mo/uni/tn-'+tenant+'/ap-'+app+'/epg-'+epg+'/rspathAtt-[topology/pod-1/paths-' + \
                leaf + '/pathep-[' + port + ']].json'
            data = '{"fvRsPathAtt":{"attributes":{"dn":"uni/tn-'+tenant+'/ap-'+app+'/epg-'+epg+'/rspathAtt-[topology/pod-1/paths-' + \
                leaf + '/pathep-[' + port + \
                ']]","status":"deleted"},"children":[]}}'
        token = self.token
        cookie = {'APIC-cookie': token}
        resp = requests.post(path, cookies=cookie, data=data, verify=False)
        data = resp.json()
        print 'here in epg'
        return data, "Here"

    def port_channe_group(self):
        list_por_group = []
        path = 'http://' + self.ip_addr + '/api/node/class/lacpLagPol.json'
        token = self.token
        cookie = {'APIC-cookie': token}
        resp = requests.get(path, cookies=cookie, verify=False)
        data = resp.json()
        # print data
        for elem in data["imdata"]:
            a = elem['lacpLagPol']['attributes']['name']
            list_por_group.append(a)
        return list_por_group

    def GET_pg_pc(self):
        path = 'http://198.18.133.200/api/node/mo/topology/pod-1/node-102/sys/phys-[eth1/3].json?&rsp-subtree-include=relations'
        token = self.token
        cookie = {'APIC-cookie': token}
        r = requests.get(path, cookies=cookie, verify=False)
        data = r.json()
        for elem in data['imdata']:
            if 'pcAggrIf' in elem:
                return elem['pcAggrIf']['attributes']['name']

    def deprovision_tenant_info(self):
        static_port_dict = {}
        tenant_list = self.get_all_tenant()
        for tenant in tenant_list: 
            path = 'http://'+self.ip_addr+'/api/node/mo/uni/tn-'+tenant+'.json?query-target=subtree&target-subtree-class=fvAp&target-subtree-class=tagAliasInst&query-target=subtree&&page=0&page-size=40'
            token = self.token
            cookie = {'APIC-cookie': token}
            r = requests.get(path, cookies=cookie, verify=False)
            data = r.json()
            for elem in data['imdata']:
                dn= elem["fvAp"]["attributes"]["dn"]
                path = 'http://'+self.ip_addr+'/api/node/mo/'+dn+'.json?query-target=subtree&target-subtree-class=fvAEPg&query-target-filter=eq(fvAEPg.isAttrBasedEPg,"false")&query-target=subtree&target-subtree-class=fvRsProv,fvRsCons,tagAliasInst&&page=0&page-size=40'
                token = self.token
                cookie = {'APIC-cookie': token}
                r = requests.get(path, cookies=cookie, verify=False)
                data = r.json()
                for elem in data['imdata']:
                    dn = elem["fvAEPg"]["attributes"]["dn"]
                    path = 'http://'+self.ip_addr+'/api/node/mo/'+dn+'.json?query-target=children&target-subtree-class=fvRsPathAtt&query-target-filter=not(wcard(fvRsPathAtt.dn,"__ui_"))'
                    token = self.token
                    cookie = {'APIC-cookie': token}
                    r = requests.get(path, cookies=cookie, verify=False)
                    data = r.json()
                    # static_port_dict = {}
                    for elem in data['imdata']:
                        data_dict = {}
                        dn = elem["fvRsPathAtt"]["attributes"]["dn"]
                        print dn
                        m1 = re.search(r'uni/tn-(\S.+)/ap-(\S.+)/epg-(\S.+)/rspathAtt\S.+paths-(\d+).+.eth(\d\S\d+)', dn)
                        if m1:
                            tenant =  m1.group(1)
                            ap =  m1.group(2)
                            epg =  m1.group(3)
                            paths =  m1.group(4)
                            eth =  m1.group(5)
                            data_dict['interface'] = 'eth'+eth 
                            data_dict['leaf'] = paths 
                            data_dict['epg'] = epg 
                            data_dict['app'] = ap 
                            data_dict['tenant'] = tenant
                            
                        vlan=elem["fvRsPathAtt"]["attributes"]["encap"]
                        data_dict['vlan'] = vlan
                        static_port_dict['eth'+eth] = data_dict
                        # data_dict['vlan'] = vlan        
        return static_port_dict
    
    def deprovision_delete_switchport(self, interface, leaf):
        leaf_data = self.get_override_name('102','eth1/1')
        print leaf_data
        all_tenant_data = self.deprovision_tenant_info()
        for k, v in all_tenant_data.iteritems():
            if k == interface and v['leaf'] == leaf:
                print '>>>>>>',v 
        
    
def Display_Inputs_for_policy(response_dict):
    return_list = []
    # for key, val in response_dict.iteritems():
    #     if key == "tenant_new":
    if response_dict.has_key('tenant_new'):
        return_list.append(
            "<strong> Tenant : </strong> <span style=color:#5e8ff7;'>" + str(response_dict['tenant_new']) + "</span>")
    if response_dict.has_key('vrf_new'):
        return_list.append(
            "<strong> VRF : </strong> <span style=color:#5e8ff7;'>" + str(response_dict['vrf_new']) + "</span>")
    if response_dict.has_key('bd_new'):
        return_list.append(
            "<strong> Bridge Domain : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['bd_new']) + "</span>")
    if response_dict.has_key('app_name_new'):
        return_list.append(
            "<strong> Application Name : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['app_name_new']) + "</span>")
    if response_dict.has_key('epg_name_new'):
        return_list.append(
            "<strong> EPG : </strong> <span style=color:#5e8ff7;'>" + str(response_dict['epg_name_new']) + "</span>")
    if response_dict.has_key('policy_name'):
        return_list.append(
            "<strong> Policy Name : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['policy_name']) + "</span>")
        
    if response_dict.has_key('speed'):
        return_list.append(
            "<strong> Speed : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['speed']) + "</span>")

    return return_list


def Display_Inputs_for_PCpolicy(response_dict):
    return_list = []
    print response_dict, '???????'
    if response_dict.has_key('PC_group_name'):
        return_list.append(
            "<strong> PC Group Name : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['PC_group_name']) + "</span>")

    if response_dict.has_key('port_channel_policy'):
        return_list.append(
            "<strong> PC Policy Name : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['port_channel_policy']) + "</span>")

    if response_dict.has_key('existing_PC_policy'):
        return_list.append(
            "<strong> PC Policy Name : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['existing_PC_policy']) + "</span>")

    if response_dict.has_key('port_channel_mode'):
        return_list.append(
            "<strong> PC Mode : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['port_channel_mode']) + "</span>")

    if response_dict.has_key('description'):
        return_list.append(
            "<strong> Description : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['description']) + "</span>")
    return return_list

# {u'provision_reason': u'new_server', u'work_order_no': u'REQ00000011', u'server_name': u'S-01-01-01',
#  u'physical_port_101': [u'eth 1/7', u'eth 1/8'], u'temporary_port_reservation': u'no', u'rack_number': u'R-01-01',
#  u'apic_services': u'Port Configuration', u'action': u'Reservation', u'admin_state': u'disable',
#  u'rack_row_number': u'01', u'policy_grp': u'PG_PHY', u'leaf_id': [u'101']}


def Display_Inputs_for_port_resrv(response_dict):
    apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
    get_data = apic_auth.leafprofile_details()
    print response_dict
    return_list = []
    # for key, val in response_dict.iteritems():
    # if key == "provision_reason":
    
    leaf_list = apic_auth.get_leaf_list()
    print response_dict
    if response_dict.has_key('work_order_no'):
        return_list.append(
            "<strong> Work Order Number : </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + str(
                response_dict['work_order_no']) + "</span>")
    if response_dict.has_key('port_type'):
        return_list.append("<strong> Port Type : </strong> <span style=color:#5e8ff7;'>" + str(
            response_dict['port_type']) + "</span>")
    if response_dict.has_key('provision_reason'):
        return_list.append(
            "<strong> Provision Reason : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['provision_reason']) + "</span>")
    if response_dict.has_key('rack_row_number'):
        return_list.append(
            "<strong> Row Rack Number : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['rack_row_number']) + "</span>")
    if response_dict.has_key('rack_number'):
        return_list.append(
            "<strong> Rack Number : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['rack_number']) + "</span>")
    if response_dict.has_key('leaf_id'):
        return_list.append("<strong> Leaf Switches : </strong> <span style=color:#5e8ff7;'>" + ", ".join(
            response_dict['leaf_id']) + "</span>")
     
    for leaf in leaf_list:
        print 'physical_port_{}'.format(leaf['name'])
        if 'physical_port_{}'.format(leaf['name']) in response_dict:
            return_list.append(
            "<strong> Leaf "+leaf['name']+" Physical Port : </strong> <span style=color:#5e8ff7;'>" + ", ".join(
                response_dict['physical_port_{}'.format(leaf['name'])]).title() + "</span>")
    if response_dict.has_key('description'):
        if response_dict['description']:
            return_list.append(
                "<strong> Description : </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + str(response_dict['work_order_no']) +'_'+response_dict['description'] + "</span>")
        else:
            return_list.append(
                    "<strong> Description : </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + str(response_dict['work_order_no']) +"</span>")
    if response_dict.has_key('server_name'):
        return_list.append(
            "<strong> Server Name : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['server_name']) + "</span>")
    if response_dict.has_key('policy_grp') and response_dict.get('policy_grp')!= 'null':
        return_list.append(
            "<strong> Policy Group : </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + str(
                response_dict['policy_grp']) + "</span>")
    if response_dict.has_key('temporary_port_reservation'):
        return_list.append(
            "<strong> Temporary Port Reservation : </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + str(
                response_dict['temporary_port_reservation']) + "</span>")
    
    if response_dict.has_key('admin_state'):
        return_list.append(
            "<strong> Admin Status : </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + str(
                response_dict['admin_state']) + "</span>")

        return return_list

def Display_Inputs_for_rollback(response_dict):
    return_list = []
    if response_dict.has_key('overridename'):
        return_list.append("<strong> Work Order Number : </strong> <span style=color:#5e8ff7;'>" + str(
            response_dict['overridename']) + "</span>")

    if response_dict.has_key('desc'):
        return_list.append(
            "<strong> Description: </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + str(
                response_dict['desc']) + "</span>")

    if response_dict.has_key('leaf'):
        return_list.append(
            "<strong> Leaf Switches : </strong> <span style=color:#5e8ff7;'>" + response_dict['leaf'] + "</span>")

    if response_dict.has_key('port'):
        return_list.append(
            "<strong> Physical Port : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['port']) + "</span>")

    if response_dict.has_key('policy'):
        return_list.append(
            "<strong> Policy : </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + str(
                response_dict['policy']) + "</span>")

        return return_list

def Display_Inputs_for_port_provision(response_dict):
    return_list = []
    # for key, val in response_dict.iteritems():
    # if key == "provision_reason":
    print response_dict
    apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
    leaf_list = apic_auth.get_leaf_list()
    if response_dict.has_key('work_order_no'):
        return_list.append(
            "<strong> Work Order Number : </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + str(
                response_dict['work_order_no']) + "</span>")
    
    if response_dict.has_key('tenant_name'):
        return_list.append(
            "<strong> Tenant Name : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['tenant_name']).title() + "</span>")
    
    if response_dict.has_key('leaf_id'):
        return_list.append(
            "<strong> Leaf Switches : </strong> <span style=color:#5e8ff7;'>" + ", ".join(
                response_dict['leaf_id']).title() + "</span>")
    for leaf in leaf_list:
        print 'physical_port_{}'.format(leaf['name'])
        if 'physical_port_{}'.format(leaf['name']) in response_dict:
            return_list.append(
                "<strong> Leaf {} Physical Port : </strong> <span style=color:#5e8ff7;'>".format(leaf['name']) + ", ".join(response_dict['physical_port_{}'.format(leaf['name'])]).title() + "</span>")
            for port in response_dict['physical_port_{}'.format(leaf['name'])]:
                port_status = apic_auth.leaf_status_details(leaf['name'],port )
                operation_state = apic_auth.oper_status(leaf['name'],port )
                return_list.append("<strong> {} </strong> <span style=color:#457b9d;'>".format(port.title())+ "</span>")
                name = str(response_dict['work_order_no'])
                if name not in response_dict['Desc_int_{}'.format(port.title())].split("_")[0]:
                    dsc = name +'_'+ response_dict['Desc_int_{}'.format(port.title())]
                else:
                    dsc = response_dict['Desc_int_{}'.format(port.title())]
                return_list.append(
                "<strong style=margin-left:40px;> Description : </strong> <span style=color:#5e8ff7;'>".format(port) + " "+dsc + "</span>")
            
                return_list.append(
                "<strong style=margin-left:40px;> Operational State : </strong> <span style=color:#5e8ff7;'>".format(port) + " "+operation_state.title() + "</span>")
                return_list.append("<hr>")
    
    if response_dict.has_key('description'):
        
        return_list.append(
            "<strong> Description : </strong> <span style=text-transform:capitalize;color:#5e8ff7;'>" + +'_'+ response_dict['description']  + "</span>")
    if 'port_mode' in response_dict:
        if response_dict['port_mode'] == 'regular':
            port_mode = 'Trunk'
            return_list.append(
                "<strong> Port Mode : </strong> <span style=color:#5e8ff7;'>" + port_mode + "</span>")
        else:
            port_mode = 'Access'
            return_list.append(
                "<strong> Port Mode : </strong> <span style=color:#5e8ff7;'>" + port_mode + "</span>")
    if 'vlan_id' in response_dict:
        if type(response_dict['vlan_id']) == list:
            vlan = []
            for ele in response_dict['vlan_id']:
                vlan_data = ele.split('-')[0].title()
                vlan.append(vlan_data)
            return_list.append(
                "<strong> Vlan ID : </strong> <span style=color:#5e8ff7;'>" + ", ".join(vlan)  + "</span>")
        else:
            return_list.append(
                "<strong> Vlan ID : </strong> <span style=color:#5e8ff7;'>" + str(
                    response_dict['vlan_id'].split('-')[0]).title() + "</span>")
    if 'speed' in response_dict:
        return_list.append(
            "<strong> Speed : </strong> <span style=color:#5e8ff7;'>" + str(response_dict['speed']).title() + "</span>")
    if 'policy_grp' in response_dict:
        return_list.append(
            "<strong> Policy Group : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['policy_grp']) + "</span>")
    if 'admin_state' in response_dict:
        return_list.append(
            "<strong> Admin Status : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['admin_state']).title() + "</span>")
    if 'action_service_now' in response_dict:
        return_list.append(
            "<strong> Action From Service Now : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['action_service_now']).title() + "</span>")
    if 'action_service_now' in response_dict and 'close_notes' in response_dict:
        return_list.append(
            "<strong> Close Notes : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['close_notes']).title() + "</span>")

    return return_list

def Display_Inputs_for_deprovision(response_dict):
    print response_dict, ">>>>>>>>>>>>>>>>>>>>>>>>///////////"
    return_list = []
    apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
    leaf_list = apic_auth.get_leaf_list()
    if response_dict.has_key('work_order_no'):
        return_list.append(
            "<strong> Work Order Number : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['work_order_no']).upper() + "</span>")
    if 'new_work_order_no' in response_dict:
        return_list.append(
            "<strong> New Work Order No. : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['new_work_order_no']).upper() + "</span>")
    if response_dict.has_key('leaf_id'):
        return_list.append(
            "<strong> Leaf Switches : </strong> <span style=color:#5e8ff7;'>" + ", ".join(
                response_dict['leaf_id']).title() + "</span>")
    for leaf in leaf_list:
        print 'physical_port_{}'.format(leaf['name'])
        if 'physical_port_{}'.format(leaf['name']) in response_dict:
            return_list.append(
                "<strong> Leaf {} Physical Port : </strong> <span style=color:#5e8ff7;'>".format(leaf['name']) + ", ".join(response_dict['physical_port_{}'.format(leaf['name'])]).title() + "</span>")
            
            for port in response_dict['physical_port_{}'.format(leaf['name'])]:
                port_status = apic_auth.leaf_status_details(leaf['name'],port )
                operation_state = apic_auth.oper_status(leaf['name'],port )
                return_list.append("<strong> {} </strong> <span style=color:#457b9d;'>".format(port.title())+ "</span>")

                return_list.append(
                "<strong style=margin-left:40px;> Description : </strong> <span style=color:#5e8ff7;'>".format(port) + " "+port_status['descr'] + "</span>")
            
                return_list.append(
                "<strong style=margin-left:40px;> Operational State : </strong> <span style=color:#5e8ff7; '>".format(port) + " "+operation_state.title() + "</span>")
                return_list.append("<hr>")
            
    # if 'physical_port_102' in response_dict:
    #     return_list.append(
    #         "<strong> Leaf 102 Physical Port : </strong> <span style=color:#5e8ff7;'>" + ", ".join(
    #             response_dict['physical_port_102']).title() + "</span>")  
    if 'admin_state' in response_dict:
        return_list.append(
            "<strong> Admin Status : </strong> <span style=color:#5e8ff7;'>" + str(
                response_dict['admin_state']).title() + "</span>")

    return return_list

def Display_Inputs_for_port_bulk(response_dict):
    return_list = []
    # for key, val in response_dict.iteritems():
    # if key == "provision_reason":

    return_list.append(
        "<strong> Work Order Number : </strong> <span style=color:#5e8ff7;'>" + str(
            response_dict['work_order_no']) + "</span>")
    return_list.append(
        "<strong> Tenant Name : </strong> <span style=color:#5e8ff7;'>" + str(response_dict['tenant_name']) + "</span>")
    return_list.append(
        "<strong> Leaf Switches : </strong> <span style=color:#5e8ff7;'>" + ", ".join(
            response_dict['leaf_id']) + "</span>")
    if 'physical_port_101' in response_dict:
        return_list.append(
            "<strong> Leaf 101 Physical Port : </strong> <span style=color:#5e8ff7;'>" + ", ".join(
                response_dict['physical_port_101']) + "</span>")
    if 'physical_port_102' in response_dict:
        return_list.append(
            "<strong> Leaf 101 Physical Port : </strong> <span style=color:#5e8ff7;'>" + ", ".join(
                response_dict['physical_port_102']) + "</span>")
    return_list.append(
        "<strong> Port Mode : </strong> <span style=color:#5e8ff7;'>" + str(response_dict['port_mode']) + "</span>")
    return_list.append(
        "<strong> Vlan ID : </strong> <span style=color:#5e8ff7;'>" + str(response_dict['vlan_id']) + "</span>")
    return_list.append(
        "<strong> Speed : </strong> <span style=color:#5e8ff7;'>" + str(response_dict['speed']) + "</span>")
    return_list.append(
        "<strong> Policy Group : </strong> <span style=color:#5e8ff7;'>" + str(response_dict['policy_grp']) + "</span>")
    return_list.append(
        "<strong> Admin Status : </strong> <span style=color:#5e8ff7;'>" + str(
            response_dict['admin_state']) + "</span>")

    return return_list
