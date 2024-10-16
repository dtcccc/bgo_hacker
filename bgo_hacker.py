#usage: mitmdump -s bgo_hacker.py

import base64, urllib, json
from mitmproxy import http

def replace_svt_info(battle_info):
    svtlist=battle_info["userSvt"]
    enemylist=battle_info["enemyDeck"]

    dropflag=False
    for phase in enemylist:
        for enemy in phase["svts"]:
            for drop in enemy.get("dropInfos",()):
                if drop["rarity"]==8:
                    dropflag=True

    for svt in svtlist:
        if svt["userId"]==0 and svt.get("isFollower",False)==False:
            svt["atk"]=1
            svt["hp"]=2 if dropflag else 1
        elif "parentSvtId" not in svt:
            svt["classPassive"]+=[990131]*3 #2030
            svt["classPassive"]+=[990066]*3 #red
            svt["classPassive"]+=[990062]*3 #blue
            svt["classPassive"]+=[990064]*3 #green
            svt["classPassive"]+=[990070]*3 #baoju
            svt["classPassive"]+=[990113]*3 #critical
            svt["classPassive"]+=[990079]*10 #np
            svt["classPassive"]+=[990447]*10 #atk&np
            svt["classPassive"]+=[461550]*10 #db&resist
            svt["classPassive"]+=[991315]*10 #hp
            svt["classPassive"].append(990453) #wdgt
            svt["classPassive"].append(993507) #wsfy

def response(flow: http.HTTPFlow):
    if flow.request.method != "POST" or flow.response.status_code != 200:
        return

    key=flow.request.query.get("_key")
    if key not in ["battlesetup","battleresume","warboardbattlesetup","warboardbattleresume"]:
        return

    jdata=json.loads(base64.b64decode(urllib.parse.unquote_to_bytes(flow.response.get_content())))
    battle=jdata.get("cache",{}).get("replaced",{}).get("battle")
    if battle is None:
        return
    battle_info=battle[0].get("battleInfo")
    if battle_info is None:
        return

    replace_svt_info(battle_info)

    del jdata["sign"]
    flow.response.set_text(urllib.parse.quote_from_bytes(base64.b64encode(json.dumps(jdata).encode("utf8"))))
