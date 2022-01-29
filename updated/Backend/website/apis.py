from flask import Blueprint, redirect, request ,render_template, flash, jsonify,url_for
from flask_login import login_required, current_user
import json
import requests
import copy
from requests.auth import HTTPBasicAuth

apis = Blueprint('apis', __name__)


@apis.route('/show_data', methods=['GET', 'POST'])
@login_required
def showData():
    url="http://10.15.3.10:8181/restconf/operational/network-topology:network-topology"
    response = requests.get(url,auth=HTTPBasicAuth('admin', 'admin'))
    data=response.json()
    if data:
        nodesCount = len(data["network-topology"]["topology"][0]["node"])
        nodeDetailsList=[]
    count=1
    for nodeC in range(0,nodesCount):
        if "host" in data["network-topology"]["topology"][0]["node"][nodeC]["node-id"]:
            nodeDetailsList.append([count,data["network-topology"]["topology"][0]["node"][nodeC]['host-tracker-service:addresses'][0]['mac'],data["network-topology"]["topology"][0]["node"][nodeC]['host-tracker-service:addresses'][0]['ip'],data["network-topology"]["topology"][0]["node"][nodeC]['host-tracker-service:attachment-points'][0]['active']])
            count=count+1

    url="http://10.15.3.10:8181/restconf/operational/opendaylight-inventory:nodes"
    response = requests.get(url,auth=HTTPBasicAuth('admin', 'admin'))
    data2=response.json()
    if data2:
        switchData=[]
        nodesCount = len(data2["nodes"]["node"])
        for switch in range(0,nodesCount):
            for i in data2["nodes"]["node"][switch]["flow-node-inventory:table"]:
                if i["opendaylight-flow-table-statistics:flow-table-statistics"]["active-flows"] != 0:
                    switchData.append([data2["nodes"]["node"][switch]["id"],i["id"],i["opendaylight-flow-table-statistics:flow-table-statistics"]["active-flows"],i["opendaylight-flow-table-statistics:flow-table-statistics"]["packets-looked-up"],i["opendaylight-flow-table-statistics:flow-table-statistics"]["packets-matched"]])

    return render_template("scj_page.html", user=current_user, nodeData = nodeDetailsList,switchData=switchData)


jsonLayout ="""{
     "input": {
         "node": "/opendaylight-inventory:nodes/opendaylight-inventory:node[opendaylight-inventory:id='openflow:1']",
         "table_id": 0,
         "priority":99 ,
         "match": {
             "ipv4-destination": "10.0.0.4/32",
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
                                 "drop-action": {
                                 }
                             }
                         ]
                     }
                 }
             ]
         }
     }
 }"""
jsonData = json.loads(jsonLayout)
addFlowUrl = "http://10.15.3.10:8181/restconf/operations/sal-flow:add-flow"
removeFlowUrl = "http://10.15.3.10:8181/restconf/operations/sal-flow:remove-flow"
headers = {'Content-Type': 'application/json'}

@apis.route('/addFlow', methods=['GET', 'POST'])
@login_required
def addFlow():
    if request.method == 'POST':
        dstIP = request.form.get('dstIP')
        switch = request.form.get("switch")
        if switch == "0":
            for sw in range (1,8,1):
                tempData = copy.deepcopy(jsonData)
                tempData['input']["match"]["ipv4-destination"] = str(dstIP)
                tempData['input']["node"]= "/opendaylight-inventory:nodes/opendaylight-inventory:node[opendaylight-inventory:id='openflow:"+ str(sw) +"']"
                sendData = json.dumps(tempData)
                response = requests.post(addFlowUrl,auth=HTTPBasicAuth('admin', 'admin'), data=sendData,headers=headers)
            if response.status_code ==200:
                flash('Flow Added', category='success')
                return redirect(url_for('views.postPage'))
            else:
                flash('Flow Adding Error', category='error')
                return redirect(url_for('views.postPage'))
        else:
            tempData = copy.deepcopy(jsonData)
            tempData['input']["match"]["ipv4-destination"] = str(dstIP)
            tempData['input']["node"]= "/opendaylight-inventory:nodes/opendaylight-inventory:node[opendaylight-inventory:id='openflow:"+ str(switch) +"']"
            sendData = json.dumps(tempData)
            response = requests.post(addFlowUrl,auth=HTTPBasicAuth('admin', 'admin'), data=sendData,headers=headers)
            if response.status_code ==200:
                flash('Flow Added', category='success')
                return redirect(url_for('views.postPage'))
            else:
                flash('Flow Adding Error', category='error')
                return redirect(url_for('views.postPage'))
    else:
        flash('Error', category='error')
        return redirect(url_for('views.postPage'))


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

