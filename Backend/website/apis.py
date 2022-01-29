from flask import Blueprint, redirect, request ,render_template, flash, jsonify,url_for,session
from flask_login import login_required, current_user
import json
import requests
import copy
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from os import getenv

load_dotenv()
apis = Blueprint('apis', __name__)

@apis.route('/show_data', methods=['GET', 'POST'])
@login_required
def showData():
    url=f"http://{getenv('SERVER_IP')}:{getenv('PORT')}/{getenv('ENDPOINT')}/network-topology:network-topology"
    response = requests.get(url, auth=HTTPBasicAuth("admin","admin"))
    data=response.json()
    if data:
        nodesCount = len(data["network-topology"]["topology"][0]["node"])
        nodeDetailsList=[]
    count=1
    for nodeC in range(0,nodesCount):
        if "host" in data["network-topology"]["topology"][0]["node"][nodeC]["node-id"]:
            nodeDetailsList.append([count,data["network-topology"]["topology"][0]["node"][nodeC]['host-tracker-service:addresses'][0]['mac'],data["network-topology"]["topology"][0]["node"][nodeC]['host-tracker-service:addresses'][0]['ip'],data["network-topology"]["topology"][0]["node"][nodeC]['host-tracker-service:attachment-points'][0]['active']])
            count=count+1

    url=f"http://{getenv('SERVER_IP')}:{getenv('PORT')}/{getenv('ENDPOINT')}/opendaylight-inventory:nodes"
    response = requests.get(url, auth=HTTPBasicAuth("admin","admin"))
    data2=response.json()
    if data2:
        switchData=[]
        nodesCount = len(data2["nodes"]["node"])
        for switch in range(0,nodesCount):
            for i in data2["nodes"]["node"][switch]["flow-node-inventory:table"]:
                if i["opendaylight-flow-table-statistics:flow-table-statistics"]["active-flows"] != 0:
                    switchData.append([data2["nodes"]["node"][switch]["id"],i["id"],i["opendaylight-flow-table-statistics:flow-table-statistics"]["active-flows"],i["opendaylight-flow-table-statistics:flow-table-statistics"]["packets-looked-up"],i["opendaylight-flow-table-statistics:flow-table-statistics"]["packets-matched"]])

    return render_template("scj_page.html", user=current_user, nodeData = nodeDetailsList,switchData=switchData)



dataLayoutDic = {
     "input": {
         "node": "/opendaylight-inventory:nodes/opendaylight-inventory:node[opendaylight-inventory:id='openflow:1']",
         "table_id": 0,
         "priority":99 ,
         "match": {
             "ethernet-match": {
                 "ethernet-type": {
                     "type": 2048
                 }
             }
         },
         "instructions": {
             "instruction": [
                 {
                     "order": 0,
                     "apply-actions": {
                         "action": [
                             {
                                 "order": 0,
                                 "drop-action": {}
                             }
                         ]
                     }
                 }
             ]
         }
     }
 }
jsonData = dataLayoutDic
addFlowUrl = f"http://{getenv('SERVER_IP')}:{getenv('PORT')}/restconf/operations/sal-flow:add-flow"
removeFlowUrl = f"http://{getenv('SERVER_IP')}:{getenv('PORT')}/restconf/operations/sal-flow:remove-flow"
headers = {'Content-Type': 'application/json'}

@apis.route('/addFlow', methods=['GET', 'POST'])
@login_required
def addFlow():
    if request.method == 'POST':
        switch = request.form.get("switch")
        switchCount = session.get('switch-count')
        if switch == "0":
            tempData = copy.deepcopy(jsonData)
            tempData['input']["priority"] = request.form.get('priority')
            if request.form.get('action') == "1":
                tempData['input']["instructions"]["instruction"][0]["apply-actions"]["action"]= [{"order": 0,"output-action": {"output-node-connector": "ALL","max-length": 60}}]
            else:
                tempData['input']["instructions"]["instruction"][0]["apply-actions"]["action"]= [{"order": 0,"drop-action": {}}]
            count =0
            if request.form.get('dstIP')!="None":
                count =1
                tempData['input']["match"]["ipv4-destination"] = request.form.get('dstIP')
            if request.form.get('srcIP')!="None":
                count =1
                tempData['input']["match"]["ipv4-source"] = request.form.get('srcIP')
            if request.form.get('dstMAC')!="None":
                count =1
                tempData['input']["match"]["ethernet-match"]["ethernet-source"]={"address":request.form.get('dstMAC')}
            if request.form.get('srcMAC')!="None":
                count =1
                tempData['input']["match"]["ethernet-match"]["ethernet-destination"]={"address":request.form.get('srcMAC')}
            if request.form.get('ipProtocol')!="None":
                count =1
                tempData['input']["match"]["ip-match"]={"ip-protocol": int(request.form.get('ipProtocol'))}
            if count ==1:
                for sw in range (1,switchCount+1,1):
                    tempData['input']["node"]= "/opendaylight-inventory:nodes/opendaylight-inventory:node[opendaylight-inventory:id='openflow:"+ str(sw) +"']"
                    sendData = json.dumps(tempData)
                    response = requests.post(addFlowUrl,auth=HTTPBasicAuth('admin', 'admin'), data=sendData,headers=headers)
                if response.status_code ==200:
                    flash('Flow Added', category='success')
                    return redirect(url_for('apis.showFlows'))
                else:
                    flash('Flow Adding Error', category='error')
                    return redirect(url_for('apis.showFlows'))
            else:
                flash('NO Flow Data to Add', category='error')
                return redirect(url_for('apis.showFlows'))
        else:
            tempData = copy.deepcopy(jsonData)
            tempData['input']["priority"] = request.form.get('priority')
            if request.form.get('action') == "1":
                tempData['input']["instructions"]["instruction"][0]["apply-actions"]["action"]= [{"order": 0,"output-action": {"output-node-connector": "ALL","max-length": 60}}]
            else:
                tempData['input']["instructions"]["instruction"][0]["apply-actions"]["action"]= [{"order": 0,"drop-action": {}}]
            count =0
            if request.form.get('dstIP')!="None":
                count =1
                tempData['input']["match"]["ipv4-destination"] = request.form.get('dstIP')
            if request.form.get('srcIP')!="None":
                count =1
                tempData['input']["match"]["ipv4-source"] = request.form.get('srcIP')
            if request.form.get('dstMAC')!="None":
                count =1
                tempData['input']["match"]["ethernet-match"]["ethernet-source"]={"address":request.form.get('dstMAC')}
            if request.form.get('srcMAC')!="None":
                count =1
                tempData['input']["match"]["ethernet-match"]["ethernet-destination"]={"address":request.form.get('srcMAC')}
            if request.form.get('ipProtocol')!="None":
                count =1
                tempData['input']["match"]["ip-match"]={"ip-protocol": int(request.form.get('ipProtocol'))}
            tempData['input']["node"]= "/opendaylight-inventory:nodes/opendaylight-inventory:node[opendaylight-inventory:id='openflow:"+ str(switch) +"']"
            sendData = json.dumps(tempData)
            if count ==1:
                response = requests.post(addFlowUrl,auth=HTTPBasicAuth('admin', 'admin'), data=sendData,headers=headers)
                if response.status_code ==200:
                    flash('Flow Added', category='success')
                    return redirect(url_for('apis.showFlows'))
                else:
                    flash('Flow Adding Error', category='error')
                    return redirect(url_for('apis.showFlows'))
            else:
                flash('NO Flow Data to Add', category='error')
                return redirect(url_for('apis.showFlows'))
    else:
        flash('Error', category='error')
        return redirect(url_for('apis.showFlows'))


@apis.route('/removeFlow', methods=['GET', 'POST'])
@login_required
def removeFlow():
    if request.method == 'POST':
        dstIP = request.form.get('dstIP')
        switch = request.form.get("switch")
        if switch == "0":
            for sw in range (1,8,1):
                tempData = copy.deepcopy(jsonData)
                tempData['input']["match"]["ipv4-destination"] = str(dstIP)
                tempData['input']["node"]= "/opendaylight-inventory:nodes/opendaylight-inventory:node[opendaylight-inventory:id='openflow:"+ str(sw) +"']"
                sendData = json.dumps(tempData)
                response = requests.post(removeFlowUrl,auth=HTTPBasicAuth('admin', 'admin'), data=sendData,headers=headers)
            if response.status_code ==200:
                flash('Flow Removed', category='success')
                return redirect(url_for('views.postPage'))
            else:
                flash('Flow Removing Error', category='error')
                return redirect(url_for('views.postPage'))
        else:
            tempData = copy.deepcopy(jsonData)
            tempData['input']["match"]["ipv4-destination"] = str(dstIP)
            tempData['input']["node"]= "/opendaylight-inventory:nodes/opendaylight-inventory:node[opendaylight-inventory:id='openflow:"+ str(switch) +"']"
            sendData = json.dumps(tempData)
            response = requests.post(removeFlowUrl,auth=HTTPBasicAuth('admin', 'admin'), data=sendData,headers=headers)
            if response.status_code ==200:
                flash('Flow Removed', category='success')
                return redirect(url_for('views.postPage'))
            else:
                flash('Flow Removing Error', category='error')
                return redirect(url_for('views.postPage'))
    else:
        flash('Error', category='error')
        return redirect(url_for('views.postPage'))

@apis.route('/show_flows', methods=['GET', 'POST'])
@login_required
def showFlows():
    url=f"http://{getenv('SERVER_IP')}:{getenv('PORT')}/{getenv('ENDPOINT')}/opendaylight-inventory:nodes"
    response = requests.get(url, auth=HTTPBasicAuth("admin","admin"))
    data2=response.json()
    if data2:
        switchData=[]
        nodesCount = len(data2["nodes"]["node"])
        session['switch-count'] = nodesCount
        count=0 
        for switch in range(0,nodesCount):
            for i in data2["nodes"]["node"][switch]["flow-node-inventory:table"]:
                if i["opendaylight-flow-table-statistics:flow-table-statistics"]["active-flows"] != 0:
                    for flows in i["flow"]:
                        switchData.append([data2["nodes"]["node"][switch]["id"],i["opendaylight-flow-table-statistics:flow-table-statistics"]["active-flows"],flows["id"],flows["priority"]])
                        # print(flows['id'],flows["priority"],flows["match"]["ethernet-match"])
                        if "ethernet-match" in flows["match"]:
                            temp=[]
                            if "ethernet-source" in flows["match"]["ethernet-match"]:
                                temp.append(flows["match"]["ethernet-match"]["ethernet-source"]["address"])
                            else: 
                                temp.append("None")
                            if "ethernet-destination" in flows["match"]["ethernet-match"]:
                                temp.append(flows["match"]["ethernet-match"]["ethernet-destination"]["address"])
                            else: 
                                temp.append("None")
                            switchData[count].extend(temp) 
                        else: switchData[count].extend(["None1","None2"])                             
                        if "in-port" in flows["match"]:   
                            # print(flows['id'],flows['match'])
                            switchData[count].extend([flows["match"]["in-port"]]) 
                            # switchData[switch].extend(["500"]) 
                        elif "in-port" not in flows["match"]: 
                            # print(flows['match'])
                            switchData[count].extend(["None3"]) 
                        if "ip-match" in flows["match"]:
                            switchData[count].extend([flows["match"]["ip-match"]["ip-protocol"]]) 
                        elif "ip-match" not in flows["match"]:
                            switchData[count].extend(["None"]) 
                        if "ipv4-destination" in flows["match"]:
                            switchData[count].extend([flows["match"]["ipv4-destination"]]) 
                        elif "ipv4-destination" not in flows["match"]:
                            switchData[count].extend(["None"]) 
                        if "ipv4-source" in flows["match"]:
                            switchData[count].extend([flows["match"]["ipv4-source"]]) 
                        elif "ipv4-source" not in flows["match"]:
                            switchData[count].extend(["None"]) 
                        count+=1
    return render_template("flows.html", user=current_user, switchData=switchData , switchCount = nodesCount )
