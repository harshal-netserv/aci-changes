from __future__ import absolute_import
import re
import codecs
import csv
import os
from math import ceil
import collections
from django.conf import settings
from django.db.models import Q

if not settings.configured:
    settings.configure('mysite', DEBUG=True)
from mysite.nlead_library.ent_com import *
from mysite.nlead_library.aci_api_functions import *
from mysite.nlead_library.service_now import *

TS_LEVEL = 0

# print TS_LEVEL

# global preso_variable_output
# global glb_multi_inputs
global glb_tech_options
global glb_template_dir
global glb_plat_specific_tech
global tech_with_vrf
global customer_type

# vendor customer (with multicast customers and partners, more detail/platform troubleshootin
vendor_customers = ['cisco']
# partners (with multiple customers, configuration is more important)
partner_customers = ['eplus', 'groupware']
# enterprise customers (default)
enterprise_customers = ['stanford']
# Alpa customers (evaluation/testing)
evaluating_customer = ['stanford']
customer_type = 'cisco'
tech_with_vrf = ['mvpn', 'l3vpn']

preso_variable_output = {}
glb_tech_options = {'ipversion': ['dhcp', 'mcast', 'bgp', 'ospf', 'isis']}
glb_template_dir = "./mysite/user_templates"
# glb_template_dir = "/home/ubuntu/prepro/mysite/mysite/user_templates"
# glb_template_dir = "/home/netserv/Webapp/Netserv/mysite/user_templates"
glb_plat_specific_tech = ['vxlan']

# import datetime
# import json

try:
    from mysite.models import combimatin_db
    from mysite.models import template_db
    from mysite.models import InputValueDb
    from mysite.models import UserInputValueDb, SwitchMigrationDB
    from mysite.models import Training
    from mysite.models import SetupParameters
    from mysite.models import ACIInterfaceStatusDB
except ValueError:
    print "Need to figure it out"
# settings.configure()
# from mysite.models import combimatin_db

global glb_nx9k_nonsupported


class NleadData():
    '''
    Description :
        This function is used to get IoS list and get platform of  IoS
	Inputs :
		ios
	Output:
        Return the output based on function call

    '''

    def __init__(self, ios=''):
        ''' ios, platform, tech and type combination.
        users:c1_checked
        input:
        output:
        '''
        demo_flag = False
        if demo_flag:
            key_plat = []
            covered_plat = []
            non_nx = []
            xr_plat = []
            glb_nx9k_nonsupported = ['MPLS', 'L2FWD', 'L3VPN', 'OTV']
            self.all_combinations = {1: {'tech': 'IPv4', 'type': ['fwd', 'flap'], 'ios': 'any', 'plat': ['any'],
                                         'area': 'Core Technologies'}}
            any_plat = ['Any_Platform']
            self.ios_list = ['Any_IOS', 'ASA', 'XR-IOS']
            self.xr_plat_list = ['ASR9000']
            self.nx_plat_list = []
            self.os_plat_list = []
            self.eos_plat_list = []
            self.asa_plat_list = ['Any ASA Platform', '5505', '5585']
            self.nos_plat_list = []
            sp_plat_list = ['ASR9000', 'C6500', 'CRS', 'ASR1000']
        else:
            key_plat = ['NX7000', 'ASR9000', 'C6800', 'C6500', 'CRS', 'C4500', 'C3750']
            covered_plat = ['NX7000', 'ASR9000', 'C6800', 'C6500', 'CRS', 'ASR1000', 'C4500', 'C3750']
            tac_isp_plat = ['ASR9000', 'C6800', 'C6500', 'CRS', 'ASR1000', 'C4500', 'C3750']

            non_nx = ['ASR9000', 'C6500', 'CRS', 'ASR1000']
            xr_plat = ['ASR9000', 'CRS']
            self.junos_plat = ['EX Series', 'QFX Series', 'ACX Series', 'MX Series']
            # junos_rtr_plat = ['ACX Series', 'MX Series']
            # junos_sw_plat = ['EX Series', 'QFX Series']
            sp_plat_list = ['ASR9000', 'C6800', 'C6500', 'CRS', 'ASR1000', 'C4500', 'C3750']
            self.fw_plat_list = ['ASA5500-X', 'ASA5585-X', 'Any ASA Platform']

            glb_nx9k_nonsupported = ['MPLS', 'L2FWD', 'L3VPN', 'OTV']
            nx_plat_list = ['NX9300', 'NX9500', 'NX7000', 'NX5000', 'NX3000', 'Any_NX_Platform']
            self.all_combinations = {
                1: {'tech': 'IPv4', 'type': ['eastwest', 'fwd', 'con', 'loss', 'latency'], 'ios': 'any',
                    'plat': ['any'], 'area': 'Core Technologies'},
                2: {'tech': 'VXLAN (BGP-EVPN)', 'type': [], 'ios': 'any',
                    'plat': ['NX9300', 'ASR1000', 'CSR', 'ASR9000', 'ARISTA', 'VDX'], 'area': 'Data Center'},
                # 3: {'tech': 'FabricPath', 'type': ['fwd'], 'ios': 'any', 'plat': ['NX5000', 'NX7000', 'NX6000'],'area':'Data Center'},
                29: {'tech': 'MPLS', 'type': ['fwd'], 'ios': 'any', 'plat': covered_plat, 'area': 'Service Provider'},
                # 4: {'tech': 'PWHE', 'type': ['fwd'], 'ios': 'XR-IOS', 'plat': xr_plat,'area':'Service Providers'},
                5: {'tech': 'Multicast', 'type': ['fwd'], 'ios': 'any', 'plat': ['any'], 'area': 'Core Technologies'},
                # 6: {'tech': 'IPv6 6VPE', 'type': ['ifwd', 'dfwd', 'fwd'], 'ios': 'any', 'plat': non_nx,'area':'Service Providers'},
                8: {'tech': 'VPLS', 'type': ['ifwd', 'dfwd', 'fwd'], 'ios': 'any', 'plat': key_plat,
                    'area': 'Service Provider'},
                9: {'tech': 'Layer-2 VPN', 'type': ['ifwd', 'dfwd', 'fwd'], 'ios': 'any', 'plat': 'any',
                    'area': 'Service Provider'},
                10: {'tech': 'MPLS TE', 'type': ['fwd'], 'ios': 'any', 'plat': covered_plat,
                     'area': 'Service Provider'},
                # 11: {'tech': 'IPv6 Neighbor Discovery', 'type': ['fwd'], 'ios': 'any', 'plat': ['any'],'area':'Core Technologies'},
                # 12: {'tech': 'Layer3 QOS', 'type': ['fwd'], 'ios': 'any', 'plat': key_plat,'area':'Core Technologies'},
                13: {'tech': 'IPv6', 'type': ['fwd'], 'ios': 'any', 'plat': ['any'], 'area': 'Core Technologies'},
                14: {'tech': 'HealthCheck', 'type': ['Overall Health-Check'], 'ios': 'any',
                     'plat': ['NX9300', 'NX9500'], 'area': 'Others'},
                15: {'tech': 'High CPU', 'type': ['High CPU'], 'ios': 'any',
                     'plat': covered_plat + ['NX9300', 'NX9500'], 'area': 'Others'},
                16: {'tech': 'MPLS LDP', 'type': ['fwd'], 'ios': 'any', 'plat': covered_plat,
                     'area': 'Service Providers'},
                17: {'tech': 'BFD', 'type': ['down', 'flap', 'cfg'], 'ios': 'any', 'plat': ['any'],
                     'area': 'Core Technologies'},
                18: {'tech': 'MP-BGP', 'type': ['down', 'flap', 'receive', 'send', 'install'], 'ios': 'any',
                     'plat': ['any'], 'area': 'Core Technologies'},
                19: {'tech': 'OSPF/OSPFv3', 'type': ['down', 'flap', 'missing', 'wrong', 'install', 'cfg'],
                     'ios': 'any', 'plat': ['any'], 'area': 'Core Technologies'},
                20: {'tech': 'ISIS', 'type': ['down', 'flap', 'receive', 'send', 'install', 'cfg'], 'ios': 'any',
                     'plat': non_nx, 'area': 'Core Technologies'},
                21: {'tech': 'DHCP/DHCPV6', 'type': ['proxy', 'relay', 'snoop'], 'ios': 'XR-IOS', 'plat': xr_plat,
                     'area': 'Core Technologies'},
                # 22: {'tech': 'Quality of Service (QoS)', 'type': ['fwd'], 'ios': 'any', 'plat': sp_plat_list,'area':'Core Technologies'},
                # 22: {'tech': 'IPv6 6PE', 'type': ['fwd'], 'ios': 'any', 'plat': sp_plat_list,'area':'Service Providers'},
                23: {'tech': 'Layer2 Multicast (IGMP)', 'type': ['fwd'], 'ios': 'any',
                     'plat': key_plat + ['NX9300', 'NX9500', 'NX5000'], 'area': 'Core Technologies'},
                24: {'tech': 'MVPN', 'type': ['fwd'], 'ios': 'any', 'plat': tac_isp_plat, 'area': 'Service Providers'},
                25: {'tech': 'Layer2 Forwarding', 'type': ['fwd'], 'ios': 'any',
                     'plat': key_plat + ['NX9300', 'NX9500', 'NX5000'], 'area': 'Core Technologies'},
                26: {'tech': 'OTV', 'type': ['ifwd', 'dfwd', 'fwd'], 'ios': 'any',
                     'plat': ['NX7000', 'ASR1000'], 'area': 'Data Center'},
                27: {'tech': 'ACL', 'type': [], 'ios': 'Firewalls', 'plat': self.fw_plat_list, 'area': 'Security'},
                28: {'tech': 'Network Address Translation (NAT)', 'type': [], 'ios': 'Firewalls',
                     'plat': self.fw_plat_list, 'area': 'Security'},
                30: {'tech': 'VPN', 'type': [], 'ios': 'Firewalls', 'plat': self.fw_plat_list, 'area': 'Security'},
                31: {'tech': 'L3VPN', 'type': ['ifwd', 'dfwd', 'fwd'], 'ios': 'any', 'plat': tac_isp_plat,
                     'area': 'Service Providers'},
                32: {'tech': 'ACL', 'type': [], 'ios': 'IOS', 'plat': ['ASR1000'], 'area': 'Security'},
                33: {'tech': 'Firewall', 'type': [], 'ios': 'IOS', 'plat': ['ASR1000'], 'area': 'Security'},
                34: {'tech': 'VPN', 'type': [], 'ios': 'IOS', 'plat': ['ASR1000'], 'area': 'Security'},
                35: {'tech': 'VPN', 'type': [], 'ios': 'SD-WAN', 'plat': ['VCE'], 'area': 'SD-WAN'},
                36: {'tech': 'VPN', 'type': ['sdown'], 'ios': 'Enterprise-1', 'plat': ['any'], 'area': 'Services'},
                37: {'tech': 'Segment Routing', 'type': [''], 'ios': 'any',
                     'plat': ['Any_NX_Platform'] + ['NX7000', 'NX3000', 'NX5000', 'NX6000', 'NX9300'],
                     'area': 'Data Center'},
                # 38: {'tech': 'Virtual PortChannel (vPC)', 'type': [''], 'ios': 'any',
                #      'plat': ['Any_NX_Platform'] + ['NX7000', 'NX5000', 'NX6000', 'NX9300'],
                #      'area':'Data Center'},
                39: {'tech': 'Fabric Extender', 'type': [''], 'ios': 'any',
                     'plat': ['Any_NX_Platform'] + ['NX7000', 'NX5000', 'NX6000', 'NX9300'],
                     'area': 'Data Center'},
                40: {'tech': 'Intelligent   Traffic Director (ITD)', 'type': [''], 'ios': 'any',
                     'plat': ['Any_NX_Platform'] + ['NX7000', 'NX3000', 'NX5000', 'NX6000', 'NX9300'],
                     'area': 'Data Center'},
                41: {'tech': 'Load Balancer', 'type': [''], 'ios': 'F5',
                     'plat': ['BIG-IP 12000, BIG-IP 10000, BIG-IP 7000'],
                     'area': 'Layer4-7 Services'},
                42: {'tech': 'Firewall', 'type': [''], 'ios': 'CP',
                     'plat': ['CP5600', 'CP5800'],
                     'area': 'Security'},
                43: {'tech': 'IPv4', 'type': [''], 'ios': 'Linux',
                     'plat': ['Linux', 'MAC'],
                     'area': 'Wireless'},
                43: {'tech': 'IPv4', 'type': [''], 'ios': 'Windows',
                     'plat': ['Server', 'Desktop'],
                     'area': 'Wireless'},
                44: {'tech': 'Cisco', 'type': [''], 'ios': 'Cisco WLC',
                     'plat': ['C8540', 'C5520'],
                     'area': 'Wireless'}
            }

            any_plat = ['Any_Platform']
            self.ios_list = ['IOS', 'NX-IOS', 'XR-IOS', 'ASA Firewall', 'F5', 'EOS', 'NOS', 'Linux', 'Windows',
                             'Multiple Devices',
                             'Enterprise-1']
            # self.ios_list = ['Any_IOS','NX-IOS', 'IOS', 'XR-IOS', 'ASA Firewall', 'EOS', 'NOS', 'Enterprise-1']
            # self.xr_plat_list = ['ASR9000', 'CRS', '12000-XR', 'Any_XR_Platform']
            self.xr_plat_list = ['ASR9000', 'CRS', '12000-XR', 'Any XR Platform']
            self.nx_plat_list = ['NX9500', 'NX9300', 'NX7000', 'NX5000', 'NX3000', 'Any NX Platform']
            # self.nx_plat_list = ['NX7000', 'NX3000', 'NX5000', 'NX6000', 'NX9300', 'Any_NX_Platform']
            self.os_plat_list = ['ASR1000', 'C6800', 'C6500', 'C7600', 'C3750 C3850', 'C4500', 'C3900 C2900',
                                 'C3800 C2800', 'Any IOS Platform']
            self.F5_plat_list = ['BIG-IP 12000', 'BIG-IP 10000', 'BIG-IP 7000']
            self.Linux_plat_list = ['Linux', 'MAC']
            self.Windows_plat_list = ['Server', 'Desktop']
            self.CP_plat_list = ['CP5600', 'CP5800']
            self.CWLC_plat_list = ['C8540', 'C5520']
            self.CWLC_plat_list = ['C8540', 'C5520']
            self.eos_plat_list = ['ARISTA']
            self.sdwan_plat_list = ['VCE']
            self.enterprise_plat_list = ['Any_Platform']
            self.nos_plat_list = ['VDX']
        self.all_plat_list = any_plat + self.nx_plat_list + self.xr_plat_list + self.os_plat_list \
                             + self.eos_plat_list + self.nos_plat_list + self.Windows_plat_list + self.Linux_plat_list

    def getIosList(self):

        '''
        Description:
            Function used to declare ios data and get that data into list
	    Inputs:
			ios
		Output:
            Return IoS list

        '''
        #         self.ios_list = {"meta": {"label": "", "default": ""}, "sections":
        #             [{"name": "Campus", "options": [
        #                 {"label": "Patching Matrix", "value": "Patching Matrix"},
        # ]}]}
        self.ios_list = {"meta": {"label": "", "default": ""}, "sections":
            [{"name": "Router and Switches", "options": [
                {"label": "NX IOS", "value": "NX-IOS"},
                {"label": "IOS", "value": "IOS"},
                {"label": "XR IOS", "value": "XR-IOS"},
                {"label": "JUNOS", "value": "JUNOS"},
                {"label": "Arista EOS", "value": "EOS"},
                {"label": "Brocade EOS", "value": "NOS"},
                {"label": "ACI", "value": "ACI"},
                {"label": "Fabric Configuration", "value": "fabric configuration"}
            ]},
             {"name": "Other Network Devices", "options": [
                 {"label": "ASA Firewall", "value": "ASA Firewall"},
                 {"label": "Check Point Firewall", "value": "CP"},
                 {"label": "F5 Load Balancer", "value": "F5"},
                 {"label": "Cisco Wireless", "value": "Cisco WLC"}]},
             # {"label": "Any IOS", "value": "Any_IOS"}]},
             # {"name": "Server and Desktop",
             #  "options": [{"label": "Linux", "value": "Linux"},
             #              {"label": "Windows", "value": "Windows"}]},
             # {"name": "Multiple Devices",
             #  "options": [{"label": "Multiple Devices Config", "value": "Multiple_Devices"}]},
             {"name": "Network Config and T/S",
              "options": [{"label": "Enterprise Network T/S", "value": "Enterprise-1"},
                          {"label": "Deployment", "value": "Deployment"},
                          {"label": "Fabric Configuration", "value": "fabric configuration"},
                          {"label": 'Enterprise Firewalls',
                           "value": "Enterprise_Firewalls"},
                          {"label": "Multiple Devices Config", "value": "Multiple_Devices"}
                          ]}]}
        return self.ios_list

    def getAllPlatfromList(self):
        return self.all_plat_list

    def getAllTechList(self):
        return self.all_tech_list

    def getPlatfromList(self, usr_ios):
        self.plat_list = []
        print '+ usr_ios +'
        print usr_ios
        if usr_ios == 'XR-IOS':
            self.plat_list = self.xr_plat_list
            # self.plat_list = ['ASR9000', 'CRS', '12000-XR', 'Any XR Platform']
        elif usr_ios == 'NX-IOS':
            self.plat_list = self.nx_plat_list
            # self.plat_list = ['NX7000', 'NX3000', 'NX5000', 'NX6000', 'NX9300', 'Any NX Platform']
        elif usr_ios == 'IOS':
            self.plat_list = self.os_plat_list
        elif usr_ios == 'Firewalls' or usr_ios == 'ASA Firewall':
            self.plat_list = self.fw_plat_list
        elif usr_ios == 'SD-WAN':
            self.plat_list = self.sdwan_plat_list
        elif usr_ios == 'Enterprise-1':
            self.plat_list = self.enterprise_plat_list
        elif usr_ios == 'EOS':
            self.plat_list = self.eos_plat_list
        elif usr_ios == 'NOS':
            self.plat_list = self.nos_plat_list
        elif usr_ios == 'Linux':
            self.plat_list = self.Linux_plat_list
        elif usr_ios == 'Windows':
            self.plat_list = self.Windows_plat_list
        elif usr_ios == 'F5':
            self.plat_list = self.F5_plat_list
        elif usr_ios == 'CP':
            self.plat_list = self.CP_plat_list
        elif usr_ios == 'JUNOS':
            self.plat_list = self.junos_plat
        elif usr_ios == 'ACI':
            self.plat_list = ['na']
        elif usr_ios == 'Cisco WLC':
            self.plat_list = self.CWLC_plat_list
        elif usr_ios == 'Multiple_Devices' or usr_ios == 'Multiple Devices':
            self.plat_list = ['na']
        elif usr_ios == 'Enterprise_Firewalls' or usr_ios == 'Enterprise Firewalls':
            self.plat_list = ['na']
        elif usr_ios == 'fabric_configuration' or usr_ios == 'Fabric Configuration':
            self.plat_list = ["East-DC", "West-DC"]
        elif usr_ios == 'Any_IOS':
            self.plat_list = self.all_plat_list
        # else:
        #     return -1

        return self.plat_list

    def getTechList(self, user_ios, user_plat):

        self.tech_list = []
        for id in self.all_combinations.keys():
            if self.all_combinations[id]['ios'] == user_ios or self.all_combinations[id][
                'ios'] == 'any' or user_ios == 'Any_IOS' or user_ios == 'Multiple_Devices':
                if user_plat:
                    if self.all_combinations[id]['plat'].__contains__(user_plat) or \
                            self.all_combinations[id]['plat'].__contains__('any') \
                            or user_plat == 'Any_Platform' or user_ios == 'Multiple_Devices':
                        if not self.tech_list.__contains__(self.all_combinations[id]['tech']):
                            self.tech_list.append(self.all_combinations[id]['tech'])
                else:
                    if not self.tech_list.__contains__(self.all_combinations[id]['tech']):
                        self.tech_list.append(self.all_combinations[id]['tech'])
        return self.tech_list

    def getTechSectionDict(self, user_ios, user_plat):
        self.tech_list = []
        tech_list_sp = []
        tech_list_dc = []
        tech_list_core = []
        tech_list_sec = []
        tech_list_services = []
        tech_list_other = []
        self.tech_dct = {}
        for id in self.all_combinations.keys():
            if self.all_combinations[id]['ios'] == user_ios or self.all_combinations[id][
                'ios'] == 'any' or user_ios == 'Any_IOS':
                if self.all_combinations[id]['ios'] == 'any' and user_ios == 'SD-WAN':
                    continue
                elif self.all_combinations[id]['ios'] == user_plat:
                    if self.all_combinations[id].has_key('area'):
                        if self.all_combinations[id].get('area') == "Data Center":
                            if not tech_list_dc.__contains__(self.all_combinations[id]['tech']):
                                tech_list_dc.append(self.all_combinations[id]['tech'])
                        elif self.all_combinations[id].get('area') == "Service Providers":
                            if not tech_list_sp.__contains__(self.all_combinations[id]['tech']):
                                tech_list_sp.append(self.all_combinations[id]['tech'])
                        elif self.all_combinations[id].get('area') == "Core Technologies":
                            if not tech_list_core.__contains__(self.all_combinations[id]['tech']):
                                tech_list_core.append(self.all_combinations[id]['tech'])
                        elif self.all_combinations[id].get('area') == "Security":
                            if not tech_list_sec.__contains__(self.all_combinations[id]['tech']):
                                tech_list_sec.append(self.all_combinations[id]['tech'])
                        elif self.all_combinations[id].get('area') == "SD-WAN":
                            if not tech_list_sec.__contains__(self.all_combinations[id]['tech']):
                                tech_list_sec.append(self.all_combinations[id]['tech'])
                        elif self.all_combinations[id].get('area') == "Services":
                            if not tech_list_services.__contains__(self.all_combinations[id]['tech']):
                                tech_list_services.append(self.all_combinations[id]['tech'])
                        elif self.all_combinations[id].get('area') == "Others":
                            if not tech_list_other.__contains__(self.all_combinations[id]['tech']):
                                tech_list_other.append(self.all_combinations[id]['tech'])
                else:
                    if user_plat:
                        if self.all_combinations[id]['plat'].__contains__(user_plat) or self.all_combinations[id][
                            'plat'].__contains__('any') or user_plat == 'Any_Platform':
                            if self.all_combinations[id].has_key('area'):
                                if self.all_combinations[id].get('area') == "Data Center":
                                    if not tech_list_dc.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_dc.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Service Providers":
                                    if not tech_list_sp.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_sp.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Core Technologies":
                                    if not tech_list_core.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_core.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Security":
                                    if not tech_list_sec.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_sec.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "SD-WAN":
                                    if not tech_list_sec.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_sec.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Services":
                                    if not tech_list_services.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_services.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Others":
                                    if not tech_list_other.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_other.append(self.all_combinations[id]['tech'])
                    else:
                        if not self.tech_list.__contains__(self.all_combinations[id]['tech']):
                            if self.all_combinations[id].has_key('area'):
                                if self.all_combinations[id].get('area') == "Data Center":
                                    if not tech_list_dc.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_dc.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Service Providers":
                                    if not tech_list_sp.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_sp.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Core Technologies":
                                    if not tech_list_core.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_core.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Security":
                                    if not tech_list_sec.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_sec.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "SD-WAN":
                                    if not tech_list_sec.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_sec.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Services":
                                    if not tech_list_services.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_services.append(self.all_combinations[id]['tech'])
                                elif self.all_combinations[id].get('area') == "Others":
                                    if not tech_list_other.__contains__(self.all_combinations[id]['tech']):
                                        tech_list_other.append(self.all_combinations[id]['tech'])

        # only if not empty
        if tech_list_dc:
            self.tech_dct['Data Center'] = tech_list_dc
        if tech_list_sp:
            self.tech_dct['Service Providers'] = tech_list_sp
        if tech_list_core:
            self.tech_dct['Core Technologies'] = tech_list_core
        if tech_list_sec:
            self.tech_dct['Security'] = tech_list_sec
        if tech_list_services:
            self.tech_dct['Services'] = tech_list_services
        if tech_list_other:
            self.tech_dct['Others'] = tech_list_other
        return self.tech_dct

    def getTypeList(self, user_ios, user_plat, user_tech):
        print 'user_tech'
        print user_tech
        self.type_list = []
        for id in self.all_combinations.keys():
            if self.all_combinations[id]['ios'] == user_ios or self.all_combinations[id]['ios'].__contains__(
                    'any') or user_ios == 'Any_IOS':
                if self.all_combinations[id]['tech'] == user_tech:
                    for ty in self.all_combinations[id]['type']:
                        type_el = ConvertDbToUser('type', ty)
                        if type_el:
                            self.type_list.append(type_el)
                            # ConvertUeseInputs
                            # self.type_list = self.all_combinations[id]['type']
        self.type_list.append('Add New Template')
        self.type_list.append('Delete Existing Template')
        self.type_list.append('Modify Existing Template')
        return self.type_list

        # user_dict['link_section'] = {"label": "Recommended Training",
        #                              "options": [{"ABC": "http://google.com"},
        #                                          {"XYZ": "http://facebook.com"}]}
        #

        # sym_list =  {"meta": {"label": "", "default": "", "na": ""},
        #            "sections": [{"name": "Configuration", "options":
        #                [{"label": "Firewall Rules with New Object Groups", "value": "New Object Groups"},
        #                 {"label": "Firewall Rules with Existing Object Groups",
        #                  "value": "Existing Object Groups"},
        #                 ]}]}

    def getTypeAndTpDictOld(self, user_ios, user_plat, user_tech, template_list=[], training_dict={}):
        self.type_and_tp = {}
        type_list = []
        training_list = []
        if user_tech == 'L2FWD':
            user_tech = 'Layer2 Forwarding'

        elif user_tech == 'MCAST':
            user_tech = 'Multicast'

        elif user_tech == 'L2MCAST':
            user_tech = 'Layer2 Multicast (IGMP)'

        elif user_tech == 'VXLAN':
            user_tech = 'VXLAN (BGP-EVPN)'

        for id in self.all_combinations.keys():
            if self.all_combinations[id]['ios'] == user_ios or self.all_combinations[id]['ios'].__contains__(
                    'any') or user_ios == 'Any_IOS':
                if self.all_combinations[id]['tech'] == user_tech:
                    for ty in self.all_combinations[id]['type']:
                        type_el = ConvertDbToUser('type', ty)
                        if type_el:
                            type_list.append(type_el)
        type_list.append('Problem Solving')
        if training_dict:
            for training_name in training_dict:
                training_info = {}
                training_info[training_name] = training_dict.get(training_name)
                training_list.append(training_info)
            # self.type_and_tp["Recommended Training"]=training_dict
            self.type_and_tp["link_section"] = {"label": "Recommended Training", "options": training_list}
        for template_name in template_list:
            if not template_name.find('Troubleshooting') == -1:
                type_list.append(template_name)
                template_list.remove(template_name)
        self.type_and_tp["Troubleshooting"] = type_list

        if template_list:
            # self.type_and_tp["User Options"]=['Add New Template', 'Modify Existing Template', 'Delete Existing Template', 'Fork Existing Template']
            self.type_and_tp["User Options"] = ['Add New Template', 'Delete Existing Template']
            self.type_and_tp["Configurations"] = template_list
        else:
            self.type_and_tp["User Options"] = ['Add New Template']
        return self.type_and_tp

    def getTypeAndTpDict(self, user_ios, user_plat, user_tech, template_list=[], training_dict={}):
        '''
        Description :
            Function used to creating options for troubleshooting.
		Inputs :
            user_ios, user_plat, user_tech, templat list, training_dict
		Output :
            Loads inputs for troubleshooting.

        :param user_ios:
        :param user_plat:
        :param user_tech:
        :param template_list:
        :param training_dict:
        :return:
        '''
        self.type_and_tp = {}
        type_list = []
        training_list = []
        all_data_list = []
        all_data = {}
        to_return = {}
        template_dict_1 = {}
        template_list_1 = []
        if template_list:
            # self.type_and_tp["User Options"]=['Add New Template', 'Modify Existing Template', 'Delete Existing Template', 'Fork Existing Template']
            # all_data['name'] = 'User Options'
            # all_data['options'] = [{"label": "Add New Template","value":"Add New Template"}]
            for template_name in template_list:
                template_dict_1["label"] = template_name
                template_dict_1["value"] = template_name
                template_list_1.append(template_dict_1.copy())
            all_data['name'] = 'Configurations'
            all_data['options'] = template_list_1
            all_data_list.append(all_data.copy())
            # self.type_and_tp["User Options"]=['Add New Template']
            # self.type_and_tp["Configurations"]=template_list
        self.type_and_tp["User Options"] = ['Add New Template', 'Delete Existing Template']
        all_data['name'] = 'User Options'
        all_data['options'] = [{"label": "Add New Template", "value": "Add New Template"},
                               {"label": "Delete Existing Template", "value": "Delete Existing Template"},
                               {"label": "Modify Existing Template", "value": "Modify Existing Template"}]
        all_data_list.append(all_data.copy())

        troubleshooting_dict = {}
        troubleshooting_list = []

        for id in self.all_combinations.keys():
            if self.all_combinations[id]['ios'] == user_ios or self.all_combinations[id]['ios'].__contains__(
                    'any') or user_ios == 'Any_IOS':
                if self.all_combinations[id]['tech'] == user_tech:
                    for ty in self.all_combinations[id]['type']:
                        type_el = ConvertDbToUser('type', ty)
                        if type_el:
                            print 'type_el'
                            print type_el
                            troubleshooting_dict['label'] = type_el
                            troubleshooting_dict['value'] = type_el

                            print 'troubleshooting_dict'
                            print troubleshooting_dict
                            troubleshooting_list.append(troubleshooting_dict.copy())

        print troubleshooting_list
        # type_list.append('Problem Solving')

        # #self.type_and_tp["Recommended Training"]=training_dict
        # self.type_and_tp["link_section"]={"label": "Recommended Training","options": training_list}
        # troubleshooting_dict = {}
        # troubleshooting_list = []
        for template_name in template_list:
            if not template_name.find('Troubleshooting') == -1:
                type_list.append(template_name)
                troubleshooting_dict['label'] = template_name
                troubleshooting_dict['value'] = template_name
                troubleshooting_list.append(troubleshooting_dict.copy())
                template_list.remove(template_name)

        print troubleshooting_list
        all_data['name'] = 'Troubleshooting'
        all_data['options'] = troubleshooting_list
        all_data_list.append(all_data.copy())

        # self.type_and_tp["Troubleshooting"]=type_list

        training_dict_1 = {}
        training_list_1 = []
        print 'training_dict'
        print training_dict
        if training_dict:
            for training_name in training_dict:
                # for k,v in training_dict.iterateitems():
                training_info = {}
                training_info[training_name] = training_dict.get(training_name)
                training_list.append(training_info)
                training_dict_1['label'] = training_name
                training_dict_1['value'] = training_dict.get(training_name)
                training_list_1.append(training_dict_1.copy())
            all_data['name'] = 'Recommended Training'
            all_data['options'] = training_list_1
            all_data_list.append(all_data.copy())

        to_return["meta"] = {"label": "", "default": "", "na": ""}
        to_return["sections"] = all_data_list

        print all_data_list
        return to_return


def format_filter_script_output(output, user_sel={}):
    global TS_LEVEL
    global preso_variable_output
    # global glb_input_list_for_script
    new_output = []
    # NEED TO REMOVE AFTER FIXING THE Recovery PART!!
    if user_sel.get('user_role'):
        user_role = user_sel.get('user_role')
    else:
        user_role = ''
    plat = user_sel.get('plat')
    tech = user_sel.get('tech')
    for line in output:
        skip_flag = False
        line = re.sub('<in_lc>', '<ingress_linecard_num>', line)
        line = re.sub('<ou_lc>', '<egress_linecard_num>', line)
        line = re.sub('<out_lc>', '<egress_linecard_num>', line)
        # Need to add for escalation
        if not user_role == 'esc':
            if plat == '7000' and tech == 'mcast':
                if re.search('hardware internal', line):
                    continue
        if re.search('Following are the links', line):
            continue
        if re.search('^\{##', line):
            continue
        if re.search('##', line):
            continue
        if re.search('End STR', line) or re.search('Non Imp', line):
            # line = ' !<-- Additional Data -->!'
            continue
        #
        if re.search('End of STR|www-tac|wwwin|cisco\.com|Recovery !!', line):
            skip_flag = True
        if re.search('For more information refer following link|Mailers:|EDCS', line):
            skip_flag = True
        if not re.search('!<-- ', line):
            line = re.sub('^!+', '-', line)
        else:
            line = re.sub('!<-- ', '<span style="color:rgb(237, 125, 49);">!<-- ', line)
            line = re.sub(' -->!', ' -->! </span>', line)

        if get_key_value(preso_variable_output, 'in_int', 'output'):
            line = re.sub('in_int', get_key_value(preso_variable_output, 'in_int', 'output'), line)
        if get_key_value(preso_variable_output, 'ou_int', 'output'):
            line = re.sub('out_int', get_key_value(preso_variable_output, 'ou_int', 'output'), line)
        if get_key_value(preso_variable_output, 'out_int', 'output'):
            line = re.sub('out_int', get_key_value(preso_variable_output, 'out_int', 'output'), line)
        if get_key_value(preso_variable_output, 'des_ip', 'output'):
            line = re.sub('des_ip', get_key_value(preso_variable_output, 'des_ip', 'output'), line)
        if get_key_value(preso_variable_output, 'des_net', 'output'):
            line = re.sub('des_net', get_key_value(preso_variable_output, 'des_net', 'output'), line)
        if get_key_value(preso_variable_output, 'dst_ml', 'output'):
            line = re.sub('dst_ml', get_key_value(preso_variable_output, 'dst_ml', 'output'), line)
        if not skip_flag:
            new_output.append(line)
    return new_output


def get_key_value(my_dict, item1, item2=False):
    value = ""
    result = ""
    try:
        if my_dict.get(item1):
            value = my_dict.get(item1)
            if item2:
                if type(value) is dict:
                    if value.get(item2):
                        value = value.get(item2)
                    else:
                        return result
                else:
                    return result
    except Exception as err:
        raise err
    return value


class ConvertUserToDbVar:
    '''
    Description :
        This class used to convert user to database var.
	Inputs :
		user_ios, user_plat, user_tech, user_type, template_name
	Output :
        Return the output based on function call

    '''

    def __init__(self, user_ios, user_plat, user_tech, user_type, template_name=''):
        '''
        Get the parameters for DB and TCL
        Get template list
        Get Problem type list
        :param user_ios:
        :param user_plat:
        :param user_tech:
        :param user_type:
        :return: dictionary
        '''
        self.type = '';
        self.plat = '';
        self.ios = '';
        self.type = ''
        self.ios = ConvertUeseInputs('ios', user_ios)
        self.tech = ConvertUeseInputs('tech', user_tech)
        self.plat = ConvertUeseInputs('plat', user_plat)
        if user_type:
            self.type = ConvertUeseInputs('ios', user_type)
        self.db_inputs = {'ios': self.ios, 'plat': self.plat, 'tech': self.tech, 'type': self.type}
        self.user_plat = user_plat

    def getUserToDbDict(self):
        return self.db_inputs

    def getIos(self):
        return self.ios

    def getTech(self):
        return self.tech

    def getPlat(self):
        return self.plat

    def getType(self):
        return self.type

    def deleteTpFromDb(self, template_name, customer):
        flag = False
        entry = template_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech, template=template_name)
        if entry:
            entry.delete()
            file_name = template_name.replace(' ', '_')
            if customer != "common":
                if glb_plat_specific_tech.__contains__(self.tech):
                    file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + self.ios + "_" + self.plat + "_" + self.tech
                else:
                    file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + self.ios + "_" + self.tech
            else:
                if glb_plat_specific_tech.__contains__(self.tech):
                    file_name = glb_template_dir + "/" + file_name + "_" + self.ios + "_" + self.plat + "_" + self.tech
                else:
                    file_name = glb_template_dir + "/" + file_name + "_" + self.ios + "_" + self.tech
            os.remove(file_name)
            return ' Template " %s " Deleted Successfully' % template_name
        # entry2 = combimatin_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech, type=self.type)
        #     if entry2:
        #         entry2.delete()
        #         flag = True
        # if flag:
        #     return True
        # else:
        return 'Template " %s " - Does not exist' % template_name

    def getTrainingList(self):
        training_list = []
        self.training_dict = {}
        entry = Training.objects.filter(ios=self.ios, plat=self.plat, tech=' '.join(self.tech.split()))
        if entry:
            for el in entry:
                if not training_list.__contains__(el.description):
                    training_list.append(el.description)
                    self.training_dict[el.description] = el.link
        entry = Training.objects.filter(ios=self.ios, plat='any', tech=' '.join(self.tech.split()))
        if entry:
            for el in entry:
                if not training_list.__contains__(el.description):
                    training_list.append(el.description)
                    self.training_dict[el.description] = el.link
        # return self.training_list

        return self.training_dict

    def getTpList(self):
        print self.ios
        print self.plat
        print self.tech
        self.template_list = []
        if self.ios == 'Any_IOS' and self.plat == 'Any_Platform':
            entry = template_db.objects.filter(tech=self.tech)
            if entry:
                for el in entry:
                    plat = el.plat
                    if plat == '9000':
                        plat = "ASR9000"
                    elif plat == 'asr':
                        plat = "ASR1000"
                    elif plat == 'asr':
                        plat = "ASR1000"
                    elif plat == 'nx9k':
                        plat = "NX9300"
                    elif plat == '7000':
                        plat = "NX7000"
                    if el.template:
                        self.template_list.append(plat + '_' + el.template)
        else:
            entry = template_db.objects.filter(ios=self.ios, plat__in=['any', self.plat], tech=self.tech, type=1)
            if entry:
                for el in entry:
                    if not self.template_list.__contains__(el.template):
                        self.template_list.append(el.template)
            if self.ios == 'ios':
                entry = template_db.objects.filter(ios=self.ios, plat='Any_IOS_Platform', tech=self.tech)
            elif self.ios == 'nx':
                entry = template_db.objects.filter(ios=self.ios, plat='Any_NX_Platform', tech=self.tech)
            elif self.ios == 'xr':
                entry = template_db.objects.filter(ios=self.ios, plat='Any_XR_Platform', tech=self.tech)
            elif self.ios == 'Firewalls':
                entry = template_db.objects.filter(ios=self.ios, plat='Any_ASA_Platform', tech=self.tech)
            if entry:
                for el in entry:
                    if not self.template_list.__contains__(el.template):
                        self.template_list.append(el.template)
        print 'self.template_list'
        print self.template_list
        return self.template_list

    def addDictToDb(self):

        entry = combimatin_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech)
        if not entry:
            p1 = combimatin_db(ios=self.ios, plat=self.plat, tech=self.tech, type=self.type)
            p1.save()
            return True
        else:
            print 'entry already exists'
            return False

    def updateTpToTypeList(self, val):
        # if combimatin_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech, type=val):
        #     print "matching db entry already exists no need to add type"
        #     # entry = combimatin_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech, type=val)
        if combimatin_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech):
            entry2 = combimatin_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech)
            old_type = entry2.type
            if old_type:
                old_type_list = old_type.split(" ")
                if val in old_type_list:
                    print 'template already exists'
                else:
                    new_type = old_type + " " + val
                    combimatin_db.objects.filter(id=entry2.id).update(type=new_type)
            else:
                new_type = val
                combimatin_db.objects.filter(id=entry2.id).update(type=new_type)
        else:
            print "No matching entry - need to add"

    def is_it_new_type(self, val):
        # if combimatin_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech, type=val):
        #     print "matching db entry already exists no need to add type"
        #     # entry = combimatin_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech, type=val)
        # NEED TO REMOVE True - ONLY FOR TESTING
        # return True
        if combimatin_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech):
            entry2 = combimatin_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech)
            old_type = entry2.type
            if old_type:
                old_type_list = old_type.split(" ")
                if val in old_type_list:
                    return False
                else:
                    return True
        return True

    def showMatchingEntry(self):
        entry = combimatin_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech)
        if entry:
            print "ios:" + self.ios
            print "plat:" + self.plat
            print "tech:" + self.tech
            print "type:" + self.type
        else:
            print 'There is not matching db enty'

    def getTypeFromDb(self):
        self.db_type = ""
        # NEED TO REMOVE - Only for Demo
        if self.ios == 'Any_IOS' and self.plat == 'Any_Platform':
            entry = combimatin_db.objects.filter(tech=self.tech)
            new_type_list = []
            if entry:
                for el in entry:
                    plat = el.plat
                    if el.type:
                        type_list = el.type.split(' ')
                        for type in type_list:
                            new_type = plat + "_" + type
                            new_type_list.append(new_type)
            self.db_type = ' '.join(new_type_list)
        else:
            if combimatin_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech):
                entry = combimatin_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech)
                if entry:
                    self.db_type = entry.type
        return self.db_type

        # def updateDbEntry(self, field, val):
        #     if field == "type":
        #         p1 = combimatin_db(ios=self.ios, plat=self.plat, tech=self.tech, type=self.type)

        return self.db_inputs

    def getUserToDbIos(self):
        return self.db_inputs

    def getUserToDbPlat(self):
        return self.db_inputs

    def getUserToDbTech(self):
        return self.db_inputs

    def getUserToDbType(self):
        return self.db_inputs


# global glb_non_common_que


class GetInputVariable:
    def __init__(self, user_ios, user_plat, user_tech, user_type):
        # global glb_non_common_que
        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format'''
        # com_dict = {'ip': {'ios': 'nx', 'plat': '7000', 'type': 'forwarding'}}
        glb_non_common_que = {}
        self.non_common_que = {}
        glb_input_list_for_script = []
        com_dict = {user_tech: {'ios': user_ios, 'plat': user_plat, 'type': user_type}}
        self.combine_list = []
        if user_tech == 'L2FWD2':
            combine_list = ['src_ip', 'src_mac', 'in_int', 'vlan_id', 'out_int', 'dst_mac', 'des_ip']
            if user_plat == 'NX7000':
                combine_list.append('in_lc')
                combine_list.append('ou_lc')
                self.non_common_que = {'in_l3': 'Enter line-card <in_lc> type [m108 m132 m148 m224 m206 m202 f248]',
                                       'ou_l3': 'Enter line-card <out_lc> type [m108 m132 m148 m224 m206 m202 f248]'}
        elif user_tech == 'L2MCAST2':
            combine_list = ['src_ip', 'src_mac', 'in_int', 'vlan_id', 'out_int', 'dst_mac', 'des_ip']
            if user_plat == 'NX7000':
                combine_list.append('in_lc')
                combine_list.append('ou_lc')
                self.non_common_que = {'in_l3': 'Enter line-card <in_lc> type [m108 m132 m148 m224 m206 m202 f248]',
                                       'ou_l3': 'Enter line-card <out_lc> type [m108 m132 m148 m224 m206 m202 f248]'}
        else:
            for tech2 in com_dict.keys():
                tech = ConvertUeseInputs('tech', tech2)
                type = ConvertUeseInputs('type', com_dict.get(tech2).get('type'))

                plat = ConvertUeseInputs('plat', com_dict.get(tech2).get('plat'))
                ios = ConvertUeseInputs('ios', com_dict.get(tech2).get('ios'))
                print ios, tech, type, plat
                if type == 'jjj' and ios == 'SD-WAN':
                    print '!!!!! change the type to value !!!!'
                combine_list = []
                type = type.strip(' ').replace(' ', '_')
                if type == 'loss' and tech == 'ip':
                    tech = 'loss'
                print " New  ... tclsh /home/ubuntu/nlead/run_from_py.tcl %s %s %s %s" % (plat, tech, ios, type)
                p = subprocess.Popen(
                    "tclsh /home/ubuntu/nlead/run_from_py.tcl %s %s %s %s" % (plat, tech, ios, type),
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                inputlist = stdout.splitlines()
                flag = 0
                for line in inputlist:
                    if re.search("\-\-\-\-\-\-\-\-", line):
                        flag = 0
                    if flag:
                        line = re.sub(r'\s+', ' ', line)
                        input_list = line.split(" CCCC ;; ")
                        input_pa = input_list[0]
                        input_pa_list = input_pa.split()
                        if input_pa_list[0] == tech:
                            input_pa_list.pop(0)
                        for para in input_pa_list:
                            if para == "<mask_len>":
                                para = "<dst_ml>"
                                var = "dst_ml"
                                # need to verify
                                if var == 'ou_int':
                                    var = 'out_int'
                                if not combine_list.__contains__(var):
                                    combine_list.append(var)
                            else:
                                var = para.replace("<", "").replace(">", "").replace(",", "_")
                                var = " ".join(var.split())
                                var = re.sub(r' ', '', var)
                            if not combine_list.__contains__(var):
                                combine_list.append(var)
                        if len(input_list) > 1:
                            input_que = input_list[1]
                            input_que_list = input_que.split(';;')
                            for que in input_que_list:
                                que_info = que.split('-set-')
                                if len(que_info) == 2:
                                    var = que_info[1]
                                    para = que_info[0]
                                    para = re.sub(r'^\s+', '', para)
                                    var = re.sub(r' ', '', var).replace(",", "_")
                                    if var == 'ou_int':
                                        var = 'out_int'
                                    if not combine_list.__contains__(var) and var != 'typ':
                                        glb_non_common_que[var] = para
                                        self.non_common_que[var] = para
                                        combine_list.append(var)
                                    else:
                                        print 'not valid or duplicate %s' % var
                    if re.search("\+\+\+\+\+\+\+\+", line):
                        flag = 1
                        # print "%s | %s | %s | %s | %s" % (tech, ios, plat, type, combine_list)
                        # if ios == 'nx' and tech == 'ip' and type == 'fwd':
                        #     if not combine_list.__contains__('vrf'):
                        #         combine_list.append('vrf')
                        #     if not combine_list.__contains__('nh_ip'):
                        #         combine_list.append('nh_ip')
        self.combine_list = combine_list
        glb_input_list_for_script = self.combine_list
        # self.user_inputs_to_tcl = {'ios': ios,'plat': plat,'tech': tech,'type': type}

    def getTypeList(self):
        return self.combine_list

    # def getUserInputsToTcl(self):
    #     return self.user_inputs_to_tcl
    def get_non_common_que(self):
        return self.non_common_que


class ReadTemplateDb:

    '''
    Description:
	    This class used to check the template is already in database
	    And also used to update and modify database.
	Inputs:
		com_dict, template_name, customer, ext_dict
	Output:
        Used to update and modify database.


    '''

    def __init__(self, com_dict, template_name, customer, ext_dict={}):
        '''
        Get the tempalte file
        Read the input parameters

        '''
        global glb_plat_specific_tech
        global glb_template_dir
        global tech_with_vrf
        ''' Process the txt box for creating new or modifying the template. Get the input list'''
        tech = ConvertUeseInputs('tech', com_dict.get('tech'))
        plat = ConvertUeseInputs('plat', com_dict.get('plat'))
        ios = ConvertUeseInputs('ios', com_dict.get('ios'))
        user_name = multi_level_value(com_dict, 'user_name')
        self.user_name = customer
        self.db_inputs = ""
        # need to check at the end of the reguler expression
        if ios == 'Any_IOS' and plat == 'Any_Platform':
            plat = template_name[:template_name.find('_')]
            if plat == 'ASR9000':
                ios = 'xr'
                plat = '9000'
            elif plat == 'NX9300':
                ios = 'nx'
                plat = 'nx9k'
            elif plat == 'NX9500':
                ios = 'nx'
            elif plat == 'ASR1000':
                ios = 'ios'
                plat = 'asr'
            elif plat == 'C3750 C3850':
                ios = 'ios'
                plat = 'C3750'
            elif plat == 'C3900 C2900':
                ios = 'ios'
                plat = 'C4500'
            elif plat == 'C3800 C2800':
                ios = 'ios'
                plat = 'C4500'
            elif plat == 'NX7000':
                ios = 'nx'
                plat = '7000'
            elif plat == 'ARISTA':
                ios = 'EOS'
            elif plat == 'VDX':
                ios = 'NOS'
            template_name = template_name[template_name.find('_') + 1:]
        # NEED TO ADD $ FOR END CHECK

        match = re.search(r"(.+)_Template$", template_name)
        if match:
            template_name = match.group(1)
        self.type = template_name
        self.template_name = template_name
        self.input_str = ""
        # check if file_name is there or not
        # if 
        q1 = template_db.objects.filter(ios=ios, plat=plat, tech=tech, template=self.template_name,
                                        customer__contains=customer).values_list("filename").last()
        if q1 and q1[0]:
            file_name = q1[0]
        else:
            file_name = template_name.replace(' ', '_')
        if customer != "common":
            if glb_plat_specific_tech.__contains__(tech):
                file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
            else:
                file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + ios + "_" + tech
        else:
            if glb_plat_specific_tech.__contains__(tech):
                file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
            else:
                file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + tech
        # if ext_name then files_name + "_" + 
        if ext_dict.has_key("ext_name") and ext_dict.has_key("action"):
            file_name = file_name + "_" + ext_dict.get("ext_name") + "_" + ext_dict.get("action") + ".txt"
        elif ext_dict.has_key("ext_name"):
            file_name = file_name + "_" + ext_dict.get("ext_name") + ".txt"
        if os.path.exists(file_name):
            pass
        else:
            file_name = file_name.replace(customer + "/", '')
        self.filename_name = file_name
        print 'Template Name'
        print file_name

        # Need to add platform in future or remote plafrom
        # need to add currunt_user in the filter
        if template_db.objects.filter(ios=ios, plat__in=['any', plat], tech=tech, template=self.type):
            try:
                entry = template_db.objects.get(ios=ios, plat__in=['any', plat], tech=tech, template=self.type)
                if entry:
                    self.db_inputs = entry.inputs
            except:
                entry = template_db.objects.get(ios=ios, plat__in=[plat], tech=tech, template=self.type)
                if entry:
                    self.db_inputs = entry.inputs

    # need to remote not in used
    def update_user_input_value(self, para, taskid="", subtaskid=""):
        # para = {'neigh_ip': "1.1.1.1", 'neigh_as': "65001"}
        # print " USER INPUT PARA DB ", taskid, ">>>> ", subtaskid
        if taskid != "":
            # print "entry to DB"
            for field_name in para.iterkeys():
                if para.get(field_name) and not re.search('<\S+>', para.get(field_name)):
                    if not UserInputValueDb.objects.filter(field_name=field_name, user=self.user_name, taskid=taskid,
                                                           subtaskid=subtaskid):
                        p1 = UserInputValueDb(field_name=field_name, field_value=para.get(field_name),
                                              user=self.user_name, taskid=taskid, subtaskid=subtaskid)
                        p1.save()
                    else:
                        entry = UserInputValueDb.objects.filter(field_name=field_name, user=self.user_name,
                                                                taskid=taskid, subtaskid=subtaskid).last()
                        # p1 = UserInputValueDb.objects.filter(field_name=field_name, user=self.user_name).update(field_name=field_name, field_value=para.get(field_name), user=self.user_name)
                        p1 = UserInputValueDb.objects.filter(id=entry.id).update(field_value=para.get(field_name))
                        # p1 = UserInputValueDb.objects.filter(id=entry.id).update(field_name=field_name, field_value=para.get(field_name), user=self.user_name)
                        # old_entry = UserInputValueDb.objects.get(field_name=field_name, user=self.user_name)
                        # old_entry.delete()
                        # p1 = UserInputValueDb(field_name=field_name, field_value=para.get(field_name), user=self.user_name)
                        # p1.save()
                        # return True
        else:
            for field_name in para.iterkeys():
                if para.get(field_name) and not re.search('<\S+>', para.get(field_name)):
                    if not UserInputValueDb.objects.filter(field_name=field_name, user=self.user_name):
                        p1 = UserInputValueDb(field_name=field_name, field_value=para.get(field_name),
                                              user=self.user_name)
                        p1.save()
                    else:
                        entry = UserInputValueDb.objects.filter(field_name=field_name, user=self.user_name).last()
                        # p1 = UserInputValueDb.objects.filter(field_name=field_name, user=self.user_name).update(field_name=field_name, field_value=para.get(field_name), user=self.user_name)
                        p1 = UserInputValueDb.objects.filter(id=entry.id).update(field_value=para.get(field_name))

    # def get_last_user_input_value(self, field_name):
    #     field_value = ""
    #     entry = UserInputValueDb.objects.filter(field_name=field_name, user= self.user_name)
    #     if entry:
    #         field_value = UserInputValueDb.objects.get(field_name=field_name, user= self.user_name)
    #         # print field_value
    #     return field_value

    def updateTemplate(self, para):
        # para = {'neigh_ip': "1.1.1.1", 'neigh_as': "65001"}
        output = ""
        output2 = []
        with open(self.filename_name) as f:
            for line in f:
                # static
                # output = ""
                # output2 = []
                # para = {'as_num': "<as_num>",'nei_ip': "<nei_ip>"}
                # # para = {'nei_ip': "1.1.1.1", 'as_num': "65001"}
                # line = 'neighbor <nei_ip> remote-as <as_num>'
                # static
                flag_conflict = False
                match = re.search(r"<\S+>/<\S+>", line)
                if match:
                    flag_conflict = True
                    line = re.sub('>/<', '> /<', line)
                for match in re.finditer(r"<\S+>", line):
                    var = match.group().replace('<', '').replace('>', '')
                    var = re.sub(' ', '', var)
                    if para.has_key(var):
                        if para.get(var):
                            para_val = para.get(var)
                            if re.search(r"<\S+>", para_val):
                                para_val = para_val.replace('<', '&#60;').replace('>', '&#62;')
                            new_val = "555" + para_val + "666"
                            line = re.sub(r'<%s>' % var, new_val, line)
                # print line
                output = output + "\n" + line
                output2.append(line)
                # print output2

        # print output
        self.output = output2
        # self.output = output.split(' ')
        return self.output

    # This expand the input values to the list example eth3/1-3 -> eth3/1, eth3/2, eth3/3
    def convet_inputs_to_dict(self, user_para={}, template_name=""):
        self.new_user_para = {}
        for user_variable in user_para:
            user_range_str = user_para.get(user_variable)
            if user_range_str:
                # print " Range >>>>>>>"
                # below code tweak to enable range for vlan_id on non aci added on 09-12-2017
                if user_variable == "vlan_id" and 0:
                    new_list = get_list_from_range(user_range_str)
                # elif template_name and re.search("ACI", template_name):
                #     new_list = [user_range_str]
                else:
                    # if user_variable == "hostname"  or user_variable == "vlan_id" or 'physical_port' in user_variable:
                    if user_variable == "hostname" or 'physical_port' in user_variable:
                        new_list = [user_range_str]
                        # print "*********new_list********"
                        # print new_list
                    elif "," in user_range_str:
                        new_list = user_range_str.split(",")
                    else:
                        new_list = get_list_from_range(user_range_str)
            else:
                new_list = []
            self.new_user_para[user_variable] = new_list
        self.user_para = user_para
        return self.new_user_para

    def convet_template_to_config(self, request, user_input_range_dict={}, user_feature_list=[], optional_para=['']):

        # user_input_range_dict = {"vlan_id": ['101','102','105','108'], "vxlan_id": ['9101','9102','9105'], 'name':['vxlan_vlan'],'bgp_as': ['<bgp_as>'], 'mcast_group': ['225.1.1.1', '225.1.1.2']}
        #
        # line_list = ['feature vxlan', '!', 'vlan <vlan_id>  !tag_start vlan_id', 'name <name>', 'vxlan <vxlan_id> !tag_end']
        # line_list.append('ip route <mcast_group> 1.1.1.2 !tag_start vlan_id !tag_end')
        # line_list.append('router bgp <bgp_as>')
        # line_list.append('neigh 1.1.1.1 remote_as')
        # line_list = line_list + ['interface vlan<vlan_id>  !tag_start mcast_group', 'ip address <mcast_group> remote <vlan_id>', 'no shut !tag_end']
        no_vrf_flag = False
        start_flag = False
        skip_section = True
        end_flag = False
        save_flag = False

        combine_commands = ''
        range_variable_name = ''
        save_to_filename = ''
        group_commands_list = []
        save_to_file_list = {}
        if get_key_value(user_input_range_dict, 'vrf_option') == [u'No']:
            # user_input_range_dict.__delitem__('vrf_name')
            no_vrf_flag = True
        skip_flag = False
        with open(self.filename_name) as f:
            for line in f:
                group_commands = ''
                single_commands = ''

                line_skip_flag = False
                # new code to skip the expantion of commands by modifying the disc
                for optional in optional_para:
                    if re.search('<%s>' % optional, line):
                        if get_key_value(user_input_range_dict, optional)[0] == '<' + optional + '>':
                            print 'line delete'
                            print line
                            print user_input_range_dict
                            line_skip_flag = True
                            continue

                if re.search('\[\[\[\[(.+)\]\]\]\]', line):
                    # print line
                    match = re.search('\[\[\[\[(.+)\]\]\]\]', line)
                    if match:
                        if match.group(1) == "end":
                            # line_skip_flag = True
                            skip_flag = False
                            continue
                        else:
                            condition = match.group(1)
                            # print 'condition ', condition
                            # print 'condition >>res    ', check_commands_condition(condition, user_input_range_dict)
                            if not check_commands_condition(condition, user_input_range_dict):
                                # line_skip_flag = True
                                skip_flag = True
                                continue
                            else:
                                # line_skip_flag = True
                                skip_flag = False
                                continue

                if re.search(r'\X\X\X\X', line):
                    skip_section = False
                    continue
                elif re.search(r"YY", line):
                    skip_section = True
                    continue
                if not skip_section:
                    continue
                #
                # if  skip_section and not skip_flag:
                #     skip_flag = False
                # elif not skip_section and not skip_flag:
                #     skip_flag = True

                # if skip_flag:
                #     print line
                if not skip_flag:
                    if no_vrf_flag:
                        line = line.replace('vrf <vrf_name>', '')
                    if re.search('!tag_skip', line):
                        match = re.search('!tag_skip\s+(\S+)', line)
                        if match:
                            skip_variable_name = match.group(1)
                            line = line.split('!tag_skip')[0]
                            if user_input_range_dict.has_key(skip_variable_name):
                                skip_variable_value = user_input_range_dict.get(skip_variable_name)
                                skip_variable_value = ','.join(skip_variable_value)
                                skip_variable_value = [skip_variable_value]
                                # set new value in the disct
                                user_input_range_dict[skip_variable_name] = skip_variable_value
                    if re.search(r'!tag_save', line):
                        match1 = re.search(r'!tag_save\s+(.+)', line)
                        if match1:
                            # print " <><><><><><><><>>>", match1.group(1)
                            save_flag = True
                            save_to_filename = match1.group(1)
                            save_to_file_list[save_to_filename.split('.')[0]] = []
                            line = line.split('!tag_save')[0]
                    if re.search(r'!tag_save_end', line) and save_flag:
                        save_flag = False
                        line = re.sub('!tag_save_end', '', line)
                    if re.search('!tag_start', line) :
                        match = re.search('!tag_start\s+(\S+)', line)
                        if match:
                            range_variable_name = match.group(1)
                            temp_line = line
                            line = line.split('!tag_start')[0]
                            if user_input_range_dict.has_key(range_variable_name) and range_variable_name:
                                start_flag = True
                                if re.search('!tag_end', temp_line):
                                    start_flag = False
                                    line = re.sub('!tag_end', '', line)
                                    # need to fix why is it not working for mvpn temaplate
                                    range_commands = commands_with_input_range([line], user_input_range_dict,
                                                                               self.user_para, range_variable_name)
                                    combine_commands = combine_commands + range_commands
                                    range_variable_name = ''

                        group_commands_list = []


                    match = re.search(r"@for_feature_(\S+)", line)
                    if match:
                        feature_name = match.group(1)
                        # user_feature_list = ['vpc']
                        # Handling NOT feature
                        #                    print 'match_1'
                        #                    print match.group(1)
                        if re.search(r"not_\S+", match.group(1)):
                            match = re.search(r"not_(\S+)", match.group(1))
                            if match:
                                feature_name = match.group(1)
                                if user_feature_list.__contains__(feature_name):
                                    line_skip_flag = True
                                    continue
                                else:
                                    line = re.sub('@for_feature_(\S+)', '', line)
                        elif re.search(r"\S+_or_\S+", match.group(1)):
                            match = re.search(r"(\S+)_or_(\S+)", match.group(1))
                            if match:
                                if user_feature_list.__contains__(match.group(1)) or user_feature_list.__contains__(
                                        match.group(2)):
                                    line = re.sub('@for_feature_(\S+)', '', line)
                                else:
                                    continue

                        elif re.search(r"\w+_and_\w+", match.group(1)):
                            print 'in match_2'
                            match = re.search(r"(\w+)_and_(\w+)", match.group(1))
                            if match:
                                if user_feature_list.__contains__(match.group(1)) and user_feature_list.__contains__(
                                        match.group(2)):
                                    line = re.sub('@for_feature_(\S+)', '', line)
                                else:
                                    continue
                        elif user_feature_list.__contains__(feature_name):
                            line = re.sub('@for_feature_(\S+)', '', line)
                        else:
                            line_skip_flag = True
                            # continue
                    if re.search('!tag_end', line) and start_flag:
                        start_flag = False
                        end_flag = True
                        line = re.sub('!tag_end', '', line)

                    if start_flag:
                        if not line_skip_flag:
                            group_commands_list.append(line)
                    elif end_flag:
                        print "group_commands_list"
                        # print group_commands_list
                        if not line_skip_flag:
                            group_commands_list.append(line)
                        # Call the function to expand the commands for given range, pass the group_commands_list and list dict
                        # print  "reset the group_commands_list"
                        # print group_commands_list
                        range_commands = commands_with_input_range(group_commands_list, user_input_range_dict,
                                                                   self.user_para, range_variable_name)

                        if save_flag:
                            save_to_file_list[save_to_filename.split('.')[0]] += range_commands.split("\n")
                        else:
                            combine_commands = combine_commands + range_commands
                        range_variable_name = ''
                        group_commands_list = []
                        end_flag = False

                    elif re.search('<(\S+)>', line):
                        # print line
                        if not line_skip_flag:
                            line = commands_without_input_range(request, line, user_input_range_dict)
                            if save_flag:
                                save_to_file_list[save_to_filename.split('.')[0]].append(line)
                                continue
                            if line:
                                combine_commands = combine_commands + '\n' + line
                    else:
                        if not line_skip_flag:
                            if save_flag:
                                save_to_file_list[save_to_filename.split('.')[0]].append(line)
                            else:
                                combine_commands = combine_commands + '\n' + line.decode('utf8')
        if len(save_to_file_list) > 0:
            taskid = request.session.get("taskid")
            FILE_SAVE_DIR = "/home/ubuntu/prepro/mysite/mysite/user_outputs/" + str(taskid) + "/"
            if not os.path.isdir(FILE_SAVE_DIR):
                os.makedirs(FILE_SAVE_DIR)
            combine_commands = combine_commands + 'File Saved lines:' + '\n'
            for key, value in save_to_file_list.iteritems():
                print ">>>>>>", key
                combine_commands = combine_commands + "Filename: " + str(key) + '\n'
                file_data = open(FILE_SAVE_DIR + key + ".txt", "w+")
                for cmd_lines in value:
                    combine_commands = combine_commands + '\n' + cmd_lines
                    cmd_lines = re.sub('555', '', cmd_lines)
                    cmd_lines = re.sub('666', '', cmd_lines)
                    file_data.write(cmd_lines)
                file_data.close()
            combine_commands = combine_commands + '!- File Saved lines end'

        self.combine_commands = combine_commands.split('\n')
        print "self.combine_commands"
        print self.combine_commands
        return self.combine_commands

    def updateTemplate(self, para):
        output = ""
        output2 = []
        with open(self.filename_name) as f:
            for line in f:
                flag_conflict = False
                match = re.search(r"<\S+>/<\S+>", line)
                if match:
                    flag_conflict = True
                    line = re.sub('>/<', '> /<', line)
                # to get the feature list
                for match in re.finditer(r"<\S+>", line):
                    var = match.group().replace('<', '').replace('>', '')
                    var = re.sub(' ', '', var)
                    if para.has_key(var):
                        if para.get(var):
                            para_val = para.get(var)
                            if re.search(r"<\S+>", para_val):
                                para_val = para_val.replace('<', '&#60;').replace('>', '&#62;')
                            new_val = "555" + para_val + "666"
                            line = re.sub(r'<%s>' % var, new_val, line)
                output = output + "\n" + line
                output2.append(line)
                # print output2
        # print output
        self.output = output2
        # self.output = output.split(' ')
        return self.output

    def getInputsFromDb(self):
        return self.db_inputs

    # def update_aci_interface_db(self, user_dict):


class GetInputsForTemplate:
    def __init__(self, user_ios, user_plat, user_tech, user_type):
        ''' Get the input list for new template'''
        self.template_input_list = []
        self.template_input_list = ['template_name', 'template_text']

    def getTemplateInputs(self):
        return self.template_input_list


# com_dict = {'tech': user_ios, 'ios': user_ios, 'plat': user_plat, 'type': user_type}
class ParseNewTemplate:

    '''
    Description:
        Class is used to create template and update the database.
	Inputs:
        com_dict, customer, template_name, txttbox, ext_dict
    Output:
		Return template name and TRUE and FALSE.

    '''
    def __init__(self, com_dict, customer, template_name, txttbox, ext_dict={}):
        ''' Process the txt box for creating new or modifying the template. Get the input list'''
        global glb_plat_specific_tech
        global glb_template_dir
        tech = ConvertUeseInputs('tech', com_dict.get('tech'))
        plat = ConvertUeseInputs('plat', com_dict.get('plat'))
        ios = ConvertUeseInputs('ios', com_dict.get('ios'))
        self.ios = ios
        self.plat = plat
        self.tech = tech
        self.customer = customer
        input_list = []
        match = re.search(r"(.+)_Template$", template_name)
        if match:
            template_name = match.group(1)
        self.template_name = template_name
        self.input_str = ""
        self.feature_list = []
        file_name = template_name.replace(' ', '_')
        # if glb_plat_specific_tech.__contains__(tech):
        # file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
        # else:
        # file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + tech
        if customer != "common":
            if glb_plat_specific_tech.__contains__(tech):
                file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
            else:
                file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + ios + "_" + tech
        else:
            if glb_plat_specific_tech.__contains__(tech):
                file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
            else:
                file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + tech
        # temp_output = u'router bgp <as_num>\r\nneigh <neigh_ip> remote-as <as_num>\r\n'

        # if ext_name then files_name + "_" + 
        if ext_dict.has_key("ext_name") and ext_dict.has_key("action"):
            file_name = file_name + "_" + ext_dict.get("ext_name") + "_" + ext_dict.get("action") + ".txt"
        elif ext_dict.has_key("ext_name"):
            file_name = file_name + "_" + ext_dict.get("ext_name") + ".txt"

        output_list = txttbox.split('\r\n')
        with open(file_name, 'w') as the_file:
            for cmd in output_list:
                flag_conflict = False
                match = re.search(r"<\S+>/<\S+>", cmd)
                if match:
                    flag_conflict = True
                    cmd = re.sub('>/<', '> /<', cmd)
                # match = re.search(r"@for_feature_(\S+)", line)
                # if match:
                #     feature_flag = True
                #     line = re.sub('@for_feature_(\S+)', '', line)
                #     if not self.feature_list.__contains__(match.group(1)):
                #         self.feature_list.append(match.group(1))
                for match in re.finditer(r"<\S+>", cmd):
                    var = match.group().replace('<', '').replace('>', '')
                    if not input_list.__contains__(var):
                        var = re.sub(' ', '', var)
                        input_list.append(var)
                if flag_conflict:
                    cmd = re.sub('> /<', '>/<', cmd)
                # print cmd
                the_file.write(cmd + '\n')
        the_file.close()
        if input_list:
            self.input_str = ' '.join(input_list)

    def getTemplateInput(self):
        return self.input_str

    def addTemplateParaToDb(self):
        entry = template_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name,
                                           inputs=self.input_str)
        if not entry:
            p1 = template_db(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name,
                             inputs=self.input_str)
            p1.save()
            return True
        else:
            return False

    def overwriteTemplateParaToDb(self):
        if not template_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name,
                                          customer=self.customer):
            p1 = template_db(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name,
                             customer=self.customer,
                             inputs=self.input_str, type="1")
            p1.save()
            return True
        else:
            # p1 = template_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name).update(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name, inputs=self.input_str)
            entry = template_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name,
                                            customer=self.customer)
            p1 = template_db.objects.filter(id=entry.id).update(inputs=self.input_str)
            # old_entry = template_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name)
            # old_entry.delete()
            # print 'addTemplateParaToDb: entry already exists - Overwritting'
            # p1 = template_db(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name, inputs=self.input_str)
            # p1.save()
            return True


# com_dict = {'tech': user_ios, 'ios': user_ios, 'plat': user_plat, 'type': user_type}

class ParseNewTpFile:

    '''
    Description:
        In this class we assign the name to templates and called with respect to user selection on webapp.
	Inputs:
		com_dict, template_name, customer, ext_dict
	Output:
        Create and display the templates.



    '''

    def __init__(self, com_dict, template_name, customer, ext_dict={}):
        ''' Process the txt box for creating new or modifying the template. Get the input list'''
        # port_mode: Server Port Mode default: Trunk
        # port_mode: Server Port Mode Ex: 1.1.1.1
        global glb_plat_specific_tech
        global glb_template_dir
        tech = ConvertUeseInputs('tech', com_dict.get('tech'))
        plat = ConvertUeseInputs('plat', com_dict.get('plat'))
        ios = ConvertUeseInputs('ios', com_dict.get('ios'))
        print com_dict
        self.ios = ios
        self.plat = plat
        self.tech = tech
        input_list = []
        feature_intputs = []
        feature_dic = {}
        self.feature_list = []
        self.optional_list = []
        if ios == 'Any_IOS' and plat == 'Any_Platform':
            plat = template_name[:template_name.find('_')]
            if plat == 'ASR9000':
                ios = 'xr'
                plat = '9000'
            elif plat == 'NX9300':
                ios = 'nx'
                plat = 'nx9k'
            elif plat == 'NX9500':
                ios = 'nx'
            elif plat == 'ASR1000':
                ios = 'ios'
                plat = 'asr'
            elif plat == 'C3750 C3850':
                ios = 'ios'
                plat = 'C3750'
            elif plat == 'C3900 C2900':
                ios = 'ios'
                plat = 'C4500'
            elif plat == 'C3800 C2800':
                ios = 'ios'
                plat = 'C4500'
            elif plat == 'NX7000':
                ios = 'nx'
                plat = '7000'
            elif plat == 'ARISTA':
                ios = 'EOS'
            elif plat == 'VDX':
                ios = 'NOS'
            template_name = template_name[template_name.find('_') + 1:]
        print ">>>>>>><<<<", template_name
        match = re.search(r"(.+)_Template$", template_name)
        if match:
            template_name = match.group(1)
        self.type = template_name
        self.template_name = template_name
        print self.template_name
        self.input_str = ""
        feature_option = {}
        q1 = template_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name,
                                        customer__contains=customer).values_list("filename").last()
        if q1:
            print q1
            print ">>>>File name .. from DB", q1[0]
        else:
            print ">>>>>>>template_name", template_name
        if q1 and q1[0]:
            file_name = q1[0]
        else:
            print template_name.replace(' ', '_')
            file_name = template_name.replace(' ', '_')
        tech = tech.replace('\t', '_')
        # print tech
        # if glb_plat_specific_tech.__contains__(tech):
        # file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
        # else:
        # file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + tech
        if customer != "common":
            if glb_plat_specific_tech.__contains__(tech):
                file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
            else:
                file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + ios + "_" + tech
        else:
            if glb_plat_specific_tech.__contains__(tech):
                file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
            else:
                file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + tech
        print file_name
        # if ext_name then files_name + "_" + 
        if ext_dict.has_key("ext_name") and ext_dict.has_key("action"):
            file_name = file_name + "_" + ext_dict.get("ext_name") + "_" + ext_dict.get("action") + ".txt"
        elif ext_dict.has_key("ext_name"):
            file_name = file_name + "_" + ext_dict.get("ext_name") + ".txt"
        if os.path.exists(file_name):
            pass
        else:
            file_name = file_name.replace(customer + "/", '')

        multi_feature_flag = False
        # ce_link:ospf, ce_link:bgp, feature:bfd, feature:max-prefix
        feature_combination_list = []
        # all feature related inputs
        feature_intput_list = []
        start_flag = False
        field_desc_list = []
        print 'File Name:' + file_name
        with open(file_name, 'r') as the_file:
            for line in the_file:
                match = re.search(r"Template Parameters End:", line)
                if match:
                    break
                match = re.search(r"Template Parameters:", line)
                if match:
                    start_flag = True
                    continue
                if start_flag:
                    field_dict = {}
                    match = re.search(r"(\S+):", line)
                    if match:
                        field_dict['field'] = match.group(1)
                    match = re.search(r":\s+(.+)", line)
                    if match:
                        if match.group(1).split('default: ').__len__() > 1:
                            field_dict['desc'] = match.group(1).split('default: ')[0]
                            field_dict['default'] = match.group(1).split('default: ')[1].strip()
                        elif match.group(1).split('ex: ').__len__() > 1:
                            field_dict['desc'] = match.group(1).split('ex: ')[0]
                            field_dict['example'] = 'Ex:' + match.group(1).split('ex: ')[1].strip()
                        elif match.group(1).split('tag_optional').__len__() > 1:
                            field_dict['desc'] = match.group(1).split('tag_optional')[0]
                            self.optional_list.append(line.split(' ')[0].split(':')[0])
                            field_dict['example'] = '(Optional)'
                        else:
                            field_dict['desc'] = match.group(1)
                    # match = re.search(r"default:\s+(.+)", line)
                    # if match:
                    #     field_dict['default'] = match.group(1)
                    field_desc_list.append(field_dict)

        self.field_desc_list = field_desc_list
        with open(file_name, 'r') as the_file:
            feature_data = {}
            for line in the_file:
                feature_name = ""
                option_name = ""
                new_feature_flag = False
                # router ospf <router_id> @for_feature_ce_link:ospf
                match = re.search(r"@for_feature_(\S+)", line)
                feature_options = ""
                if match:
                    # not_ is not used here, used after input sumbutted
                    # f_name = re.sub('not_', '', match.group(1))
                    f_name = match.group(1)
                    # used in view to set user feature values
                    if not feature_combination_list.__contains__(f_name):
                        feature_combination_list.append(f_name)
                    if f_name.__contains__(':'):
                        # {"note": "please select choices", "type": "checkbox", "name": "games", "default1": "",
                        #  "desc": "Select the options",
                        #  "options": [{"label": "abc", "value": "abc", "hide": "hide", "trigger": ["hidden", "hidden1"]},
                        #              {"label": "xyz", "value": "xyz"}]},
                        feature_name = f_name.split(':')[0]
                        option_name = f_name.split(':')[1]
                        # feature_type = 'checkbox'
                        feature_type = 'radio'
                    else:
                        feature_name = 'features'
                        feature_type = 'checkbox'
                        # feature_type = 'radio'
                        option_name = f_name
                    # feature_data = {'ce_link': {'options': [{'ospf': ['router_id', 'area_id']}, {'bgp': ['bgp_remote_as', 'neigh_ip']}]}, 'ce_link2': {'options': [{'isis': []}]}}
                    # print multi_level_check(my_dict, 'ce_link2', 'options', 'isis')
                    # print multi_level_value(my_dict, 'ce_link2', 'options', 'isis')
                    line = re.sub('@for_feature_(\S+)', '', line)
                    if feature_name == 'features':
                        if not self.feature_list.__contains__(feature_name):
                            self.feature_list.append(feature_name)
                        if not multi_feature_flag:
                            multi_feature_flag = True
                            feature_dic[feature_name] = []
                            feature_data[feature_name] = {}
                            feature_data[feature_name]['type'] = feature_type
                            feature_data[feature_name]['options'] = [{option_name: []}]
                        if not multi_level_check(feature_data, feature_name):
                            print 'error'
                        else:
                            if not multi_level_check(feature_data, feature_name, 'options'):
                                feature_data[feature_name]['options'] = []
                            else:
                                if not multi_level_check(feature_data, feature_name, 'options', option_name):
                                    feature_data[feature_name]['options'].append({option_name: []})
                    else:
                        if not self.feature_list.__contains__(feature_name):
                            self.feature_list.append(feature_name)
                            feature_dic[feature_name] = []
                            feature_data[feature_name] = {}
                            feature_data[feature_name]['type'] = feature_type
                            feature_data[feature_name]['options'] = [{option_name: []}]
                        if not multi_level_check(feature_data, feature_name):
                            print 'error'
                        else:
                            if not multi_level_check(feature_data, feature_name, 'options'):
                                feature_data[feature_name]['options'] = []
                            else:
                                if not multi_level_check(feature_data, feature_name, 'options', option_name):
                                    feature_data[feature_name]['options'].append({option_name: []})
                m = re.search(r'<(\S+)>', line)
                if m:
                    if re.search(r'\d', m.group(1)):
                        exp = "<\S+>"
                    else:
                        exp = "<\w+>"
                    for match in re.finditer(exp, line):
                        var = match.group().replace('<', '').replace('>', '')
                        if feature_name:
                            if multi_level_check(feature_data, feature_name, 'options', option_name):
                                el_index = multi_level_index(feature_data, feature_name, 'options', option_name)
                                feature_intputs = multi_level_value(feature_data, feature_name, 'options', option_name)
                                if not feature_intputs.__contains__(var):
                                    if not input_list.__contains__(var):
                                        feature_data[feature_name]['options'].__delitem__(el_index)
                                        feature_intputs.append(var)
                                        # total feature related intputs
                                        if not feature_intput_list.__contains__(var):
                                            feature_intput_list.append(var)
                                        feature_data[feature_name]['options'].insert(el_index,
                                                                                     {option_name: feature_intputs})
                                        # feature_intputs = feature_dic.get(feature_name)
                                        # feature_intputs.append(var)
                        elif not input_list.__contains__(var):
                            var = re.sub(' ', '', var)
                            input_list.append(var)
                            # if feature_name:
                            #     feature_dic[feature_name] = feature_intputs
        new_input_list = []
        for input in input_list:
            match = re.match(r'(\w+)\+\d+', input)
            if match:
                if match.group(1) not in new_input_list:
                    new_input_list.append(match.group(1))
            elif re.search(r"task_id|taskid", input) or re.search(r"vpc_peer_id", input) or re.search(r"aci_int_tag",
                                                                                                      input):
                continue
            else:
                if input not in new_input_list:
                    new_input_list.append(input)
        if new_input_list:
            self.input_str = ' '.join(new_input_list)
        self.feature_data = feature_data
        self.feature_intput_list = feature_intput_list
        self.feature_combination_list = feature_combination_list

    def get_feature_list(self):
        return self.feature_list

    def get_feature_data(self):
        return self.feature_data

    def get_feature_data(self):
        return self.feature_data

    def get_feature_intput_list(self):
        return self.feature_intput_list

    def get_feature_combination_list(self):
        return self.feature_combination_list

    def overwriteTlDb(self):
        print " In Overwrite TEmplate "
        if not template_db.objects.filter(ios=self.ios, plat__in=['any', self.plat], tech=self.tech,
                                          template=self.template_name):
            print "Inserting New Entry ", self.template_name
            p1 = template_db(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name,
                             inputs=self.input_str)
            p1.save()
            return True
        else:
            print "Updating New Entry ", self.template_name
            try:
                entry = template_db.objects.get(ios=self.ios, plat__in=['any', self.plat], tech=self.tech,
                                                template=self.template_name)
                # p1 = template_db.objects.filter(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name).update(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name, inputs=self.input_str)
                p1 = template_db.objects.filter(id=entry.id).update(inputs=self.input_str)
            except:
                print "Error Occured still updarteed"
                entry = template_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech,
                                                template=self.template_name)
                p1 = template_db.objects.filter(id=entry.id).update(inputs=self.input_str)
            # old_entry = template_db.objects.get(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name)
            # old_entry.delete()
            # print 'overwriteTlDb: entry already exists - Overwriting'
            # p1 = template_db(ios=self.ios, plat=self.plat, tech=self.tech, template=self.template_name, inputs=self.input_str)
            # p1.save()
            return True


# need to add 3rd parameter


# need to add 3rd parameter
class GetInputVariableDictOpration:
    '''
    Description:
        Class is used to section of template and loads inputs.
	Inputs:
	    para_list,com_dict,customer,template_name , ext_dict
	Output:
        Return dict input_para_dict.
    '''
    global preso_variable_output
    global glb_tech_options

    def __init__(self, para_list, template_name="", user_sel_dict={}):
        global preso_variable_output
        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format
        Example:
        input: ['src_ip', 'in_int', 'out_int', 'des_ip', 'des_net', 'dst_ml', 'in_l3', 'ou_l3']
        output: [{'default1': '', 'format': 'ip', 'type': 'text', 'name': 'src_ip', 'desc': 'Enter <src_ip>'}, {
        '''
        tech = ''
        if user_sel_dict:
            ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
            plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))
            tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
            type = ConvertUeseInputs('type', user_sel_dict.get('type'))

        new_var_dict = {}
        input_para_dict = []
        para_dict = {}
        for el in para_list:
            output = ''
            name = el
            desc = 'Enter %s' % name
            if el == 'template_name':
                para_dict = {'name': name, 'type': 'text', 'desc': 'Template Name', 'default1': template_name}
            elif el == 'template_text':
                desc = 'Template Text'
                # get file contents  in variable fc

                para_dict = {'name': name, 'type': 'textarea', 'desc': desc, 'default1': '', 'rows': '10', 'format': '',
                             'default1': 'Pre Check Verification:\n'
                                         '\n!- Pre Check Verification end\n'
                                         'Prerequisites and Assumptions:\n'
                                         '\nFeatures:\n'
                                         'Configuration:\n'
                                         '\n!<-- Configuration end -->!\n'
                                         'Post Check Verification:\n'
                                         'Post Check Verification end:\n'
                                         '\nConfiguration Testing:\n'
                                         '\nConfiguration Testing end\n'
                                         '\nRoll-back Configuration:\n'
                                         '!- Roll-back Configuration end\n'}
            para_dict['output'] = output
            input_para_dict.append(para_dict)
            new_var_dict[el] = para_dict
        self.input_para_dict = {"column": "12", "newline": "yes", "inputs": input_para_dict}
        self.new_var_dict = new_var_dict
        preso_variable_output = new_var_dict

    def getInputDict(self):
        return self.input_para_dict

    def format_variable_old_to_new(self):
        return self.new_var_dict


class GetInputVariableDictOpration_new:
    '''
    Description:
        Class is used to section of template and loads inputs.
	Inputs:
		para_list,com_dict,customer,template_name , ext_dict
	Output:
        Return dict input_para_dict.

    '''
    global preso_variable_output
    global glb_tech_options

    def __init__(self, para_list, com_dict, customer, template_name="", ext_dict={}):
        global preso_variable_output
        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format
        Example:
        input: ['src_ip', 'in_int', 'out_int', 'des_ip', 'des_net', 'dst_ml', 'in_l3', 'ou_l3']
        output: [{'default1': '', 'format': 'ip', 'type': 'text', 'name': 'src_ip', 'desc': 'Enter <src_ip>'}, {
        '''
        tech = ''
        global glb_plat_specific_tech
        global glb_template_dir
        tech = ConvertUeseInputs('tech', com_dict.get('user_tech'))
        plat = ConvertUeseInputs('plat', com_dict.get('user_plat'))
        ios = ConvertUeseInputs('ios', com_dict.get('user_ios'))
        self.ios = ios
        self.plat = plat
        self.tech = tech
        self.customer = customer
        template_text = ""
        if ios == 'Any_IOS' and plat == 'Any_Platform':
            plat = template_name[:template_name.find('_')]
            if plat == 'ASR9000':
                ios = 'xr'
                plat = '9000'
            elif plat == 'NX9300':
                ios = 'nx'
                plat = 'nx9k'
            elif plat == 'NX9500':
                ios = 'nx'
            elif plat == 'ASR1000':
                ios = 'ios'
                plat = 'asr'
            elif plat == 'C3750 C3850':
                ios = 'ios'
                plat = 'C3750'
            elif plat == 'C3900 C2900':
                ios = 'ios'
                plat = 'C4500'
            elif plat == 'C3800 C2800':
                ios = 'ios'
                plat = 'C4500'
            elif plat == 'NX7000':
                ios = 'nx'
                plat = '7000'
            elif plat == 'ARISTA':
                ios = 'EOS'
            elif plat == 'VDX':
                ios = 'NOS'
            template_name = template_name[template_name.find('_') + 1:]
        match = re.search(r"(.+)_Template$", template_name)
        if match:
            template_name = match.group(1)
        self.type = template_name
        self.template_name = template_name
        self.input_str = ""
        file_name = template_name.replace(' ', '_')
        tech = tech.replace('\t', '_')
        print tech
        if customer != "common":
            if glb_plat_specific_tech.__contains__(tech):
                file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
            else:
                file_name = glb_template_dir + "/" + customer + "/" + file_name + "_" + ios + "_" + tech
        else:
            if glb_plat_specific_tech.__contains__(tech):
                file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + plat + "_" + tech
            else:
                file_name = glb_template_dir + "/" + file_name + "_" + ios + "_" + tech

        # if ext_name then files_name + "_" + 
        if ext_dict.has_key("ext_name") and ext_dict.has_key("action"):
            file_name = file_name + "_" + ext_dict.get("ext_name") + "_" + ext_dict.get("action") + ".txt"
        elif ext_dict.has_key("ext_name"):
            file_name = file_name + "_" + ext_dict.get("ext_name") + ".txt"

        print 'File Name:' + file_name
        with open(file_name, 'r') as the_file:
            for line in the_file:
                template_text += line
        new_var_dict = {}
        input_para_dict = []
        para_dict = {}
        for el in para_list:
            output = ''
            name = el
            desc = 'Enter %s' % name
            if el == 'template_name':
                para_dict = {'name': name, 'type': 'text', 'desc': 'Template Name', 'default1': template_name}
            elif el == 'template_text':
                desc = 'Template Text'
                para_dict = {'name': name, 'type': 'textarea', 'desc': desc, 'default1': '', 'rows': '10', 'format': '',
                             'default1': template_text}
            para_dict['output'] = output
            input_para_dict.append(para_dict)
            new_var_dict[el] = para_dict
        self.input_para_dict = {"column": "12", "newline": "yes", "inputs": input_para_dict}
        self.new_var_dict = new_var_dict
        preso_variable_output = new_var_dict

    def getInputDict(self):
        return self.input_para_dict


class Firewall_Resend_InputVariable:
    def __init__(self, request, com_dict, user_value_dict, input_data_list):
        self.para_dict = []
        modified_para_dict = []
        if type(input_data_list) is dict:
            if input_data_list.has_key('column'):
                input_data_list = input_data_list.get('inputs')

                # input_dict = {u'name': u'features', u'note': u'FEATURES', u'default1': u'', u'type': u'checkbox', u'options': [
                #     {u'trigger': [u'src_object', u'src_net'], u'hide': u'hide', u'value': u'src_object', u'send': u'yes',
                #      u'label': u'Src Object'},
                #     {u'trigger': [u'src_object', u'src_net', u'dst_object', u'dst_net'], u'hide': u'hide', u'value': u'dst_object',
                #      u'send': u'yes', u'label': u'Dst Object'},
                #     {u'trigger': [u'src_object', u'src_net', u'dst_object', u'dst_net', u'service_object', u'port_num'],
                #      u'hide': u'hide', u'value': u'service_object', u'send': u'yes', u'label': u'Service Object'}],
                #  u'desc': u'FEATURES'}

        for input_field in user_value_dict.iterkeys():
            if input_field == 'features':
                feature_list = user_value_dict.get(input_field).split('++')
                # print feature_list
        if not user_value_dict:
            # print "captured here !"
            self.para_dict = input_data_list
        else:
            # print "captured here !2222222"
            option_list = []
            src_check = ''
            dst_check = ''
            ser_check = ''
            work_order_no = ''
            print input_data_list
            for input_dict in input_data_list:
                # print "input_dict"
                # print input_dict
                # input_dict =  {'name': u'remote_vtp_ip', 'format': '', 'default1': '', 'output': '', 'type': 'text',
                # 'desc': 'Remote VTP IP'}], 'newline': 'yes'}
                input_field = input_dict.get('name')
                if input_dict.get('name') == 'features':
                    if feature_list.__contains__('src_object'):
                        src_check = 'checked'
                    option_list.append({'trigger': ['src_object', 'src_net'], 'hide': 'hide',
                                        'value': 'src_object', 'send': 'yes', 'label': 'Src Object',
                                        'checked': src_check})
                    if feature_list.__contains__('dst_object'):
                        dst_check = 'checked'
                    option_list.append({'trigger': ['dst_object', 'dst_net'], 'hide': 'hide',
                                        'value': 'dst_object', 'send': 'yes', 'label': 'Dst Object',
                                        'checked': dst_check})
                    if feature_list.__contains__('service_object'):
                        ser_check = 'checked'
                    option_list.append({'trigger': ['service_object', 'port_num'], 'hide': 'hide',
                                        'value': 'service_object', 'send': 'yes', 'label': 'Service Object',
                                        'checked': ser_check})
                    input_dict['options'] = option_list
                    self.para_dict.append(input_dict)
                elif input_dict.get('name') == 'service_object' or input_dict.get(
                        'name') == 'dst_object' or input_dict.get('name') == 'src_object':
                    if feature_list.__contains__(input_dict.get('name')):
                        self.para_dict.append(input_dict)
                elif input_dict.get('name') == 'tenant_name_2' or input_dict.get(
                        'name') == 'application_name_2' or input_dict.get('name') == 'epg_name_2' or input_dict.get(
                    'name') == 'leaf_id2':
                    if user_value_dict.has_key("leaf_id2") and input_dict.get('name') == 'leaf_id2':
                        leaf = get_apic_data().get("leaf")
                        input_dict['default1'] = user_value_dict.get("leaf_id2")
                        leaf_options = []
                        for each in leaf:
                            dic = {}
                            dic["label"] = each
                            dic["value"] = each
                            leaf_options.append(dic)
                        input_dict['options'] = leaf_options
                    if user_value_dict.has_key("tenant_name_2") and input_dict.get('name') == 'tenant_name_2':
                        tenant = get_apic_data(user_value_dict.get("tenant_name_2")).get("tenant")
                        input_dict['default1'] = user_value_dict.get("tenant_name_2")
                        tnt_options = []
                        for each in tenant:
                            dic = {}
                            dic["label"] = each
                            dic["value"] = each
                            dic["send"] = "yes"
                            tnt_options.append(dic)
                        input_dict['options'] = tnt_options
                    if user_value_dict.has_key("tenant_name_2") and input_dict.get('name') == 'application_name_2':
                        application = get_apic_data(user_value_dict.get("tenant_name_2")).get("app")
                        if user_value_dict.has_key("application_name_2"):
                            input_dict['default1'] = user_value_dict.get("application_name_2")
                        else:
                            input_dict['default1'] = application[0]
                        app_options = []
                        for each in application:
                            dic = {}
                            dic["label"] = each
                            dic["value"] = each
                            dic["send"] = "yes"
                            app_options.append(dic)
                        input_dict['options'] = app_options
                        input_dict["send"] = "yes"
                    if user_value_dict.has_key("application_name_2") and input_dict.get('name') == 'epg_name_2':
                        print "Gotcch here .. !"
                        epg = get_apic_data(user_value_dict.get("tenant_name_2"),
                                            user_value_dict.get("application_name_2")).get("epg")
                        epg_options = []
                        for each in epg:
                            dic = {}
                            dic["label"] = each
                            dic["value"] = each
                            epg_options.append(dic)
                        input_dict['options'] = epg_options

                    self.para_dict.append(input_dict)

                else:
                    input_dict['default1'] = user_value_dict.get(input_field)
                    self.para_dict.append(input_dict)

        # print 'self.para_dict'
        # print self.para_dict
        self.para_dict = {"column": "12", "newline": "yes", "inputs": self.para_dict}

    def get_response_data(self):
        return self.para_dict


class ACI_Resend_InputVariable:
    def __init__(self, request, com_dict, user_value_dict, input_data_list):
        print " In ACI Resend"
        self.para_dict = []
        modified_para_dict = []
        if type(input_data_list) is dict:
            if input_data_list.has_key('column'):
                input_data_list = input_data_list.get('inputs')

        if not user_value_dict:
            print "captured here !"
            self.para_dict = input_data_list
        else:
            print user_value_dict
            option_list = []
            work_order_no = ''
            servicenow = ServiceNowRequest('admin', 'vqfQxF3KqB7X')
            apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
            if user_value_dict.get("work_order_no") and user_value_dict.get('service_now_check') == "yes":
                # all_req_dict = servicenow.fetching(user_value_dict.get("work_order_no"))
                # Read Json File 1) work orderc base, desc ,
                with open('/home/ubuntu/prepro/mysite/Cron_script_data/all_serviceNow_data.json', 'r+') as jdata:
                    json_service_data = json.load(jdata)
                desc = json_service_data[user_value_dict.get("work_order_no")]['description']
                print ">>>>>>>>>>>>>>", [desc]
                desc_dict = {j.split(":")[0].strip(): j.split(":")[1].strip() for j in [i for i in desc.split("\n")]}
                print desc_dict

            for input_dict in input_data_list:
                # print "input_dict"
                # print input_dict
                input_field = input_dict.get('name')
                if input_dict.get('name') == 'tenant_name_2' or input_dict.get(
                        'name') == 'application_name_2' or input_dict.get('name') == 'epg_name_2' or input_dict.get(
                    'name') == 'leaf_id2':
                    if user_value_dict.has_key("leaf_id2") and input_dict.get('name') == 'leaf_id2':
                        leaf = get_apic_data().get("leaf")
                        input_dict['default1'] = user_value_dict.get("leaf_id2")
                        leaf_options = []
                        for each in leaf:
                            dic = {}
                            dic["label"] = each
                            dic["value"] = each
                            leaf_options.append(dic)
                        input_dict['options'] = leaf_options
                    if user_value_dict.has_key("tenant_name_2") and input_dict.get('name') == 'tenant_name_2':
                        tenant = get_apic_data(user_value_dict.get("tenant_name_2")).get("tenant")
                        input_dict['default1'] = user_value_dict.get("tenant_name_2")
                        tnt_options = []
                        for each in tenant:
                            dic = {}
                            dic["label"] = each
                            dic["value"] = each
                            dic["send"] = "yes"
                            tnt_options.append(dic)
                        input_dict['options'] = tnt_options
                    if user_value_dict.has_key("tenant_name_2") and input_dict.get('name') == 'application_name_2':
                        application = get_apic_data(user_value_dict.get("tenant_name_2")).get("app")
                        if user_value_dict.has_key("application_name_2"):
                            input_dict['default1'] = user_value_dict.get("application_name_2")
                        else:
                            input_dict['default1'] = application[0]
                        app_options = []
                        for each in application:
                            dic = {}
                            dic["label"] = each
                            dic["value"] = each
                            dic["send"] = "yes"
                            app_options.append(dic)
                        input_dict['options'] = app_options
                        input_dict["send"] = "yes"
                    if user_value_dict.has_key("application_name_2") and input_dict.get('name') == 'epg_name_2':
                        print "Gotcch here .. !"
                        epg = get_apic_data(user_value_dict.get("tenant_name_2"),
                                            user_value_dict.get("application_name_2")).get("epg")
                        epg_options = []
                        for each in epg:
                            dic = {}
                            dic["label"] = each
                            dic["value"] = each
                            epg_options.append(dic)
                        input_dict['options'] = epg_options

                    self.para_dict.append(input_dict)
                elif request.session["user_type"] == "ACI Port Provisioning" and user_value_dict.get(
                        "port_mode") == 'trunk' and input_dict.get('name') == 'vlan_id':
                    input_dict['type'] = 'dropdown-checkbox'
                    self.para_dict.append(input_dict)
                # elif input_dict.get('name') == 'work_order_no':
                #     work_order_no = user_value_dict.get(input_field)
                #     if user_value_dict.get(input_field):
                #         input_dict['default1'] = user_value_dict.get(input_field)
                #     else:
                #         input_dict['default1'] = input_dict['example'].replace("Ex: ", "")
                #     self.para_dict.append(input_dict)

                elif input_dict.get('name') == 'provision_reason':
                    if user_value_dict.get('service_now_check') == "yes":
                        input_dict['default1'] = desc_dict['Provision Reason'].strip()
                    elif user_value_dict.get(input_field):
                        input_dict['default1'] = user_value_dict.get(input_field)
                    else:
                        input_dict['default1'] = ""
                    # print input_dict
                    self.para_dict.append(input_dict)

                elif input_dict.get('name') == 'application' and user_value_dict.has_key("tenant_name"):
                    app = apic_auth.apps_profile(tenant)
                    input_dict['default1'] = app[0]
                    self.para_dict.append(input_dict)
                elif input_dict.get('name') == 'vlan_id' and user_value_dict.has_key("tenant_name") :
                    print "hi there"
                    tenant = user_value_dict.get("tenant_name")
                    app = apic_auth.apps_profile(tenant)
                    epg_bd = apic_auth.get_epg_bd(tenant,app[0])     
                    epg_list = epg_bd['epg']
                    bd_list = epg_bd['bd']
                    vlan_options = []
                    count = 1
                    for i in range(len(epg_bd['epg'])):
                        dict1 = {}
                        dict1['value'] = "12"+str(count)+"-"+epg_list[i]+"-"+bd_list[i] 
                        dict1['label'] = "12"+str(count)+" [EPG: "+epg_list[i]+", BD: "+bd_list[i]+"]"
                        vlan_options.append(dict1)
                        count+=1
                    if user_value_dict.get("port_type") in ['Physical','Virtual Port-Channel','Port-Channel'] and user_value_dict.get("port_mode") == 'regular':
                        print "????????"
                        input_dict['type'] = 'dropdown-checkbox'
                        input_dict['options'] = vlan_options
                        input_dict['default1'] = user_value_dict.get(input_field)
                        self.para_dict.append(input_dict)
                    else: 
                        print ">>>>>>>"
                        input_dict['type'] = 'dropdown'
                        input_dict['options'] = vlan_options
                        input_dict['default1'] = user_value_dict.get(input_field)
                        self.para_dict.append(input_dict)
                    
                elif input_dict.get('name') in ['physical_port1', 'physical_port2'] and request.session["ext_dict"][
                    "action"] in ["provision", 'Provision', "activation", "deprovision"]:
                    a = 1
                elif input_dict.get('name') == 'rack_number' and user_value_dict.has_key("rack_row_number"):
                    print " Reaching 1 for ", request.session["ext_dict"]["action"]
                    rack_row = user_value_dict.get("rack_row_number")
                    rack_options = input_dict['options']
                    for r_dict in rack_options:
                        r_dict['label'] = re.sub('(\d+)', rack_row, r_dict['label'], 1)
                        r_dict['value'] = re.sub('(\d+)', rack_row, r_dict['value'], 1)
                    input_dict['options'] = rack_options
                    input_dict['default1'] = user_value_dict.get(input_field)
                    # if user_value_dict.has_key("leaf_id"):
                    #     user_value_dict["leaf_id"]=""
                    self.para_dict.append(input_dict)
                elif input_dict.get('name') == 'server_name' and user_value_dict.has_key("rack_number"):

                    if user_value_dict.get('service_now_check') == "yes":
                        input_dict['type'] = "hidden"
                        input_dict['default1'] = desc_dict['Server Name'].strip()
                        self.para_dict.append(input_dict)
                    else:
                        rack_num = user_value_dict.get("rack_number").replace("R-", "")
                        server_options = input_dict['options']
                        for s_dict in server_options:
                            s_dict['label'] = re.sub('\d+-\d+', rack_num, s_dict['label'], 1)
                            s_dict['value'] = re.sub('\d+-\d+', rack_num, s_dict['value'], 1)
                        input_dict['options'] = server_options
                        input_dict['default1'] = user_value_dict.get(input_field)
                        self.para_dict.append(input_dict)


                elif input_dict.get('name') == 'leaf_id' and user_value_dict.has_key("rack_number") and \
                        request.session["ext_dict"]["action"] in ["Reservation", "reserve", "deprovision_reservation",
                                                                  "leaf_port_status"]:
                    # if not user_value_dict.get("leaf_id"):
                    print " Reaching 2 for ", request.session["ext_dict"]["action"]
                    rack_num = user_value_dict.get("rack_number").replace("R-", "")
                    leaf_options = input_dict['options']
                    for l_dict in leaf_options:
                        l_dict['label'] = re.sub('\d+-\d+', rack_num, l_dict['label'], 1)
                        l_dict['selected'] = "no"
                    print leaf_options
                    input_dict['options'] = leaf_options
                    input_dict['default1'] = user_value_dict.get(input_field)
                    if not user_value_dict.get("leaf_id") or request.session["ext_dict"][
                        "action"] == "leaf_port_status":
                        self.para_dict.append(input_dict)
                    if user_value_dict.get("leaf_id") and request.session["ext_dict"]["action"] in ["Reservation"]:
                        # print " Leaf IDnnnnnnnnnnnn???? ", user_value_dict.get(input_field)
                        leaf_options = input_dict['options']
                        input_dict['options'] = leaf_options
                        # input_dict['default1'] = user_value_dict.get(input_field)
                        if "++" in user_value_dict.get(input_field):
                            user_value_dict[input_field] = user_value_dict.get(input_field).split("++")
                        # else:
                        #     user_value_dict[input_field] = [user_value_dict.get(input_field)]

                        # for each in leaf_options:
                        #     if each.has_key("selected"):
                        #         del leaf_options[leaf_options.index(each)]["selected"]
                        for cst in user_value_dict[input_field]:
                            for opt in input_dict['options']:
                                if opt.get("value") == cst:
                                    opt["selected"] = "yes"
                        # input_dict['options'] = leaf_options
                        # print input_dict
                        self.para_dict.append(input_dict)
                        prereserved_ports = ['Eth 1/45', 'Eth 1/46', 'Eth 1/47', 'Eth 1/48']
                        count = 1
                        for cst in user_value_dict.get(input_field):
                            print ">>>>!!!!!!", cst
                            port_options = []
                            reserved_ports = []
                            query = ACIInterfaceStatusDB.objects.filter(leaf_id=cst).values('physical_port').all()
                            if query:
                                for dct in query:
                                    if dct["physical_port"] not in reserved_ports:
                                        reserved_ports.append(dct["physical_port"])
                            # if input_data_l
                            apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                            port_details = apic_auth.get_port_details(cst)
                            for each in range(1, 49):
                                get_port_details = ""
                                dict1 = {}
                                each = "Eth 1/" + str(each) 
                                if request.session["ext_dict"]["action"] in ["reserve", "Reservation"]:
                                    port = each.lower().replace(" ","")
                                    if port in port_details and port_details[port]['oper_state'] != 'up' and not port_details[port]['description'] and each not in prereserved_ports and each.lower().replace(" ", "") not in reserved_ports:
                                        
                                        dict1["label"] = each
                                        dict1["value"] = each.lower()
                                        dict1["disabled"] =  "no"
                                        port_options.append(dict1)
                                    if port in port_details and port_details[port]['oper_state'] == 'up' and not port_details[port]['description'] and each not in prereserved_ports and each.lower().replace(" ", "") not in reserved_ports:
                                        
                                        dict1["label"] = each
                                        dict1["value"] = each.lower()
                                        dict1["disabled"] =  "yes"
                                        port_options.append(dict1)
                                    
                                elif request.session["ext_dict"]["action"] == "deprovision_reservation":
                                    if each not in prereserved_ports and each.lower() in reserved_ports:
                                        dict1["label"] = each
                                        dict1["value"] = each.lower()
                                        port_options.append(dict1)
                            # else:
                            #     apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                            #     port_details = apic_auth.get_port_details(cst)
                            #     port_list = []
                            #     for details in port_details:
                            #         # port_list = {}
                            #         if details['admin_state'] == 'up'  and not details['description']:
                            #             port_list.append(details['port'])
                            #     dict1 = {}
                            #     print collections.OrderedDict(port_list)
                            #     for port in port_list:
                            #         dict1 = {}
                            #         dict1["label"] = port.title()
                            #         dict1["value"] = port.lower()
                            #         port_options.append(dict1)
                            #     # print port_details
                            inp1 = {"name": "physical_port_" + str(cst), "send": "yes", "length": "full",
                                    "desc": "Leaf " + cst + " Physical Port", "type": "dropdown-checkbox","mendatory":"yes",
                                    'options': port_options}
                            self.para_dict.append(inp1)
                            count += 1
                    
                    if user_value_dict.get("leaf_id") and request.session["ext_dict"]["action"] in [ "reserve", "deprovision_reservation"]:
                        # print " Leaf IDnnnnnnnnnnnn???? ", user_value_dict.get(input_field)
                        leaf_options = input_dict['options']
                        input_dict['options'] = leaf_options
                        # input_dict['default1'] = user_value_dict.get(input_field)
                        if "++" in user_value_dict.get(input_field):
                            user_value_dict[input_field] = user_value_dict.get(input_field).split("++")
                        else:
                            user_value_dict[input_field] = [user_value_dict.get(input_field)]

                        # for each in leaf_options:
                        #     if each.has_key("selected"):
                        #         del leaf_options[leaf_options.index(each)]["selected"]
                        for cst in user_value_dict[input_field]:
                            for opt in input_dict['options']:
                                if opt.get("value") == cst:
                                    opt["selected"] = "yes"
                        # input_dict['options'] = leaf_options
                        # print input_dict
                        self.para_dict.append(input_dict)
                        prereserved_ports = ['Eth 1/45', 'Eth 1/46', 'Eth 1/47', 'Eth 1/48']
                        count = 1
                        for cst in user_value_dict.get(input_field):
                            print ">>>>", cst
                            port_options = []
                            reserved_ports = []
                            query = ACIInterfaceStatusDB.objects.filter(leaf_id=cst).values('physical_port').all()
                            if query:
                                for dct in query:
                                    if dct["physical_port"] not in reserved_ports:
                                        reserved_ports.append(dct["physical_port"])
                            # if input_data_l

                            for each in range(1, 49):
                                get_port_details = ""
                                dict1 = {}
                                each = "Eth 1/" + str(each)
                                # print each.lower()
                                # if request.session["ext_dict"]["action"] in ["Reservation"]:
                                #     data_dict = {'leaf_node':cst,'phy_port':each.lower().replace(" ", "")}
                                #     print '????????',data_dict
                                #     apic_auth = ACIconfig_by_API('ip_address','username','password')
                                #     get_port_details = apic_auth.leaf_status_details(data_dict)
                                #     if not get_port_details:
                                #         print True
                                #     else:
                                #         print False
                                # print '>>>>>>>>>>> get port details',get_port_details
                                if request.session["ext_dict"]["action"] in ["Reservation", "reserve"]:
                                    # print " >>>>> Reserverd Ports", reserved_ports
                                    if each not in prereserved_ports and each.lower().replace(" ",
                                                                                              "") not in reserved_ports:
                                        dict1["label"] = each
                                        dict1["value"] = each.lower()
                                        port_options.append(dict1)
                                elif request.session["ext_dict"]["action"] == "deprovision_reservation":
                                    if each not in prereserved_ports and each.lower() in reserved_ports:
                                        dict1["label"] = each
                                        dict1["value"] = each.lower()
                                        port_options.append(dict1)
                            inp1 = {"name": "physical_port_" + str(cst), "send": "yes", "length": "full",
                                    "desc": "Leaf " + cst + " Physical Port", "type": "dropdown-checkbox",
                                    'options': port_options}
                            self.para_dict.append(inp1)
                            count += 1

                elif input_dict.get('name') == 'description':
                    input_dict['default1'] = ''
                    self.para_dict.append(input_dict)
                    
                elif input_dict.get('name') == 'leaf_id' and user_value_dict.has_key(input_field) and \
                        request.session["ext_dict"]["action"] in ["Provision",
                                                                  "provision",
                                                                  "activation",
                                                                  "deprovision",
                                                                  "De-Provision"]:
                    print "Action ", request.session["ext_dict"]["action"]
                    if "++" in user_value_dict.get(input_field):
                        user_value_dict[input_field] = user_value_dict.get(input_field).split("++")
                    reserved_leafs = []
                    leaf_options = input_dict['options']
                    work_order_no = user_value_dict.get('work_order_no')
                    query = ACIInterfaceStatusDB.objects.filter(work_order_no=work_order_no).values(
                        'leaf_id').all()
                    if query:
                        for dct in query:
                            if dct["leaf_id"] not in reserved_leafs:
                                reserved_leafs.append(dct["leaf_id"])
                                input_dict['options'] = []
                        for each in leaf_options:
                            if each.has_key("selected"):
                                del leaf_options[leaf_options.index(each)]["selected"]
                    for cst in user_value_dict[input_field]:
                        for opt in leaf_options:
                            if opt.get("value") == cst:
                                opt["selected"] = "yes"
                    input_dict['options'] = leaf_options
                    # Added for Radio button Change in Lead ID ,   dt 04-02-19
                    # input_dict['default1'] = user_value_dict.get(input_field)[0]
                    print reserved_leafs
                    # input_dict['default1'] = user_value_dict.get(input_field)
                    self.para_dict.append(input_dict)
                    apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                    prereserved_ports = ['Eth 1/45', 'Eth 1/46', 'Eth 1/47', 'Eth 1/48']
                    count = 1
                    for cst in user_value_dict.get(input_field):
                        print ">>>>!!!!!!", cst
                        port_options = []
                        reserved_ports = []
                        query = ACIInterfaceStatusDB.objects.filter(leaf_id=cst).values('physical_port').all()
                        if query:
                            for dct in query:
                                if dct["physical_port"] not in reserved_ports:
                                    reserved_ports.append(dct["physical_port"])
                        # if input_data_l
                        apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                        port_details = apic_auth.get_port_details(cst)
                        for each in range(1, 49):
                            get_port_details = ""
                            dict1 = {}
                            each = "Eth 1/" + str(each) 
                            if request.session["ext_dict"]["action"] in ["Provision"]:
                                port = each.lower().replace(" ","")
                                
                                if port in port_details and port_details[port]['oper_state'] != 'up' and not port_details[port]['description'] and each not in prereserved_ports and each.lower().replace(" ", "") not in reserved_ports:
                                    
                                    dict1["label"] = each
                                    dict1["value"] = each.lower()
                                    dict1["send"] = "yes"
                                    dict1["disabled"] =  "no"
                                    port_options.append(dict1)
                                
                                if port in port_details and port_details[port]['oper_state'] == 'up' and not port_details[port]['description'] and each not in prereserved_ports and each.lower().replace(" ", "") not in reserved_ports:
                                    
                                    dict1["label"] = each
                                    dict1["value"] = each.lower()
                                    dict1["disabled"] =  "yes"
                                    port_options.append(dict1)
                                
                                if port in port_details and port_details[port]['oper_state'] != 'up' and not port_details[port]['description'] and each not in prereserved_ports and each.lower().replace(" ", "") in reserved_ports:
                                    
                                    dict1["label"] = each
                                    dict1["value"] = each.lower()
                                    dict1["disabled"] =  "yes"
                                    port_options.append(dict1)
                                
                                if port in port_details and port_details[port]['oper_state'] != 'up' and port_details[port]['description'] and each not in prereserved_ports and each.lower().replace(" ", "") not in reserved_ports:
                                    
                                    dict1["label"] = each
                                    dict1["value"] = each.lower()
                                    dict1["disabled"] =  "yes"
                                    port_options.append(dict1)
                                
                            elif request.session["ext_dict"]["action"] == "deprovision_reservation":
                                if each not in prereserved_ports and each.lower() in reserved_ports:
                                    dict1["label"] = each
                                    dict1["value"] = each.lower()
                                    port_options.append(dict1)
                        # else:
                        #     apic_auth = ACIconfig_by_API(ACI_IP, Username, Password)
                        #     port_details = apic_auth.get_port_details(cst)
                        #     port_list = []
                        #     for details in port_details:
                        #         # port_list = {}
                        #         if details['admin_state'] == 'up'  and not details['description']:
                        #             port_list.append(details['port'])
                        #     dict1 = {}
                        #     print collections.OrderedDict(port_list)
                        #     for port in port_list:
                        #         dict1 = {}
                        #         dict1["label"] = port.title()
                        #         dict1["value"] = port.lower()
                        #         port_options.append(dict1)
                        #     # print port_details
                        
                        if user_value_dict.has_key("physical_port_" + str(cst)) :
                            print "Here in Physical Port !", user_value_dict.get("physical_port_" + str(cst))
                            for prt in user_value_dict.get("physical_port_" + str(cst)):
                                for opt in port_options:
                                    if opt.get("value") == prt:
                                        opt["selected"] = "yes"
                        
                        inp1 = {"name": "physical_port_" + str(cst), "send": "yes", "length": "full",
                                "desc": "Leaf " + cst + " Physical Port","mandatory":"yes", "type": "dropdown-checkbox",
                                'options': port_options}
                        count += 1
                        self.para_dict.append(inp1)

                        
                        if user_value_dict.has_key("physical_port_" + str(cst)) :
                            for prt in user_value_dict.get("physical_port_" + str(cst)):
                                port_status = apic_auth.leaf_status_details(cst,prt )
                                inp1 = {"name": "Desc_int_{}".format(prt.title()),"length": "full",'default1':"","mendatory":"yes",
                                "desc": "Description for interface {} (Optional)".format(prt.title()), "type": "text",
                                'options': port_options}
                                count += 1
                                self.para_dict.append(inp1)
                    
                    
                elif input_dict.get('name') == 'description':
                    input_dict['default1'] = ''
                    self.para_dict.append(input_dict)
                elif input_dict.get('name') == 'leaf_id1' and request.session["ext_dict"]["action"] in ["Provision","provision", "activation","deprovision", "De-Provision"]:
                    print " In ACI  POrt Provisioning Template "
                    user_value_dict[input_field] = user_value_dict.get(input_field).split("++")
                    reserved_leafs = []
                    leaf_options = input_dict['options']
                    query = ACIInterfaceStatusDB.objects.filter(work_order_no=work_order_no).values(
                        'leaf_id').all()
                    if query:
                        for dct in query:
                            if dct["leaf_id"] not in reserved_leafs:
                                reserved_leafs.append(dct["leaf_id"])
                                input_dict['options'] = []
                        for each in leaf_options:
                            if each.has_key("selected"):
                                del leaf_options[leaf_options.index(each)]["selected"]
                    for cst in reserved_leafs:
                        for opt in leaf_options:
                            if opt.get("value") == cst:
                                opt["selected"] = "yes"
                    # input_dict['default1'] = user_value_dict.get(input_field)
                    input_dict['options'] = leaf_options
                    print reserved_leafs
                    self.para_dict.append(input_dict)
                    count = 1

                    port_options = []
                    reserved_ports = []
                    for cst in reserved_leafs:
                        print cst
                        query = ACIInterfaceStatusDB.objects.filter(leaf_id=cst, work_order_no=work_order_no).values(
                            'physical_port').all()
                        if query:
                            for dct in query:
                                if dct["physical_port"] not in reserved_ports:
                                    reserved_ports.append(dct["physical_port"])
                            for each in reserved_ports:
                                dict1 = {}
                                dict1["label"] = each
                                dict1["value"] = each
                                port_options.append(dict1)
                            inp1 = {"name": "physical_port_" + str(cst), "send": "yes", "length": "full",
                                    "desc": "Leaf " + cst + " Physical Port", "type": "dropdown-checkbox",
                                    'options': port_options}
                            count += 1
                            self.para_dict.append(inp1)
                else:
                    input_dict['default1'] = user_value_dict.get(input_field)
                    self.para_dict.append(input_dict)

        # print 'self.para_dict'
        # print self.para_dict
        self.para_dict = {"column": "12", "newline": "yes", "inputs": self.para_dict}

    def get_response_data(self):
        return self.para_dict


class GetInputVariableDictForTp:
    global preso_variable_output

    def __init__(self, request, customer, user_sel_dict, para_list, feature_data={}, field_desc_list=[]):
        global preso_variable_output
        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format
        Example:
        input: ['src_ip', 'in_int', 'out_int', 'des_ip', 'des_net', 'dst_ml', 'in_l3', 'ou_l3']
        output: [{'default1': '', 'format': 'ip', 'type': 'text', 'name': 'src_ip', 'desc': 'Enter <src_ip>'}, {
        '''
        para_dict = {}
        # com_dict = {'ip': {'ios': 'nx', 'plat': '7000', 'type': 'forwarding'}}
        # para_list = ['in_int', 'in_phy', 'out_int', 'ou_phy', 'in_l3', 'ou_l3', 'vrf', 'src_ip', 'mdt_src', 'mdt_gr', 'des_ip', 'vrf_rp_add']
        # if user_sel_dict:
        #     ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
        #     plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))
        tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
        type = ConvertUeseInputs('type', user_sel_dict.get('type'))
        new_var_dict = {}

        self.tech_with_vrf = ['mvpn', 'l3vpn']
        self.tech_with_optional_vrf = ['ip', 'con', 'mcast', 'ipv6', 'conv6', 'dhcp', 'bgp', 'ospf', 'isis', 'bfd']

        if tech:
            if self.tech_with_vrf.__contains__(tech):
                vrf_type = 'force'
            elif self.tech_with_optional_vrf.__contains__(tech):
                vrf_type = 'optional'
            else:
                vrf_type = 'no applicable'

        input_para_dict = []
        if feature_data:
            input_para_dict = get_feature_jason_data(feature_data, para_list, field_desc_list)
            # input_para_dict['send'] = 'yes'
        option_variable_list = []
        for feature_data_info in input_para_dict:
            if feature_data_info.has_key('name'):
                option_variable_list.append(feature_data_info.get('name'))
        for el in para_list:
            default1 = ''
            example = ''
            if el:
                # if not option_variable_list.__contains__(el):
                output = ''
                name = el
                # if in the cu BD, Fixed, input type, regex,
                #  print "Customer --> "+customer
                # print "EL --> "+el
                location = request.session["acilocation"]
                checkflag = str(checkifelexists(el, customer, location))
                checkflagc = str(checkifelexistsc(el, location))
                # print "flag"+str(checkflag)
                if checkflag != "0":
                    from mysite.models import SetupParameters
                    if checkflag == "1":
                        entry = SetupParameters.objects.filter(variable=el, customer__contains=customer,
                                                               location=location).last()
                    else:
                        entry = SetupParameters.objects.filter(variable=el, customer__contains=customer,
                                                               location="all").last()
                    # print entry
                    parameter = entry.parameter
                    variable = entry.variable
                    value = entry.value
                    label = entry.label
                    regex = entry.regex
                    type = entry.type
                    regextype = entry.regextype
                    value = entry.value
                    regexmainstr = ""
                    vmessage = ""
                    if regextype == 3:
                        regexmainstr = regex
                        vmessage = "Please enter " + parameter + " Correctly"
                    if regextype == 2:
                        # print "regex  - ",regex
                        if regex == "1":
                            # ipv4
                            regexmainstr = "([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?"
                            vmessage = "Please enter " + parameter + " Correctly. It should in a valid IP"
                        if regex == "2":
                            # IPV6
                            regexmainstr = "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
                            vmessage = "Please enter " + parameter + " Correctly. It should in a valid IPV6"

                        if regex == "3":
                            # IPV4 Multicast
                            regexmainstr = "IPV4 Multicast Pattern here"
                            vmessage = "Please enter " + parameter + " Correctly. It should in a valid IPv4 multicast"
                        if regex == "4":
                            # Digit
                            regexmainstr = "\d+"
                            vmessage = "Please enter " + parameter + " Correctly. It should in a valid DIGIT"

                    # print el+"type ----->>>>"+str(regexmainstr)
                    # if str(type) == "":
                    # para_dict = {'name': variable, 'type': 'radio', 'desc': "", 'default1': value, 'format': ''}
                    # para_dict['output'] = output
                    if str(type) == "1" or str(type) == "2":
                        valuelist = value.split(",")
                        labellist = label.split(",")
                        # check if label is empty or equal to value list
                        if len(valuelist) == len(labellist) or (len(labellist) == 1 and len(valuelist) > 1):
                            # print "Iterate here"
                            finallist = []
                            for k, val in enumerate(valuelist):
                                tempdict = {}
                                tempdict["value"] = val.strip()
                                if len(labellist) == 1 or len(labellist) == 0:
                                    tempdict["label"] = val.strip()
                                else:
                                    tempdict["label"] = labellist[k]
                                finallist.append(tempdict)
                            # radio 
                            if str(type) == "1":
                                para_dict = {'name': variable, 'type': 'radio', 'desc': parameter,
                                             'default1': finallist[0]["value"],
                                             'format': '', "options": finallist, 'validate': regexmainstr,
                                             'vmessage': vmessage}
                                para_dict['output'] = output
                            # dropdown
                            elif str(type) == "2":
                                para_dict = {'name': variable, 'type': 'dropdown', 'desc': parameter, 'default1': '',
                                             'format': '', "options": finallist, 'validate': regexmainstr,
                                             'vmessage': vmessage}
                                para_dict['output'] = output
                    elif str(type) == "3":
                        para_dict = {'name': variable, 'type': 'hidden', 'desc': "", 'default1': value, 'format': ''}
                        para_dict['output'] = output
                        # elif "," in value:
                        # valuelist = value.split(",")
                        # labellist = label.split(",")
                        # #check if label is empty or equal to value list

                        # if len(valuelist)==len(labellist) or (len(labellist)==1 and len(valuelist) >1):
                        # print "Iterate here"
                        # finallist = []
                        # for k,val in enumerate(valuelist):
                        # tempdict = {}
                        # tempdict["value"] = val
                        # if len(labellist)==1 or  len(labellist) == 0:
                        # tempdict["label"] = val
                        # else:
                        # tempdict["label"] = labellist[k]
                        # finallist.append(tempdict)

                        # if len(valuelist)>=2 and len(valuelist) <=4 :
                        # para_dict = {'name': variable, 'type': 'radio', 'desc': parameter, 'default1': '',
                        # 'format': '',"options": finallist}
                        # para_dict['output'] = output

                        # elif len(valuelist) > 4 :
                        # para_dict = {'name': variable, 'type': 'dropdown', 'desc': parameter, 'default1': '',
                        # 'format': '',"options": finallist}
                        # para_dict['output'] = output

                        # else:
                        # print "Lengths do not match"
                    else:
                        # print "regexmainstr"+regexmainstr
                        para_dict = {'name': variable, 'type': 'text', 'desc': parameter, 'default1': value,
                                     'validate': regexmainstr, 'format': '', 'vmessage': vmessage}
                        para_dict['output'] = output
                    # new_var_dict[el] = para_dict
                    # input_para_dict.append(para_dict)
                elif checkflagc != "0":
                    from mysite.models import CommonSetupParameters
                    if checkflagc == "1":
                        entry = CommonSetupParameters.objects.filter(variable=el, location=location).last()
                    else:
                        entry = CommonSetupParameters.objects.filter(variable=el, location="all").last()
                    parameter = entry.parameter
                    variable = entry.variable
                    value = entry.value
                    label = entry.label
                    regex = entry.regex
                    type = entry.type
                    regextype = entry.regextype
                    value = entry.value
                    regexmainstr = ""
                    vmessage = ""
                    if regextype == 3:
                        regexmainstr = regex
                        vmessage
                        "Please enter " + parameter + " Correctly"
                    if regextype == 2:
                        # print "regex  - ",regex
                        if regex == "1":
                            # ipv4
                            regexmainstr = "([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?"
                            vmessage = "Please enter " + parameter + " Correctly. It should in a valid IP"
                        if regex == "2":
                            # IPV6
                            regexmainstr = "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
                            vmessage = "Please enter " + parameter + " Correctly. It should in a valid IPV6"

                        if regex == "3":
                            # IPV4 Multicast
                            regexmainstr = "IPV4 Multicast Pattern here"
                            vmessage = "Please enter " + parameter + " Correctly. It should in a valid IPv4 multicast"
                        if regex == "4":
                            # Digit
                            regexmainstr = "\d+"
                            vmessage = "Please enter " + parameter + " Correctly. It should in a valid DIGIT"

                    # print el + "type ----->>>>" + str(regexmainstr)
                    # if str(type) == "":
                    # para_dict = {'name': variable, 'type': 'radio', 'desc': "", 'default1': value, 'format': ''}
                    # para_dict['output'] = output
                    if str(type) == "1" or str(type) == "2":
                        valuelist = value.split(",")
                        labellist = label.split(",")
                        # check if label is empty or equal to value list
                        if len(valuelist) == len(labellist) or (len(labellist) == 1 and len(valuelist) > 1):
                            # print "Iterate here"
                            finallist = []
                            for k, val in enumerate(valuelist):
                                tempdict = {}
                                tempdict["value"] = val.strip()
                                if len(labellist) == 1 or len(labellist) == 0:
                                    tempdict["label"] = val.strip()
                                else:
                                    tempdict["label"] = labellist[k]
                                finallist.append(tempdict)
                            # radio
                            if str(type) == "1":
                                para_dict = {'name': variable, 'type': 'radio', 'desc': parameter,
                                             'default1': finallist[0]["value"],
                                             'format': '', "options": finallist, 'validate': regexmainstr,
                                             'vmessage': vmessage}
                                para_dict['output'] = output
                            # dropdown
                            elif str(type) == "2":
                                para_dict = {'name': variable, 'type': 'dropdown', 'desc': parameter, 'default1': '',
                                             'format': '', "options": finallist, 'validate': regexmainstr,
                                             'vmessage': vmessage}
                                para_dict['output'] = output
                    elif str(type) == "3":
                        para_dict = {'name': variable, 'type': 'hidden', 'desc': "", 'default1': value, 'format': ''}
                        para_dict['output'] = output
                        # elif "," in value:
                        # valuelist = value.split(",")
                        # labellist = label.split(",")
                        # #check if label is empty or equal to value list

                        # if len(valuelist)==len(labellist) or (len(labellist)==1 and len(valuelist) >1):
                        # print "Iterate here"
                        # finallist = []
                        # for k,val in enumerate(valuelist):
                        # tempdict = {}
                        # tempdict["value"] = val
                        # if len(labellist)==1 or  len(labellist) == 0:
                        # tempdict["label"] = val
                        # else:
                        # tempdict["label"] = labellist[k]
                        # finallist.append(tempdict)

                        # if len(valuelist)>=2 and len(valuelist) <=4 :
                        # para_dict = {'name': variable, 'type': 'radio', 'desc': parameter, 'default1': '',
                        # 'format': '',"options": finallist}
                        # para_dict['output'] = output

                        # elif len(valuelist) > 4 :
                        # para_dict = {'name': variable, 'type': 'dropdown', 'desc': parameter, 'default1': '',
                        # 'format': '',"options": finallist}
                        # para_dict['output'] = output

                        # else:
                        # print "Lengths do not match"
                    else:
                        # print "regexmainstr" + regexmainstr
                        para_dict = {'name': variable, 'type': 'text', 'desc': parameter, 'default1': value,
                                     'validate': regexmainstr, 'format': '', 'vmessage': vmessage}
                        para_dict['output'] = output
                elif el == "leaf_id2":
                    leaf = get_apic_data().get("leaf")
                    print leaf
                    leaf_options = []
                    for each in leaf:
                        dic = {}
                        dic["label"] = each
                        dic["value"] = each
                        dic["send"] = "yes"
                        leaf_options.append(dic)
                    para_dict = {'name': el, 'type': 'dropdown', 'desc': 'Leaf ID', 'default1': leaf[0],
                                 'format': '', "options": leaf_options}
                elif el == "tenant_name_2":
                    tenant = get_apic_data().get("tenant")
                    # print get_apic_data()
                    tnt_options = []
                    for each in tenant:
                        dic = {}
                        dic["label"] = each
                        dic["value"] = each
                        dic["send"] = "yes"
                        tnt_options.append(dic)
                    para_dict = {'name': el, 'type': 'radio', 'desc': 'Tenant', 'default1': tenant[0],
                                 'format': '', "options": tnt_options}
                elif el == "application_name_2":
                    app = get_apic_data(get_apic_data().get("tenant")[0]).get("app")
                    # print app
                    app_options = []
                    for each in app:
                        dic = {}
                        dic["label"] = each
                        dic["value"] = each
                        dic["send"] = "yes"
                        app_options.append(dic)
                    para_dict = {'name': el, 'type': 'dropdown', 'desc': 'Application', 'default1': '',
                                 'format': '', "options": app_options}
                elif el == "epg_name_2":
                    epg = get_apic_data(get_apic_data().get("tenant")[0],
                                        get_apic_data(get_apic_data().get("tenant")[0]).get("app")[0]).get("epg")
                    epg_options = []
                    for each in epg:
                        dic = {}
                        dic["label"] = each
                        dic["value"] = each
                        dic["send"] = "yes"
                        epg_options.append(dic)
                    para_dict = {'name': el, 'type': 'dropdown', 'desc': 'EPG', 'default1': '',
                                 'format': '', "options": epg_options}
                elif el == 'vrf_name':
                    if vrf_type == 'optional':
                        para_dict = {'name': 'vrf_option', 'type': 'radio', 'desc': 'Is VRF Involved', 'default1': '',
                                     'format': '', "options": [
                                {"label": "Yes", "value": "Yes", "hide": "hide", "trigger": ["vrf_name"]},
                                {"label": "No", "value": "No", "hide": "hide"}]}
                        para_dict['output'] = output
                        input_para_dict.append(para_dict)
                        new_var_dict['vrf_option'] = para_dict
                    desc = 'VRF Name'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default1, 'format': ''}
                    para_dict['output'] = output
                    input_para_dict.append(para_dict)
                    new_var_dict[el] = para_dict
                else:
                    field_desc_dict = {}
                    desc = 'Enter %s' % name
                    for field_desc_dict in field_desc_list:
                        if field_desc_dict.get('field') == name:
                            desc = field_desc_dict.get('desc')
                            if field_desc_dict.has_key('default'):
                                default1 = field_desc_dict.get('default')
                            if field_desc_dict.has_key('example'):
                                example = field_desc_dict.get('example')

                    # [{'field': 'vrf_name', 'desc': 'VRF Name'}, {'field': 'access_list_num', 'desc': 'Access-list Name'}, {'field': 'wild_mask', 'desc': 'Wild-card Mask'}, {'field': 'rp_interface', 'desc': 'RP Interface'}, {'field': 'interface', 'desc': 'Interface'}, {'field': 'ospf_process', 'desc': 'OSPF Process ID'}]
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default1, 'format': '',
                                 'example': example}
                    para_dict['output'] = output
                    if el == 'anycast_gw_virtual_ip-mask_len':
                        para_dict['example'] = 'Ex:20.1.1.1/24'
                    elif el == 'tenant_vni_segment_num':
                        para_dict['example'] = 'Ex:30001'
                    elif el == 'tenant_vlan_num':
                        para_dict['example'] = 'Ex:3001'
                    elif el == 'l2_vlan_num':
                        para_dict['example'] = 'Ex:101, 104'
                    elif el == 'vlan_num':
                        para_dict['example'] = 'Ex:101, 104'
                    elif el == 'l2_vni_num':
                        para_dict['example'] = 'Ex:20101, 20104'
                    elif el == 'access_interface':
                        para_dict['example'] = 'Ex:eth9/1, eth10/2'
                    elif el == 'import_route_target' or el == 'export_route_target':
                        para_dict['example'] = 'Ex:3001:1'
                #
                # if para_dict['name'] == 'port_media_type':
                #     for opt in para_dict['options']:
                #         if opt['value'] =="copper":
                #             indx = para_dict['options'].index(opt)
                #             para_dict['options'][indx]['hide'] = 'hide'
                #             para_dict['options'][indx]['trigger'] =[ 'speed']

                input_para_dict.append(para_dict)
                new_var_dict[el] = para_dict
        input_para_dict = convert_input_para_dict_tp(input_para_dict, tech, type)
        # input_para_dict.append({'name': 'sship', 'type': 'text', 'desc': 'Device IP','default1': '', "mandatory": "yes", 'example':''})
        self.input_para_dict = {"column": "12", "newline": "yes", "inputs": input_para_dict}
        self.new_var_dict = new_var_dict
        preso_variable_output = new_var_dict

    def getInputDict(self):
        return self.input_para_dict

    def format_variable_old_to_new(self):
        return self.new_var_dict


class GetInputVariableDictForAsaTP:
    global preso_variable_output

    def __init__(self, user_sel_dict, para_list, feature_data={}, field_desc_list=[]):
        global preso_variable_output
        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format
        Example:
        input: ['src_ip', 'in_int', 'out_int', 'des_ip', 'des_net', 'dst_ml', 'in_l3', 'ou_l3']
        output: [{'default1': '', 'format': 'ip', 'type': 'text', 'name': 'src_ip', 'desc': 'Enter <src_ip>'}, {
        '''
        para_dict = {}
        # com_dict = {'ip': {'ios': 'nx', 'plat': '7000', 'type': 'forwarding'}}
        # para_list = ['in_int', 'in_phy', 'out_int', 'ou_phy', 'in_l3', 'ou_l3', 'vrf', 'src_ip', 'mdt_src', 'mdt_gr', 'des_ip', 'vrf_rp_add']
        # if user_sel_dict:
        #     ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
        #     plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))

        tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
        #     type = ConvertUeseInputs('type', user_sel_dict.get('type'))
        new_var_dict = {}

        self.tech_with_vrf = ['mvpn', 'l3vpn']
        self.tech_with_optional_vrf = ['ip', 'con', 'mcast', 'ipv6', 'conv6', 'dhcp', 'bgp', 'ospf', 'isis', 'bfd']

        if tech:
            if self.tech_with_vrf.__contains__(tech):
                vrf_type = 'force'
            elif self.tech_with_optional_vrf.__contains__(tech):
                vrf_type = 'optional'
            else:
                vrf_type = 'no applicable'

        input_para_dict = []
        if feature_data:
            input_para_dict = get_feature_jason_data_v2(feature_data, para_list, field_desc_list)
            # input_para_dict['send'] = 'yes'
        option_variable_list = []
        for feature_data_info in input_para_dict:
            if feature_data_info.has_key('name'):
                option_variable_list.append(feature_data_info.get('name'))
        for el in para_list:
            default1 = ''
            if el:
                # if not option_variable_list.__contains__(el):
                output = ''
                name = el
                if el == 'vrf_name':
                    if vrf_type == 'optional':
                        para_dict = {'name': 'vrf_option', 'type': 'radio', 'desc': 'Is VRF Involved', 'default1': '',
                                     'format': '',
                                     "options": [
                                         {"label": "Yes", "value": "Yes", "hide": "hide", "trigger": ["vrf_name"]},
                                         {"label": "No", "value": "No", "hide": "hide"}]}
                        para_dict['output'] = output
                        input_para_dict.append(para_dict)
                        new_var_dict['vrf_option'] = para_dict
                    desc = 'VRF Name'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default1, 'format': ''}
                    para_dict['output'] = output
                    input_para_dict.append(para_dict)
                    new_var_dict[el] = para_dict
                else:
                    field_desc_dict = {}
                    desc = 'Enter %s' % name
                    for field_desc_dict in field_desc_list:
                        if field_desc_dict.get('field') == name:
                            desc = field_desc_dict.get('desc')
                            if field_desc_dict.has_key('default'):
                                default1 = field_desc_dict.get('default')
                    if el == 'direction2':
                        para_dict = {'name': el, 'type': 'radio', 'desc': 'Direction', 'default1': default1,
                                     'format': '',
                                     "options": [{"label": "Inbound", "value": "in"},
                                                 {"label": "Outbound", "value": "out"}]}

                    elif el == 'protocol':
                        para_dict = {'name': 'protocol', 'type': 'dropdown', 'desc': 'Protocol', 'default1': default1,
                                     'format': '',
                                     "options": [{"label": "TCP", "value": "tcp"}, {"label": "UDP", "value": "udp"},
                                                 {"label": 'IPv4', "value": "ip"},
                                                 ]}
                    else:
                        para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default1, 'format': ''}
                        para_dict['output'] = output
                        if el == 'anycast_gw_virtual_ip-mask_len':
                            para_dict['example'] = 'Ex:20.1.1.1/24'
                        elif el == 'tenant_vni_segment_num':
                            para_dict['example'] = 'Ex:30001'
                        elif el == 'tenant_vlan_num':
                            para_dict['example'] = 'Ex:3001'
                        elif el == 'l2_vlan_num':
                            para_dict['example'] = 'Ex:20101'
                        elif el == 'access_interface':
                            para_dict['example'] = 'Ex:eth9/1, eth10/2'
                        elif el == 'import_route_target' or el == 'export_route_target':
                            para_dict['example'] = 'Ex:3901:1'
                    input_para_dict.append(para_dict)
                    new_var_dict[el] = para_dict
        # input_para_dict.append({'name': 'sship', 'type': 'text', 'desc': 'Device IP',
        # 'default1': '', "mandatory": "yes", 'vmessage': 'Please Enter the IP' })
        self.input_para_dict = {"column": "12", "newline": "yes", "inputs": input_para_dict}
        self.new_var_dict = new_var_dict
        preso_variable_output = new_var_dict

    def getInputDict(self):
        return self.input_para_dict

    def format_variable_old_to_new(self):
        return self.new_var_dict


class PresScriptOutput:
    def __init__(self, user_sel_dict, inputlist, user_role=""):

        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format'''
        ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
        plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))
        tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
        type = ConvertUeseInputs('type', user_sel_dict.get('type'))
        com_dict = {}
        com_dict['ios'] = ios
        com_dict['plat'] = plat
        com_dict['tech'] = tech
        com_dict['type'] = type
        com_dict['user_role'] = user_role
        print 'user_role:' + user_role
        str = ""
        # print 'inputlist'
        # print inputlist
        # topology_output = ['                                                             VRF=ISP1_VRF', '                   eth8/2                      eth9/2         94.16.20.1', '  192.168.1.1      vlan102       NX9300        vlan103       94.16.20.0/24', '    source----ingress_interface----DUT----egress_interface----destination']
        topology_output = []
        # for line in topology_output:
        #     print line
        #
        show_cmd = []
        trace_cmd = ['Relevant Logs and Traces:']
        debug_cmd = [
            'Relevant Debugs:', 'Warning: Use debug commands with caution.',
            'Note: In general, it is recommended that debugs only be used under the direction of your technical support representative.']
        tech_support_cmd = ['Relevant Show-Tech:']
        show_config_cmd = []
        elam_capture_cmd = []
        html_link = []
        pkt_cap_output = []
        skip_cmd = []
        additional_output = []
        questionnaire_otuput = []
        restoration_output = ['Possible Restoration Options:',
                              'Note: These steps are from least to more service intrusive order.']
        rca_output = ['Possible Root Cause:']

        # restoration_output = ['<restoration>']
        # rca_output = ['<root cause>']
        skip_start_flag = False
        pkt_cap_start_flag = False  # config and end flags
        additional_output_start_flag = False  # Extra outputs line show int
        elam_capture_start_flag = False
        topology_start_flag = False
        rca_output_start_flag = False
        restoration_output_start_flag = False
        questionnaire_otuput_flag = False
        input_index_num = 0
        inputlist = format_filter_script_output(inputlist, com_dict)
        start_flag = False
        for line in inputlist:
            line = re.sub('<des_ip>', '<dst_ip>', line)
            line = re.sub('<in_int>', '<ingress_interface>', line)
            line = re.sub('<out_int>', '<egress_interface>', line)
            line = line.strip()
            if line:
                input_index_num += 1
                if re.search("-nlead_v1_start Packet Capture", line) or pkt_cap_start_flag:
                    if re.search("nlead_v1_end Packet Capture", line):
                        pkt_cap_start_flag = False
                    elif re.search("-nlead_v1_start Packet Capture", line):
                        pkt_cap_start_flag = True
                    else:
                        pkt_cap_output.append(line)
                elif re.search("-nlead_v1_start Topology:", line) or topology_start_flag:
                    if line == "-nlead_v1_end Topology:":
                        topology_start_flag = False
                    elif line == "-nlead_v1_start Topology:":
                        topology_start_flag = True
                    else:
                        topology_output.append(line)
                elif re.search("show run", line):
                    if not show_config_cmd.__contains__(line):
                        show_config_cmd.append(line)
                elif user_role == 'esc' and (
                        re.search("-nlead_v1_start Additional Commands", line) or additional_output_start_flag):
                    if re.search("-nlead_v1_end Additional Commands", line):
                        additional_output_start_flag = False
                    elif re.search("-nlead_v1_start Additional Commands", line):
                        additional_output_start_flag = True
                    else:
                        if not additional_output.__contains__(line):
                            additional_output.append(line)
                elif not user_role == 'esc' and re.search("Additional Commands", line):
                    continue
                elif re.search(" trace ", line):
                    trace_cmd.append(line)
                elif re.search(" ltrace ", line):
                    trace_cmd.append(line)
                elif re.search("^debug |-debug |- debug|debug-filter", line):
                    debug_cmd.append(line)
                elif re.search("tech-support", line):
                    tech_support_cmd.append(line)
                elif re.search("http://\S+", line):
                    html_link.append(line)
                elif re.search("-nlead_start_Questionnaire", line) or questionnaire_otuput_flag:
                    if re.search("-nlead_end_Questionnaire", line):
                        questionnaire_otuput_flag = False
                    elif re.search("-nlead_start_Questionnaire", line):
                        questionnaire_otuput_flag = True
                    else:
                        questionnaire_otuput.append(line)
                elif re.search("-nlead_v1_start Possible Restoration", line) or restoration_output_start_flag:
                    if re.search("-nlead_v1_end Possible Restoration", line):
                        restoration_output_start_flag = False
                    elif re.search("-nlead_v1_start Possible Restoration", line):
                        restoration_output_start_flag = True
                    else:
                        if not line[0] == '-':
                            line = '- ' + line
                        restoration_output.append(line)


                # elif re.search("nlead_v1_start Elam Capture", line) or elam_capture_start_flag:
                #     if re.search("nlead_v1_end Elam Capture", line):
                #         elam_capture_start_flag = False
                #     elif re.search("nlead_v1_start Elam Capture", line):
                #         elam_capture_start_flag = True
                #     else:
                #         elam_capture_cmd.append(line)
                # elif re.search("nlead_v1_start Packet Capture", line) or elam_capture_start_flag:
                #     if re.search("nlead_v1_end Packet Capture", line):
                #         elam_capture_start_flag = False
                #     elif re.search("nlead_v1_start Packet Capture", line):
                #         elam_capture_start_flag = True
                #     else:
                #         elam_capture_cmd.append(line)
                elif re.search("-nlead_v1_start Possible RCA", line) or rca_output_start_flag:
                    if re.search("-nlead_v1_end Possible RCA", line):
                        rca_output_start_flag = False
                    elif re.search("-nlead_v1_start Possible RCA", line):
                        rca_output_start_flag = True
                    else:
                        if not line[0] == '-':
                            line = '- ' + line
                        rca_output.append(line)
                elif not skip_start_flag:
                    if re.search(r'module \d+', line):
                        line = re.sub(r'module ', 'mod ', line)
                    if not show_cmd.__contains__(line):
                        show_cmd.append(line)
                    # if re.search("-nlead_v1_start Elam Capture", line) and re.search("elam slot ", inputlist[input_index_num]):
                    #     elam_capture_start_flag = True
                    #     elam_capture_cmd.append(line)
                    # if elam_capture_start_flag and re.search("^exi", line):
                    #     elam_capture_start_flag = False

        # output_list = {'show_config_cmd':'', 'show_cmd':'', 'pkt_cap_output':'', 'additional_output':'',
        #                'trace_cmd':'', 'debug_cmd':'', 'config_cmd':'', 'tech_support_cmd':'',
        #                'html_link':'', 'recovery_option':'', 'possible_root_cause':'','topology_output':''}
        # output_list = {}
        output_list = []
        # if show_config_cmd:
        #     output_list.append({"Relevant Configuration": show_config_cmd})
        # if show_config_cmd:
        #     show_config_cmd.insert(0, ' !<- Relevant Configuration ->!')
        if show_cmd:
            final_ks_array = {}
            if not show_cmd[0] == 'Key Troubleshooting Commands:':
                show_cmd = show_config_cmd + show_cmd
                show_cmd.insert(0, 'Key Troubleshooting Commands:')
            else:
                show_cmd.__delitem__(0)
                show_cmd = show_config_cmd + show_cmd
                show_cmd.insert(0, 'Key Troubleshooting Commands:')

            ref_file_name = ios + '_' + tech + '.txt'
            # if os.path.isfile('/home/ubuntu/prepro/mysite/mysite/static/reference_ts_outputs/' + ref_file_name):
            #     show_cmd.insert(0, 'You can check the reference working output here: http://74.95.1.202/static/reference_ts_outputs/' + ref_file_name)
            if topology_output:
                final_ks_array["pre"] = topology_output
                final_ks_array["line"] = show_cmd
                output_list.append({"Key Show Commands": final_ks_array})
            else:
                final_ks_array["pre"] = ""
                final_ks_array["line"] = show_cmd
                output_list.append({"Key Show Commands": final_ks_array})

        # if skip_cmd:
        #     output_list.append({"Skip Show Commands": skip_cmd})
        if elam_capture_cmd:
            output_list.append({"Elam Capture Commands To Narrow Down the Issue": elam_capture_cmd})
        if pkt_cap_output:
            if not pkt_cap_output[0] == 'Packet Capture:':
                pkt_cap_output.insert(0, 'Packet Capture:')
            output_list.append({"Packet Capture": pkt_cap_output})
        if len(tech_support_cmd) > 1:
            output_list.append({"Tech Support": tech_support_cmd})
        if len(questionnaire_otuput) > 1:
            output_list.append({"Questionnaire": questionnaire_otuput})
        if len(rca_output) > 1:
            if not rca_output[0] == 'Possible Root Cause:':
                rca_output.insert(0, 'Possible Root Cause:')
            output_list.append({"Possible Root Cause": rca_output})
        if len(restoration_output) > 2:
            if not restoration_output[0] == 'Possible Restoration Options:':
                restoration_output.insert(0, 'Possible Restoration Options:')
            output_list.append({"Possible Recovery": restoration_output})
        # if len(trace_cmd) > 1:
        #     if not trace_cmd[0] == 'Relevant Logs and Traces:':
        #         trace_cmd.insert(0, 'Relevant Logs and Traces:')
        #     output_list.append({"Logs and Traces": trace_cmd})
        # if len(debug_cmd) > 3:
        #     output_list.append({"Debug": debug_cmd})
        # if config_cmd:
        #     output_list["config_cmd"] = config_cmd
        # if tech_support_cmd:
        #     output_list.append({"Tech Support": tech_support_cmd})
        # if html_link:
        #     output_list.append({"Relevant Resources": html_link})
        # if topology_output:
        #     output_list.append({"Topology": topology_output})

        if len(additional_output) > 1 and TS_LEVEL != 1:
            if not additional_output[0] == 'Additional Key Commands:':
                additional_output.insert(0, 'Additional Commands:')
            output_list.append({"Additional Commands": additional_output})

        self.output_list = output_list
        self.topology_output = topology_output

    # append the restoration steps
    def getModScriptOutput(self):
        return self.output_list

    def getModTopologyOutput(self):
        return self.topology_output


class PresTroubleshootingOutput:
    '''
    Description:
        Class is used to show command output with command and show it to the template.
	Inputs:
		user_sel_dict, inputlist, user_role
	Output:
        Return output_list & topology_output.

    '''

    def __init__(self, user_sel_dict, inputlist, user_role=""):

        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format'''
        ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
        plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))
        tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
        type = ConvertUeseInputs('type', user_sel_dict.get('type'))
        com_dict = {}
        com_dict['ios'] = ios
        com_dict['plat'] = plat
        com_dict['tech'] = tech
        com_dict['type'] = type
        com_dict['user_role'] = user_role
        topology_output = []
        show_cmd = [];
        trace_cmd = ['Relevant Logs and Traces:']
        debug_cmd = ['Relevant Debugs:'];
        tech_support_cmd = [];
        show_config_cmd = []
        elam_capture_cmd = []
        html_link = []
        pkt_cap_output = []
        skip_cmd = []
        additional_output = []
        questionnaire_otuput = []
        restoration_output = ['Possible Restoration Options:']
        rca_output = ['Possible Root Cause:']
        skip_start_flag = False
        pkt_cap_start_flag = False  # config and end flags
        additional_output_start_flag = False  # Extra outputs line show int
        elam_capture_start_flag = False;
        topology_start_flag = False
        rca_output_start_flag = False
        restoration_output_start_flag = False
        questionnaire_otuput_flag = False
        config_flag = False
        input_index_num = 0
        inputlist = format_filter_script_output(inputlist, com_dict)
        for line in inputlist:
            line = re.sub('des_ip', 'dst_ip', line)
            line = re.sub('in_int', 'ingress_interface', line)
            line = re.sub('out_int', 'egress_interface', line)
            line = line.strip()
            if line:
                line = re.sub('-<-', '!<- ', line)
                line = re.sub('-->!', '', line)
                input_index_num += 1
                if re.search("Packet Capture:", line) or pkt_cap_start_flag:
                    if re.search("Packet Capture end", line):
                        pkt_cap_start_flag = False
                    elif re.search("Packet Capture:", line):
                        pkt_cap_start_flag = True
                    else:
                        pkt_cap_output.append(line)
                elif re.search("Key Show Commands:", line) or config_flag:
                    if re.search("Key Show Commands end", line):
                        config_flag = False
                    elif re.search("Key Show Commands:", line):
                        config_flag = True
                        show_cmd.append(line)
                    else:
                        show_cmd.append(line)
                elif re.search("-nlead_v1_start Topology", line) or topology_start_flag:
                    if line == "-nlead_v1_end Topology":
                        topology_start_flag = False
                    elif line == "-nlead_v1_start Topology":
                        topology_start_flag = True
                    else:
                        topology_output.append(line)
                elif re.search("show run", line):
                    show_config_cmd.append(line)
                elif re.search("Additional Commands:", line) or additional_output_start_flag:
                    if re.search("Additional Commands end", line):
                        additional_output_start_flag = False
                    elif re.search("Additional Commands:", line):
                        additional_output_start_flag = True
                    else:
                        additional_output.append(line)
                elif re.search(" trace ", line):
                    trace_cmd.append(line)
                elif re.search(" ltrace ", line):
                    trace_cmd.append(line)
                elif re.search("^debug |-debug |- debug", line):
                    debug_cmd.append(line)
                elif re.search("tech-support", line):
                    tech_support_cmd.append(line)
                elif re.search("http://\S+", line):
                    html_link.append(line)
                elif re.search("-nlead_start_Questionnaire", line) or questionnaire_otuput_flag:
                    if re.search("-nlead_end_Questionnaire", line):
                        questionnaire_otuput_flag = False
                    elif re.search("-nlead_start_Questionnaire", line):
                        questionnaire_otuput_flag = True
                    else:
                        questionnaire_otuput.append(line)
                elif re.search("Possible Restoration:", line) or restoration_output_start_flag:
                    if re.search("Possible Restoration end", line):
                        restoration_output_start_flag = False
                    elif re.search("Possible Restoration:", line):
                        restoration_output_start_flag = True
                    else:
                        restoration_output.append(line)
                elif re.search("Possible RCA:", line) or rca_output_start_flag:
                    if re.search("Possible RCA end", line):
                        rca_output_start_flag = False
                    elif re.search("Possible RCA:", line):
                        rca_output_start_flag = True
                    else:
                        rca_output.append(line)
        output_list = []

        if show_cmd:
            final_ks_array = {}
            if not show_cmd[0] == 'Key Troubleshooting Commands:':
                show_cmd = show_config_cmd + show_cmd
                show_cmd.insert(0, 'Key Troubleshooting Commands:')
            else:
                show_cmd.__delitem__(0)
                show_cmd = show_config_cmd + show_cmd
                show_cmd.insert(0, 'Key Troubleshooting Commands:')

            ref_file_name = ios + '_' + tech + '.txt'
            # if os.path.isfile('/home/ubuntu/prepro/mysite/mysite/static/reference_ts_outputs/' + ref_file_name):
            #     show_cmd.insert(0, 'You can check the reference working output here: http://74.95.1.202/static/reference_ts_outputs/' + ref_file_name)

            if topology_output:
                final_ks_array["pre"] = topology_output
                final_ks_array["line"] = show_cmd
                output_list.append({"Key Show Commands": final_ks_array})
            else:
                final_ks_array["pre"] = ""
                final_ks_array["line"] = show_cmd
                output_list.append({"Key Show Commands": final_ks_array})
        # if show_cmd:
        #     output_list.append({"Key Show Commands": show_cmd})
        # # if skip_cmd:
        # #     output_list.append({"Skip Show Commands": skip_cmd})
        if elam_capture_cmd:
            output_list.append({"Elam Capture Commands To Narrow Down the Issue": elam_capture_cmd})
        if pkt_cap_output:
            output_list.append({"Packet Capture": pkt_cap_output})
        if len(tech_support_cmd) > 1:
            output_list.append({"Tech Support": tech_support_cmd})
        # if topology_output:
        #     output_list.append({"Topology": topology_output})
        if len(rca_output) > 1:
            output_list.append({"Possible Root Cause": rca_output})
        if len(restoration_output) > 1:
            output_list.append({"Possible Recovery": restoration_output})
        if len(trace_cmd) > 1:
            output_list.append({"Logs and Traces": trace_cmd})
        # if len(debug_cmd) > 1:
        #     output_list.append({"Debug": debug_cmd})
        # if html_link:
        #     output_list.append({"Relevant Resources": html_link})
        if questionnaire_otuput:
            output_list.append({"Questionnaire": questionnaire_otuput})
        if len(additional_output) > 1 and TS_LEVEL != 1:
            output_list.append({"Additional Show Commands": additional_output})

        self.output_list = output_list
        self.topology_output = topology_output

    # append the restoration steps
    def getModTemplateOutput(self):
        return self.output_list

    def getModTopologyOutput(self):
        return self.topology_output


# class GetRawOutput:
#     def __init__(self, ios, plat, tech, type, inputs, val):
#         ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
#         and description more user friendly and appropriate convert them into dict format'''
#
#         # type = ConvertUeseInputs('type', com_dict.get(tech2).get('type'))
#         # plat = ConvertUeseInputs('plat',com_dict.get(tech2).get('plat'))
#         # ios = ConvertUeseInputs('ios', com_dict.get(tech2).get('ios'))
#
#
#         #com_dict = {'ip': {'ios': 'nx', 'plat': '7000', 'type': 'forwarding'}}
#         print "tclsh /home/ubuntu/nlead/run_from_py_no_db.tcl %s %s %s %s \"%s\" \"%s\"" % (plat, tech, ios, type, inputs, val)
#         #" % (plat, tech, ios, type)
#         p = subprocess.Popen(
#             "tclsh /home/ubuntu/nlead/run_from_py_no_db.tcl %s %s %s %s \"%s\" \"%s\"" % (plat, tech, ios, type, inputs, val),
#             shell=True,
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE)
#         stdout, stderr = p.communicate()
#         #print stdout
#         inputlist = stdout.splitlines()
#         print inputlist
#         self.raw_script_output = inputlist
#     def getRawScriptOutput(self):
#         return self.raw_script_output

class GetRawOutputFromScript:
    def __init__(self, user_sel_dict, inputs, val, symptom=""):
        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format'''
        ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
        plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))
        tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
        type = ConvertUeseInputs('type', user_sel_dict.get('type'))
        self.raw_script_output = []
        # com_dict = {'ip': {'ios': 'nx', 'plat': '7000', 'type': 'forwarding'}}
        if type == 'loss' and tech == 'ip':
            tech = 'loss'
        if symptom:
            print "tclsh /home/ubuntu/nlead/run_from_py_no_db.tcl %s %s %s %s \"%s\" \"%s\" \"%s\"" % (
                plat, tech, ios, type, inputs, val, symptom)
        else:
            print "tclsh /home/ubuntu/nlead/run_from_py_no_db.tcl %s %s %s %s \"%s\" \"%s\"" % (
                plat, tech, ios, type, inputs, val)
        # " % (plat, tech, ios, type)
        if symptom:
            p = subprocess.Popen(
                "tclsh /home/ubuntu/nlead/run_from_py_no_db.tcl %s %s %s %s \"%s\" \"%s\" \"%s\"" % (
                    plat, tech, ios, type, inputs, val, symptom),
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        else:
            p = subprocess.Popen(
                "tclsh /home/ubuntu/nlead/run_from_py_no_db.tcl %s %s %s %s \"%s\" \"%s\"" % (
                    plat, tech, ios, type, inputs, val),
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        stdout, stderr = p.communicate()
        inputlist = stdout.splitlines()
        start_flag = False
        output_line_counter = 0
        # print 'inputlist'
        # print inputlist
        for line in inputlist:
            # print 'line'
            # print line
            if re.search("!nlead_output_start", line):
                start_flag = True
                continue
            if re.search("!nlead_output_end", line):
                start_flag = False
                continue
            if start_flag:
                output_line_counter += 1
                self.raw_script_output.append(line)
        self.output_line_counter = output_line_counter

    def getRawScriptOutput(self):
        return self.raw_script_output

    def getRawScriptOutputLineCounter(self):
        return self.output_line_counter


class GetRawOutputFromEntScript:
    def __init__(self, user_sel_dict, sym_dict={}):
        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format'''
        ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
        plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))
        tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
        # type2 = ConvertUeseInputs('type', user_sel_dict.get('type'))
        type2 = 'fwd'
        self.raw_script_output = []
        input_list = []
        output_list = []

        if sym_dict:
            for field in sym_dict:
                if sym_dict.get(field):
                    input_list.append(field)
                    value = sym_dict.get(field)
                    if type(value) is list:
                        # input_list.append(key.split("[]")[0])
                        output_list.append(re.sub(', ', '++', (', '.join(value))))
                    else:
                        # input_list.append(key)
                        output_list.append(re.sub(' ', '++', value.strip()))

        input_para_str = (' ').join(input_list)
        output_data_str = (' ').join(output_list)

        # com_dict = {'ip': {'ios': 'nx', 'plat': '7000', 'type': 'forwarding'}}
        print "tclsh /home/ubuntu/nlead/run_enterprise_py.tcl %s %s %s %s \"%s\" \"%s\"" % (
            plat, tech, ios, type2, input_para_str, output_data_str)
        # " % (plat, tech, ios, type)
        p = subprocess.Popen(
            "tclsh /home/ubuntu/nlead/run_enterprise_py.tcl %s %s %s %s \"%s\" \"%s\"" % (
                plat, tech, ios, type2, input_para_str, output_data_str),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        stdout, stderr = p.communicate()
        inputlist = stdout.splitlines()
        start_flag = False
        output_line_counter = 0
        # print 'inputlist'
        # print inputlist
        for line in inputlist:
            # print 'line'
            # print line
            if re.search("!nlead_output_start", line):
                start_flag = True
                continue
            if re.search("!nlead_output_end", line):
                start_flag = False
                continue
            if start_flag:
                output_line_counter += 1
                self.raw_script_output.append(line)
        self.output_line_counter = output_line_counter

    def getRawScriptOutput(self):
        return self.raw_script_output

    def getRawScriptOutputLineCounter(self):
        return self.output_line_counter


class MappingVariable:
    def __init__(self):
        ''' Python to TCL and TCL to Python '''
        # get the input parameters from tcl script


#
class GetRawOutput4:
    def __init__(self):
        ''' Run TCL script, get the output, format the output and return '''


class OutputFormating:
    def __init__(self):
        ''' Run TCL script, get the output, format the output and return '''


def constant(f):
    def fset(self, value):
        raise SyntaxError

    def fget(self):
        return f()

    return property(fget, fset)


class _Const(object):
    @constant
    def FOO():
        return 0xBAADFACE

    @constant
    def BAR():
        return 0xDEADBEEF


#
# CONST = _Const()
#
# print CONST.FOO
# ##3131964110
#
# CONST.FOO = 0
# ##Traceback (most recent call last):
# ##    ...
# ##    CONST.FOO = 0
# ##SyntaxError: None


class UserInputValProcessing:
    global glb_combine_input_list
    global glb_combine_input_val_list

    # global glb_multi_inputs

    # if para == 'vrf':
    #     if input_data[para] == "Yes":
    #         self.extra_input_list.append('vrf')
    #     elif input_data[para] == "No":
    #         vrf_flag = True

    def __init__(self, user_sel_dict, input_data={}, all_user_input_data=[]):
        '''
        - check each input and value - based on diff ios call diffrent fuctions
        - based on input/value create new input list
        - return new_inptut list to view
        - return need_for_new_input_flag True/False
        - return combine_input_para_list
        - return combine_input_val_list
        - return optional Disct of para and values
        '''

        glb_multi_inputs = {}
        ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
        plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))
        tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
        type = ConvertUeseInputs('type', user_sel_dict.get('type'))
        self.raw_script_output = []
        self.extra_input_list = []
        self.additional_input_list = []
        self.port_chanel = {}
        vrf_flag = False
        empty_in_phy_flag = False
        empty_out_phy_flag = False
        for para in input_data.iterkeys():
            if para == 'in_phy':
                if not input_data['in_phy']:
                    empty_in_phy_flag = True

            if para == 'out_phy':
                if not input_data['out_phy']:
                    empty_out_phy_flag = True

        if input_data.has_key('in_int'):
            if empty_in_phy_flag:
                input_data.pop('in_int')
            else:
                if input_data.has_key('in_phy'):
                    input_data['in_int'] = input_data['in_phy']

        if input_data.has_key('out_int'):
            if empty_out_phy_flag:
                input_data.pop('out_int')
            else:
                if input_data.has_key('out_phy'):
                    input_data['out_int'] = input_data['out_phy']

        new_input_data_list = []
        for para in input_data.iterkeys():
            if not new_input_data_list.__contains__(para):
                new_input_data_list.append(para)
        for para in new_input_data_list:
            # if para == 'in_int' or para == 'out_int' and all_user_input_data.__contains__('paragen'):
            #     print 'para'
            #     print para
            #     print 'para value'
            #     print input_data[para]
            #     # call the fuction to get the interface type and next input variable
            #     new_variable = interface_type(ios,para,input_data[para])
            #     # print 'new_variable'
            #     # print new_variable
            #
            #     if new_variable:
            #         if new_variable == 'in_cha':
            #             if not self.extra_input_list.__contains__('in_phy_3'):
            #                 self.extra_input_list.append('in_phy_3')
            #                 self.port_chanel['in_cha'] = input_data[para]
            #             if not self.additional_input_list.__contains__(new_variable):
            #                 self.additional_input_list.append(new_variable)
            #         elif new_variable == 'ou_cha':
            #             if not self.extra_input_list.__contains__('out_phy_3'):
            #                 self.extra_input_list.append('out_phy_3')
            #                 self.port_chanel['ou_cha'] = input_data[para]
            #             if not self.additional_input_list.__contains__(new_variable):
            #                 self.additional_input_list.append(new_variable)
            #         else:
            #             if not self.extra_input_list.__contains__(new_variable):
            #                 self.extra_input_list.append(new_variable)

            if para == 'vrf_option' and not glb_multi_inputs.has_key('vrf'):
                if input_data[para] == 'Yes':
                    glb_multi_inputs['vrf'] = 'Yes'
                    self.extra_input_list.append('tech_with_vrf')
                else:
                    glb_multi_inputs['vrf'] = 'No'
                    self.extra_input_list.append('tech_without_vrf')

            if para == 'ip_ver':
                self.additional_input_list.append(para)

        self.input_data = input_data

    def getExtraInputs(self):
        return self.extra_input_list

    def getReplaceInputs(self):
        return self.additional_input_list

    def getPortChannelInfo(self):
        return self.port_chanel

    def getModInputParaList(self, intput_para):
        extra_inputs = self.extra_input_list
        for ext_input in extra_inputs:
            # print 'from sub_class'
            # print ext_input
            # print intput_para
            if not intput_para.__contains__(ext_input):
                if ext_input == 'in_phy_2':
                    intput_para.append('in_phy')
                elif ext_input == 'in_phy_3':
                    intput_para.append('in_phy')
                elif ext_input == 'out_phy_2':
                    intput_para.append('out_phy')
                elif ext_input == 'out_phy_3':
                    intput_para.append('out_phy')
                else:
                    intput_para.append(ext_input)
        return intput_para

    def GetNewInputPara(self, new_input_para):
        port_channel = self.port_chanel
        for el in new_input_para:
            if port_channel.has_key(el):
                port_channel['in_cha']
                new_input_para.append(el)
        self.new_input_para = new_input_para
        return self.new_input_para

    def GetNewOutputList(self, new_input_para, outputlist):
        port_channel = self.port_chanel
        for el in new_input_para:
            if port_channel.has_key(el):
                outputlist.append(port_channel[el])
        self.outputlist = outputlist
        return self.outputlist


# def interface_type(ios='', para='', interface_name=''):
#     global TS_LEVEL
#     new_input = ''
#     # NEED TO REMOVE AFTER FIXING THE Recovery PART!!
#     #if {($CON(ios) == "ios") || ($CON(ios) == "nx")} {
#     sub_num = ""
#     new_input_flag = False
#     if ios == 'nx':
#         if re.search('^[vV]',interface_name):
#             new_input_flag = True
#         if re.search('^[pP]',interface_name):
#             new_input_flag = True
#         if new_input_flag:
#             print 'para'
#             print para
#             if para == 'in_int':
#                 return 'in_phy'
#             elif para == 'out_int':
#                 return 'out_phy'
#             else:
#                 print 'error: para %s' %para
#         return False

def interface_type(ios='', para='', interface_name=''):
    global TS_LEVEL
    new_input = ''
    # NEED TO REMOVE AFTER FIXING THE Recovery PART!!
    # if {($CON(ios) == "ios") || ($CON(ios) == "nx")} {
    sub_num = ""
    new_input_flag = False
    if ios == 'nx' or 'ios':
        if re.search('^[vV]', interface_name):
            new_input_flag = True
        if re.search('^[pP]', interface_name):
            if para == 'in_int':
                return 'in_cha'
            elif para == 'out_int':
                return 'ou_cha'
        if new_input_flag:
            if para == 'in_int':
                return 'in_phy_2'
            elif para == 'out_int':
                return 'out_phy_2'
            else:
                print 'error: para %s' % para
        return False


def change_interface_format(ios='', interface_name=''):
    # need to modify for XR bridge domain and other interface types
    return interface_name.lower()


def validate_interface_format(ios='', interface_name=''):
    # need to modify for XR bridge domain and other interface types
    interface_name = interface_name.lower()
    if re.search('^[lL]', interface_name):
        match = re.search(r"(\d+)", interface_name)
        if match:
            if int(match.group(0)) > 0 and int(match.group(0)) < 4095:
                return True
            else:
                return 'Loopback number %s is out of range: %s' % (match.group(0), interface_name)
    if ios == 'NX-IOS':
        if re.search('^[v]', interface_name):
            match = re.search(r"(\d+)", interface_name)
            if match:
                if int(match.group(0)) > 0 and int(match.group(0)) < 4095:
                    return True
                else:
                    return 'VLAN number %s is out of range: %s' % (match.group(0), interface_name)
        if re.search('^[p]|^[bB]', interface_name):
            match = re.search(r"(\d+)", interface_name)
            if match:
                if int(match.group(0)) > 0 and int(match.group(0)) < 4095:
                    return True
                else:
                    return 'Port-channel number %s is out of range: %s' % (match.group(0), interface_name)
        if re.search('^[e]', interface_name):
            # return True
            match = re.search(r"(\d+)/(\d+)", interface_name)
            if match:
                if int(match.group(1)) > 0 and int(match.group(1)) < 253:
                    match = re.search(r"(\d+)/(\d+)", interface_name)
                    if match:
                        if int(match.group(2)) > 0 and int(match.group(2)) < 253:
                            return True
                    else:
                        return 'Chassis/slot number %s is out of range: %s' % (match.group(2), interface_name)
                else:
                    return 'Chassis/slot number %s is out of range: %s' % (match.group(1), interface_name)
            else:
                return 'Invalid Interface Name: %s' % interface_name
        return 'Invalid or unsupported Interface: %s' % interface_name
    elif ios == 'XR-IOS':
        if re.search('^v|^e', interface_name):
            return 'Invalid Interface format %s' % interface_name
        if re.search('^[f]|^[g]|^[te]|^[p]|^[h]', interface_name):
            match = re.search(r"\S+\s?(\d+)/(\d+)/(\d+)/(\d+)", interface_name)
            if match:
                if int(match.group(1)) in range(0, 253):
                    if int(match.group(2)) in range(0, 253):
                        if int(match.group(3)) in range(0, 253):
                            return True
                        else:
                            return 'Interface  %s is out of range: %s' % (match.group(0), interface_name)
                    else:
                        return 'Interface  %s is out of range: %s' % (match.group(0), interface_name)
                else:
                    return 'Interface %s is out of range: %s' % (match.group(0), interface_name)
            else:
                return 'Invalid Interface format %s: %s' % (interface_name, interface_name)
        return True
    elif ios == 'IOS':
        match = re.search(r"\S+\s?(\d+)/(\d+)/(\d+)/(\d+)", interface_name)
        if match:
            return 'Invalid Interface format %s' % interface_name
        if re.search('^[f]|^[g]|^[te]|^[p]|^[h]', interface_name):
            match = re.search(r"\S+\s?(\d+)/(\d+)", interface_name)
            if match:
                if int(match.group(1)) in range(0, 253):
                    if int(match.group(2)) in range(0, 253):
                        return True
                    else:
                        return 'Interface  %s is out of range' % match.group(0)
                else:
                    return 'Interface %s is out of range' % match.group(0)
            else:
                return 'Invalid Interface format %s' % interface_name
        return True
    return True


def get_interface_type(ios='', interface_name=''):
    # need to modify for XR bridge domain and other interface types
    if re.search('^[vV]', interface_name):
        return 'svi'
    if re.search('^[pP]|^[bB]', interface_name):
        return 'cha'
    if re.search('\/\d+', interface_name):
        return 'def'
    return False


def get_last_user_input_value(field_name, user_name, taskid="", subtaskid="", customer="", device=""):
    # logic for getting field value based on nested if else
    db_value = ""
    if taskid != "":
        entry = UserInputValueDb.objects.filter(field_name=field_name, taskid=taskid, subtaskid=subtaskid)
        if entry:
            db_field_data = UserInputValueDb.objects.filter(field_name=field_name, taskid=taskid,
                                                            subtaskid=subtaskid).last()
            if db_field_data:
                db_value = db_field_data.field_value
        else:
            entry = UserInputValueDb.objects.filter(field_name=field_name, customer=customer)
            if entry:
                db_field_data = UserInputValueDb.objects.filter(field_name=field_name, customer=customer).last()

                if db_field_data:
                    db_value = db_field_data.field_value
            # else:
            # entry = UserInputValueDb.objects.filter(field_name=field_name, user=user_name)
            # if entry:
            # db_field_data = UserInputValueDb.objects.filter(field_name=field_name, user=user_name).last()
            # if db_field_data:
            # db_value = db_field_data.field_value
    else:
        entry = UserInputValueDb.objects.filter(field_name=field_name, user=user_name).last()
        if entry:
            db_field_data = UserInputValueDb.objects.filter(field_name=field_name, user=user_name).last()
            if db_field_data:
                db_value = db_field_data.field_value

    return db_value


# function for gtting list
def search_last_user_input_value(field_name, customer):
    from mysite.models import UserInputValueDb
    # logic for getting field value based on nested if else
    entry = UserInputValueDb.objects.filter(field_name=field_name, customer=customer).values_list('field_value',
                                                                                                  flat=True).distinct()
    if entry:
        return entry
    else:
        return []


def get_new_response_data(response_data, user_name, taskid="", subtaskid="", customer="", device=""):
    new_response_data = []
    if type(response_data) is dict:
        if response_data.has_key('column'):
            response_data = response_data.get('inputs')
    ingress_interface_type = 'def'
    egress_interface_type = 'def'
    in_phy_2_send = False
    in_phy_3_send = False
    ou_phy_2_send = False
    ou_phy_3_send = False
    for comb_input in response_data:
        if type(comb_input) is dict:
            bd_entry_found = False
            if comb_input.has_key('name'):
                field_value = ""
                if not comb_input.get('name') == 'user':
                    field_value = get_last_user_input_value(comb_input.get('name'), user_name, taskid, subtaskid,
                                                            customer, device)
                if comb_input.get('name') == 'in_int':
                    ingress_interface_type = get_interface_type('ios', field_value)
                    if not ingress_interface_type == 'def':
                        in_phy_2_send = True

                if comb_input.get('name') == 'in_phy_2':
                    if in_phy_2_send:
                        ingress_interface_type = get_interface_type('ios', field_value)
                        if not ingress_interface_type == 'def':
                            in_phy_3_send = True
                # else:
                #         continue
                # if comb_input.get('name') == 'in_phy_3' and in_phy_3_send == False:
                #     continue

                if comb_input.get('name') == 'out_int':
                    egress_interface_type = get_interface_type('ios', field_value)
                    if not egress_interface_type == 'def':
                        ou_phy_2_send = True

                if comb_input.get('name') == 'ou_int':
                    egress_interface_type = get_interface_type('ios', field_value)
                    if not egress_interface_type == 'def':
                        ou_phy_2_send = True

                if comb_input.get('name') == 'ou_phy_2':
                    if ou_phy_2_send:
                        egress_interface_type = get_interface_type('ios', field_value)
                        if not egress_interface_type == 'def':
                            ou_phy_3_send = True
                            # else:
                            #     continue
                # if comb_input.get('name') == 'ou_phy_3' and ou_phy_3_send == False:
                #     continue

                if comb_input.get('name') == 'in_phy_2' and not in_phy_2_send:
                    bd_entry_found = False
                elif comb_input.get('name') == 'in_phy_3' and not in_phy_3_send:
                    bd_entry_found = False
                elif comb_input.get('name') == 'ou_phy_2' and not ou_phy_2_send:
                    bd_entry_found = False
                elif comb_input.get('name') == 'ou_phy_3' and not ou_phy_3_send:
                    bd_entry_found = False
                elif field_value:
                    # print 'field_value'
                    # print field_value
                    comb_input_new = comb_input
                    comb_input_new['default1'] = field_value
                    bd_entry_found = True
                if bd_entry_found:
                    new_response_data.append(comb_input_new)
                else:
                    new_response_data.append(comb_input)
    return {"column": "12", "newline": "yes", "inputs": new_response_data}


def get_new_response_data_ts(response_data, user_name, sel_para={}, taskid="", subtaskid="", customer="", device=""):
    new_response_data = []
    if type(response_data) is dict:
        if response_data.has_key('column'):
            response_data = response_data.get('inputs')
    ingress_interface_type = 'def'
    egress_interface_type = 'def'
    in_phy_2_send = False
    in_phy_3_send = False
    ou_phy_2_send = False
    ou_phy_3_send = False
    response_data = convert_new_to_old_para_dict(response_data)
    for comb_input in response_data:
        if type(comb_input) is dict:
            bd_entry_found = False
            if comb_input.has_key('name'):
                field_value = ""
                if not comb_input.get('name') == 'user':
                    print "I am going for an update ::"
                    field_value = get_last_user_input_value(comb_input.get('name'), taskid, subtaskid, user_name,
                                                            customer, device)
                    if field_value:
                        comb_input_for_validate = {}
                        comb_input_for_validate[comb_input.get('name')] = field_value
                        #
                        # comb_input_for_validate = comb_input
                        # comb_input_for_validate['default1'] = field_value
                        # print 'comb_input_for_validate need to del'
                        # print comb_input_for_validate
                        # print 'user_input_validation'
                        # print user_input_validation(sel_para, comb_input_for_validate)
                        if user_input_validation(sel_para, comb_input_for_validate):
                            new_response_data.append(comb_input)
                            continue
                if comb_input.get('name') == 'in_int':
                    ingress_interface_type = get_interface_type('ios', field_value)
                    if not ingress_interface_type == 'def':
                        in_phy_2_send = True

                if comb_input.get('name') == 'in_phy_2':
                    if in_phy_2_send:
                        ingress_interface_type = get_interface_type('ios', field_value)
                        if not ingress_interface_type == 'def':
                            in_phy_3_send = True
                # else:
                #         continue
                # if comb_input.get('name') == 'in_phy_3' and in_phy_3_send == False:
                #     continue

                if comb_input.get('name') == 'out_int':
                    egress_interface_type = get_interface_type('ios', field_value)
                    if not egress_interface_type == 'def':
                        ou_phy_2_send = True

                if comb_input.get('name') == 'ou_int':
                    egress_interface_type = get_interface_type('ios', field_value)
                    if not egress_interface_type == 'def':
                        ou_phy_2_send = True

                if comb_input.get('name') == 'ou_phy_2':
                    if ou_phy_2_send:
                        egress_interface_type = get_interface_type('ios', field_value)
                        if not egress_interface_type == 'def':
                            ou_phy_3_send = True
                            # else:
                            #     continue
                # if comb_input.get('name') == 'ou_phy_3' and ou_phy_3_send == False:
                #     continue

                if comb_input.get('name') == 'in_phy_2' and not in_phy_2_send:
                    bd_entry_found = False
                elif comb_input.get('name') == 'in_phy_3' and not in_phy_3_send:
                    bd_entry_found = False
                elif comb_input.get('name') == 'ou_phy_2' and not ou_phy_2_send:
                    bd_entry_found = False
                elif comb_input.get('name') == 'ou_phy_3' and not ou_phy_3_send:
                    bd_entry_found = False
                elif field_value:
                    # print 'field_value'
                    # print field_value
                    comb_input_new = comb_input
                    comb_input_new['default1'] = field_value
                    bd_entry_found = True
                if bd_entry_found:
                    new_response_data.append(comb_input_new)
                else:
                    new_response_data.append(comb_input)
    new_response_data = convert_input_para_dict(new_response_data)
    # response_data = convert_new_to_old_para_dict(response_data)
    return {"column": "12", "newline": "yes", "inputs": new_response_data}


global os_specific_fields
os_specific_fields = ['in_int', 'out_int', 'ou_int', 'interface_1', 'interface_2', 'in_phy', 'ou_phy',
                      'layer2_interface',
                      'in_phy_2', 'ou_phy_2', 'in_phy_3', 'ou_phy_3', 'site_vlan_int', 'join_interface']

tech_specific_fields = ['src_ip', 'des_ip', 'nh', 'peer_ip']

from netaddr import *


def user_input_validation(sel_para={}, user_input={}):
    # print 'sel_para'
    # print sel_para
    # print 'user_input'
    # print user_input
    input_validation_errors = []
    ipv4_add_type = ['remote_vtp_ip']
    ipv4_mulitcast_add_type = ['mcast_group', 'mcast_control_group']
    number_type = ['l2_vlan_num', 'vlan_id']
    interface_type = []
    for key, value in user_input.iteritems():
        # print key
        # print value
        if value:
            # verify range is not included
            if value.__contains__(','):
                continue
            elif value.__contains__('-'):
                continue
            if ipv4_mulitcast_add_type.__contains__(key):
                if not re.search(
                        r"\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b",
                        value):
                    input_validation_errors.append({'id': key, 'message': '%s is invalid: %s' % ('Input', value)})
                else:
                    try:
                        ip = IPAddress(value)
                        if not ip.is_multicast():
                            print input_validation_errors
                            input_validation_errors.append(
                                {'id': key, 'message': '%s is invalid: %s' % ('Input', value)})
                    except ValueError:
                        input_validation_errors.append({'id': key, 'message': '%s is invalid: %s' % ('Input', value)})
                    except:
                        input_validation_errors.append({'id': key, 'message': '%s is invalid: %s' % ('Input', value)})
            elif ipv4_add_type.__contains__(key):
                if not re.search(
                        r"\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b",
                        value):
                    input_validation_errors.append({'id': key, 'message': '%s is invalid: %s' % ('Input', value)})
                else:
                    try:
                        ip = IPAddress(value)
                        if not ip.is_unicast():
                            print input_validation_errors
                            input_validation_errors.append(
                                {'id': key, 'message': '%s is invalid: %s' % ('Input', value)})
                    except ValueError:
                        input_validation_errors.append({'id': key, 'message': '%s is invalid: %s' % ('Input', value)})
                    except:
                        input_validation_errors.append({'id': key, 'message': '%s is invalid: %s' % ('Input', value)})
            elif os_specific_fields.__contains__(key):
                validation_result = validate_interface_format(sel_para.get('ios'), value)
                if not validation_result == True:
                    input_validation_errors.append({'id': key, 'message': validation_result})
            elif number_type.__contains__(key):
                if not re.search(r"^\d+$", value):
                    input_validation_errors.append({'id': key, 'message': '%s is invalid: %s' % ('Input', value)})
                    # print key
                    # print value
    # return False
    # result = {"status":"0","inputs":[{"id":"tenant_vlan_num","message":"Please Enter Email Address"}]}
    # return {"status":"0","inputs":[{"id":"tenant_vlan_num","message":"Please Enter Email Address"}]}
    # print 'input_validation_errors'
    # print input_validation_errors
    return input_validation_errors

    # response_data = {"status":"0","inputs":[{"id":"tenant_vlan_num","message":"Please Enter Email Address"}]}


def convert_new_to_old_para_dict(new_list):
    # print 'new_list'
    # print new_list
    old_list = []
    if type(new_list) is dict:
        if new_list.has_key('column'):
            new_list = new_list.get('inputs')
    # print 'new_list'
    # print new_list

    for el in new_list:
        if el.get('type') == 'oneline':
            for input_data in el.get('data').get('inputs'):
                old_list.append(input_data)
        else:
            old_list.append(el)
    return old_list


# working 4/30
def get_new_response_data_old(response_data, user_name, taskid="", subtaskid="", cusomer="", device=""):
    new_response_data = []
    if type(response_data) is dict:
        if response_data.has_key('column'):
            response_data = response_data.get('inputs')
    ingress_interface_type = 'def'
    egress_interface_type = 'def'
    in_phy_2_send = False
    in_phy_3_send = False
    ou_phy_2_send = False
    ou_phy_3_send = False
    for comb_input in response_data:
        if type(comb_input) is dict:
            bd_entry_found = False
            if comb_input.has_key('name'):
                field_value = ""
                if not comb_input.get('name') == 'user':
                    field_value = get_last_user_input_value(comb_input.get('name'), user_name, taskid, subtaskid,
                                                            customer, device)
                if comb_input.get('name') == 'in_int':
                    ingress_interface_type = get_interface_type('ios', field_value)
                    if not ingress_interface_type == 'def':
                        in_phy_2_send = True

                if comb_input.get('name') == 'in_phy_2':
                    if in_phy_2_send:
                        ingress_interface_type = get_interface_type('ios', field_value)
                        if not ingress_interface_type == 'def':
                            in_phy_3_send = True
                    else:
                        continue
                if comb_input.get('name') == 'in_phy_3' and in_phy_3_send == False:
                    continue

                if comb_input.get('name') == 'out_int':
                    egress_interface_type = get_interface_type('ios', field_value)
                    if not egress_interface_type == 'def':
                        ou_phy_2_send = True

                if comb_input.get('name') == 'ou_int':
                    egress_interface_type = get_interface_type('ios', field_value)
                    if not egress_interface_type == 'def':
                        ou_phy_2_send = True

                if comb_input.get('name') == 'ou_phy_2':
                    if ou_phy_2_send:
                        egress_interface_type = get_interface_type('ios', field_value)
                        if not egress_interface_type == 'def':
                            ou_phy_3_send = True
                    else:
                        continue
                if comb_input.get('name') == 'ou_phy_3' and ou_phy_3_send == False:
                    continue

                if field_value:
                    # print 'field_value'
                    # print field_value
                    comb_input_new = comb_input
                    comb_input_new['default1'] = field_value
                    bd_entry_found = True
                if bd_entry_found:
                    new_response_data.append(comb_input_new)
                else:
                    new_response_data.append(comb_input)
    return {"column": "12", "newline": "yes", "inputs": new_response_data}


def get_new_response_data_tp(response_data, user_name, user_tech, user_type, taskid="", subtaskid="", customer="",
                             device=""):
    new_response_data = []

    if type(response_data) is dict:
        if response_data.has_key('column'):
            response_data = response_data.get('inputs')
    response_data = convert_new_to_old_para_dict(response_data)
    for comb_input in response_data:
        bd_entry_found = False
        if comb_input.has_key('name'):
            field_value = ""
            field_value = get_last_user_input_value(comb_input.get('name'), user_name, taskid, subtaskid, customer,
                                                    device)
            if field_value:
                # print 'field_value'
                # print field_value
                comb_input_new = comb_input
                comb_input_new['default1'] = field_value
                bd_entry_found = True
        if bd_entry_found:
            new_response_data.append(comb_input_new)
        else:
            new_response_data.append(comb_input)
    new_response_data = convert_input_para_dict_tp(new_response_data, user_tech, user_type)
    return {"column": "12", "newline": "yes", "inputs": new_response_data}


def get_new_response_data_tp_old(response_data, user_name, taskid, subtaskid, customer, device):
    new_response_data = []
    if type(response_data) is dict:
        if response_data.has_key('column'):
            response_data = response_data.get('inputs')
    response_data = convert_new_to_old_para_dict(response_data)
    for comb_input in response_data:
        bd_entry_found = False
        if comb_input.has_key('name'):
            field_value = ""
            field_value = get_last_user_input_value(comb_input.get('name'), user_name, taskid, subtaskid, customer,
                                                    device)
            if field_value:
                # print 'field_value'
                # print field_value
                comb_input_new = comb_input
                comb_input_new['default1'] = field_value
                bd_entry_found = True
        if bd_entry_found:
            new_response_data.append(comb_input_new)
        else:
            new_response_data.append(comb_input)
    new_response_data = convert_input_para_dict(new_response_data)
    return {"column": "12", "newline": "yes", "inputs": new_response_data}


def update_user_input_in_db(para, user_name, taskid="", subtaskid="", customer="", device=""):
    # para = {'neigh_ip': "1.1.1.1", 'neigh_as': "65001"}
    for field_name in para.iterkeys():
        # print 'field_name'
        # print field_name
        # print para.get(field_name)
        if (field_name == 'vrf' or para.get(field_name)) and not re.search('<\S+>', para.get(field_name)):
            if taskid != "":

                entry = UserInputValueDb.objects.filter(field_name=field_name, taskid=taskid,
                                                        subtaskid=subtaskid).last()
                if not entry:
                    p1 = UserInputValueDb(field_name=field_name, field_value=para.get(field_name), user=user_name,
                                          taskid=taskid, subtaskid=subtaskid,
                                          customer=customer, device=device)
                    p1.save()
                else:
                    p1 = UserInputValueDb.objects.filter(id=entry.id).update(field_value=para.get(field_name))
            else:
                entry = UserInputValueDb.objects.filter(field_name=field_name, user=user_name).last()
                # print entry
                if not entry:
                    p1 = UserInputValueDb(field_name=field_name, field_value=para.get(field_name), user=user_name,
                                          customer="", device="")
                    p1.save()
                else:
                    print "here in update"
                    p1 = UserInputValueDb.objects.filter(id=entry.id).update(field_value=para.get(field_name))
    return True


def genrate_inputs_dict(input_dict, hostname=[]):
    '''
    Description :
        In this function declaration of global vrf and their ips  and updating the input_dict with data respect to vrf.
	Inputs :
		input_dict, hostname
	Output:
        Updating the input_dict with data respect to vrf.

    :param input_dict:
    :param hostname:
    :return:
    '''
    print "IN Genrate Input Dicts"
    global_val_dict_1 = {'grn200_loopback': '10.145.255.0/32',
                         'vl200_subnet': '10.144.0.0/23',
                         'vl210_subnet': '10.145.0.0/25',
                         'vl700_subnet': '10.188.0.0/23',
                         'vl1100_subnet': '10.145.64.0/25',
                         'blu300_loopback': '10.148.63.0/32',
                         'vl300_subnet': '10.148.0.0/26',
                         'blu310_loopback': '10.148.191.0/32',
                         'vl310_subnet': '10.148.128.0/25',
                         'blu320_loopback': '10.148.255.0/32',
                         'vl320_subnet': '10.148.192.0/27',
                         'blu330_loopback': '10.148.127.0/32',
                         'vl330_subnet': '10.148.64.0/26',
                         'orn400_loopback': '10.143.255.0/32',
                         'vl400_subnet': '10.143.0.0/27',
                         'red910_loopback': '10.146.191.0/32',
                         'vl910_subnet': '10.146.128.0/25',
                         'remote_uplink_subnet': '10.145.250.0/30',
                         'grn200_uplink_subnet': '10.145.250.0/30',
                         'blu310_uplink_subnet': '10.145.250.0/30',
                         'blu300_uplink_subnet': '10.145.250.0/30',
                         'orn400_uplink_subnet': '10.145.250.0/30', }
    # grn200_loopback_pool = "10.145.255.0/24"
    # grn200_loopback = list[sr_no]
    # grn200_loopback = 10.145.255.1/32
    # grn200_loopback = grn200_loopback_pool
    global_val_dict = dict(grn200_loopback='10.145.255.0/32', vl200_subnet='', vl200_vip='', vl210_subnet='',
                           vl210_vip='', vl700_subnet='', vl700_vip='', vl1100_subnet='', vl1100_vip='',
                           blu300_loopback='10.148.63.0/32', vl300_subnet='', vl300_vip='',
                           blu310_loopback='10.148.191.0/32', vl310_subnet='', vl310_vip='',
                           blu320_loopback='10.148.255.0/32', vl320_subnet='', vl320_vip='',
                           blu330_loopback='10.148.127.0/32', vl330_subnet='', blu350_loopback='10.148.127.0/32',
                           vl350_subnet='', vl350_vip='', vl330_vip='', orn400_loopback='10.143.255.0/32',
                           vl400_subnet='', vl400_vip='', red910_loopback='10.146.191.0/32', vl910_subnet='',
                           vl910_vip='', remote_as="65240", site_of_origin="500:500", local_as="",
                           remote_uplink_subnet='10.145.250.0/30', grn200_uplink_subnet='10.146.250.0/30',
                           blu310_uplink_subnet='10.147.250.0/30', blu300_uplink_subnet='10.148.250.0/30',
                           blu350_uplink_subnet='10.148.250.0/30', orn400_uplink_subnet='10.149.250.0/30')
    if hostname:
        for device in hostname:
            with open('/home/ubuntu/prepro/mysite/mysite/Json_DATA/device_subnet.json') as subnet_json_data:
                subnet_data = json.load(subnet_json_data)

                for key, value in subnet_data[device.strip()].iteritems():
                    vlan = 'vl' + key.strip('Vlan')
                    vlan_subnet = vlan + "_subnet"
                    # print " Key >>", key
                    if vlan_subnet in global_val_dict and 'ip' in value:
                        global_val_dict[vlan_subnet] = value['ip'] + " " + value['mask']
                    vlan_vip = vlan + "_vip"
                    if vlan_vip in global_val_dict and 'vip' in value:
                        global_val_dict[vlan_vip] = value['vip']
                    elif 'vip' not in value and 'ip' in value:
                        vlan_vip_ip = str(IPAddress(value['ip']) - 1)
                        global_val_dict[vlan_vip] = vlan_vip_ip
    # print global_val_dict
    # net_mask = int(input_dict['subnet_mask']) - 6
    sr_no = int(input_dict['sr_no'])
    for key, val in global_val_dict.iteritems():
        if "/" in val:
            subnet_mask = val.split('/')[1]
            ip_addr = val.split('/')[0]
            if "loopback" in key:
                input_dict[key + "_pool"] = ip_addr + "/24"
                ip = IPNetwork(input_dict[key + "_pool"])
                subnet = list(ip.subnet(32))
                input_dict[key] = str(IPAddress(subnet[sr_no]))
                # print ">>>>>IP >>>>>",sr_no, ip, key, input_dict[key]
            else:
                net_mask = int(subnet_mask) - 6
                ip = IPNetwork(ip_addr + '/' + str(net_mask))
                subnet = list(ip.subnet(31))
                input_dict[key] = str(IPAddress(subnet[sr_no]))
        else:
            input_dict[key] = val
    if input_dict['ext_dict']['ext_name'] == "9300":
        input_dict['trunk_interface_1'] = "Ten1/1"
        input_dict['trunk_interface_2'] = "Ten2/1"
    elif input_dict['ext_dict']['ext_name'] == "9400":
        input_dict['trunk_interface_1'] = "Ten5/0/1"
        input_dict['trunk_interface_2'] = "Ten6/0/1"
    elif input_dict['ext_dict']['ext_name'] == "9300_stack":
        input_dict['trunk_interface_1'] = "Ten1/1/1"
        input_dict['trunk_interface_2'] = "Ten2/1/1"
    elif input_dict['ext_dict']['ext_name'] in ["4500", "3850"]:
        input_dict['trunk_interface_1'] = "Ten1/1/1"
        input_dict['trunk_interface_2'] = "Ten2/1/1"
    input_dict['remote_uplink_interface'] = input_dict['distro_sw_port']
    # input_dict['uplink_vlan_thr'] = str((sr_no-1)*14)
    input_dict['uplink_vlan_thr'] = '3000'
    if input_dict.has_key('local_as_nm'):
        input_dict['local_as'] = input_dict.get('local_as_nm')
    l3_int_dict = {'l3_int_grn200_remote': input_dict['distro_sw_port'] + ".3201",
                   'l3_int_grn200_remote_2': input_dict['distro_sw_port'] + ".3202",
                   'l3_int_blu300_remote': input_dict['distro_sw_port'] + ".3301",
                   'l3_int_blu300_remote_2': input_dict['distro_sw_port'] + ".3302",
                   'l3_int_blu310_remote': input_dict['distro_sw_port'] + ".3311",
                   'l3_int_blu310_remote_2': input_dict['distro_sw_port'] + ".3312",
                   'l3_int_blu320_remote': input_dict['distro_sw_port'] + ".3321",
                   'l3_int_blu320_remote_2': input_dict['distro_sw_port'] + ".3322",
                   'l3_int_blu330_remote': input_dict['distro_sw_port'] + ".3331",
                   'l3_int_blu330_remote_2': input_dict['distro_sw_port'] + ".3332",
                   'l3_int_orn400_remote': input_dict['distro_sw_port'] + ".3401",
                   'l3_int_orn400_remote_2': input_dict['distro_sw_port'] + ".3402",
                   'l3_int_red910_remote': input_dict['distro_sw_port'] + ".3911",
                   'l3_int_red910_remote_2': input_dict['distro_sw_port'] + ".3912", }
    input_dict.update(l3_int_dict)

    return input_dict


# important
def get_list_from_range(user_range_str, total_count=30):
    input_list = []
    last_digit = ""
    print user_range_str
    match = re.search(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}-(?:[0-9]{1,3}\.){3}[0-9]{1,3}", user_range_str)
    if match:
        return [user_range_str.split('-')[0]]
        # match = re.search(r"^?:(([0-9]{1,3}\.){3}[0-9]{1,3})-(?:[0-9]{1,3}\.){3}[0-9]{1,3}", user_range_str)
        # if match:
        #     return input_list.append(match.group(1))
    list = user_range_str.split(',')
    # 101-105
    match2 = re.search(r"(\d+)-(\d+)", user_range_str)
    # interface 5/6-8
    match3 = re.search(r"/", user_range_str)
    match4 = re.search(r"(\d+)-", user_range_str)
    # ip address
    match = re.search(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}/\d", user_range_str)
    if match:
        return list
    elif len(list) <= 1 and not match2 and not match3:
        return list
    elif not match4:
        return list
    else:
        count = 1
        for el in list:
            new_value = ""
            input_name = ""
            match = re.search(r"(\d+)-(\d+)", el)
            if match:
                lower_range = int(match.group(1))
                high_range = int(match.group(2))
                if not re.search(r"^\d+-\d+", el):
                    # match = re.search(r"(\S+)\d+-\d+", el)
                    if match:
                        input_name = re.sub('%s-%s' % (lower_range, high_range), '', el)
                        # input_name = match.group(1)
                while lower_range <= high_range:
                    if count > total_count:
                        return input_list
                    else:
                        if not input_list.__contains__(lower_range):
                            if input_name:
                                new_value = input_name + str(lower_range)
                            else:
                                new_value = str(lower_range)
                            input_list.append(new_value)
                            count += 1
                        else:
                            print "error: overlapping range %s" % user_range_str
                    lower_range += 1
                continue
            if not re.search(r"^\d+$", el):
                # vlan102
                match = re.search(r"(\S+)(\d+)$", el)
                if match:
                    input_name = match.group(1)
                    last_digit = match.group(2)
            # 103
            match = re.search(r"(\d+)$", el)
            if match:
                if count > total_count:
                    print 'elements in the range exceeded the allowed limit of %d' % total_count
                    return input_list
                else:
                    # 225.1.1.20,225.1.2.20
                    if not input_list.__contains__(str(match.group(1))):
                        if input_name:
                            new_value = el
                            # new_value = input_name + str(match.group(1))
                        else:
                            new_value = str(match.group(1))
                        input_list.append(new_value)
                        count += 1
                    else:
                        print "error: overlapping range %s" % user_range_str

    return input_list


def get_list_from_range_old(user_range_str, total_count=30):
    input_list = []
    match = re.search(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}-(?:[0-9]{1,3}\.){3}[0-9]{1,3}", user_range_str)
    if match:
        return [user_range_str.split('-')[0]]
        # match = re.search(r"^?:(([0-9]{1,3}\.){3}[0-9]{1,3})-(?:[0-9]{1,3}\.){3}[0-9]{1,3}", user_range_str)
        # if match:
        #     return input_list.append(match.group(1))
    list = user_range_str.split(',')
    match2 = re.search(r"(\d+)-(\d+)", user_range_str)
    match3 = re.search(r"/", user_range_str)
    match = re.search(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}/\d", user_range_str)
    if match:
        return list
    elif len(list) <= 1 and not match2 and not match3:
        return list
    else:
        count = 1
        for el in list:
            new_value = ""
            input_name = ""
            match = re.search(r"(\d+)-(\d+)", el)
            if match:
                lower_range = int(match.group(1))
                high_range = int(match.group(2))
                if not re.search(r"^\d+-\d+", el):
                    match = re.search(r"(\S+)\d+-\d+", el)
                    if match:
                        input_name = match.group(1)
                while lower_range <= high_range:
                    if count > total_count:
                        return input_list
                    else:
                        if not input_list.__contains__(lower_range):
                            if input_name:
                                new_value = input_name + str(lower_range)
                            else:
                                new_value = str(lower_range)
                            input_list.append(new_value)
                            count += 1
                        else:
                            print "error: overlapping range %s" % user_range_str
                    lower_range += 1
                continue
            if not re.search(r"^\d+$", el):
                match = re.search(r"(\S+)\d+$", el)
                if match:
                    input_name = match.group(1)
            match = re.search(r"(\d+)$", el)
            if match:
                if count > total_count:
                    print 'elements in the range exceeded the allowed limit of %d' % total_count
                    return input_list
                else:
                    # 225.1.1.20,225.1.2.20
                    if not input_list.__contains__(str(match.group(1))):
                        if input_name:
                            new_value = input_name + str(match.group(1))
                        else:
                            new_value = str(match.group(1))
                        input_list.append(new_value)
                        count += 1
                    else:
                        print "error: overlapping range %s" % user_range_str
    return input_list


def check_commands_condition(condition, user_input_range_dict):
    # print user_input_range_dict
    # print user_input_range_dict
    import operator
    flag1 = False
    flag2 = False
    if "and" in condition:
        # print " In And Condition of square conditions "
        match_1 = re.search(r"<(\S+)>:(.+):(\S+)\s+and\s+<(\S+)>:(.+):(\S+)", condition)
        if match_1:
            variable_1 = match_1.group(1).replace('<', '').replace('>', '')
            oprator_1 = match_1.group(2)
            limit_1 = match_1.group(3).strip()
            variable_2 = match_1.group(4).replace('<', '').replace('>', '')
            oprator_2 = match_1.group(5)
            limit_2 = match_1.group(6).strip()
            # print ">>>>--", variable, ">>>>>>",limit
            # if variable==match.group(3):
            #     return False
            if re.search(r'\d+$', limit_1):
                limit_1 = int(limit_1)
            if re.search(r'\d+$', limit_2):
                limit_2 = int(limit_2)

            # First Condition  Check
            if oprator_1 == "len":
                var_1 = user_input_range_dict[variable_1]
            elif re.search(r'^\d+$', user_input_range_dict[variable_1][0]):
                var_1 = int(user_input_range_dict[variable_1][0])
            else:
                var_1 = user_input_range_dict[variable_1][0].replace('<', '').replace('>', '').strip()

            # Secound Condition  Check
            if oprator_2 == "len":
                var_2 = user_input_range_dict[variable_2]
            elif re.search(r'^\d+$', user_input_range_dict[variable_2][0]):
                var_2 = int(user_input_range_dict[variable][0])
            else:
                var_2 = user_input_range_dict[variable_2][0].replace('<', '').replace('>', '').strip()

            ops = {"+": operator.add, "-": operator.sub, "%": operator.mod, 'index': operator.indexOf,
                   "<": operator.lt, ">": operator.gt, "==": operator.eq, "!=": operator.ne}
            # print var, limit
            # print ops[oprator](var, limit)
            if var_1:
                if oprator_1 == "%":
                    if ops[oprator_1](var_1, limit_1) == 1:
                        flag1 = True
                    else:
                        flag1 = False
                elif oprator_1 == "index":
                    # print variable, type(var), user_input_range_dict[variable]
                    if ops[oprator_1](user_input_range_dict[variable_1], str(var_1)) == limit_1:
                        flag1 = True
                    else:
                        flag1 = False
                elif oprator_1 == "seo(2)":
                    if variable_1 == "hostname":
                        m = re.search(r'(\d\d)$', var_1)
                        if m:
                            if int(m.group(1)) % 2 == limit_1:
                                flag1 = True
                            else:
                                flag1 = False
                        else:
                            flag1 = False
                    else:
                        flag1 = False
                elif oprator_1 == "len":
                    # print " variable", var_1, limit_1
                    if len(var_1) == limit_1:
                        flag1 = True
                    else:
                        flag1 = False
                elif ops[oprator_1](var_1, limit_1):
                    flag1 = True
                else:
                    flag1 = False
            if var_2:
                if oprator_2 == "%":
                    if ops[oprator_2](var_2, limit_2) == 1:
                        flag2 = True
                    else:
                        flag2 = False
                elif oprator_2 == "index":
                    # print variable, type(var), user_input_range_dict[variable]
                    if ops[oprator_2](user_input_range_dict[variable_2], str(var_2)) == limit_2:
                        flag2 = True
                    else:
                        flag2 = False
                elif oprator_2 == "seo(2)":
                    if variable == "hostname":
                        m = re.search(r'(\d\d)$', var_2)
                        if m:
                            if int(m.group(1)) % 2 == limit_2:
                                flag2 = True
                            else:
                                flag2 = False
                        else:
                            flag2 = False
                    else:
                        flag2 = False
                elif oprator_2 == "len":
                    print " variable", var_2, limit_2
                    if len(var_2) == limit_2:
                        flag2 = True
                    else:
                        flag2 = False
                elif ops[oprator_2](var_2, limit_2):
                    flag2 = True
                else:
                    flag2 = False
        # print flag1, flag2, (flag1 and flag2)
        return (flag1 and flag2)
    match = re.search(r"<(\S+)>:(.+):(\S+)", condition)
    if match:
        # print ">><<--", match.group(1), match.group(2), match.group(3)

        variable = match.group(1).replace('<', '').replace('>', '')
        oprator = match.group(2)
        limit = match.group(3).strip()
        # print ">>>>--", variable, ">>>>>>",limit
        # if variable==match.group(3):
        #     return False
        if re.search(r'\d+$', limit):
            limit = int(limit)
        if oprator == "len":
            var = user_input_range_dict[variable]
        elif re.search(r'^\d+$', user_input_range_dict[variable][0]):
            var = int(user_input_range_dict[variable][0])
        else:
            var = user_input_range_dict[variable][0].replace('<', '').replace('>', '').strip()

        ops = {"+": operator.add, "-": operator.sub, "%": operator.mod, 'index': operator.indexOf,
               "<": operator.lt, ">": operator.gt, "==": operator.eq, "!=": operator.ne}
        # print var, limit
        # print ops[oprator](var, limit)
        if oprator == "%":
            if ops[oprator](var, limit) == 1:
                return True
            else:
                return False
        elif oprator == "index":
            # print variable, type(var), user_input_range_dict[variable]
            if ops[oprator](user_input_range_dict[variable], str(var)) == limit:
                return True
            else:
                return False
        elif oprator == "seo(2)":
            if variable == "hostname":
                m = re.search(r'(\d\d)$', var)
                if m:
                    if int(m.group(1)) % 2 == limit:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        elif oprator == "len":
            print " variable", var, limit
            if len(var) == limit:
                return True
            else:
                return False
        elif ops[oprator](var, limit):
            return True
        else:
            return False


# expand and add html tags for non-range commands
def commands_without_input_range(request, line, user_input_range_dict):
    m = re.search(r'<(\S+)>', line)
    m1 = re.search(r'<<(\S+)>>', line)
    if m1:
        if re.search(r'\d', m.group(1)):
            exp = "<\S+>"
        else:
            exp = "<\w+>"
        for match in re.finditer(exp, line):
            flag = False
            var = match.group().replace('<', '').replace('>', '')
            var = re.sub(' ', '', var)
            if "+" in var:
                var2 = var
            if user_input_range_dict.has_key(var):
                m = re.search(r'(\w+)\+(\d+)', var)
                if m:
                    value = user_input_range_dict.get(m.group(1))[0]
                    if re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', value):
                        incrmt = int(m.group(2))
                        if user_input_range_dict.get(m.group(1)):
                            variable_value = user_input_range_dict.get(m.group(1))[0]
                        elif SetupParameters.objects.filter(
                                Q(location=request.session["acilocation"]) | Q(location="all"),
                                variable=m.group(1), customer__contains=request.session['customer']):
                            query = SetupParameters.objects.filter(
                                Q(location=request.session["acilocation"]) | Q(location="all"), variable=m.group(1),
                                customer__contains=request.session['customer']).last()
                            if query:
                                if query.type == "3":
                                    variable_value = query.value
                        if "/" in variable_value:
                            mask = variable_value.split("/")[1]
                            variable_value = IPNetwork(variable_value)
                            variable_value = str(variable_value.ip + incrmt) + "/" + mask
                        else:
                            variable_value = str(IPAddress(variable_value) + incrmt)
                    elif re.match(r'\d+', value):
                        if user_input_range_dict.get(m.group(1)):
                            variable_value = user_input_range_dict.get(m.group(1))[0]
                        elif SetupParameters.objects.filter(
                                Q(location=request.session["acilocation"]) | Q(location="all"),
                                variable=m.group(1), customer__contains=request.session['customer']):
                            query = SetupParameters.objects.filter(
                                Q(location=request.session["acilocation"]) | Q(location="all"), variable=m.group(1),
                                customer__contains=request.session['customer']).last()
                            if query:
                                if query.type == "3":
                                    print variable_value, query.value
                                    variable_value = query.value
                        variable_value = int(variable_value) + int(m.group(2))
                        variable_value = str(variable_value)
                elif SetupParameters.objects.filter(Q(location=request.session["acilocation"]) | Q(location="all"),
                                                    variable=var, customer__contains=request.session['customer']):

                    query = SetupParameters.objects.filter(
                        Q(location=request.session["acilocation"]) | Q(location="all"),
                        variable=var, customer__contains=request.session['customer']).last()
                    if query:
                        if int(query.type) == 3:
                            variable_value = query.value

                elif len(user_input_range_dict.get(var)) > 1:
                    variable_value = user_input_range_dict.get(var)[0]
                else:
                    variable_value = "<" + var + ">"
                if re.search(r"<\S+>", variable_value):
                    variable_value = variable_value.replace('<', '&#60;').replace('>', '&#62;')
                # Change of tags for SDA output:  on 11-12-2019
                new_val = "555" + variable_value + "666"
                if "+" in var:
                    line = line.replace("<<" + var2 + ">>", new_val)
                    # line = re.sub(r'<%s>' % var2, new_val, line)
                else:
                    line = re.sub(r'<<%s>>' % var, new_val, line)
    elif m:

        if re.search(r'\d', m.group(1)):
            exp = "<\S+>"
        else:
            exp = "<\w+>"
        for match in re.finditer(exp, line):
            flag = False
            var = match.group().replace('<', '').replace('>', '')
            var = re.sub(' ', '', var)
            # print "&&&", var
            if "+" in var:
                var2 = var
                user_input_range_dict[var] = "1"
            elif "physical_port" in var and "ACI" in request.session["user_type"]:
                print "&&&", user_input_range_dict.get(var)[0]
                m_port = re.search(r'(\w+)\s?(\d/\d+)', user_input_range_dict.get(var)[0])
                if m_port:
                    print m_port.group()
                    if "," in user_input_range_dict[var][0]:
                        user_input_range_dict[var][0] = m_port.group(1) + "" + \
                                                        user_input_range_dict.get(var)[
                                                            0].replace(m_port.group(1), "")
                    else:
                        user_input_range_dict[var][0] = m_port.group(1) + " " + m_port.group(2)
            elif var == "task_id" or var == "taskid":
                user_input_range_dict[var] = [request.session["taskid"]]
            elif var == "aci_int_tag":
                if user_input_range_dict.has_key("physical_port"):
                    user_input_range_dict[var] = [
                        ("".join(user_input_range_dict.get("physical_port")[0].split())).replace("/", "_")]
                    if "," in user_input_range_dict[var][0]:
                        user_input_range_dict[var][0] = user_input_range_dict.get(var)[0].replace(",", "_")
            elif var == "vpc_peer_id":
                if user_input_range_dict.has_key("leaf_id") and re.search(r"\d+$",
                                                                          user_input_range_dict.get("leaf_id")[0]):
                    if (int(user_input_range_dict.get("leaf_id")[0]) % 2) == 1:
                        user_input_range_dict[var] = [str(int(user_input_range_dict.get("leaf_id")[0]) + 1)]
                    elif (int(user_input_range_dict.get("leaf_id")[0]) % 2) == 0:
                        user_input_range_dict[var] = [str(int(user_input_range_dict.get("leaf_id")[0]) - 1)]
            elif var == "vlan_id":
                from mysite.models import ACI_EPG_Mapping
                e1 = ACI_EPG_Mapping.objects.values_list('tenant_name', 'app_profile', 'epg_name').filter(
                    vlan=user_input_range_dict[var][0]).last()
                if e1:
                    user_input_range_dict["tenant_name"] = [e1[0]]
                    user_input_range_dict["application_name"] = [e1[1]]
                    user_input_range_dict["epg_name"] = [e1[2]]



            if user_input_range_dict.has_key(var):
                if user_input_range_dict.get(var):
                    # m = re.search(r'(\w+)\+(\d+)',var)
                    if re.search(r'\+', var):
                        var_list = var.split("+")
                        value = user_input_range_dict.get(var_list[0])[0]
                        if user_input_range_dict.has_key(var_list[0]) and user_input_range_dict.has_key(var_list[1]):
                            val1 = value
                            val2 = user_input_range_dict.get(var_list[1])[0]
                            variable_value = int(val1) + int(val2)
                            variable_value = str(variable_value)
                        elif re.match(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', value):
                            incrmt = int(var_list[1])
                            # EVEN ODD Logic For Accesss Switch 9300-9400 SHC
                            # if incrmt == 2:
                            #     if user_input_range_dict.has_key("hostname"):
                            #         sw_no = re.search(r'(\d+)$', user_input_range_dict.get("hostname")[0])
                            #         if sw_no:
                            #             #print "Switch name ............... and no ... ",sw_no.group(), sw_no.group(1)
                            #             if int(sw_no.group(1))%2 == 0:
                            #                 incrmt = 3
                            #             else:
                            #                 incrmt =incrmt
                            variable_value = user_input_range_dict.get(var_list[0])[0]
                            if "/" in variable_value:
                                mask = variable_value.split("/")[1]
                                variable_value = IPNetwork(variable_value)
                                variable_value = str(variable_value.ip + incrmt) + "/" + mask
                            else:
                                variable_value = str(IPAddress(variable_value) + incrmt)
                        elif re.match(r'\d+', value):
                            variable_value = int(user_input_range_dict.get(var_list[0])[0]) + int(var_list[1])
                            variable_value = str(variable_value)
                        else:
                            variable_value = "<" + var + ">"
                    else:
                        if len(user_input_range_dict.get(var)) > 1:
                            variable_value = ', '.join(user_input_range_dict.get(var))
                        else:
                            variable_value = user_input_range_dict.get(var)[0]
                else:
                    variable_value = "<" + var + ">"
                if re.search(r"<\S+>", variable_value):
                    variable_value = variable_value.replace('<', '&#60;').replace('>', '&#62;')

                    # added following if condition to not  remove space from eth for acess & truc ports 20-09-2017
                if var != "access_ports" and var != "trunk_ports" and var != "vpc_ports" and var != "fex_ports":
                    # variable_value = re.sub(' ', '', variable_value)
                    variable_value = variable_value.strip()
                # print "=========", variable_value,request.session["ext_dict"]["ext_name"]
                # if "Plan" in request.session["ext_dict"]["ext_name"]:
                if 'ext_name' in request.session["ext_dict"] and "Plan" in request.session["ext_dict"]['ext_name']:
                    new_val = "@@@@" + variable_value + "&&&&"
                else:
                    new_val = "555" + variable_value + "666"

                if "+" in var:
                    line = line.replace("<" + var2 + ">", new_val)
                    # line = re.sub(r'<%s>' % var2, new_val, line)
                else:
                    line = re.sub(r'<%s>' % var, new_val, line)
    return line


# expand and add html tags for non-range commands
def commands_with_input_range(group_commands_list, user_input_range_dict, user_data, range_variable_name=""):
    expanded_output_str = ''
    if user_input_range_dict.has_key(range_variable_name) and range_variable_name:
        range_list = user_input_range_dict.get(range_variable_name)
        # print range_variable_name, user_input_range_dict.get(range_variable_name)
        index_num = 0
        inc_counter = 0
        for element in range_list:
            # print  "In range function"
            # print element
            if range_variable_name == "vlan_id":
                from mysite.models import ACI_EPG_Mapping
                e1 = ACI_EPG_Mapping.objects.values_list('tenant_name', 'app_profile', 'epg_name').filter(
                    vlan=element).last()
                if e1:
                    user_input_range_dict["tenant_name"] = [e1[0]]
                    user_input_range_dict["application_name"] = [e1[1]]
                    user_input_range_dict["epg_name"] = [e1[2]]
            for line in group_commands_list:
                tag_user_range = False
                tag_user_inc_range = False
                match = re.search('!tag_user_range', line)
                if match:
                    line = line.split('!tag_user_range')[0]
                    tag_user_range = True
                match2 = re.search('!tag_user_inc_range', line)
                if match2:
                    line = line.split('!tag_user_inc_range')[0]
                    tag_user_inc_range = True
                # Need to put other loop for multiple variables
                for match in re.finditer(r"<\S+>", line):
                    var = match.group().replace('<', '').replace('>', '')
                    var = re.sub(' ', '', var)
                    # print "*****", var
                    if "physical_port" in var:
                        print " Im here"
                        m_port = re.search(r'(\w+)\s?(\d/\d+)', user_input_range_dict.get(var)[0])
                        if m_port:
                            print m_port.group()
                            if "," in user_input_range_dict[var][0]:
                                user_input_range_dict[var][0] = m_port.group(1) + "" + \
                                                                user_input_range_dict.get(var)[
                                                                    0].replace(m_port.group(1), "")
                            else:
                                user_input_range_dict[var][0] = m_port.group(1) + " " + m_port.group(2)
                    if user_input_range_dict.has_key(var):
                        variable_list = user_input_range_dict.get(var)
                        if tag_user_range:
                            print var
                            variable_value = user_data[var]
                        elif len(variable_list) > index_num:
                            variable_value = variable_list[index_num]

                        elif len(variable_list) < 1:
                            continue
                        else:
                            variable_value = variable_list[len(variable_list) - 1]
                        if re.search(r"<\S+>", variable_value):
                            variable_value = variable_value.replace('<', '&#60;').replace('>', '&#62;')
                        # variable_value = re.sub(' ', '', variable_value)
                        variable_value = variable_value.strip()
                        new_val = "555" + variable_value + "666"
                        line = re.sub(r'<%s>' % var, new_val, line)
                    elif tag_user_inc_range:
                        new_var = var.split("+")
                        inc = int(new_var[1])
                        if new_var[0] == range_variable_name and element:
                            print "here", element
                            variable_value = str(int(element) + inc)
                        elif user_input_range_dict.has_key(new_var[0]):
                            print "here", element
                            print "here", new_var[0], user_input_range_dict.get(new_var[0])[0]

                            if re.search(r'\d+.\d+.\d+.\d+', user_input_range_dict.get(new_var[0])[0]):
                                variable_value = str(IPAddress(user_input_range_dict.get(new_var[0])[0]) + inc_counter)
                            else:
                                variable_value = str(int(user_input_range_dict.get(new_var[0])[0]) + inc_counter)
                            inc_counter += inc
                        else:
                            variable_value = user_data[new_var[0]]
                        variable_value = variable_value.strip()
                        new_val = "555" + variable_value + "666"
                        line = line.replace("<" + var + ">", new_val)
                        # line = re.sub(r'<%s>' % var, new_val, line)
                        # line = re.sub('<\S+>', variable_value, line)
                expanded_output_str = expanded_output_str + '\n' + line
            index_num += 1
    else:
        for line in group_commands_list:
            line = commands_without_input_range(line, user_input_range_dict)
            expanded_output_str = expanded_output_str + '\n' + line
    return expanded_output_str


# need to modify for diffrent list, string and dic combinations
# my_dict = {'ce_link': {'options': [{'ospf': ['router_id', 'area_id']}, {'bgp': ['bgp_remote_as', 'neigh_ip']}]}, 'ce_link2': {'options': [{'isis': []}]}}
# print multi_level_check(my_dict, 'ce_link2', 'options', 'isis')
# print multi_level_value(my_dict, 'ce_link2', 'options', 'isis')
def multi_level_value(my_dict, item1, item2=False, item3=False):
    value = ""
    result = False
    try:
        if my_dict.get(item1):
            value = my_dict.get(item1)
            if item2:
                if type(value) is dict:
                    if value.get(item2):
                        value = value.get(item2)
                    else:
                        return result
                    if item3:
                        if type(value) is list:
                            for el in value:
                                if type(el) is dict:
                                    if el.has_key(item3):
                                        return el.get(item3)
                    else:
                        return value
            else:
                return value
    except Exception as err:
        raise err
    return False


def multi_level_check(my_dict, item1, item2=False, item3=False):
    result = False
    try:
        if my_dict.get(item1):
            if item2:
                value = my_dict.get(item1)
                if type(value) is dict:
                    if not value.get(item2):
                        return result
                    if item3:
                        value = value.get(item2)
                        if type(value) is list:
                            for el in value:
                                if type(el) is dict:
                                    if el.has_key(item3):
                                        return True
                    else:
                        return True
            else:
                return True
    except Exception as err:
        raise err
    return False


def multi_level_index(my_dict, item1, item2=False, item3=False):
    result = False
    try:
        if my_dict.get(item1):
            if item2:
                value = my_dict.get(item1)
                if type(value) is dict:
                    if not value.get(item2):
                        return result
                    if item3:
                        value = value.get(item2)
                        if type(value) is list:
                            index_count = 0
                            for el in value:
                                if type(el) is dict:
                                    if el.has_key(item3):
                                        return index_count
                                index_count += 1
    except Exception as err:
        raise err
    return False


# feature_data = {'multicast_mode': {'type': 'radio',
#                     'options': [{'Yes': ['mcast_control_group', 'data_group-mask_len', 'autorp_address']},
#                                 {'No': ['adjacency-server']}]}}

# template_inputs_variables = [u'otv_vdc_name', u'interface_range', u'ospf_process_id', u'site_vlan', u'vlan_num',
#                              u'site_vlan_int',
#                              u'internal_interface', u'join_interface', u'join_interface_ip', u'overlay_int_num',
#                              u'otv_int_description',
#                              u'site_identifier']


def get_feature_jason_data(feature_data, template_inputs_variables, field_desc_list={}):
    response_list = []
    # complete_variable_list = template_inputs_variables
    complete_variable_list = []
    response_data = {}
    for feature in feature_data:
        default1 = ''
        option_list = []
        hide_input_variable_flag = False
        hide_input_variable_list = []
        response_data['name'] = feature
        type = multi_level_value(feature_data, feature, 'type')
        # response_data['type'] = 'checkbox'
        response_data['type'] = type
        feature_desc = '%s' % feature
        for field_desc_dict in field_desc_list:
            if field_desc_dict.get('field') == feature:
                feature_desc = '%s' % field_desc_dict.get('desc')
                if field_desc_dict.has_key('default'):
                    default1 = field_desc_dict.get('default')
        if feature_desc == 'vpc':
            feature_desc = 'vPC Enabled'
        elif not feature_desc[0].isupper():
            feature_desc = feature_desc.upper()
        feature_desc = feature_desc.replace('_', ' ')
        response_data['desc'] = feature_desc
        response_data['default1'] = default1
        response_data['note'] = response_data['desc']
        for option in multi_level_value(feature_data, feature, 'options'):
            option_data = {}
            option_data['label'] = ' '.join(option.keys())
            option_data['value'] = ' '.join(option.keys())
            option_data['hide'] = "hide"
            hide_input_variable = []
            for feature_input in multi_level_value(feature_data, feature, 'options', option_data['value']):
                if not template_inputs_variables.__contains__(feature_input):
                    if not hide_input_variable.__contains__(feature_input):
                        hide_input_variable.append(feature_input)
            if hide_input_variable:
                hide_input_variable_flag = True
                option_data['trigger'] = hide_input_variable
                # option_data['trigger'] = multi_level_value(feature_data,feature, 'options', option_data['value'])
                option_list.append(option_data)
                for hidden_inputs in hide_input_variable:
                    if not complete_variable_list.__contains__(hidden_inputs):
                        complete_variable_list.append(hidden_inputs)
                        name = hidden_inputs
                        desc = 'Enter %s' % name
                        for field_desc_dict in field_desc_list:
                            if field_desc_dict.get('field') == name:
                                desc = field_desc_dict.get('desc')
                        hide_input_variable_list.append({'name': name, 'type': 'text', 'desc': desc, 'default1': '',
                                                         'format': '', 'output': ''})
            else:
                # hide input is empty
                option_list.append(option_data)
                # hide_input_variable_list.append()
        # if hide_input_variable_flag:
        response_data['options'] = option_list
        response_list.append(response_data.copy())
        response_list = response_list + hide_input_variable_list
    return response_list


# Used for Firewall for now to gnerate the jason for radio and check-box options
def get_feature_jason_data_v2(feature_data, template_inputs_variables, field_desc_list={}):
    response_list = []
    new_hide_variable = []
    complete_variable_list = []
    response_data = {}
    for feature in feature_data:
        default1 = ''
        option_list = []
        hide_input_variable_flag = False
        hide_input_variable_list = []
        response_data['name'] = feature
        type = multi_level_value(feature_data, feature, 'type')
        # response_data['type'] = 'checkbox'
        response_data['type'] = type
        feature_desc = '%s' % feature
        for field_desc_dict in field_desc_list:
            if field_desc_dict.get('field') == feature:
                feature_desc = '%s' % field_desc_dict.get('desc')
                if field_desc_dict.has_key('default'):
                    default1 = field_desc_dict.get('default')
        if feature_desc == 'vpc':
            feature_desc = 'vPC Enabled'
        elif not feature_desc[0].isupper():
            feature_desc = feature_desc.upper()
        feature_desc = feature_desc.replace('_', ' ')
        response_data['desc'] = feature_desc
        response_data['default1'] = default1
        response_data['note'] = response_data['desc']

        for option in multi_level_value(feature_data, feature, 'options'):
            option_data = {}
            option_data['label'] = ' '.join(option.keys()).replace('_', ' ').title()
            option_data['value'] = ' '.join(option.keys())
            option_data['hide'] = "hide"
            option_data['send'] = ""
            hide_input_variable = []
            for feature_input in multi_level_value(feature_data, feature, 'options', option_data['value']):
                if not template_inputs_variables.__contains__(feature_input):
                    if not hide_input_variable.__contains__(feature_input):
                        hide_input_variable.append(feature_input)
                else:
                    new_hide_variable.append(feature_input)
            if hide_input_variable:
                hide_input_variable_flag = True
                option_data['trigger'] = hide_input_variable
                # option_data['trigger'] = multi_level_value(feature_data,feature, 'options', option_data['value'])
                option_list.append(option_data)
                for hidden_inputs in hide_input_variable:
                    default1 = ''
                    if not complete_variable_list.__contains__(hidden_inputs):
                        complete_variable_list.append(hidden_inputs)
                        name = hidden_inputs
                        desc = 'Enter %s' % name
                        for field_desc_dict in field_desc_list:
                            if field_desc_dict.get('field') == name:
                                desc = field_desc_dict.get('desc')
                                if field_desc_dict.has_key('default'):
                                    default1 = field_desc_dict.get('default')
                        if hidden_inputs == 'action':
                            hide_input_variable_list.append(
                                {'name': name, 'type': 'radio', 'desc': 'Action', 'default1': default1, 'format': '',
                                 "options": [{"label": "Permit", "value": "permit"},
                                             {"label": "Deny", "value": "deny"}]})

                        else:
                            hide_input_variable_list.append({'name': name, 'type': 'text', 'desc': desc, 'default1': '',
                                                             'format': '', 'output': ''})
            else:
                # hide input is empty
                if new_hide_variable:
                    option_data['trigger'] = hide_input_variable + new_hide_variable
                option_list.append(option_data)
                # hide_input_variable_list.append()
        # if hide_input_variable_flag:
        response_data['options'] = option_list
        response_list.append(response_data.copy())
        response_list = response_list + hide_input_variable_list
    return response_list


class DrawTopology:
    '''
    Description:
        This class gets the all user inputs and saved to the topology dict.
	Inputs:
		input_para, request_get
	Output:
        Return topology_data.

    '''

    def __init__(self, input_para, request_get):
        feature_combination_list = []
        feature_combination_str = ""
        topology_data = {}
        for key, value in request_get.iteritems():
            if "features[" in key:
                if request_get.getlist(key):
                    #  if feature_combination_str:
                    #      feature_combination_str = feature_combination_str + ", " + request_get.getlist(key)[0]
                    # else:
                    #      feature_combination_str = request_get.getlist(key)[0]
                    feature_combination_list += request_get.getlist(key)
            elif "[" in key:
                parent_feature = key.split("[]")[0]
                if request_get.getlist(key):
                    for child_feature in request_get.getlist(key):
                        feature_combination = parent_feature + ":" + child_feature
                        # if feature_combination_str:
                        #     feature_combination_str = feature_combination_str + ", " + feature_combination
                        # else:
                        #     feature_combination_str = feature_combination
                        feature_combination_list.append(feature_combination)
            else:
                if value:
                    topology_data[key] = value
                else:
                    topology_data[key] = key
        # self.key = key
        # if feature_combination_str:
        #     topology_data['feature_combination_list'] = feature_combination_str

        if feature_combination_list:
            topology_data['feature_combination_list'] = feature_combination_list

        self.feature_combination_list = feature_combination_list
        self.topology_data = topology_data

    def get_topology_output(self):
        return self.topology_data

    def get_feature_combination_list(self):
        return self.feature_combination_list


import subprocess
import re

from django.conf import settings

if not settings.configured:
    settings.configure('mysite', DEBUG=True)


def get_space_count(input_para={}):
    total_first_line_len = int(0)
    first_line_para = {}
    field_count = 0
    for field in input_para.iterkeys():
        if field != 'type':
            if input_para[field]:
                value = input_para[field][0]
                total_first_line_len = total_first_line_len + len(value)
                first_line_para[field] = value
                field_count += 1
    if field_count > 5:
        total_spaces = 96 - total_first_line_len
    else:
        total_spaces = 76 - total_first_line_len
    spaces_count = total_spaces / field_count
    return spaces_count


def get_field_count(input_para={}):
    total_first_line_len = int(0)
    first_line_para = {}
    field_count = 0
    for field in input_para.iterkeys():
        if field != 'type':
            if input_para[field]:
                value = input_para[field][0]
                total_first_line_len = total_first_line_len + len(value)
                first_line_para[field] = value
                field_count += 1
    return field_count


def modify_str(inputs_str, insert_val, count, side):
    num = 0;
    temp_str = ''
    while num < count:
        temp_str = temp_str + insert_val
        num += 1
    if side == 'right':
        mod_str = inputs_str + temp_str
    else:
        mod_str = temp_str + inputs_str
    return mod_str


def first_line(input_para, field_count, space_count):
    # space_count = 8
    field = 1
    # field_count = 5
    first_line = ''
    while field <= field_count:
        field_name = str(field)
        if field_name != 'type':
            if input_para[field_name]:
                value = input_para[field_name][0]
                if field_name == '1':
                    first_line = first_line + modify_str(value, ' ', int(4), 'left')
                else:
                    first_line = first_line + modify_str(value, '-', int(space_count), 'left')
            field += 1
    return first_line


# return the list
# print new_value
def str_second_line(input_para, field_count, space_count, first_line):
    print input_para
    print field_count
    print space_count
    print first_line

    second_line = ""
    third_line = ""
    forth_line = ""
    field = 1
    output_list = []
    while field <= field_count:
        field_name = str(field)
        if len(input_para[field_name]) > 1:
            line_first_field_start = first_line.find(input_para[field_name][0])
            mid_point = line_first_field_start + (len(input_para[field_name][0]) / 2)
            new_line_start = mid_point - (len(input_para[field_name][1]) / 2) - len(second_line)
            second_line = second_line + modify_str(input_para[field_name][1], ' ', int(new_line_start), 'left')
        if len(input_para[field_name]) > 2:
            line_first_field_start = first_line.find(input_para[field_name][0])
            mid_point = line_first_field_start + (len(input_para[field_name][0]) / 2)
            new_line_start = mid_point - (len(input_para[field_name][2]) / 2) - len(third_line)
            third_line = third_line + modify_str(input_para[field_name][2], ' ', int(new_line_start), 'left')
        if len(input_para[field_name]) > 3:
            line_first_field_start = first_line.find(input_para[field_name][0])
            mid_point = line_first_field_start + (len(input_para[field_name][0]) / 2)
            new_line_start = mid_point - (len(input_para[field_name][3]) / 2) - len(forth_line)
            forth_line = forth_line + modify_str(input_para[field_name][3], ' ', int(new_line_start), 'left')
        field += 1

    # print "\nTopology:\n"
    # print forth_line
    # print third_line
    # print second_line
    # print first_line
    output_list.append(forth_line)
    third_line = third_line.replace(' ', '=')
    output_list.append(third_line)
    second_line = second_line.replace(' ', '=')
    output_list.append(second_line)
    # second_line_list = second_line.split()
    # space_count = len(second_line_list[0]) - 9
    # start_count = 0
    # while space_count > start_count:
    #     print 'adding space'
    #     first_line = '-' + first_line + '-'
    #     start_count += 1
    first_line = first_line.replace(' ', '=')
    output_list.append(first_line)
    # print 'output_list'
    # print output_list
    return output_list
    # print second_line_list[0]
    # print len(second_line_list[0])


class GetTopology:
    '''
    Description:
	    ----
	Inputs:
		sel_para, topology_data
	Output:
        Return topology_output.

    '''

    def __init__(self, sel_para, topology_data):
        self.topology_output = []
        self.input_para = {}
        input_para = {}
        str_line_2 = []
        for key, value in sel_para.iteritems():
            if key == 'ios':
                ios = value
            elif key == 'plat':
                plat = value
            elif key == 'tech':
                tech = value
            elif key == 'type':
                type = value
        feature_combination_str = ''

        # print 'GetTopology type'
        # print type
        vrf_name = ''

        if type == 'Provisioning CE':
            for key, value in topology_data.iteritems():
                if key == value:
                    value = "<" + value + ">"
                if key == 'feature_combination_list':
                    feature_combination_str = ' '.join(value)
                    feature_combination_str = feature_combination_str.replace(' ', ', ')
                elif key == 'bgp_remote_as':
                    bgp_remote_as = value
                elif key == 'bgp_as_num':
                    bgp_as_num = value
                elif key == 'vrf_name':
                    vrf_name = value
                elif key == 'ebgp_peer_ip':
                    ebgp_peer_ip = value
                elif key == 'interface_name':
                    interface_name = value
                if key == value:
                    value = "<" + value + ">"
            input_para = {'type': 'isp', 'features': feature_combination_str,
                          '1': ['egrp_peer', ebgp_peer_ip, bgp_remote_as],
                          '2': ['interface', interface_name, 'vrf_name', vrf_name],
                          '3': ['DUT', plat, ios], '4': ['bgp_as_num', bgp_as_num]}
        elif type.__contains__('Provisioning VXLAN Tenant'):
            anycast_gw = ''
            remote_vtp_ip = ''
            remote_host_ip = ''
            host_interface = '<host_interface>'
            port_mode = ''
            evpn_mode = ''
            feature_combination_str = tech + ' ' + ios + '/' + plat
            for key, value in topology_data.iteritems():
                if value.__contains__(', '):
                    value = value[:value.find(',')]
                if key == value:
                    value = "<" + value + ">"
                if key == 'feature_combination_list':
                    feature_combination_str = ' '.join(value)
                    feature_combination_str = feature_combination_str.replace(' ', ', ')
                elif key == 'multcast_mode':
                    evpn_mode = 'EVPN Mode:' + value
                elif key == 'port_mode':
                    port_mode = value
                elif key == 'server_interface':
                    host_interface = value
                elif key == 'l2_vlan_num':
                    l2_vlan_num = 'V' + value
                elif key == 'anycast_gw_virtual_ip-mask_len':
                    if value.__contains__('/'):
                        value = 'GW:' + value[:value.find('/')]
                    anycast_gw = value
                elif key == 'vrf_name':
                    vrf_name = 'Tenant:' + value
                elif key == 'bgp_as_num':
                    bgp_as_num = 'AS:' + value
                elif key == 'anycast_gw_virtual_ip/mask_len':
                    anycast_gw_virtual_ip = value
                elif key == 'mcast_group':
                    mcast_group = value
                elif key == 'remote_vtp_ip':
                    remote_vtp_ip = value
                if key == value:
                    value = "<" + value + ">"
            input_para = {'type': 'isp', 'features': feature_combination_str, '1': ['local_host'],
                          '2': [host_interface, port_mode, l2_vlan_num],
                          '3': ['DUT', plat, anycast_gw], '4': ['EVPN VXLAN Cloud', vrf_name, bgp_as_num],
                          '5': ['remote_peer', evpn_mode]}
            # input_para = {'type': 'isp', 'features': feature_combination_str, '1': ['server_interface', server_interface, vrf_name, l2_vlan_num],
            #           '2': ['DUT', plat, anycast_gw], '3': ['eEPN VXLAN Cloud', vrf_name, bgp_as_num], '4': ['remote_peer'], '5': ['remote_host']}
        elif type.__contains__('EVPN General Troubleshooting'):
            remote_vtp_ip = ''
            dst_ip = ''
            dst_mac = ''
            server_interface = '<host_interface>'
            mcast_group = ''
            feature_combination_str = tech + ' ' + ios + '/' + plat
            for key, value in topology_data.iteritems():
                if value.__contains__(', '):
                    value = value[:value.find(',')]
                if key == value:
                    value = "<" + value + ">"
                if key == 'feature_combination_list':
                    feature_combination_str = ' '.join(value)
                    feature_combination_str = feature_combination_str.replace(' ', ', ')
                elif key == 'server_interface':
                    host_interface = value
                elif key == 'l2_vlan_num':
                    l2_vlan_num = 'V' + value
                elif key == 'vrf_name':
                    vrf_name = 'Tenant:' + value
                elif key == 'mcast_group':
                    mcast_group = value
                elif key == 'remote_vtp_ip':
                    remote_vtp_ip = value
                elif key == 'host_ip':
                    dst_ip = value
                elif key == 'host_mac':
                    dst_mac = value
                if key == value:
                    value = "<" + value + ">"
            input_para = {'type': 'isp', 'features': feature_combination_str, '1': ['local_host'],
                          '2': [server_interface, l2_vlan_num],
                          '3': ['DUT', plat], '4': ['EVPN VXLAN Cloud', vrf_name],
                          '5': ['remote_peer', remote_vtp_ip, mcast_group],
                          '6': ['remote_host', dst_ip, dst_mac]}
        elif type.__contains__('Provisioning OTV Node') or type.__contains__('Provisioning Overlay Network'):
            remote_vtp_ip = ''
            site_vlan_int = internal_interface = overlay_int_num = join_interface = join_interface_ip = ''
            ospf_process_id = vlan_num = mcast_group = site_identifier = ''
            vlan_num = '<Vlan Num>'
            mcast_group = ''
            feature_combination_str = tech + ' ' + ios + '/' + plat
            for key, value in topology_data.iteritems():
                if value.__contains__(', '):
                    value = value[:value.find(',')]
                if key == value:
                    value = "<" + value + ">"
                if key == 'feature_combination_list':
                    feature_combination_str = ' '.join(value)
                    feature_combination_str = feature_combination_str.replace(' ', ', ')
                elif key == 'internal_interface':
                    internal_interface = value
                elif key == 'vlan_num':
                    vlan_num = 'V' + value
                elif key == 'site_vlan_int':
                    site_vlan_int = 'V' + value
                elif key == 'site_identifier':
                    site_identifier = value
                elif key == 'overlay_int_num':
                    overlay_int_num = 'Overlay ' + value
                elif key == 'mcast_group':
                    mcast_group = value
                elif key == 'join_interface':
                    join_interface = value
                elif key == 'join_interface_ip':
                    join_interface_ip = value
                elif key == 'ospf_process_id':
                    ospf_process_id = value
                if key == value:
                    value = "<" + value + ">"
            input_para = {'type': 'isp', 'features': feature_combination_str,
                          '1': ['internal_int', internal_interface, site_identifier],
                          '2': ['DUT', plat], '3': ['otv_join_int', join_interface, join_interface_ip],
                          '4': ['OTV Cloud', overlay_int_num, mcast_group]}
        elif type.__contains__('ASA Forwarding Troubleshooting'):
            port_num = ''
            src_ip = ''
            des_ip = ''
            protocol = ''
            acl_name = ''
            feature_combination_str = tech + ' ' + ios + '/' + plat
            for key, value in topology_data.iteritems():
                if value.__contains__(', '):
                    value = value[:value.find(',')]
                if key == value:
                    value = "<" + value + ">"
                if key == 'feature_combination_list':
                    feature_combination_str = ' '.join(value)
                    feature_combination_str = feature_combination_str.replace(' ', ', ')
                elif key == 'port_num':
                    port_num = value
                elif key == 'protocol':
                    protocol = value
                elif key == 'acl_name':
                    if value:
                        acl_name = 'ACL: ' + value
                elif key == 'in_int':
                    in_int = value
                elif key == 'out_int':
                    out_int = value
                elif key == 'src_ip':
                    src_ip = value
                elif key == 'des_ip':
                    des_ip = value
                if key == value:
                    value = "<" + value + ">"
                port_info = protocol + ':' + port_num
            input_para = {'type': 'isp', 'features': feature_combination_str, '1': ['SrcIp', src_ip, acl_name],
                          '2': ['DUT', plat],
                          '3': ['DstIP', des_ip, port_info]}
        if input_para:
            features = ''
            if input_para.has_key('features'):
                if input_para.get('features'):
                    features = "\nTopology: " + input_para.get('features')
                input_para.__delitem__('features')
            self.input_para = input_para
            self.space_count = get_space_count(self.input_para)
            self.field_count = get_field_count(self.input_para)
            line1 = first_line(self.input_para, int(self.field_count), int(self.space_count))
            str_line_2 = str_second_line(self.input_para, int(self.field_count), int(self.space_count), line1)
            if features:
                str_line_2.insert(0, features)
        if str_line_2:
            self.topology_output.append('-nlead_v1_start Topology')
            self.topology_output = self.topology_output + str_line_2
            self.topology_output.append('-nlead_v1_end Topology')

    def get_topology_output(self):
        return self.topology_output


def capitalize(line):
    # return ' '.join(s[0].upper() + s[1:] for s in line.split(' '))
    return ' '.join([s[0].upper() + s[1:] for s in line.split(' ') if len(s) > 0])


def convert_inputs_to_new_dict(user_para={}):
    new_user_para = {}
    for user_variable in user_para:
        user_range_str = user_para.get(user_variable)
        if user_range_str:
            new_list = get_list_from_range(user_range_str)
        else:
            new_list = []
        new_user_para[user_variable] = new_list
    return new_user_para


def convet_template_to_config(user_para, user_input_range_dict={}, user_feature_list=[], file_name=''):
    print "Entered Here --->"
    # user_input_range_dict = {"vlan_id": ['101','102','105','108'], "vxlan_id": ['9101','9102','9105'], 'name':['vxlan_vlan'],'bgp_as': ['<bgp_as>'], 'mcast_group': ['225.1.1.1', '225.1.1.2']}
    #
    # line_list = ['feature vxlan', '!', 'vlan <vlan_id>  !tag_start vlan_id', 'name <name>', 'vxlan <vxlan_id> !tag_end']
    # line_list.append('ip route <mcast_group> 1.1.1.2 !tag_start vlan_id !tag_end')
    # line_list.append('router bgp <bgp_as>')
    # line_list.append('neigh 1.1.1.1 remote_as')
    # line_list = line_list + ['interface vlan<vlan_id>  !tag_start mcast_group', 'ip address <mcast_group> remote <vlan_id>', 'no shut !tag_end']
    no_vrf_flag = False
    start_flag = False
    end_flag = False
    combine_commands = ''
    range_variable_name = ''
    group_commands_list = []

    if get_key_value(user_input_range_dict, 'vrf_option') == [u'No']:
        # user_input_range_dict.__delitem__('vrf_name')
        no_vrf_flag = True
    if not get_key_value(user_input_range_dict, 'vrf_name'):
        # user_input_range_dict.__delitem__('vrf_name')
        no_vrf_flag = True
    # need to add the code to combine the both files
    combine_file_line_list = []
    file_name = glb_template_dir + "/" + file_name
    with open(file_name, 'r') as the_file:
        feature_data = {}
        for line in the_file:
            group_commands = ''
            single_commands = ''
            line_skip_flag = False
            # new code to skip the expantion of commands by modifying the disc
            if no_vrf_flag:
                line = line.replace('vrf <vrf_name>', '')
                line = line.replace('vrf ', '')
            if re.search('!tag_skip', line):
                match = re.search('!tag_skip\s+(\S+)', line)
                if match:
                    skip_variable_name = match.group(1)
                    line = line.split('!tag_skip')[0]
                    if user_input_range_dict.has_key(skip_variable_name):
                        skip_variable_value = user_input_range_dict.get(skip_variable_name)
                        skip_variable_value = ','.join(skip_variable_value)
                        skip_variable_value = [skip_variable_value]
                        # set new value in the disct
                        user_input_range_dict[skip_variable_name] = skip_variable_value

            if re.search('!tag_start', line):
                match = re.search('!tag_start\s+(\S+)', line)
                if match:
                    range_variable_name = match.group(1)
                    temp_line = line
                    line = line.split('!tag_start')[0]
                    if user_input_range_dict.has_key(range_variable_name) and range_variable_name:
                        start_flag = True
                        if re.search('!tag_end', temp_line):
                            start_flag = False
                            line = re.sub('!tag_end', '', line)
                            # need to fix why is it not working for mvpn temaplate
                            range_commands = commands_with_input_range([line], user_input_range_dict, user_para,
                                                                       range_variable_name)
                            combine_commands = combine_commands + range_commands
                            range_variable_name = ''
                group_commands_list = []

            match = re.search(r"@for_feature_(\S+)", line)
            if match:
                feature_name = match.group(1)
                # user_feature_list = ['vpc']
                # Handling NOT feature
                if re.search(r"not_\S+", match.group(1)):
                    match = re.search(r"not_(\S+)", match.group(1))
                    if match:
                        feature_name = match.group(1)
                        if user_feature_list.__contains__(feature_name):
                            # line_skip_flag = True
                            continue
                        else:
                            line = re.sub('@for_feature_(\S+)', '', line)
                elif re.search(r"\w+_or_\w+", match.group(1)):
                    match = re.search(r"(\w+)_or_(\w+)", match.group(1))
                    if match:
                        if user_feature_list.__contains__(match.group(1)) or user_feature_list.__contains__(
                                match.group(2)):
                            line = re.sub('@for_feature_(\S+)', '', line)
                        else:
                            continue
                elif re.search(r"\w+_and_\w+", match.group(1)):
                    match = re.search(r"(\w+)_and_(\w+)", match.group(1))
                    if match:
                        if user_feature_list.__contains__(match.group(1)) and user_feature_list.__contains__(
                                match.group(2)):
                            line = re.sub('@for_feature_(\S+)', '', line)
                        else:
                            continue
                elif user_feature_list.__contains__(feature_name):
                    line = re.sub('@for_feature_(\S+)', '', line)
                else:
                    line_skip_flag = True
                    # continue
            if re.search('!tag_end', line) and start_flag:
                start_flag = False
                end_flag = True
                line = re.sub('!tag_end', '', line)
            if re.search('!tag_end', line) and start_flag:
                start_flag = False
                end_flag = True
                line = re.sub('!tag_end', '', line)
            if start_flag:
                if not line_skip_flag:
                    group_commands_list.append(line)
            elif end_flag:
                if not line_skip_flag:
                    group_commands_list.append(line)
                # Call the function to expand the commands for given range, pass the group_commands_list and list dict
                # reset the group_commands_list
                range_commands = commands_with_input_range(group_commands_list, user_input_range_dict, user_para,
                                                           range_variable_name)
                combine_commands = combine_commands + range_commands
                range_variable_name = ''
                group_commands_list = []
                end_flag = False
            elif re.search('<(\S+)>', line):
                # print line
                if not line_skip_flag:
                    line = commands_without_input_range(line, user_input_range_dict)
                    # print "command line "
                    # print line
                    if line:
                        combine_commands = combine_commands + '\n' + line
            else:

                if not line_skip_flag:
                    combine_commands = combine_commands + '\n' + line
    combine_command_list = combine_commands.split('\n')
    return combine_command_list


def get_lc_number(ios='', interface=''):
    # interface = eth1/1
    interface_list = []
    if ios == 'nx':
        interface_list = interface.split('/')
        if interface_list.__len__() == 2:
            match = re.search(r'\D+(\d+)', interface_list[0])
            if match:
                return match.group(1)


def get_interface_port_number(ios='', interface=''):
    # interface = eth1/1
    interface_list = []
    if ios == 'nx':
        interface_list = interface.split('/')
        return interface_list[interface_list.__len__() - 1]


def get_device_info_dict(para_list=[], user_sel_dict={}, user_dict={}):
    # user_dict = {u'des_ip': u'239.1.1.1', u'in_int': u'port-channel10', u'ou_l3': u'f324', u'src_ip': u'1.1.1.1',
    #              u'out_int': u'port-ch56', u'in_l3': u'f324', u'vlan_id': u'200', u'ou_phy_2': u'eth5/7',
    #              u'in_phy_2': u'eth3/2', u'user': u'esc'}
    result_dict = {}
    result_dict['in_lc_num'] = '<ingress_module>'
    result_dict['in_port_num'] = '<ingress_port_num>'
    result_dict['ou_lc_num'] = '<egress_module>'
    result_dict['ou_port_num'] = '<egress_port_num>'

    if user_sel_dict:
        ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
        plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))
        tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
        type = ConvertUeseInputs('type', user_sel_dict.get('type'))
    else:
        return result_dict
    if not ios == 'nx':
        return result_dict

    for key in user_dict:
        if key == 'in_phy_3':
            if re.search('\/\d+', user_dict.get('in_phy_3')):
                result_dict['in_lc_num'] = get_lc_number(ios, user_dict.get('in_phy_3'))
                result_dict['in_port_num'] = get_interface_port_number(ios, user_dict.get('in_phy_3'))
        elif key == 'in_phy_2':
            if re.search('\/\d+', user_dict.get('in_phy_2')):
                result_dict['in_lc_num'] = get_lc_number(ios, user_dict.get('in_phy_2'))
                result_dict['in_port_num'] = get_interface_port_number(ios, user_dict.get('in_phy_2'))
        elif key == 'in_int':
            if re.search('\/\d+', user_dict.get('in_int')):
                result_dict['in_lc_num'] = get_lc_number(ios, user_dict.get('in_int'))
                result_dict['in_port_num'] = get_interface_port_number(ios, user_dict.get('in_int'))

        if key == 'ou_phy_3':
            if re.search('\/\d+', user_dict.get('ou_phy_3')):
                result_dict['ou_lc_num'] = get_lc_number(ios, user_dict.get('ou_phy_3'))
                result_dict['ou_port_num'] = get_interface_port_number(ios, user_dict.get('ou_phy_3'))
        elif key == 'ou_phy_2':
            if re.search('\/\d+', user_dict.get('ou_phy_2')):
                result_dict['ou_lc_num'] = get_lc_number(ios, user_dict.get('ou_phy_2'))
                result_dict['ou_port_num'] = get_interface_port_number(ios, user_dict.get('ou_phy_2'))
        elif key == 'ou_int':
            if re.search('\/\d+', user_dict.get('ou_int')):
                result_dict['ou_lc_num'] = get_lc_number(ios, user_dict.get('ou_int'))
                result_dict['ou_port_num'] = get_interface_port_number(ios, user_dict.get('ou_int'))
        elif key == 'out_int':
            if re.search('\/\d+', user_dict.get('out_int')):
                result_dict['ou_lc_num'] = get_lc_number(ios, user_dict.get('out_int'))
                result_dict['ou_port_num'] = get_interface_port_number(ios, user_dict.get('out_int'))

    if get_key_value(user_dict, 'model'):
        if get_key_value(user_dict, 'model') == '9396PX' or get_key_value(user_dict, 'model') == '93128TX':
            if not result_dict.get('in_port_num') == '<ingress_port_num>':
                if int(result_dict.get('in_port_num')) > 48:
                    if get_key_value(result_dict, 'in_lc_num') == '3':
                        result_dict['in_lc_num'] = '2'
                    elif get_key_value(result_dict, 'in_lc_num') == '2':
                        result_dict['in_lc_num'] = '1'
            if not result_dict.get('ou_port_num') == '<egress_port_num>':
                if int(result_dict.get('ou_port_num')) > 48:
                    if get_key_value(result_dict, 'ou_lc_num') == '3':
                        result_dict['ou_lc_num'] = '2'
                    elif get_key_value(result_dict, 'ou_lc_num') == '2':
                        result_dict['ou_lc_num'] = '1'
    # print 'result_dict'
    # print result_dict
    return result_dict


class GetInputVariableDict:
    # global preso_variable_output
    global glb_tech_options

    def __init__(self, para_list=[], user_sel_dict={}, glb_non_common_que={}, user_dict={}):
        global customer_type
        global glb_tech_without_vrf
        # global preso_variable_output
        ''' Run TCL script to get the needed input parameters, filter platform specific, change the default values
        and description more user friendly and appropriate convert them into dict format
        Example:
        input: ['src_ip', 'in_int', 'out_int', 'des_ip', 'des_net', 'dst_ml', 'in_l3', 'ou_l3']
        output: [{'default1': '', 'format': 'ip', 'type': 'text', 'name': 'src_ip', 'desc': 'Enter <src_ip>'}, {
        '''
        # com_dict = {'ip': {'ios': 'nx', 'plat': '7000', 'type': 'forwarding'}}
        # para_list = ['in_int', 'in_phy', 'out_int', 'ou_phy', 'in_l3', 'ou_l3', 'vrf', 'src_ip', 'mdt_src', 'mdt_gr', 'des_ip', 'vrf_rp_add']
        vrf_type = ''
        vrf_unused_flag = True
        vrf_name = ''
        ios = ''
        plat = ''
        tech = ''
        type = ''

        para_dict_extra = {}
        if user_sel_dict:
            ios = ConvertUeseInputs('ios', user_sel_dict.get('ios'))
            plat = ConvertUeseInputs('plat', user_sel_dict.get('plat'))
            tech = ConvertUeseInputs('tech', user_sel_dict.get('tech'))
            type = ConvertUeseInputs('type', user_sel_dict.get('type'))

        print 'I am here ....'
        print type
        print plat
        print 'above is the plat'
        if ios == 'nx':
            layer_1_ex = 'Ex:eth1/5'
            layer_2_ex = 'Ex:eth1/5 or channel5'
            layer_3_ex = layer_2_ex + ' or ' + 'vlan5'
        elif ios == 'ios':
            layer_1_ex = 'Ex:ten1/5'
            layer_2_ex = 'Ex:ten1/5 or channel5'
            layer_3_ex = layer_2_ex + ' or ' + 'vlan5'
        elif ios == 'xr':
            layer_1_ex = 'Ex:ten1/0/1/5'
            layer_2_ex = 'Ex:ten1/0/1/5, bundle-eth5'
            layer_3_ex = layer_2_ex + ' or ' + 'bvi5'
        else:
            layer_1_ex = 'Ex:eth1/5'
            layer_2_ex = 'Ex:eth1/5 or channel5'
            layer_3_ex = layer_2_ex + ' or ' + 'vlan5'

        new_var_dict = {}
        input_para_dict = []
        para_dict = {}
        in_int_used_flag = False
        in_phy_unused_flag = True
        ou_int_used_flag = False
        ou_phy_unused_flag = True
        in_cha_unused_flag = True

        self.tech_with_vrf = ['mvpn', 'l3vpn']
        self.tech_with_optional_vrf = ['ip', 'con', 'mcast', 'ipv6', 'conv6', 'dhcp', 'bgp', 'ospf', 'isis', 'bfd']

        if tech:
            if self.tech_with_vrf.__contains__(tech):
                vrf_type = 'force'
            elif self.tech_with_optional_vrf.__contains__(tech):
                vrf_type = 'optional'
            else:
                vrf_type = 'no applicable'

        if vrf_type == 'optional':
            # name = 'vrf_option'
            # para_dict_extra = {'name': name, 'type': 'radio', 'desc': 'Is VRF Involved', 'default1': 'No', 'format': '',
            #              "options": [{"label": "Yes", "value": "Yes", "hide": "hide", "trigger": ["vrf"]}, {"label": "No", "value": "No", "hide": "hide"}]}
            # input_para_dict.append(para_dict_extra)
            # new_var_dict['vrf_option'] = para_dict_extra
            vrf_unused_flag = False
            name = 'vrf'
            if get_key_value(user_dict, name):
                default_value = get_key_value(user_dict, name)
                vrf_name = 'vrf ' + default_value
            else:
                default_value = ''
                vrf_name = ''
            para_dict_extra = {'name': name, 'type': 'text', 'desc': 'VRF Name', 'default1': default_value}
            input_para_dict.append(para_dict_extra)
            new_var_dict['vrf'] = para_dict_extra

        if vrf_type == 'force':
            vrf_unused_flag = False
            name = 'vrf'
            if get_key_value(user_dict, name):
                default_value = get_key_value(user_dict, name)
                vrf_name = 'vrf ' + default_value
            else:
                default_value = ''
                vrf_name = 'vrf ' + '<vrf_name>'
            para_dict = {'name': name, 'type': 'text', 'desc': 'VRF Name', 'default1': default_value}
            input_para_dict.append(para_dict)
            new_var_dict['vrf'] = para_dict

        device_info_dict = get_device_info_dict(para_list, user_sel_dict, user_dict)

        self.user_role = ''
        self.user_role = get_key_value(user_dict, 'user')

        source_ip = get_key_value(user_dict, 'src_ip')
        if get_key_value(user_dict, 'des_ip'):
            destination_ip = get_key_value(user_dict, 'des_ip')
        else:
            destination_ip = '<dst_ip>'.replace('<', '&#60;').replace('>', '&#62;')

        if get_key_value(user_dict, 'in_int'):
            ingress_interface = get_key_value(user_dict, 'in_int')
        else:
            ingress_interface = '<ingress_int>'.replace('<', '&#60;').replace('>', '&#62;')

        if get_key_value(user_dict, 'ou_int'):
            ingress_interface = get_key_value(user_dict, 'ou_int')
        else:
            ingress_interface = '<egress_int>'.replace('<', '&#60;').replace('>', '&#62;')

        if get_key_value(user_dict, 'out_int'):
            ingress_interface = get_key_value(user_dict, 'out_int')
        else:
            ingress_interface = '<egress_int>'.replace('<', '&#60;').replace('>', '&#62;')

        if vrf_name == 'vrf <vrf_name>':
            vrf_name = 'vrf <vrf_name>'.replace('<', '&#60;').replace('>', '&#62;')

        if get_key_value(user_dict, 'des_net'):
            des_net = get_key_value(user_dict, 'des_net')
        else:
            des_net = '<des_net>'.replace('<', '&#60;').replace('>', '&#62;')

        if get_key_value(user_dict, 'dst_ml'):
            mask_len = get_key_value(user_dict, 'dst_ml')
        else:
            mask_len = '<mask_len>'.replace('<', '&#60;').replace('>', '&#62;')

        if get_key_value(user_dict, 'nh_ip'):
            nh_ip = get_key_value(user_dict, 'nh_ip')
        else:
            nh_ip = '<nh_ip>'.replace('<', '&#60;').replace('>', '&#62;')

        if get_key_value(user_dict, 'vlan_id'):
            vlan_id = get_key_value(user_dict, 'vlan_id')
        else:
            vlan_id = '<vlan_id>'.replace('<', '&#60;').replace('>', '&#62;')

        if get_key_value(user_dict, 'src_mac'):
            src_mac = get_key_value(user_dict, 'src_mac')
        else:
            src_mac = '<src_mac>'.replace('<', '&#60;').replace('>', '&#62;')

        if get_key_value(user_dict, 'dst_mac'):
            dst_mac = get_key_value(user_dict, 'dst_mac')
        else:
            dst_mac = '<dst_mac>'.replace('<', '&#60;').replace('>', '&#62;')

        ingress_lc_num = device_info_dict.get('in_lc_num').replace('<', '&#60;').replace('>', '&#62;')
        egress_lc_num = device_info_dict.get('ou_lc_num').replace('<', '&#60;').replace('>', '&#62;')
        ingress_port_num = device_info_dict.get('in_port_num').replace('<', '&#60;').replace('>', '&#62;')
        egress_port_num = device_info_dict.get('ou_port_num').replace('<', '&#60;').replace('>', '&#62;')
        if customer_type == 'cisco':
            role_optons = [{'trigger': [''], 'hide': '', 'send': 'yes', 'value': 'pat', 'label': 'Quick'},
                           {'trigger': [''], 'hide': '', 'send': 'yes', 'value': 'cse', 'label': 'Normal'},
                           {'trigger': [''], 'hide': '', 'send': 'yes', 'value': 'esc', 'label': 'Advance'}]
        else:
            role_optons = [{'trigger': [''], 'hide': '', 'send': 'yes', 'value': 'esc', 'label': 'Advance'},
                           {'trigger': [''], 'hide': '', 'send': 'yes', 'value': 'cse', 'label': 'NOC'},
                           {'trigger': [''], 'hide': '', 'send': 'yes', 'value': 'pat', 'label': 'Partner'},
                           {'trigger': [''], 'hide': '', 'send': 'yes', 'value': 'customer', 'label': 'Customer'}]

        if 10 == 11:
            print 'error'
        else:

            self.tech_with_optional_vrf = ['ip', 'con', 'mcast', 'ipv6', 'conv6', 'dhcp', 'bgp', 'ospf', 'isis', 'bfd']
            # I should ask for the ipv4

            if type == 'loss':
                if not para_list.__contains__('src_ip'):
                    # para_list.append('src_ip')
                    para_list.insert(0, 'src_ip')
                if not para_list.__contains__('des_ip'):
                    # para_list.append('des_ip')
                    para_list.insert(1, 'des_ip')

            if tech == 'mpls':
                if not para_list.__contains__('bgp_nh'):
                    para_list.append('bgp_nh')

            # if tech == 'cpu':
            #     if not para_list.__contains__('pid'):
            #         para_list.append('pid')

            esc_variable = ['var_1', 'var_2', 'var_3', 'var_4', 'var_5', 'var_6', 'var_7', 'var_8', 'var_9', 'var_10',
                            'var_11', 'var_12', 'var_13', 'link1_1']
            if not plat == '7000':
                esc_variable = esc_variable + ['ou_l3', 'des_ind', 'des_ind', 'dis_adj_ind', 'in_vlan', 'ou_vlan']

            # example of adding variables from python directly
            model_info = {}
            if plat == 'nx9k':
                # ask the module type
                if get_key_value(user_dict, 'model'):
                    default_value = get_key_value(user_dict, 'model')
                else:
                    default_value = ''
                desc = 'Model Type'
                name = 'model'
                model_info = {'name': name, 'desc': desc, 'format': '', 'default1': default_value, 'type': 'radio',
                              'note': 'Check output of - show module',
                              'options': [{'value': '9396PX', 'label': '9396PX'},
                                          {'value': '93128TX', 'label': '93128TX'},
                                          {'value': 'Other', 'label': 'Other'}
                                          ]}

            if type == 'loss':
                if not para_list.__contains__('src_ip'):
                    # para_list.append('src_ip')
                    para_list.insert(0, 'src_ip')
                if not para_list.__contains__('des_ip'):
                    # para_list.append('des_ip')
                    para_list.insert(1, 'des_ip')
            for el in para_list:
                if user_dict.has_key(el):
                    default_value = user_dict.get(el).strip()
                else:
                    default_value = ''
                if el in esc_variable:
                    continue
                note = ''
                example = ''
                trigger = []
                name = el
                desc = '%s' % name
                desc = el
                desc = desc.replace('_', ' ')
                desc = capitalize(desc)
                if el == 'in_int':
                    if type == 'cpu':
                        desc = 'Suspected LC Interface'
                    elif tech == 'l2fwd' or tech == 'l2mcast':
                        desc = 'Ingress L2 Interface'
                        example = layer_2_ex
                    else:
                        desc = 'Ingress Interface'
                        example = layer_3_ex

                    in_int_used_flag = True
                    if in_phy_unused_flag:
                        para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                     'format': '', 'condition': '[Vv]|[Pp]|[Bb]',
                                     'trigger': ['in_phy_2'], 'hide': 'hide', 'example': example}
                elif el == 'ou_int':

                    if tech == 'l2fwd' or tech == 'l2mcast':
                        desc = 'Egress L2 Interface'
                        # example = layer_2_ex
                    else:
                        desc = 'Egress Interface'
                        # example = layer_3_ex

                    ou_int_used_flag = True
                    if ou_phy_unused_flag:
                        para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                     'format': '',
                                     'note': 'select egress interface', 'condition': '^[Vv]|^[Pp]|^[Bb]',
                                     'trigger': ['ou_phy_2'], 'hide': 'hide'}

                elif el == 'out_int':
                    if tech == 'l2fwd' or tech == 'l2mcast':
                        desc = 'Egress L2 Interface'
                    else:
                        desc = 'Egress Interface'
                    ou_int_used_flag = True
                    if ou_phy_unused_flag:
                        para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                     'format': '', 'condition': '^[Vv]|^[Pp]|^[Bb]',
                                     'trigger': ['ou_phy_2'], 'hide': 'hide'}
                elif el == 'ou_phy' and ou_phy_unused_flag:
                    desc = 'Egress Physical Interface'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_2_ex}
                elif el == 'ou_phy':
                    desc = 'Egress Physical Interface'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_2_ex}
                elif el == 'out_phy':
                    desc = 'Egress Physical Interface'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_2_ex}
                elif el == 'des_ip':
                    desc = 'Destination IP'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'format': 'ip'}
                elif el == 'src_ip':
                    desc = 'Source IP'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value, 'format': 'ip'}
                elif el == 'des_net':
                    desc = 'Destination Network'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value, 'format': 'ip'}
                elif el == 'des_ml' or el == 'dst_ml':
                    desc = 'Destination Mask'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value, 'maxlen': '2',
                                 'example': 'Ex:24'}
                elif el == 'src_mac' or el == 's_mac':
                    if type == 'eastwest':
                        desc = 'Router MAC'
                    else:
                        desc = 'Source MAC'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': 'Ex:28cf.da1d.1b05'}
                elif el == 'dst_mac' or el == 'd_mac':
                    desc = 'Destination MAC'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': 'Ex:0019.069c.80e0'}
                elif el == 'in_phy':
                    desc = 'Ingress Physical Interface'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_2_ex}
                elif el == 'ospf_pro':
                    desc = 'OSPF Process ID'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value}
                elif el == 'pro_src':
                    desc = 'Protocol Source IP'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value}
                # elif el == 'dst_ml':
                #     desc = 'Destination Mask'
                #     para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value, 'maxlen': '2'}
                elif el == 'con':
                    continue
                elif el == 'mdt_gr':
                    if tech == 'otv':
                        desc = 'OTV Group'
                    else:
                        desc = 'MDT Group'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value}
                elif el == 'mdt_src':
                    if tech == 'otv':
                        desc = 'OTV Source'
                    else:
                        desc = 'MDT Source'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value}
                elif el == 'mdt_src_rem':
                    if tech == 'otv':
                        desc = 'OTV Remote Source'
                    else:
                        desc = 'MDT Remote Source'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value}
                elif el == 'vlan_id':
                    desc = 'VLAN ID'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': '501'}
                elif el == 'in_phy_2' and in_phy_unused_flag:
                    desc = 'L2 ingress interface/portchannel of ingress vlan'
                    name = 'in_phy'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_2_ex}
                elif el == 'in_phy_3':
                    desc = 'member interface of ingress port-channel'
                    name = 'in_phy'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_1_ex}
                elif el == 'ou_phy_2' and ou_phy_unused_flag:
                    desc = 'L2 ingress interface/portchannel of ingress vlan'
                    name = 'ou_phy'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_2_ex}
                elif el == 'ou_phy_3':
                    desc = 'member interface of ingress port-channel'
                    name = 'ou_phy'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_1_ex}
                elif el == 'out_phy_2':
                    desc = 'L2 ingress interface/portchannel of egress vlan'
                    name = 'out_phy'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_2_ex}
                elif el == 'out_phy_3':
                    desc = 'member interface of egress port-channel'
                    name = 'out_phy'
                    para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                 'example': layer_1_ex}
                elif el == 'vrf' and vrf_unused_flag:
                    vrf_unused_flag = False
                    if glb_tech_without_vrf.__contains__(tech):
                        continue
                    else:
                        name = 'vrf'
                        desc = 'VRF Name'
                        para_dict = {'name': name, 'type': 'text', 'desc': '%s' % desc, 'default1': default_value}
                elif el == 'link1_1':
                    if not default_value:
                        default_value = str(100)
                    para_dict = {'name': name, 'type': 'dropdown', 'desc': 'Suspected Problem Area',
                                 'default1': default_value, 'format': '',
                                 "options": [{"label": "rsp-punt", "value": "1"}, {"label": "rsp-inject", "value": "2"},
                                             {"label": 'lc-punt', "value": "3"}, {"label": "lc-inject", "value": "4"},
                                             {"label": "Unknown", "value": "100"}]}
                elif el == 'in_l3' and (plat == '6500' or plat == 'C6800'):
                    name = 'in_l3'
                    desc = 'Ingress LC Type'
                    para_dict = {'name': name, 'desc': desc, 'format': '', 'default1': default_value, 'type': 'radio',
                                 'note': 'Check output of - show module output',
                                 'options': [{'value': 'dfc', 'label': 'Distributed Forwarding'},
                                             {'value': 'cfc', 'label': 'Centralized Forwarding'}]}
                elif el == 'ou_l3' and (plat == '6500' or plat == 'C6800'):
                    name = 'ou_l3'
                    desc = 'Egress Line Card Type'
                    para_dict = {'name': name, 'desc': desc, 'format': '', 'default1': default_value, 'type': 'radio',
                                 'note': 'Check output of - show module output',
                                 'options': [{'value': 'dfc', 'label': 'Distributed Forwarding'},
                                             {'value': 'cfc', 'label': 'Centralized Forwarding'}]}
                elif el == 'vrf':
                    continue
                elif el == 'tech_without_vrf':
                    continue
                else:
                    match_flag = False
                    match = None
                    if el == 'paragen':
                        continue
                    if glb_non_common_que.has_key(el):
                        match = re.search(r"\s\[(.+)\]", glb_non_common_que[el])
                        if match:
                            option_line = match.group(1)
                            match_flag = True
                        if not match_flag and re.search(r"\s(\S+/\S+)", glb_non_common_que[el]):
                            match = re.search(r"\s(\S+/\S+)", glb_non_common_que[el])
                            option_line = re.sub(r'\s+', '', match.group(1))
                            match_flag = True
                        if not match_flag and re.search(r"\s\(.+\)", glb_non_common_que[el]):
                            match = re.search(r"\s\((.+)\)", glb_non_common_que[el])
                            option_line = match.group(1)
                            match_flag = True
                    if match_flag:
                        option_dict = {}
                        para_dict = {}
                        para_dict['name'] = name
                        option_line = option_line.replace('?', '')
                        para_dict['type'] = 'radio'
                        para_dict['default1'] = default_value
                        para_dict['format'] = ''
                        if el == 'ck_7' and tech == 'bgp':
                            desc = 'BGP using BFD Protocol ?'
                        elif el == 'in_l3':
                            if not plat == '7000':
                                continue
                            if tech == 'cpu' or type == 'flap' or type == 'receive' or type == 'loss':
                                continue
                            if tech == 'bfd':
                                desc = 'Line Card Type'
                            elif type == 'down':
                                desc = 'Line Card Type'
                            else:
                                desc = 'Ingress Line Card Type'
                        elif el == 'ou_l3':
                            if not plat == '7000':
                                continue
                            if tech == 'ospf' or tech == 'bgp' or type == 'bfd' or tech == 'cpu':
                                continue
                            if type == 'flap' or type == 'receive' or type == 'loss':
                                continue
                            elif type == 'down' or type == 'flap' or type == 'receive':
                                desc = 'Line Card Type'
                            else:
                                desc = 'Egress Line Card Type'
                        elif el == 'mpbgp':
                            desc = 'MP-BGP Related ?'
                            trigger = ['des_rd']
                        else:
                            desc = glb_non_common_que[el].split("%s" % match.group(1))[0].replace('[', '').replace(']',
                                                                                                                   '')
                            if re.search(r"<in_lc>", desc):
                                desc = desc.replace('<in_lc> ', '')
                                desc = 'Ingress ' + desc
                            elif re.search(r"<out_lc>", desc):
                                desc = desc.replace('<out_lc> ', '')
                                desc = 'Egress ' + desc
                            desc = desc.replace('Select the ', '')
                            # desc = desc.replace('Enter ', '').replace('-', ' ').title()
                            desc = desc.replace('Enter ', '').replace('-', ' ')
                            desc = capitalize(desc)

                        para_dict['desc'] = desc

                        # para_dict['desc'] = glb_non_common_que[el].split("%s" %match.group(1))[0].replace('[', '').replace(']', '')
                        if re.search('\/', match.group(1)):
                            option_list = match.group(1).split('/')
                        elif re.search('\|', match.group(1)):
                            option_list = match.group(1).split('|')
                        elif re.search('\s', match.group(1)):
                            option_list = match.group(1).split(' ')
                        option_list_data = []
                        for option_info in option_list:
                            option_dict = {}
                            if option_info:
                                option_info = option_info.replace('(', '').replace('[', '').replace(']', '')
                                option_info = option_info.replace(')', '').replace('?', '')
                                if option_info == 'y':
                                    option_name = 'Yes'
                                elif option_info == 'n':
                                    option_name = 'No'
                                elif option_info == 'yes':
                                    option_name = 'Yes'
                                elif option_info == 'no':
                                    option_name = 'No'
                                elif option_info == 'ospf':
                                    option_name = 'OSPF'
                                elif option_info == 'bgp':
                                    option_name = 'BGP'
                                elif option_info == 'port-channel':
                                    option_name = 'Port-Channel'
                                else:
                                    option_name = option_info
                                option_dict['label'] = option_name
                                option_dict['value'] = option_info
                                if trigger:
                                    if option_name == 'Yes':
                                        option_dict['trigger'] = trigger
                                        option_dict['hide'] = 'hide'
                                    else:
                                        option_dict['hide'] = 'hide'

                                option_list_data.append(option_dict)
                        para_dict["options"] = option_list_data
                        if note:
                            para_dict['note'] = note
                    else:
                        glb_non_common_que[el] = el
                        if el == 'vrf':
                            desc = 'VRF Name'
                        elif el == 'peer' or el == 'peer2':
                            desc = 'Peer IP'
                        elif el == 'bridge_grp' or el == 'bg':
                            if tech == 'otv':
                                desc = 'Overlay Number'
                            else:
                                desc = 'Bridge Group'
                        elif el == 'local_label':
                            desc = 'Local Label'
                        elif el == 'vpn_lab_lo':
                            desc = 'VPN Local Label'
                        elif el == 'nh_ip':
                            desc = 'Next-Hop IP'
                        elif el == 'bgp_nh':
                            desc = 'BGP Next-Hop'
                        elif el == 'bridge_domain' or el == 'bd':
                            desc = 'Bridge Domain'
                        elif el == 'pro_srcip':
                            desc = 'Protocol Source IP'
                        elif el == 'bgp_grp':
                            desc = 'BGP Update Group Num'
                        elif el == 'dhcp':
                            continue
                        elif el == 'des_rd':
                            desc = 'Remote PE RD'
                        elif el == 'rsp_lo':
                            desc = 'Active RSP Slot'
                        elif el == 'tcp_pcb_value':
                            desc = 'TCP PCB Value'
                            note = 'show tcp brief | include <peer_ip>'
                        elif el == 'vrf_rp_add':
                            desc = 'Customer RP'
                            example = 'Ex:10.1.1.2'
                            # add example
                        elif el == 'des_ind':
                            desc = 'Destination Index'
                            # add example and need to put check for platform
                        # elif el == 'src_int':
                        #     desc = 'Source Interface'
                        #     # add example and need to put check for platform
                        elif el == 'dis_adj_ind':
                            desc = 'Disposition ADJ Index'
                            # add example and need to put check for platform
                        elif el == 'ck_15' and tech == 'bgp':
                            desc = 'PCB Value'

                            note = """get value from :'show tcp bri' cmd"""
                        elif el == 'ou_rpl':
                            if type == 'receive':
                                desc = 'Inbound Policy Name'
                            else:
                                desc = 'Outbound Policy Name'
                        elif el == 'in_vlan' and plat == '6500':
                            desc = 'Ingress Internal Vlan Id'
                            note = 'show l3-mgr interface <in_int> | in vlan'
                        elif el == 'ou_vlan' and plat == '6500':
                            desc = 'Egress Internal Vlan Id'
                            note = 'show l3-mgr interface <out_int> | in vlan'
                        else:
                            desc = glb_non_common_que[el]
                            desc = desc.replace('_', ' ')
                            # print 'desc-1'
                            # print desc
                            # desc = desc.replace('Enter ', '').replace('-', ' ').title()
                            desc = desc.replace('Enter ', '').replace('-', ' ')
                            desc = capitalize(desc)
                        para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                     'format': ''}
                        if note:
                            para_dict['note'] = note
                        if trigger:
                            para_dict['trigger'] = trigger
                            para_dict['hide'] = 'hide'
                        if example:
                            para_dict['example'] = example

                input_para_dict.append(para_dict)
                new_var_dict[el] = para_dict

                if in_int_used_flag and in_phy_unused_flag:
                    in_phy_unused_flag = False
                    if user_dict.has_key('in_phy_2'):
                        in_phy_2_value = user_dict.get('in_phy_2')
                    else:
                        in_phy_2_value = ''

                    para_dict_extra = {'name': 'in_phy_2', 'type': 'text', 'desc': 'Ingress L2 Interface',
                                       'note': 'select ingress interface', 'condition': '^[Pp]|^[Bb]',
                                       'default1': in_phy_2_value,
                                       'trigger': ['in_phy_3'], 'hide': 'hide', 'example': layer_2_ex}

                    input_para_dict.append(para_dict_extra)
                    new_var_dict['in_phy_2'] = para_dict_extra

                    if user_dict.has_key('in_phy_3'):
                        in_phy_3_value = user_dict.get('in_phy_3')
                    else:
                        in_phy_3_value = ''

                    para_dict_extra = {'name': 'in_phy_3', 'type': 'text',
                                       'desc': 'Ingress Port-channel member', 'default1': in_phy_3_value,
                                       'example': layer_1_ex
                                       }

                    input_para_dict.append(para_dict_extra)
                    new_var_dict['in_phy_3'] = para_dict_extra

                if ou_int_used_flag and ou_phy_unused_flag:
                    ou_phy_unused_flag = False
                    if user_dict.has_key('ou_phy_2'):
                        ou_phy_2_value = user_dict.get('ou_phy_2')
                    else:
                        ou_phy_2_value = ''

                    para_dict_extra = {'name': 'ou_phy_2', 'type': 'text', 'desc': 'Egress L2 Interface',
                                       'note': 'select egress interface', 'condition': '^[Pp]|^[Bb]',
                                       'default1': ou_phy_2_value,
                                       'trigger': ['ou_phy_3'], 'hide': 'hide'}

                    input_para_dict.append(para_dict_extra)
                    new_var_dict['ou_phy_2'] = para_dict_extra

                    # if ou_int_used_flag and ou_phy_unused_flag:
                    #     ou_phy_unused_flag = False
                    if user_dict.has_key('ou_phy_3'):
                        ou_phy_3_value = user_dict.get('ou_phy_3')
                    else:
                        ou_phy_3_value = ''

                    para_dict_extra = {'name': 'ou_phy_3', 'type': 'text',
                                       'desc': 'Egress Port-channel member', 'default1': ou_phy_3_value,
                                       }
                    input_para_dict.append(para_dict_extra)
                    new_var_dict['ou_phy_3'] = para_dict_extra
            if model_info:
                input_para_dict.append(model_info)
                new_var_dict['module'] = model_info

            if not user_dict:
                name = 'user'
                input_para_dict.append({'name': name, 'type': 'radio', 'desc': 'Troubleshooting',
                                        'default1': 'pat', "mandatory": "yes", 'vmessage': 'Please select the role',
                                        "options": role_optons})
                # input_para_dict.append({'name': 'sship', 'type': 'text', 'desc': 'Device IP','example':'(Optional)',
                # 'default1': '', "mandatory": "no",'example':'(Optional)' })
            else:
                name = 'user'
                input_para_dict.append({'name': name, 'type': 'radio', 'desc': 'Troubleshooting',
                                        'default1': self.user_role, "mandatory": "yes",
                                        'vmessage': 'Please select the role',
                                        "options": role_optons})
                # input_para_dict.append({'name': 'sship', 'type': 'text', 'desc': 'Device IP',
                # 'default1': '', "mandatory": "no",'example':'(Optional)'})
            if not customer_type == 'cisco':
                if glb_tech_options['ipversion'].__contains__(tech) and not para_dict.has_key('ip_ver'):
                    name = 'ip_ver'
                    para_dict = {'name': name, 'type': 'radio', 'desc': 'IP Version', 'default1': 'ipv4', 'format': '',
                                 "options": [{"label": "IPv4", "value": "ipv4"}, {"label": "IPv6", "value": "ipv6"}]}
                    input_para_dict.append(para_dict)
                    new_var_dict[name] = para_dict

            if self.user_role == 'esc':
                # add function to get ingress and egress module
                # add function to get the ingress and egress port
                for el in para_list:
                    if el in esc_variable:
                        if user_dict.has_key(el):
                            default_value = user_dict.get(el)
                        else:
                            default_value = ''
                        if not self.user_role == 'esc':
                            if el in esc_variable:
                                continue
                        note = ''
                        example = ''
                        trigger = []
                        name = el
                        desc = '%s' % name
                        desc = el
                        desc = desc.replace('_', ' ')
                        desc = capitalize(desc)
                        if el == 'var_1':
                            if plat == '7000':
                                if tech == 'mcast':
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding multicast '
                                                                     'route group %s source %s| in Index:'
                                                                     % (destination_ip, source_ip)})
                                    desc = 'OIF LIST Index'
                                    note = 'show system internal forwarding multicast route group <> source <> module <> detail'
                                elif tech == 'ip':
                                    desc = 'ML3 ADJ Index'
                                    note = ''

                                    if type == 'fwd':
                                        input_para_dict.append({'type': 'heading', 'note': '',
                                                                "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding %s ip '
                                                                         'route %s/%s detail module %s'
                                                                         % (
                                                                             vrf_name, des_net, mask_len,
                                                                             ingress_lc_num)})
                                    else:
                                        input_para_dict.append({'type': 'heading', 'note': '',
                                                                "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding %s ip '
                                                                         'route %s/32 detail module %s'
                                                                         % (vrf_name, destination_ip, ingress_lc_num)})

                                elif tech == 'l2fwd':
                                    desc = 'Source MAC Index'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show hardware mac address-table %s %s vlan %s'
                                                                     % (ingress_lc_num, src_mac, vlan_id)})
                                    note = ''
                                elif tech == 'l2mcast':
                                    desc = 'OIF LIST IDX'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show forwarding distribution ip igmp snooping vlan %s group %s | in Index:\r'
                                                                     % (vlan_id, destination_ip)})
                                    note = ''
                                elif tech == 'otv':
                                    desc = 'Destination Index'
                                    note = 'show system internal forwarding'
                            elif plat == 'nx9k':
                                if tech == 'mcast':
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding multicast '
                                                                     'route group %s source %s| in Index:'
                                                                     % (destination_ip, source_ip)})
                                    desc = 'OIF LIST Index'
                                    note = 'show system internal forwarding multicast route group <> source <> module <> detail'
                                elif tech == 'l2mcast':
                                    desc = 'OIF LIST IDX'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show forwarding distribution ip igmp snooping vlan %s group %s | in Index:\r'
                                                                     % (vlan_id, destination_ip)})
                                    note = ''
                                elif tech == 'ip':
                                    desc = 'Destination Index'
                                    note = ''
                                    if type == 'fwd':
                                        input_para_dict.append({'type': 'heading', 'note': '',
                                                                "label": '<span style="color:rgb(237, 125, 49);">From: bcm-shell mod %s "0:l3 l3table show" | egrep INTF|%s/%s'
                                                                         % (ingress_lc_num, des_net, mask_len)})
                                    else:
                                        input_para_dict.append({'type': 'heading', 'note': '',
                                                                "label": '<span style="color:rgb(237, 125, 49);">Get INTF value from: bcm-shell mod %s "0:l3 l3table show" | egrep INTF|%s'
                                                                         % (ingress_lc_num, destination_ip)})
                            elif plat == 'NX5000' or plat == 'NX6000':
                                if tech == 'mcast':
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding multicast '
                                                                     'route group %s source %s| in Index:'
                                                                     % (destination_ip, source_ip)})
                                    desc = 'OIF LIST Index'
                                    note = 'show system internal forwarding multicast route group <> source <> module <> detail'
                                elif tech == 'l2mcast':
                                    desc = 'OIF LIST IDX'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show forwarding distribution ip igmp snooping vlan %s group %s | in Index:\r'
                                                                     % (vlan_id, destination_ip)})
                                    note = ''
                                elif tech == 'ip':
                                    desc = 'L3 ADJ Index'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding ipv4 route'
                                                                     ' %s' % (destination_ip)})
                                    note = ''

                                elif tech == 'l2fwd':
                                    desc = 'Ingress Asic ID'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show hardware internal bigsur all-ports | egrep name|%s/%s' % (
                                                                ingress_lc_num, ingress_port_num)})
                                    note = ''
                                elif tech == 'l2mcast':
                                    desc = 'Multicast Tag'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding ipfib pd_tree ip-addr %s' % (
                                                                destination_ip)})
                                    note = ''

                            elif plat == 'nx9k':
                                if tech == 'ip':
                                    desc = 'L3 ADJ Index'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding ipv4 route'
                                                                     ' %s' % (destination_ip)})
                                    note = ''
                            elif plat == '6500':
                                if tech == 'mcast':
                                    desc = 'ICROIF Index'
                                    note = ''
                                elif tech == 'l3vpn':
                                    desc = 'ADJ Index'
                                    note = ''
                        elif el == 'var_2':
                            if plat == '7000':
                                if tech == 'mcast':
                                    desc = 'Platform Index'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show forwarding distribution multicast outgoing-interface-list l3 oif_list_idx'})
                                    note = 'show forwarding distribution multicast outgoing-interface-list <type> <oif_list_idx>'
                                elif tech == 'ip':
                                    if type == 'eastwest':
                                        input_para_dict.append({'type': 'heading', 'note': '',
                                                                "label": '<span style="color:rgb(237, 125, 49);">show hardware mac add %s address %s'
                                                                         % (ingress_lc_num, dst_mac)})
                                    else:
                                        input_para_dict.append({'type': 'heading', 'note': '',
                                                                "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding %s ip route %s/32 detail module %s'
                                                                         % (vrf_name, nh_ip, ingress_lc_num)})
                                    desc = 'Destination Index'
                                    note = ''

                                elif tech == 'l2fwd':
                                    desc = 'Destination MAC Index'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show hardware mac address-table %s %s vlan %s'
                                                                     % (egress_lc_num, dst_mac, vlan_id)})
                                    note = ''
                                elif tech == 'otv':
                                    desc = 'Destination Index'
                                    note = 'show system internal forwarding'
                            elif plat == 'nx9k':
                                if tech == 'ip' and not type == 'eastwest':
                                    desc = 'Next Hop Index'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">bcm-shell mod %s "0:l3 l3table show" | grep %s'
                                                                     % (ingress_lc_num, nh_ip)})
                                elif tech == 'mcast':
                                    desc = 'Mcast Group Index'
                                    note = ''
                                    if type == 'fwd':
                                        input_para_dict.append({'type': 'heading', 'note': '',
                                                                "label": '<span style="color:rgb(237, 125, 49);">From: bcm-shell mod %s "ipmc table show" | egrep GROUP|%s'
                                                                         % (ingress_lc_num, destination_ip)})
                            elif plat == 'NX5000' or plat == 'NX6000':
                                if tech == 'l2fwd':
                                    desc = 'Egress Asic ID'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show hardware internal bigsur all-ports | egrep name|%s/%s' % (
                                                                egress_lc_num, egress_port_num)})
                                    note = ''
                                elif tech == 'ip':
                                    desc = 'Ingress Asic ID'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show hardware internal bigsur all-ports | egrep name|%s/%s' % (
                                                                ingress_lc_num, ingress_port_num)})
                                    note = ''
                                elif tech == 'l2mcast':
                                    desc = 'Multicast Index'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding ipfib pd_tree ip-addr %s' % (
                                                                destination_ip)})
                                    note = ''
                                elif tech == 'mcast':
                                    desc = 'Multicast Index'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show system internal forwarding multicast metEntryptr %s' % (
                                                                    '&#60;' + 'met_index' + '&#62;')})
                                    note = ''
                            elif plat == '6500':
                                if tech == 'mcast':
                                    desc = 'ICROIF Index'
                                    note = ''
                                elif tech == 'l3vpn':
                                    desc = 'ADJ Index'
                                    note = ''
                            elif plat == 'asr':
                                desc = 'MFIB Obj Id'
                                note = 'show platform software ip f0 mfib vrf index 0 | in <des_ip>'
                        elif el == 'var_3':
                            if plat == 'NX5000' or plat == 'NX6000':
                                if tech == 'ip':
                                    desc = 'Egress Asic ID'
                                    input_para_dict.append({'type': 'heading', 'note': '',
                                                            "label": '<span style="color:rgb(237, 125, 49);">show hardware internal bigsur all-ports | egrep name|%s/%s' % (
                                                                egress_lc_num, egress_port_num)})
                                    note = ''
                        elif el == 'var_5':
                            if plat == '7000':
                                if tech == 'mcast':
                                    desc = 'ML3 ADJ Index'
                                    note = 'show forwarding distribution multicast outgoing-interface-list l3 oif_list_idx'
                            elif plat == '6500':
                                if tech == 'mcast':
                                    print 'need to add'
                                elif tech == 'l3vpn':
                                    print 'need to add'
                        elif el == 'var_8':
                            if tech == 'ospf':
                                desc = 'Route Type'
                        elif el == 'var_9':
                            if tech == 'ospf':
                                desc = 'Router-ID Of Originator'
                            elif plat == '7000':
                                if tech == 'mcast':
                                    desc = 'Egress LC MDT Index'
                                    note = 'show forwarding distribution multicast outgoing-interface-list l3 oif_list_idx'
                            elif plat == '6500':
                                if tech == 'mcast':
                                    print 'need to add'
                                elif tech == 'l3vpn':
                                    print 'need to add'
                        elif el == 'var_10':
                            if tech == 'ospf':
                                desc = 'Router-ID Of Suspected Device'
                            elif plat == '7000':
                                if tech == 'mcast':
                                    desc = 'Egress LC OIF Index'
                                    note = 'show forwarding distribution multicast outgoing-interface-list l3 oif_list_idx'
                            elif plat == '6500':
                                if tech == 'mcast':
                                    print 'need to add'
                                elif tech == 'l3vpn':
                                    print 'need to add'
                        elif el == 'var_12':
                            if plat == '7000':
                                if tech == 'mcast':
                                    desc = 'FPOE Index'
                                    note = 'sh hard int rewrite_engine ltl read instance_bitmap 0xf start_index <> end_index <> rbh 0xf'
                            elif plat == '6500':
                                if tech == 'mcast':
                                    print 'need to add'
                                elif tech == 'l3vpn':
                                    print 'need to add'
                        elif el == 'var_4' and plat == '6500' and tech == 'ip':
                            desc = 'MLS Adj Index'
                        elif el == 'var_3' and tech == 'mcast' and plat == 'asr':
                            desc = 'Ingress Int OCE Id'
                            note = 'show platform software mlist f0 index <obj-id>'
                        elif el == 'var_4' and tech == 'mcast' and plat == 'asr':
                            desc = 'Egress Int OCE Id'
                            note = 'show platform software mlist f0 index <obj-id>'
                        else:
                            desc = glb_non_common_que[el]
                            desc = desc.replace('_', ' ')
                            # print 'desc-1'
                            # print desc
                            # desc = desc.replace('Enter ', '').replace('-', ' ').title()
                            desc = desc.replace('Enter ', '').replace('-', ' ')
                            desc = capitalize(desc)
                        para_dict = {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value,
                                     'format': ''}
                        if note:
                            para_dict['note'] = note
                        if trigger:
                            para_dict['trigger'] = trigger
                            para_dict['hide'] = 'hide'
                        if example:
                            para_dict['example'] = example
                        input_para_dict.append(para_dict)
                        new_var_dict[el] = para_dict
            print 'input_para_dict'
            print input_para_dict
            input_para_dict = convert_input_para_dict(input_para_dict)
            self.input_para_dict = {"column": "12", "newline": "yes", "inputs": input_para_dict}
            self.new_var_dict = new_var_dict
            # print 'self.input_para_dict'
            # print self.input_para_dict
            preso_variable_output = new_var_dict

    def getInputDict(self):
        return self.input_para_dict
        # def format_variable_old_to_new(self):
        #     return self.new_var_dict


def convert_input_para_dict(old_para_dict):
    para_list = []
    for key in old_para_dict:
        para_list.append(key.get('name'))
    if para_list.__contains__('nh_ip') and para_list.__contains__('vrf'):
        src_dict = old_para_dict[para_list.index('nh_ip')]
        des_dict = old_para_dict[para_list.index('vrf')]
        old_para_dict.__delitem__(para_list.index('nh_ip'))
        para_list.remove('nh_ip')
        old_para_dict.__delitem__(para_list.index('vrf'))
        old_para_dict.insert(0, {"type": "oneline",
                                 "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

    para_list = []
    for key in old_para_dict:
        para_list.append(key.get('name'))

    if para_list.__contains__('des_net') and para_list.__contains__('dst_ml'):
        src_dict = old_para_dict[para_list.index('des_net')]
        des_dict = old_para_dict[para_list.index('dst_ml')]
        old_para_dict.__delitem__(para_list.index('des_net'))
        para_list.remove('des_net')
        old_para_dict.__delitem__(para_list.index('dst_ml'))
        old_para_dict.insert(0, {"type": "oneline",
                                 "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

    para_list = []
    for key in old_para_dict:
        para_list.append(key.get('name'))

    if para_list.__contains__('peer') and para_list.__contains__('pro_srcip'):
        src_dict = old_para_dict[para_list.index('peer')]
        des_dict = old_para_dict[para_list.index('pro_srcip')]
        old_para_dict.__delitem__(para_list.index('peer'))
        para_list.remove('peer')
        old_para_dict.__delitem__(para_list.index('pro_srcip'))
        old_para_dict.insert(0, {"type": "oneline",
                                 "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

    para_list = []
    for key in old_para_dict:
        para_list.append(key.get('name'))
    if para_list.__contains__('s_mac') and para_list.__contains__('d_mac'):
        src_dict = old_para_dict[para_list.index('s_mac')]
        des_dict = old_para_dict[para_list.index('d_mac')]
        old_para_dict.__delitem__(para_list.index('s_mac'))
        para_list.remove('s_mac')
        old_para_dict.__delitem__(para_list.index('d_mac'))
        old_para_dict.insert(0, {"type": "oneline",
                                 "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

    para_list = []
    for key in old_para_dict:
        para_list.append(key.get('name'))
    if para_list.__contains__('src_mac') and para_list.__contains__('dst_mac'):
        src_dict = old_para_dict[para_list.index('src_mac')]
        des_dict = old_para_dict[para_list.index('dst_mac')]
        old_para_dict.__delitem__(para_list.index('src_mac'))
        para_list.remove('src_mac')
        old_para_dict.__delitem__(para_list.index('dst_mac'))
        old_para_dict.insert(0, {"type": "oneline",
                                 "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

    para_list = []
    for key in old_para_dict:
        para_list.append(key.get('name'))
    if para_list.__contains__('in_int') and para_list.__contains__('out_int'):
        src_dict = old_para_dict[para_list.index('in_int')]
        des_dict = old_para_dict[para_list.index('out_int')]
        old_para_dict.__delitem__(para_list.index('in_int'))
        para_list.remove('in_int')
        old_para_dict.__delitem__(para_list.index('out_int'))
        old_para_dict.insert(0, {"type": "oneline",
                                 "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

    para_list = []
    for key in old_para_dict:
        para_list.append(key.get('name'))
    if para_list.__contains__('src_ip') and para_list.__contains__('des_ip'):
        src_dict = old_para_dict[para_list.index('src_ip')]
        des_dict = old_para_dict[para_list.index('des_ip')]
        old_para_dict.__delitem__(para_list.index('src_ip'))
        para_list.remove('src_ip')
        old_para_dict.__delitem__(para_list.index('des_ip'))
        old_para_dict.insert(0, {"type": "oneline",
                                 "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

    return old_para_dict
    #
    #
    # for key in old_para_dict:
    #     if key.get('name') == 'src_ip':
    #         if para_list.__contains__('des_ip'):
    #             skip_des_flag = True
    #             desc1 = 'Source IP'
    #             desc2 = 'Destination IP'
    #             para_dict = {"type": "oneline","data":{"column":"6","newline":"no","inputs":[
    #             {'name': name, 'type': 'text', 'desc': desc1, 'default1': default_value, 'format': 'ip'},
    #             {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value, 'format': 'ip'}]}}
    #         else:
    #


def checkifelexists(el, customer, location):
    entry = SetupParameters.objects.filter(variable=el, customer__contains=customer, location=location).last()
    if entry:
        return 1
    else:
        entry = SetupParameters.objects.filter(variable=el, customer__contains=customer, location="all").last()
        if entry:
            return 2
        else:
            return 0


def checkifelexistsc(el, location):
    from mysite.models import CommonSetupParameters
    entry = CommonSetupParameters.objects.filter(variable=el, location=location).last()
    if entry:
        return 1
    else:
        entry = CommonSetupParameters.objects.filter(variable=el, location="all").last()
        if entry:
            return 2
        else:
            return 0


def convert_input_para_dict_tp(old_para_dict, tech, template_name):
    if tech == 'vxlan' or tech == 'VXLAN':
        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))

        if para_list.__contains__('bgp_as_num') and para_list.__contains__('vrf_name'):
            src_dict = old_para_dict[para_list.index('bgp_as_num')]
            des_dict = old_para_dict[para_list.index('vrf_name')]
            new_index = para_list.index('bgp_as_num')
            old_para_dict.__delitem__(para_list.index('bgp_as_num'))
            para_list.remove('bgp_as_num')
            old_para_dict.__delitem__(para_list.index('vrf_name'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [des_dict, src_dict]}})

        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))

        if para_list.__contains__('l2_vni_num') and para_list.__contains__('l2_vlan_num'):
            src_dict = old_para_dict[para_list.index('l2_vni_num')]
            des_dict = old_para_dict[para_list.index('l2_vlan_num')]
            new_index = para_list.index('l2_vlan_num')
            old_para_dict.__delitem__(para_list.index('l2_vni_num'))
            para_list.remove('l2_vni_num')
            old_para_dict.__delitem__(para_list.index('l2_vlan_num'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [des_dict, src_dict]}})

        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('import_route_target') and para_list.__contains__('export_route_target'):
            src_dict = old_para_dict[para_list.index('import_route_target')]
            des_dict = old_para_dict[para_list.index('export_route_target')]
            new_index = para_list.index('import_route_target')
            old_para_dict.__delitem__(para_list.index('import_route_target'))
            para_list.remove('import_route_target')
            old_para_dict.__delitem__(para_list.index('export_route_target'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

    elif tech == 'otv' or tech == 'OTV':
        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('mcast_control_group') and para_list.__contains__('data_data_group'):
            src_dict = old_para_dict[para_list.index('mcast_control_group')]
            des_dict = old_para_dict[para_list.index('data_data_group')]
            new_index = para_list.index('mcast_control_group')
            old_para_dict.__delitem__(para_list.index('mcast_control_group'))
            para_list.remove('mcast_control_group')
            old_para_dict.__delitem__(para_list.index('data_data_group'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('site_vlan') and para_list.__contains__('site_identifier'):
            src_dict = old_para_dict[para_list.index('site_vlan')]
            des_dict = old_para_dict[para_list.index('site_identifier')]
            des_dict['example'] = 'Ex:0x2'
            new_index = para_list.index('site_vlan')
            old_para_dict.__delitem__(para_list.index('site_vlan'))
            para_list.remove('site_vlan')
            old_para_dict.__delitem__(para_list.index('site_identifier'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('join_interface') and para_list.__contains__('internal_interface'):
            src_dict = old_para_dict[para_list.index('join_interface')]
            des_dict = old_para_dict[para_list.index('internal_interface')]
            new_index = para_list.index('join_interface')
            old_para_dict.__delitem__(para_list.index('join_interface'))
            para_list.remove('join_interface')
            old_para_dict.__delitem__(para_list.index('internal_interface'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('overlay_int_num') and para_list.__contains__('site_vlan_int'):
            src_dict = old_para_dict[para_list.index('overlay_int_num')]
            src_dict['example'] = '1'
            des_dict = old_para_dict[para_list.index('site_vlan_int')]
            new_index = para_list.index('overlay_int_num')
            old_para_dict.__delitem__(para_list.index('overlay_int_num'))
            para_list.remove('overlay_int_num')
            old_para_dict.__delitem__(para_list.index('site_vlan_int'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})
    elif template_name == 'Provisioning Layer3 Link':
        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('ospf_process') and para_list.__contains__('area_id'):
            src_dict = old_para_dict[para_list.index('ospf_process')]
            des_dict = old_para_dict[para_list.index('area_id')]
            new_index = para_list.index('ospf_process')
            old_para_dict.__delitem__(para_list.index('ospf_process'))
            para_list.remove('ospf_process')
            old_para_dict.__delitem__(para_list.index('area_id'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})
        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('bgp_as_1') and para_list.__contains__('bgp_as_2'):
            src_dict = old_para_dict[para_list.index('bgp_as_1')]
            des_dict = old_para_dict[para_list.index('bgp_as_2')]
            new_index = para_list.index('bgp_as_1')
            old_para_dict.__delitem__(para_list.index('bgp_as_1'))
            para_list.remove('bgp_as_1')
            old_para_dict.__delitem__(para_list.index('bgp_as_2'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('interface_1') and para_list.__contains__('vrf_name_1'):
            src_dict = old_para_dict[para_list.index('interface_1')]
            des_dict = old_para_dict[para_list.index('vrf_name_1')]
            new_index = para_list.index('interface_1')
            old_para_dict.__delitem__(para_list.index('interface_1'))
            para_list.remove('interface_1')
            old_para_dict.__delitem__(para_list.index('vrf_name_1'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('interface_2') and para_list.__contains__('vrf_name_2'):
            src_dict = old_para_dict[para_list.index('interface_2')]
            des_dict = old_para_dict[para_list.index('vrf_name_2')]
            new_index = para_list.index('interface_2')
            old_para_dict.__delitem__(para_list.index('interface_2'))
            para_list.remove('interface_2')
            old_para_dict.__delitem__(para_list.index('vrf_name_2'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})
    elif template_name == 'New Object Groups':
        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('src_object') and para_list.__contains__('dst_object'):
            src_dict = old_para_dict[para_list.index('src_object')]
            des_dict = old_para_dict[para_list.index('dst_object')]
            new_index = para_list.index('src_object')
            old_para_dict.__delitem__(para_list.index('src_object'))
            para_list.remove('src_object')
            old_para_dict.__delitem__(para_list.index('dst_object'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})
        para_list = []
        for key in old_para_dict:
            para_list.append(key.get('name'))
        if para_list.__contains__('action') and para_list.__contains__('protocol'):
            src_dict = old_para_dict[para_list.index('action')]
            des_dict = old_para_dict[para_list.index('protocol')]
            new_index = para_list.index('action')
            old_para_dict.__delitem__(para_list.index('action'))
            para_list.remove('action')
            old_para_dict.__delitem__(para_list.index('protocol'))
            old_para_dict.insert(new_index, {"type": "oneline",
                                             "data": {"column": "6", "newline": "no", "inputs": [src_dict, des_dict]}})

            # para_list = []
            # for key in old_para_dict:
            #     para_list.append(key.get('name'))
            # if para_list.__contains__('in_int') and para_list.__contains__('out_int'):
            #     src_dict = old_para_dict[para_list.index('in_int')]
            #     des_dict = old_para_dict[para_list.index('out_int')]
            #     old_para_dict.__delitem__(para_list.index('in_int'))
            #     old_para_dict.insert(0,{"type": "oneline","data":{"column":"6","newline":"no","inputs":[src_dict, des_dict]}})
            #     old_para_dict.__delitem__(para_list.index('out_int'))
            #
            #
            # para_list = []
            # for key in old_para_dict:
            #     para_list.append(key.get('name'))
            # if para_list.__contains__('src_ip') and para_list.__contains__('des_ip'):
            #     src_dict = old_para_dict[para_list.index('src_ip')]
            #     des_dict = old_para_dict[para_list.index('des_ip')]
            #     old_para_dict.__delitem__(para_list.index('src_ip'))
            #     old_para_dict.insert(0,{"type": "oneline","data":{"column":"6","newline":"no","inputs":[src_dict, des_dict]}})
            #     old_para_dict.__delitem__(para_list.index('des_ip'))

    # print 'old_para_dict'
    # print old_para_dict
    return old_para_dict
    #
    #
    # for key in old_para_dict:
    #     if key.get('name') == 'src_ip':
    #         if para_list.__contains__('des_ip'):
    #             skip_des_flag = True
    #             desc1 = 'Source IP'
    #             desc2 = 'Destination IP'
    #             para_dict = {"type": "oneline","data":{"column":"6","newline":"no","inputs":[
    #             {'name': name, 'type': 'text', 'desc': desc1, 'default1': default_value, 'format': 'ip'},
    #             {'name': name, 'type': 'text', 'desc': desc, 'default1': default_value, 'format': 'ip'}]}}
    #         else:
    #


def parse_aci_output(cmd, filename):
    # Parsing Output of following command "cmd"
    output_lines = []
    cmd_match = False

    infile = open(filename, 'r+')
    cmd_line = [i for i in infile.readlines()]
    for line in cmd_line:
        if not cmd_match:
            match = re.search(r"\S+#\s?(.+)\s?", line)
            if match:
                if match.group(1).strip() == cmd.strip():
                    f_mtch = match.group(1).strip()
                    cmd_match = True
        else:
            match = re.search(r'\S+#\s?(.+)\s?', line)
            if match:
                if f_mtch == match.group(1).strip():
                    continue
                else:
                    break
            else:
                output_lines.append(line.rstrip())
    return output_lines


def get_tenant(op_lines):
    tenants_list = []
    for line in op_lines:
        match = re.search(r'^\s?(\S+)$', line)
        if match:
            tenants_list.append(match.group(1))
    return tenants_list


def get_app_lines(app, op_lines):
    app_flag = False
    app_lines = []
    for line in op_lines:
        if not app_flag:
            match = re.search(r"application\s+(\S+)", line)
            if match:
                if match.group(1).strip() == app.strip():
                    app_mtch = match.group(1).strip()
                    app_flag = True
        else:
            match = re.search(r'application\s+(\S+)', line)
            if match:
                if app_mtch == match.group(1).strip():
                    continue
                else:
                    break
            else:
                app_lines.append(line)
    return app_lines


def get_epg_lines(epg, op_lines):
    epg_flag = False
    epg_lines = []
    for line in op_lines:
        if not epg_flag:
            match = re.search(r"epg\s+(\S+)", line)
            if match:
                if match.group(1).strip() == epg.strip():
                    epg_mtch = match.group(1).strip()
                    epg_flag = True
        else:
            match = re.search(r'epg\s+(\S+)', line)
            if match:
                if epg_mtch == match.group(1).strip():
                    continue
                else:
                    break
            else:
                epg_lines.append(line)
    return epg_lines


def get_leaf_list(filename):
    cmd = "show  switch"
    leaf_list = []
    op_lines = parse_aci_output(cmd, filename)
    for line in op_lines:
        m = re.search(r'\s(\d+)\s', line)
        if m:
            leaf_list.append(m.group(1))
    return leaf_list


def getjsonfromdata(ip, filename):
    main_dict = {}
    tenant_dict = {}
    leaf_list = get_leaf_list(filename)
    tenant_op = parse_aci_output("show tenant", filename)
    tenant_lst = get_tenant(tenant_op)
    for tnt in tenant_lst:
        # tenant_dict[tnt] = {}
        cmd = "show running-config tenant " + tnt
        op_lines = parse_aci_output(cmd, filename)
        app_list = []
        epg_list = []
        app_dict = {}
        for line in op_lines:
            match = re.search(r'application (\S+)', line)
            if match:
                app_list.append(match.group(1))

        for app in app_list:
            app_dict[app] = {}
            app_lines = get_app_lines(app, op_lines)
            for line in app_lines:
                m = re.search(r'epg\s+(\S+)', line)
                if m:
                    epg_list.append(m.group(1))
                    app_dict[app][m.group(1)] = []
            for epg in epg_list:
                for e_line in get_epg_lines(epg, app_lines):
                    # print e_line
                    m1 = re.search(r'bridge-domain member\s+(\S+)', e_line)
                    if m1:
                        app_dict[app][epg].append(m1.group(1))

        if bool(app_dict):
            tenant_dict[tnt] = app_dict
    main_dict["leaf"] = leaf_list
    main_dict["tenant"] = tenant_dict

    return {ip: main_dict}


def get_apic_data(tnt="", aplication="", epg=""):

    '''
    Description:
        Function help read json data and select apic data.
    Inputs:
        tnt, aplication, epg
    Output:
    Return apic_data

    :param tnt:
    :param aplication:
    :param epg:
    :return:
    '''
    file_name = '/home/ubuntu/prepro/mysite/mysite/data/kaiser_apic_data/apic_data.json'
    tenants = []
    apps = []
    epgs = []
    bds = []
    leaf = []

    with open(file_name, 'r') as f:
        tenant_data = json.load(f)

        apps.append("Select")
        for ip, data in tenant_data.iteritems():
            if ip == "10.233.29.21":
                for keys, values in data.iteritems():
                    if keys == "tenant":
                        for tenant, tnt_data in values.iteritems():
                            if tenant == tnt:
                                tenants.append(tenant)
                                for app, app_data in tnt_data.iteritems():
                                    if app == aplication:
                                        apps.append(app)
                                        for el, el_data in app_data.iteritems():
                                            if el == epg:
                                                epgs.append(el)
                                                for bd in el_data:
                                                    bds = bd
                                            else:
                                                epgs.append(el)
                                    else:
                                        apps.append(app)
                            else:
                                tenants.append(tenant)
                    elif keys == "leaf":
                        leaf = values
    data = {"tenant": tenants, "app": apps, "epg": epgs, "bd": bds, "leaf": leaf}
    return data


class Cisco_to_Juniper():
    def __init__(self, filename, skip_interface=[]):
        # filename = "cs006-1xx all - upload.txt"
        infile = open(filename, 'r+')
        cmd_line = [i for i in infile.readlines()]
        sw_list = []
        main_dict = {}
        input_int_to_skip = []
        new_list_to_skip = []
        for intf in skip_interface:
            if "Gi" in intf:
                intf = intf.replace("Gi", "GigabitEthernet")
                input_int_to_skip.append(intf)
            elif "Fa" in intf:
                intf = intf.replace("Fa", "FastEthernet")
                input_int_to_skip.append(intf)
        for line in cmd_line:
            match = re.search(r"ssh.+@(\w+)-(\S+)", line)
            if match:
                sw_list.append((match.group(1) + "-" + match.group(2)).lower())
        count = 0
        # print sw_list
        if len(sw_list) != 0:
            js_int_counter = 0
            blade_count = 0
            for sw in sw_list:
                # sw = "cs006-1a"
                main_dict[sw] = []
                sw_lines = get_switch_op_c2j(sw, cmd_line)
                sh_run_lines = parse_output_c2j(sw, "show running-config", sw_lines)
                # Below for getting list of interfaces disabled
                new_list_to_skip = get_skip_list(sw, "show running-config", sw_lines)
                # print new_list_to_skip
                for line in sh_run_lines:
                    int_dict = {"counter": count, "cs_hostname": sw, "cs_interface": "", "cs_speed": "", "des": "",
                                "js_hostname": "", "js_interface": "", "vlan": "", "mode": "", "duplex": "",
                                "state": ""}
                    match = re.search(r"interface\s+(\S+\d/\d+)|interface\s+(\S+\d/\d/\d+)", line)
                    if match:
                        interface = match.group(1)
                        if interface in new_list_to_skip or interface in input_int_to_skip:
                            continue
                        slash_count = len(match.group().split("/"))
                        count += 1
                        if slash_count == 2:
                            port = match.group().split("/")[1]
                        elif slash_count == 3:
                            port = match.group().split("/")[2]

                        if re.search(r'Fast', interface):
                            int_dict["cs_interface"] = interface  # "Fa0/" + port
                            if js_int_counter > 47:
                                blade_count += 1
                                js_int_counter = 0
                            int_dict["js_interface"] = "ge-" + str(blade_count) + "/0/" + str(js_int_counter)
                            js_int_counter += 1
                        elif re.search(r'Gigabit', interface) and slash_count == 3:
                            # Gi0/0/1
                            int_match = re.search(r'\S+(\d)/\d/(\d+)', interface)
                            if int_match:
                                # int_dict["cs_interface"] = "gi" + int_match.group(1) + "/0/" + int_match.group(2)
                                int_dict["cs_interface"] = interface
                                # if int(int_match.group(1)) >= 1:
                                #     int_dict["cs_hostname"] = sw + ":" + int_match.group(1)
                                int_dict["cs_hostname"] = sw
                            if js_int_counter > 47:
                                blade_count += 1
                                js_int_counter = 0
                            if int(port) <= 48:
                                int_dict["js_interface"] = "ge-" + str(blade_count) + "/0/" + str(js_int_counter)
                                js_int_counter += 1
                        elif re.search(r'Gigabit', interface):
                            # print "Slash === 2"
                            int_dict["cs_interface"] = interface  # "Gi0/" + port

                        int_lines = interface_output(interface, sh_run_lines)
                        for ln in int_lines:
                            m1 = re.search(r'description\s(.+)\s?', ln)
                            if m1:
                                int_dict["des"] = m1.group(1).strip("*").strip(" ")
                                int_dict["des"] = int_dict["des"].replace(" ", "_").upper()
                            if slash_count == 3:
                                # switchport trunk allowed vlan 12-14,18,201,300,303
                                m2 = re.search(r'vlan\s+(\d+)|vlan\s+(\d+,\S+)', ln)
                            else:
                                m2 = re.search(r'vlan\s+(\d+)', ln)
                            if m2:
                                # print sw, ">>>", ln
                                if int_dict["vlan"] == "":
                                    int_dict["vlan"] = m2.group(1)
                                else:
                                    int_dict["vlan"] = int_dict["vlan"] + ", " + m2.group(1)
                            m3 = re.search(r'mode\s+(\w+)', ln)
                            if m3:
                                int_dict["mode"] = m3.group(1)
                            # m3_1 = re.search(r'switchport\s+(\w+)\s+vlan\s+(\d+)', ln)
                            # if m3_1:
                            #     if int_dict["mode"] =="" :
                            #         int_dict["mode"] = m3_1.group(1)
                            m4 = re.search(r'speed\s+(\d+)', ln)
                            if m4:
                                int_dict["cs_speed"] = m4.group(1)
                            m5 = re.search(r'duplex\s+(\S+)', ln)
                            if m5:
                                int_dict["duplex"] = m5.group(1)
                            m6 = re.search(r'shutdown', ln)
                            if m6:
                                int_dict["state"] = "shutdown"
                        # print int_dict

                        js_name = re.search(r'(\d{3})', sw)
                        if js_name and int_dict["js_interface"] != "":
                            int_dict["js_hostname"] = "js" + js_name.group(1) + "-1a"
                        main_dict[sw].append(int_dict)
        final_list = []
        for k, v in main_dict.iteritems():
            final_list = final_list + v

        self.finallist_sorted = sorted(final_list, key=lambda k: k['counter'])
        finallist = sorted(self.finallist_sorted, key=lambda k: k['vlan'])
        # print finallist
        self.finallist = finallist

    def create_output_file(self):
        print " Reaching here"
        # set interfaces interface-range NOW member ge-0/0/23
        # set interfaces interface-range NOW description NOW
        # set interfaces interface-range NOW unit 0 family ethernet-switching interface-mode access
        # set interfaces interface-range NOW unit 0 family ethernet-switching vlan members 100
        # set interfaces interface-range ARUBA_AP unit 0 family ethernet-switching storm-control default
        output_list = []
        pre_vlan = ""
        change_flag = False
        vlan_des = ""
        pre_dflt_int = ""
        # for each_dict in self.finallist:
        #     if each_dict["mode"] == "access":
        #         if pre_vlan == "":
        #             pre_vlan = each_dict["vlan"]
        #         if pre_vlan != each_dict["vlan"]:
        #             change_flag = True
        #         if each_dict["vlan"] != "" and each_dict["js_interface"] != "":
        #             if change_flag:
        #                 vlandata = get_json_data(pre_vlan)
        #                 # print each_dict["js_interface"], each_dict["cs_interface"]
        #                 print pre_vlan, vlandata
        #                 vlan_des = vlandata[0]
        #                 strom_control_flag = vlandata[1]
        #                 output_list.append(
        #                     "set interfaces interface-range " + vlan_des + " description " + vlan_des)
        #                 output_list.append(
        #                     "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching interface-mode " +
        #                     each_dict["mode"])
        #                 output_list.append(
        #                     "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching vlan members " + pre_vlan)
        #                 if strom_control_flag:
        #                     output_list.append(
        #                         "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching storm-control default")
        #                 output_list.append("\n")
        #                 change_flag = False
        #                 pre_vlan = each_dict["vlan"]
        #             else:
        #                 pre_vlan = each_dict["vlan"]
        #             vlandata = get_json_data(pre_vlan)
        #             # print pre_vlan
        #             if vlandata:
        #                 vlan_des = vlandata[0]
        #                 strom_control_flag = vlandata[1]
        #                 dflt_int = vlandata[2]
        #                 if dflt_int not in ["", pre_dflt_int]:
        #                     output_list.append(
        #                         "set interfaces interface-range " + vlan_des + " member " + dflt_int)
        #                     pre_dflt_int = dflt_int
        #                 output_list.append(
        #                     "set interfaces interface-range " + vlan_des + " member " + each_dict["js_interface"])
        # if vlan_des!="":
        #     output_list.append(
        #         "set interfaces interface-range " + vlan_des + " description " + vlan_des)
        #     output_list.append(
        #         "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching interface-mode access")
        #     output_list.append(
        #         "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching vlan members " + pre_vlan)
        #     output_list.append("\n")
        #     if strom_control_flag:
        #         output_list.append(
        #             "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching storm-control default")

        op_list = output_list
        # output_list.append("\n\n\n")
        output_list.append(
            "Sr.NO\tCisco Hostname\tCisco Interface\tDescription\tCisco Speed\tDuplex\tState\tJuniper Hostname\tJuniper interface\tVlan\tMode\n")

        for val in self.finallist_sorted:
            # print val
            output_list.append(
                '%(counter)s\t%(cs_hostname)s\t%(cs_interface)s\t%(des)s\t%(cs_speed)s\t%(duplex)s\t%(state)s\t%(js_hostname)s\t%(js_interface)s\t%(vlan)s\t%(mode)s' % val
            )
        # print self.finallist
        if self.finallist:
            sw_no = re.search(r'\d{3}', self.finallist[0]["cs_hostname"])
            if sw_no:
                self.sw_no = sw_no.group()
                FILE_DL_DIR = "/home/ubuntu/prepro/mysite/mysite/user_outputs/" + str("js" + self.sw_no)
                if not os.path.isdir(FILE_DL_DIR):
                    os.makedirs(FILE_DL_DIR)
                fname = "js" + sw_no.group() + ".txt"
                file = open(FILE_DL_DIR + '/' + fname, "w")
                for line in op_list:
                    file.write(line)
                    file.write("\n")
                file.close()
        # print output_list
        return output_list

    def create_csv(self):
        print " Csv file creating "
        FILE_DL_DIR = "/home/ubuntu/prepro/mysite/mysite/user_outputs/" + str("js" + self.sw_no)
        if not os.path.isdir(FILE_DL_DIR):
            os.makedirs(FILE_DL_DIR)
        fname = "js" + self.sw_no + ".csv"
        with open(FILE_DL_DIR + '/' + fname, 'w') as csvfile:
            fieldnames = ["counter", "cs_hostname", "cs_interface", "cs_speed", "js_hostname", "js_interface", "vlan",
                          "mode", "des", "duplex", "state"]
            writer = csv.writer(csvfile)
            writer.writerow(
                ["Sr.NO", "Cisco Hostname", "Cisco Interface", "Description", "Cisco Speed", "Duplex", "State",
                 "Juniper Hostname", "Juniper interface", "Vlan", "Mode"])
            for each_dict in self.finallist_sorted:
                writer.writerow([each_dict["counter"], each_dict["cs_hostname"], each_dict["cs_interface"],
                                 each_dict["des"].replace(" ", "_").upper(), each_dict["cs_speed"], each_dict["duplex"],
                                 each_dict["state"], each_dict["js_hostname"], each_dict["js_interface"],
                                 each_dict["vlan"], each_dict["mode"]])
        print "CSV File created"
        return "Successful"

    def get_switch_name(self):
        return "js" + self.sw_no


def interface_output(interface, cmd_lines):
    output_lines = []
    cmd_match = False
    cmd = "interface " + interface
    for line in cmd_lines:
        if not cmd_match:
            match = re.search("interface\s+(\S+)", line)
            if match and match.group(1) == interface:
                if match.group().strip() == cmd.strip():
                    f_mtch = match.group().strip()
                    cmd_match = True
        else:
            match = re.search('interface\s+(\S+)', line)
            if match and match.group(1) != interface:
                if f_mtch == match.group().strip():
                    continue
                else:
                    break
            else:
                output_lines.append(line.rstrip())
    return output_lines


def parse_output_c2j(sw, cmd, cmd_lines):
    output_lines = []
    cmd_match = False
    for line in cmd_lines:
        if not cmd_match:
            match = re.search("^(\S+)#\s?(.+)\s?", line)
            if match and (match.group(1)).lower() == sw:
                if match.group(2).strip() == cmd.strip():
                    f_mtch = match.group(2).strip()
                    cmd_match = True
        else:
            match = re.search('^(\S+)#\s?(.+)\s?', line)
            if match and ((match.group(1)).lower() != sw or (match.group(1)).lower() == sw):
                if f_mtch == match.group(2).strip():
                    continue
                else:
                    break
            else:
                output_lines.append(line.rstrip())
    return output_lines


def get_skip_list(sw, cmd, sw_lines):
    skiplist = []
    sh_run_lines_new = parse_output_c2j(sw, "show interface status", sw_lines)
    for line in sh_run_lines_new:
        if "disabled" in line or "notconnect" in line:
            splitlist = line.split(" ")
            int = splitlist[0]
            skiplist.append(int)
            if "Gi" in int:
                int = int.replace("Gi", "GigabitEthernet")
                skiplist.append(int)
            if "Fa" in int:
                int = int.replace("Fa", "FastEthernet")
                skiplist.append(int)
    return skiplist


def get_switch_op_c2j(sw, cmd_line):
    m_flag = False
    op_lines = []
    for line in cmd_line:
        if re.search("ssh.+@" + sw, line.lower()) or m_flag:
            # print line
            m_flag = True
            match = re.search("ssh.+@(\S+)", line)
            # if match:
            # print ">>>>>>>>>", match.group(1)
            if match and (match.group(1)).lower() != sw:

                m_flag = False
                break
            else:
                op_lines.append(line)
    return op_lines


def get_json_data(vlanid):
    with open("/home/ubuntu/prepro/mysite/mysite/patching data/vlan.json") as vlan_json_data:
        vlan_data = json.load(vlan_json_data)

        for key, value in vlan_data.iteritems():
            flag = False
            default_int = ""
            if key == vlanid:
                if value.has_key("storm_control") and value.get("storm_control") == "yes":
                    flag = True
                if value.has_key("default_interface"):
                    default_int = value.get("default_interface")
                return value["description"], flag, default_int


class YML_Parser():
    def __init__(self, filename):
        # filename = "cisco_switch_op.txt"
        infile = open(filename, 'r+')
        cmd_line = [i for i in infile.readlines()]
        self.cmd_lines = cmd_line

        info_dict = {}
        sw_list = []
        for line in cmd_line:
            match = re.search(r"->\s?ssh\s?(\w+)-(\S+)", line)
            if match:
                sw_list.append(match.group(1) + "-" + match.group(2))
        if len(sw_list) != 0:
            for sw in sw_list:
                # print sw
                store_lines = self.get_switch_op_c2j(sw, cmd_line)
                if len(store_lines) != 0:
                    for each in store_lines:
                        m = re.search(sw + '\s+([0-9]{3}\s.+)', each)
                        if m:
                            info_dict["store_name"] = m.group(1).replace(",", "").replace(" ", "_")
                # ----------- Router Type -----------
                rt_lines_1 = self.parse_output_c2j(sw, "show version | include 4300", cmd_line)
                rt_lines_2 = self.parse_output_c2j(sw, "show version | include 2900", cmd_line)
                print rt_lines_1, rt_lines_2
                if len(rt_lines_1) >= 1:
                    info_dict["router_type"] = "1"
                elif len(rt_lines_2) >= 1:
                    info_dict["router_type"] = "2"

                # ----------- Type, Circuit Size, Master Circuit ID, Backup Circuit ID -----------
                # op_lines = self.parse_output_c2j(sw, "show running-config interface gigabitethernet0/0/2", cmd_line)
                op_lines = self.parse_output_c2j(sw, "show interface description | include 0/2", cmd_line)
                # print op_lines
                for ln in op_lines:
                    if re.search(r'\w+\d+/\d/\d+', ln):
                        info_dict["iface_format"] = "2"
                    elif re.search(r'\w+\d/\d+', ln):
                        info_dict["iface_format"] = "1"
                    match = re.search(r"(\d+)M\s.+\sCKT\s?ID:\s?(\S+)", ln)
                    # Gi0/0/2                        up             up       Primary | Level3 | 10M | Ethernet-MPLS | CKT ID: FRO2006138521
                    if match:
                        # print match.group(1), ">>>>", match.group(2)
                        speed = float(match.group(1))
                        if re.search(r'1a', sw):
                            if int(speed) in [10, 20]:
                                info_dict["type"] = "fls"
                            elif int(speed) in [5]:
                                info_dict["type"] = "rack"
                            if info_dict["type"] == "fls" and int(speed) == 10:
                                info_dict["circuit_size"] = "1"
                            elif info_dict["type"] == "fls" and int(speed) == 20:
                                info_dict["circuit_size"] = "2"
                            elif info_dict["type"] == "rack" and int(speed) == 5:
                                info_dict["circuit_size"] = "3"
                        if re.search(r'1a', sw):
                            info_dict["master_circuit_id"] = match.group(2)
                        elif re.search(r'1b', sw):
                            info_dict["backup_circuit_id"] = match.group(2)

                # ----------- Serial Licence 1a & 1b -----------
                license_lines = self.parse_output_c2j(sw, "show running-config | include license", cmd_line)
                for ln in license_lines:
                    match_ser = re.search(r'license\s.+\s+sn\s+(\S+)', ln)
                    if match_ser and re.search(r'1a', sw):
                        info_dict["serialnum_cr_1a"] = match_ser.group(1)
                    elif match_ser and re.search(r'1b', sw):
                        info_dict["serialnum_cr_1b"] = match_ser.group(1)

                # ----------- Uplink 1a & 1b -----------
                uplink_lines = self.parse_output_c2j(sw, "show ip interface brief | include 0/2", cmd_line)
                for ln in uplink_lines:
                    up_ip = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ln)
                    if up_ip and re.search(r'1a', sw):
                        up_add = IPAddress(up_ip.group(1)) - 2
                        up_add = IPNetwork(str(up_add) + "/30")
                        info_dict["master_uplink"] = str(up_add)
                    elif up_ip and re.search(r'1b', sw):
                        up_add = IPAddress(up_ip.group(1)) - 2
                        up_add = IPNetwork(str(up_add) + "/30")
                        info_dict["backup_uplink"] = str(up_add)
                # ----------- Master Circuit IP address -----------
                ip_lines = self.parse_output_c2j(sw, "show ip interface brief | include oo", cmd_line)
                for ln in ip_lines:
                    ip = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", ln)
                    if ip and re.search(r'1a', sw):
                        ipadd = IPNetwork(ip.group(1) + "/19")
                        info_dict["ip_address"] = str(ipadd.network) + "/19"
                if re.search(r'1a', sw):
                    tun_lines = self.parse_output_c2j(sw, "show running-config interface tunnel900", cmd_line)
                    for ln in tun_lines:
                        ckt_ip = re.search(r'ip address\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ln)
                        if ckt_ip:
                            info_dict["master_circuit_ip"] = ckt_ip.group(1)
                elif re.search(r'1b', sw):
                    tun_lines = self.parse_output_c2j(sw, "show running-config interface tunnel901", cmd_line)
                    for ln in tun_lines:
                        ckt_ip = re.search(r'ip address\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', ln)
                        if ckt_ip:
                            info_dict["backup_circuit_ip"] = ckt_ip.group(1)
        self.info_dict = info_dict

    def get_info_data(self):
        return self.info_dict

    def parse_output_c2j(self, sw, cmd, cmd_lines):
        output_lines = []
        cmd_match = False
        for line in cmd_lines:
            if not cmd_match:
                match = re.search("(\S+)#\s?(.+)\s?", line)
                if match and match.group(1) == sw:

                    if match.group(2).strip() == cmd.strip():
                        f_mtch = match.group(2).strip()
                        cmd_match = True
            else:
                match = re.search('(\S+)#\s?(.+)\s?', line)
                if match and (match.group(1) != sw or match.group(1) == sw):
                    if f_mtch == match.group(2).strip():
                        continue
                    else:
                        break
                else:
                    # print line
                    output_lines.append(line.rstrip())
        return output_lines

    def get_switch_op_c2j(self, sw, cmd_line):
        m_flag = False
        op_lines = []
        for line in cmd_line:
            if re.search("->\s?ssh\s?" + sw, line) or m_flag:
                m_flag = True
                match = re.search("\S+#\s?", line)
                if match:
                    m_flag = False
                    break
                else:
                    op_lines.append(line)
        return op_lines


class Cisco_to_Juniper_by_VLAN_Assignment():
    def __init__(self, filename, skip_interface=[]):
        # filename = "cs006-1xx all - upload.txt"
        infile = open(filename, 'r+')
        cmd_line = [i for i in infile.readlines()]
        sw_list = []
        main_dict = {}
        input_int_to_skip = []
        new_list_to_skip = []
        for intf in skip_interface:
            if "Gi" in intf:
                intf = intf.replace("Gi", "GigabitEthernet")
                input_int_to_skip.append(intf)
            elif "Fa" in intf:
                intf = intf.replace("Fa", "FastEthernet")
                input_int_to_skip.append(intf)
        for line in cmd_line:
            match = re.search(r"ssh.+@(\w+)-(\S+)", line)
            if match:
                sw_list.append((match.group(1) + "-" + match.group(2)).lower())
        count = 0
        if len(sw_list) != 0:
            js_int_counter = 0
            blade_count = 0
            vlan_counter = {}
            for sw in sw_list:
                # sw = "cs006-1a"
                main_dict[sw] = []
                sw_lines = get_switch_op_c2j(sw, cmd_line)
                sh_run_lines = parse_output_c2j(sw, "show running-config", sw_lines)
                # Below for getting list of interfaces disabled
                new_list_to_skip = get_skip_list(sw, "show running-config", sw_lines)
                # print new_list_to_skip
                for line in sh_run_lines:
                    int_dict = {"counter": count, "cs_hostname": sw, "cs_interface": "", "cs_speed": "", "des": "",
                                "js_hostname": "", "js_interface": "", "vlan": "", "mode": "", "duplex": "",
                                "state": ""}
                    match = re.search(r"interface\s+(\S+\d/\d+)|interface\s+(\S+\d/\d/\d+)", line)
                    if match:
                        interface = match.group(1)
                        if interface in new_list_to_skip or interface in input_int_to_skip:
                            continue
                        slash_count = len(match.group().split("/"))
                        count += 1
                        if slash_count == 2:
                            port = match.group().split("/")[1]
                        elif slash_count == 3:
                            port = match.group().split("/")[2]

                        if re.search(r'Fast', interface):
                            int_dict["cs_interface"] = interface  # "Fa0/" + port
                            if js_int_counter > 47:
                                blade_count += 1
                                js_int_counter = 0
                            int_dict["js_interface"] = "ge-" + str(blade_count) + "/0/" + str(js_int_counter)
                            js_int_counter += 1
                        elif re.search(r'Gigabit', interface) and slash_count == 3:
                            # Gi0/0/1
                            int_match = re.search(r'\S+(\d)/\d/(\d+)', interface)
                            if int_match:
                                # int_dict["cs_interface"] = "gi" + int_match.group(1) + "/0/" + int_match.group(2)
                                int_dict["cs_interface"] = interface
                                # if int(int_match.group(1)) >= 1:
                                #     int_dict["cs_hostname"] = sw + ":" + int_match.group(1)
                                int_dict["cs_hostname"] = sw
                            if js_int_counter > 47:
                                blade_count += 1
                                js_int_counter = 0
                            if int(port) <= 48:
                                int_dict["js_interface"] = "ge-" + str(blade_count) + "/0/" + str(js_int_counter)
                                js_int_counter += 1
                        elif re.search(r'Gigabit', interface):
                            print "Slash === 2"
                            int_dict["cs_interface"] = interface  # "Gi0/" + port

                        int_lines = interface_output(interface, sh_run_lines)
                        for ln in int_lines:
                            m1 = re.search(r'description\s(.+)\s?', ln)
                            if m1:
                                int_dict["des"] = m1.group(1).strip("*").strip(" ")
                                int_dict["des"] = int_dict["des"].replace(" ", "_").upper()
                            if slash_count == 3:
                                # switchport trunk allowed vlan 12-14,18,201,300,303
                                m2 = re.search(r'vlan\s+(\S+)', ln)
                            else:

                                m2 = re.search(r'vlan\s+(\d+)', ln)
                            if m2:
                                # print sw, ">>>", ln
                                if int_dict["vlan"] == "":
                                    int_dict["vlan"] = m2.group(1)
                                elif m2.group(1) not in int_dict["vlan"]:
                                    int_dict["vlan"] = int_dict["vlan"] + ", " + m2.group(1)
                                if vlan_counter.has_key(int_dict["vlan"]):
                                    vlan_counter[int_dict["vlan"]]["counter"] += 1
                                else:
                                    vlan_counter[int_dict["vlan"]] = {}
                                    vlan_counter[int_dict["vlan"]]["counter"] = 1
                                    vlan_counter[int_dict["vlan"]]["inc"] = 0
                            m3 = re.search(r'mode\s+(\w+)', ln)
                            if m3:
                                int_dict["mode"] = m3.group(1)
                            # m3_1 = re.search(r'switchport\s+(\w+)\s+vlan\s+(\d+)', ln)
                            # if m3_1:
                            #     if int_dict["mode"] =="" :
                            #         int_dict["mode"] = m3_1.group(1)
                            m4 = re.search(r'speed\s+(\d+)', ln)
                            if m4:
                                int_dict["cs_speed"] = m4.group(1)
                            m5 = re.search(r'duplex\s+(\S+)', ln)
                            if m5:
                                int_dict["duplex"] = m5.group(1)
                            m6 = re.search(r'shutdown', ln)
                            if m6:
                                int_dict["state"] = "shutdown"
                        # print int_dict

                        js_name = re.search(r'(\d{3})', sw)
                        if js_name and int_dict["js_interface"] != "":
                            int_dict["js_hostname"] = "js" + js_name.group(1) + "-1a"
                        main_dict[sw].append(int_dict)
        final_list = []
        for k, v in main_dict.iteritems():
            final_list = final_list + v
        result_list = get_js_interface(vlan_counter, final_list)
        self.finallist_sorted = sorted(result_list, key=lambda k: k['counter'])
        finallist = sorted(self.finallist_sorted, key=lambda k: k['vlan'])
        # print finallist
        self.finallist = finallist

    def create_output_file(self):
        print " Reaching here"
        # set interfaces interface-range NOW member ge-0/0/23
        # set interfaces interface-range NOW description NOW
        # set interfaces interface-range NOW unit 0 family ethernet-switching interface-mode access
        # set interfaces interface-range NOW unit 0 family ethernet-switching vlan members 100
        # set interfaces interface-range ARUBA_AP unit 0 family ethernet-switching storm-control default
        output_list = []
        pre_vlan = ""
        change_flag = False
        vlan_des = ""
        pre_dflt_int = ""
        for each_dict in self.finallist:
            if each_dict["mode"] == "access":
                if pre_vlan == "":
                    pre_vlan = each_dict["vlan"]
                if pre_vlan != each_dict["vlan"]:
                    change_flag = True
                if each_dict["vlan"] != "" and each_dict["js_interface"] != "":
                    if change_flag:
                        vlandata = get_json_data(pre_vlan)
                        vlan_des = vlandata[0]
                        strom_control_flag = vlandata[1]
                        output_list.append(
                            "set interfaces interface-range " + vlan_des + " description " + vlan_des)
                        output_list.append(
                            "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching interface-mode " +
                            each_dict["mode"])
                        output_list.append(
                            "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching vlan members " + pre_vlan)
                        if strom_control_flag:
                            output_list.append(
                                "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching storm-control default")
                        output_list.append("\n")
                        change_flag = False
                        pre_vlan = each_dict["vlan"]
                    else:
                        pre_vlan = each_dict["vlan"]
                    vlandata = get_json_data(pre_vlan)
                    print pre_vlan
                    if vlandata:
                        vlan_des = vlandata[0]
                        strom_control_flag = vlandata[1]
                        dflt_int = vlandata[2]
                        if dflt_int not in ["", pre_dflt_int]:
                            output_list.append(
                                "set interfaces interface-range " + vlan_des + " member " + dflt_int)
                            pre_dflt_int = dflt_int
                        output_list.append(
                            "set interfaces interface-range " + vlan_des + " member " + each_dict["js_interface"])
        if vlan_des != "":
            output_list.append(
                "set interfaces interface-range " + vlan_des + " description " + vlan_des)
            output_list.append(
                "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching interface-mode access")
            output_list.append(
                "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching vlan members " + pre_vlan)
            output_list.append("\n")
            if strom_control_flag:
                output_list.append(
                    "set interfaces interface-range " + vlan_des + " unit 0 family ethernet-switching storm-control default")
        op_list = output_list
        output_list.append("\n\n\n")
        output_list.append(
            "Sr.NO\tCisco Hostname\tCisco Interface\tDescription\tCisco Speed\tDuplex\tState\tJuniper Hostname\tJuniper interface\tVlan\tMode\n")

        for val in self.finallist_sorted:
            # print val
            output_list.append(
                '%(counter)s\t%(cs_hostname)s\t%(cs_interface)s\t%(des)s\t%(cs_speed)s\t%(duplex)s\t%(state)s\t%(js_hostname)s\t%(js_interface)s\t%(vlan)s\t%(mode)s' % val
            )
        print self.finallist
        if self.finallist:
            sw_no = re.search(r'\d{3}', self.finallist[0]["cs_hostname"])
            if sw_no:
                self.sw_no = sw_no.group()
                FILE_DL_DIR = "/home/ubuntu/prepro/mysite/mysite/user_outputs/" + str("js" + self.sw_no)
                if not os.path.isdir(FILE_DL_DIR):
                    os.makedirs(FILE_DL_DIR)
                fname = "js" + sw_no.group() + ".txt"
                file = open(FILE_DL_DIR + '/' + fname, "w")
                for line in op_list:
                    file.write(line)
                    file.write("\n")
                file.close()
        # print output_list
        return output_list

    def create_csv(self):
        print " Csv file creating "
        FILE_DL_DIR = "/home/ubuntu/prepro/mysite/mysite/user_outputs/" + str("js" + self.sw_no)
        if not os.path.isdir(FILE_DL_DIR):
            os.makedirs(FILE_DL_DIR)
        fname = "js" + self.sw_no + ".csv"
        with open(FILE_DL_DIR + '/' + fname, 'w') as csvfile:
            fieldnames = ["counter", "cs_hostname", "cs_interface", "cs_speed", "js_hostname", "js_interface", "vlan",
                          "mode", "des", "duplex", "state"]
            writer = csv.writer(csvfile)
            writer.writerow(
                ["Sr.NO", "Cisco Hostname", "Cisco Interface", "Description", "Cisco Speed", "Duplex", "State",
                 "Juniper Hostname", "Juniper interface", "Vlan", "Mode"])
            for each_dict in self.finallist_sorted:
                writer.writerow([each_dict["counter"], each_dict["cs_hostname"], each_dict["cs_interface"],
                                 each_dict["des"].replace(" ", "_").upper(), each_dict["cs_speed"], each_dict["duplex"],
                                 each_dict["state"], each_dict["js_hostname"], each_dict["js_interface"],
                                 each_dict["vlan"], each_dict["mode"]])
        print "CSV File created"
        return "Successful"

    def get_switch_name(self):
        return "js" + self.sw_no


def get_js_interface(vlan_counter, result_list):
    new_resutl_list = []
    max_v100_port = ""
    for info_dict in result_list:
        if vlan_counter.has_key(info_dict["vlan"]) and info_dict["vlan"] == "100":
            count = vlan_counter[info_dict["vlan"]]["counter"]
            inc = vlan_counter[info_dict["vlan"]]["inc"]
            if count > 50:
                halfcount = int(ceil(count / 3))
                if inc in range(0, halfcount + 1):
                    blade = "0"
                    newinc = inc
                    vlan_counter[info_dict["vlan"]]["inc"] += 1
                elif inc in range(halfcount + 1, (2 * halfcount) + 1):
                    blade = "1"
                    newinc = inc - (halfcount + 1)
                    vlan_counter[info_dict["vlan"]]["inc"] += 1
                elif inc in range((2 * halfcount) + 1, count + 1):
                    blade = "2"
                    newinc = inc - ((2 * halfcount) + 1)
                    vlan_counter[info_dict["vlan"]]["inc"] += 1
            elif count < 50:
                halfcount = ceil(count / 2)
                if inc in range(0, int(halfcount)):
                    blade = "0"
                    newinc = inc
                    vlan_counter[info_dict["vlan"]]["inc"] += 1
                elif inc in range(int(halfcount), count):
                    blade = "1"
                    newinc = inc - int(halfcount)
                    vlan_counter[info_dict["vlan"]]["inc"] += 1
            info_dict["js_interface"] = "ge-" + blade + "/0/" + str(14 + newinc)
            max_v100_port = str(14 + newinc)
            new_resutl_list.append(info_dict)
        elif vlan_counter.has_key(info_dict["vlan"]) and info_dict["vlan"] == "300":
            count = vlan_counter[info_dict["vlan"]]["counter"]
            inc = vlan_counter[info_dict["vlan"]]["inc"]
            int_range = range(2, 12)
            halfcount = ceil(count / 2)
            if inc in range(2, int(halfcount)):
                blade = "0"
                newinc = inc
                vlan_counter[info_dict["vlan"]]["inc"] += 1
            elif inc in range(int(halfcount) + 1, count):
                blade = "1"
                newinc = inc - int(halfcount)
                vlan_counter[info_dict["vlan"]]["inc"] += 1
            if newinc in int_range:
                info_dict["js_interface"] = "ge-" + blade + "/0/" + int_range[newinc]
            new_resutl_list.append(info_dict)
        elif vlan_counter.has_key(info_dict["vlan"]) and info_dict["vlan"] == "202":
            count = vlan_counter[info_dict["vlan"]]["counter"]
            inc = vlan_counter[info_dict["vlan"]]["inc"]
            int_range = range(36, 44)
            halfcount = ceil(count / 2)
            if inc in range(0, int(halfcount)):
                blade = "0"
                newinc = inc
                vlan_counter[info_dict["vlan"]]["inc"] += 1
            elif inc in range(int(halfcount), count):
                blade = "1"
                newinc = inc - int(halfcount)
                vlan_counter[info_dict["vlan"]]["inc"] += 1
            if newinc < len(int_range):
                info_dict["js_interface"] = "ge-" + blade + "/0/" + str(int_range[newinc])
            new_resutl_list.append(info_dict)
        elif vlan_counter.has_key(info_dict["vlan"]) and info_dict["vlan"] == "303":
            count = vlan_counter[info_dict["vlan"]]["counter"]
            inc = vlan_counter[info_dict["vlan"]]["inc"]
            v100_port = int(max_v100_port)
            to_assign_int = ["ge-0/0/" + str(v100_port + 1), "ge-0/0/" + str(v100_port + 2),
                             "ge-1/0/" + str(v100_port + 1), "ge-1/0/" + str(v100_port + 2)]
            if inc in range(0, 5) and inc < len(to_assign_int):
                info_dict["js_interface"] = to_assign_int[inc]
                vlan_counter[info_dict["vlan"]]["inc"] += 1
            new_resutl_list.append(info_dict)
        elif vlan_counter.has_key(info_dict["vlan"]) and info_dict["vlan"] == "13":
            count = vlan_counter[info_dict["vlan"]]["counter"]
            inc = vlan_counter[info_dict["vlan"]]["inc"]
            to_assign_int = ["ge-0/0/7", "ge-0/0/8", "ge-1/0/7", "ge-1/0/8"]
            if inc in range(0, 5):
                info_dict["js_interface"] = to_assign_int[inc]
                vlan_counter[info_dict["vlan"]]["inc"] += 1
            new_resutl_list.append(info_dict)
        elif vlan_counter.has_key(info_dict["vlan"]) and info_dict["vlan"] == "201":
            count = vlan_counter[info_dict["vlan"]]["counter"]
            inc = vlan_counter[info_dict["vlan"]]["inc"]
            to_assign_int = ["ge-0/0/0", "ge-0/0/1", "ge-1/0/0", "ge-1/0/1"]
            if inc in range(0, 5):
                info_dict["js_interface"] = to_assign_int[inc]
                vlan_counter[info_dict["vlan"]]["inc"] += 1
            new_resutl_list.append(info_dict)
        elif vlan_counter.has_key(info_dict["vlan"]) and info_dict["vlan"] == "602":
            count = vlan_counter[info_dict["vlan"]]["counter"]
            inc = vlan_counter[info_dict["vlan"]]["inc"]
            to_assign_int = ["ge-0/0/44", "ge-0/0/45", "ge-1/0/44", "ge-1/0/45"]
            if inc in range(0, 5):
                info_dict["js_interface"] = to_assign_int[inc]
                vlan_counter[info_dict["vlan"]]["inc"] += 1
            new_resutl_list.append(info_dict)
        else:
            new_resutl_list.append(info_dict)
    return new_resutl_list


class Port_Mapping():
    def __init__(self, filename1):
        print "IN Port Mapping "
        infile1 = open(filename1, 'r+')
        cisco_line = [i for i in infile1.readlines()]

        # infile1 = open(filename2, 'r+')
        # juniper_line = [i for i in infile1.readlines()]

        self.parse_cisco_op(cisco_line)
        # self.parse_juniper_op(juniper_line)
        # self.parse_csvfile(filename3)

    # def parse_csvfile(self,filename):
    #     infile = open(filename, 'r+')
    #     line = [i for i in infile.readlines()]
    #     self.data_list = []
    #     colum = re.split(r',', line[0].replace(" ", "_").lower())
    #     if colum:
    #         for ele in line:
    #             data_dict = {}
    #             if ele == line[0]:
    #                 continue
    #             else:
    #                 match = re.split(r',', ele)
    #                 if match:
    #                     loop = len(colum)
    #                     for v in range(0, loop):
    #                         if colum[v].strip('') != "" and colum[v] in ["cisco_switch", "cisco_interface", "juniper_switch", "juniper_interface"]:
    #                             data_dict[colum[v].strip()] = match[v].strip()
    #                 else:
    #                     continue
    #             self.data_list.append(data_dict)

    def cisco_mac_output(self, cmd_lines):
        output_lines = []
        cmd_match = False
        cmd = "CISCO MACTABLE TOOL"
        for line in cmd_lines:
            if not cmd_match:
                match = re.search(cmd, line)
                if match:
                    cmd_match = True
            else:
                match = re.search(cmd, line)
                if match:
                    cmd_match = False
                else:
                    output_lines.append(line.rstrip())
        return output_lines

    def get_sw_list(self, op_lines):
        sw_list = []
        get_flag = False
        for lines in op_lines:
            # if re.search(r"STARTING DNS QUERY", lines):
            #     get_flag = True
            #     continue
            # elif re.search(r"DNS QUERY COMPLETE", lines):
            #     get_flag = False
            match = re.match(r"^(\w+-\d\w)$", lines)
            if match:
                sw_list.append(match.group(1))
        return sw_list

    def sw_mac_table(self, sw, op_lines):
        op = []
        get_flag = False
        for line in op_lines:
            dict = {"switch": sw}
            if re.search('^' + sw + '$', line):
                get_flag = True
                continue
            elif re.search("(\*)", line):
                get_flag = False

            if get_flag:
                match1 = re.search(r'v(\d+)\s+(\S+)\s.+\s(ge\S+).\d', line)
                if match1:
                    dict['vlan'] = match1.group(1)
                    dict["mac"] = match1.group(2)
                    dict["js_intf"] = match1.group(3)
                    op.append(dict)
                else:
                    match = re.search(r'(\d+)\s+(\S+)\s+\S+\s+(\S+)', line)
                    if match:
                        dict['vlan'] = match.group(1)
                        dict["mac"] = match.group(2)
                        dict["cs_intf"] = match.group(3)
                        op.append(dict)
        return op

    def juniper_mac_output(self, cmd_lines):
        output_lines = []
        cmd_match = False
        # cmd = "JUNIPER MACTABLE TOOL"
        sw = ""
        for line in cmd_lines:
            if not cmd_match:
                match = re.search('root@(\S+)>\s?show ethernet-switching table', line)
                if match:
                    sw = match.group(1)
                    cmd_match = True
                    continue
            else:
                match = re.search("root@(\S+)>\s?$", line)
                if match:
                    cmd_match = False
                else:
                    output_lines.append(line.rstrip())
        return sw, output_lines

    def juniper_interface_status(self, cmd_lines):
        output_lines = []
        cmd_match = False
        # cmd = "JUNIPER MACTABLE TOOL"
        for line in cmd_lines:
            if not cmd_match:
                match = re.search('root@(\S+)>\s?show interfaces | match Physical', line)
                if match:
                    cmd_match = True
                    continue
            else:
                match = re.search("root@(\S+)>\s?$", line)
                if match:
                    cmd_match = False
                else:
                    output_lines.append(line.rstrip())
        return output_lines

    def parse_cisco_op(self, file_line):
        self.cisco_mac_op = []
        cs_output_lines = self.cisco_mac_output(file_line)
        cs_sw_list = self.get_sw_list(cs_output_lines)
        print cs_sw_list
        for sw in cs_sw_list:
            self.cisco_mac_op += self.sw_mac_table(sw, cs_output_lines)

        # def parse_juniper_op(self, file_line):
        self.juniper_mac_op = []
        js_output_lines = self.juniper_mac_output(file_line)
        # js_sw_list =  self.get_sw_list(js_output_lines)
        sw = js_output_lines[0]
        self.js_int_status_op = []
        js_status_op = self.juniper_interface_status(file_line)
        self.down_intface = self.js_interface_status(js_status_op, sw)
        # for ele in self.sw_mac_table(sw_list[0], output_lines):
        #     print ele
        # for sw in js_sw_list:
        #     self.juniper_mac_op += self.sw_mac_table(sw, js_output_lines)
        for line in js_output_lines[1]:
            js_dict = {}
            match1 = re.search(r'v(\d+)\s+(\S+)\s.+\s(ge\S+).\d', line)
            if match1:
                js_dict['switch'] = sw
                js_dict['vlan'] = match1.group(1)
                js_dict["mac"] = match1.group(2)
                js_dict["js_intf"] = match1.group(3)
                self.juniper_mac_op.append(js_dict)

    def js_interface_status(self, op_lines, switch):
        # infile1 = open(filename, 'r+')
        # op_lines = [i for i in infile1.readlines()]
        db_interface_list = []
        entry = SwitchMigrationDB.objects.filter(newswitch=switch).all()
        if entry:
            for each in entry:
                db_interface_list.append(each.newinterface)

        down_int_list = []
        for line in op_lines:
            match = re.search(r'(\S+-\d/\d/\d+).+\s(\w+)', line)
            if match:
                # print match.group(1), match.group(2)
                if match.group(2).lower() == "down" and match.group(1) in db_interface_list:
                    down_int_list.append(match.group(1))
        return down_int_list

    def get_cisco_dict(self):
        return self.cisco_mac_op

    def get_juniper_dict(self):
        return self.juniper_mac_op

    def get_juniper_down_int(self):
        return self.down_intface

    def get_csv_dict(self):
        return self.data_list


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


class ParseSwitchConfiguration:
    def __init__(self, file_lines, taskid):
        self.file_lines = file_lines
        self.taskid = taskid

    def Parse_vlan_config(self, vlan_config):
        main_vlan_dict = {}
        my_dict = {'helper_add': []}
        my_dict['pim'] = False
        for ele in vlan_config:
            vlan_id = ""
            match1 = re.search(r'interface\s+(\S+\d)', ele)
            if match1:
                vlan_id = match1.group(1)
                main_vlan_dict[vlan_id] = {}

            match = re.search(r'description (.+)$', ele)
            if match:
                # print match.group()
                # my_dict["Vlan"]=match.group()
                my_dict["description"] = match.group(1)

            match2 = re.search(r'vrf forwarding\s(\S+)', ele)
            if match2:
                my_dict['vrf'] = match2.group(1)
                # my_dict['subnet']=match2.group(2)

            match3 = re.search(r'ip address\s+(\d+.\d+.\d+.\d+)\s(\d+.\d+.\d+.\d+)', ele)
            if match3:
                # print match3.group(1)
                my_dict['subnet'] = match3.group(1)
                my_dict['mask'] = match3.group(2)
            match4 = re.search(r'-address\s+(\d+.\d+.\d+.\d+)', ele)
            if match4:
                # print match4.group()
                my_dict['helper_add'].append(match4.group(1))
                # my_dict['mask']=match3.group(2)
            if "ip pim sparse-mode" in ele:
                my_dict['pim'] = True
            if vlan_id != "":
                main_vlan_dict[vlan_id] = my_dict
        return main_vlan_dict

    def get_hostname(self, file_data):

        host_name = ""
        for line in file_data:
            regex = re.search(r'hostname\s+(\S+)', line)
            if regex:
                host_name = regex.group(1)

                return host_name

    def get_vlan_list(self, file_data):
        vlan_list = []
        for e_line in file_data:
            m = re.search(r'^vlan\s+(\d+)', e_line)
            m2 = re.search(r'[Ii]nterface [Vv]lan\s?(\d+)', e_line)
            if m:
                vlan_list.append(m.group(1))
            if m2 and m2.group(1) not in vlan_list:
                vlan_list.append(m2.group(1))
        return vlan_list

    def get_vlan_config(self, file_data, vlan_id):
        m_flag = False
        vlan_config = []
        for line in file_data:
            m1 = re.search('interface Vlan(\d+)', line)
            if m1:
                matched_vlan = m1.group(1)
                if matched_vlan == vlan_id:
                    m_flag = True
            if m_flag:
                if re.search("!", line):
                    m_flag = False
                vlan_config.append(line)
        return vlan_config

    def parsing_switch_config(self, file_data):
        variables_store = {'dns_server': [], 'ntp_server': []}

        for var in file_data:
            matching_1 = re.search(r'domain-name\s+(\S+)', var)
            if matching_1:
                variables_store['domain_name'] = matching_1.group(1)
            # dns_server=[]
            matching_2 = re.search(r'name-server\s+(\d+.\d+.\d+.\d+)', var)
            if matching_2:
                # dns_server.append(matching_2.group(1))
                variables_store['dns_server'].append(matching_2.group(1))

            matching_3 = re.search(r'redundancy-mode\s+(\w+)', var)
            if matching_3:
                variables_store['redundancy_mode'] = matching_3.group(1)

            matching_4 = re.search(r'logging host\s+(\S+)', var)
            if matching_4:
                variables_store['logging_server'] = matching_4.group(1)

            matching_5 = re.search(r'location\s(.+)\s+<', var)
            if matching_5:
                variables_store['location'] = matching_5.group(1)
            matching_6 = re.search(r'ntp server\s+(.+)\s(\S+)', var)
            if matching_6:
                variables_store['ntp_server'].append(matching_6.group(2))
            matching_7 = re.search(r'(\S+)\s+RO', var)
            if matching_7:
                variables_store['SNMPv2_RO '] = matching_7.group(1)
            matching_8 = re.search(r'(\S+)\s+RW', var)
            if matching_8:
                variables_store['SNMPv2_RW '] = matching_8.group(1)
            matching_9 = re.search(r'server-private\s+(\S+)\s+key', var)
            if matching_9:
                variables_store['tacacs_server'] = matching_9.group(1)

            matching_10 = re.search(r' server-private\s+(\S+)\s+auth', var)
            if matching_10:
                variables_store['radius_server'] = matching_10.group(1)
        return variables_store

    def main_fun(self):
        vlan_list = self.get_vlan_list(self.file_lines)
        hostname = self.get_hostname(self.file_lines)
        file_var = self.parsing_switch_config(self.file_lines)
        output_dict = {hostname: {"vlans": {}}}
        vlan_dict = []
        for vlan in vlan_list:
            vlan_dict.append(self.Parse_vlan_config(self.get_vlan_config(self.file_lines, vlan)))

        for key, value in file_var.iteritems():
            output_dict[hostname][key] = value

        for ele in vlan_dict:
            for key, value in ele.iteritems():
                output_dict[hostname]["vlans"][key] = value
        p1 = UserInputValueDb(taskid=self.taskid, subtaskid=00, field_name='hostname', field_value=hostname)
        p1.save()
        with open('/home/ubuntu/prepro/mysite/mysite/Json_DATA/Devices.json') as devices_json_data:
            try:
                devices_data = json.load(devices_json_data)
                devices_data.update(output_dict)
                with open('/home/ubuntu/prepro/mysite/mysite/Json_DATA/Devices.json', 'w') as data:
                    json.dump(devices_data, data)
            except:
                with open('/home/ubuntu/prepro/mysite/mysite/Json_DATA/Devices.json', 'w') as data:
                    json.dump(output_dict, data)

        # file_json=open('/home/ubuntu/prepro/mysite/mysite/Json_DATA/Devices.json','w')
        # json.dump(output_dict,file_json)
        return {'msg': "Device Data saved succesfully", 'flag': True, 'output': output_dict}


def generate_sdwan_inputs(response_dict):
    input_dict = response_dict
    if "site_no" in input_dict:
        response_dict["system_id1"] = input_dict["country_or_continent"] + input_dict["region"] + input_dict[
            "site_type"] + str(1000 + int(input_dict["site_no"]))
        response_dict["system_id2"] = input_dict["country_or_continent"] + input_dict["region"] + input_dict[
            "site_type"] + str(1000 + int(input_dict["site_no"]) + 1)

        if "system_ip_pool" in input_dict:
            sys_ip = input_dict["system_ip_pool"].split("/")
            transit_ip = input_dict["transit_pool"].split("/")
            if int(input_dict["site_no"]) == 1:
                response_dict["system_ip"] = str(
                    (IPNetwork(sys_ip[0] + "/32").ip) + (int(input_dict["site_no"]))) + "/32"
                response_dict["transit_ip"] = str(
                    (IPNetwork(transit_ip[0] + "/32").ip) + (int(input_dict["site_no"]))) + "/30"
            else:
                response_dict["system_ip"] = str(
                    (IPNetwork(sys_ip[0] + "/32").ip) + (int(input_dict["site_no"]) + 1)) + "/32"
                response_dict["transit_ip"] = str(
                    (IPNetwork(transit_ip[0] + "/32").ip) + (1 + ((int(input_dict["site_no"]) - 1) * 8))) + "/30"

    return response_dict
