import json,time,datetime
from this import d #Json, time, and datetime are all inbuilt libraries with python, so you don't need to install them.
try: #Requests on the other hand, needs to be installed. This just checks to see if you have it installed..
    import requests
except: #and if you don't, it'll install it for you!
    import os
    os.system('py -m install requests')
    import requests

with open("config.json","r") as f:
    data = json.load(f)
cookie = data['Cookie']
WinWebhook = data['WinWebhook']
LoseWebhook = data['LoseWebhook']
DiscordID = data['Discord ID']

def sendnotif(tradejson):
    with open("RolimonsItems.json","r") as f: #I open this every time I start the subroutine because I want the most up-to-date values
        rolivalues = json.load(f)
    TradeValues = [0,0]
    for a,v in enumerate(tradejson['offers']): #This bit iterates through the offers, and calculates the final values
        for i in v['userAssets']:
            TradeValues[a] += rolivalues[str(i['assetId'])]['Value']
        TradeValues[a] += v['robux']
    #With this, be careful what you edit (I advise you look at https://leovoel.github.io/embed-visualizer/ for more info)
    data = {
        "username" : "Trade Notifier", #You don't NECESSARILY need to have this and the avatar_url field, I just felt like including it [You could change the name on the webhook every time]
        "avatar_url": "https://cdn.discordapp.com/icons/548263085614301186/a_bbb4230eb4af483dee66e996fdd67f18.png?size=1024", #Same as above, you don't need to specify this, but you're more than welcome to.
        "content": f"<@!{DiscordID}>, you have recieved a new trade!", #This is why I make the user put their discordID in config.json, so you get pinged each time
        "embeds":
        [
            {
                "title": "Trade Information",
                "description": f"This trade was sent by [{tradejson['user']['name']}](https://www.roblox.com/users/{tradejson['user']['id']}/profile)",
                "fields": [
                    {
                        "name": "Requesting", #This might be a bit confusing, sorry! Essentially, I add a :warning: if the item is projected, then I post the item name and a link to that item - "\n".join() is just an easier way of sending them all in separate lines
                        "value": "\n".join(f"{':warning: ' if rolivalues[str(i['assetId'])]['Projected'] else ''} [{i['name']}](https://www.roblox.com/catalog/{i['assetId']}) ({rolivalues[str(i['assetId'])]['Value']:,d})" for i in tradejson['offers'][0]['userAssets'])+f"\nRobux: {tradejson['offers'][0]['robux']}\n**Total Value:** {TradeValues[0]:,d}"
                    },
                    {
                        "name": "Offering",
                        "value": "\n".join(f"{':warning: ' if rolivalues[str(i['assetId'])]['Projected'] else ''} [{i['name']}](https://www.roblox.com/catalog/{i['assetId']}) ({rolivalues[str(i['assetId'])]['Value']:,d})" for i in tradejson['offers'][1]['userAssets'])+f"\nRobux: {tradejson['offers'][1]['robux']}\n**Total Value:** {TradeValues[1]:,d}"
                    },
                    {
                        "name": "Evaluation",
                        "value": f"Value {'Gain' if (TradeValues[1]-TradeValues[0])>0 else 'Loss'}: {abs(TradeValues[1]-TradeValues[0]):,d}\nItem {'Gain' if len(tradejson['offers'][1]['userAssets'])-len(tradejson['offers'][0]['userAssets'])>0 else 'Loss'}: {abs(len(tradejson['offers'][1]['userAssets'])-len(tradejson['offers'][0]['userAssets'])):,d}" 
                    }
                ], 
                "thumbnail": {
                    "url": f"https://www.roblox.com/headshot-thumbnail/image?userId={tradejson['user']['id']}&width=100&height=100&format=png"
                }, #Makes the image URL the avatar of the user who sent me a trade
                "color": 0x00ff00 if (TradeValues[1]-TradeValues[0])>0 else 0xff0000, #Sets the colour to a lovely green
                "footer": #Text at the very bottom
                { 
                    "icon_url": "https://cdn.discordapp.com/icons/548263085614301186/a_bbb4230eb4af483dee66e996fdd67f18.png?size=1024",
                    "text": "Made by Charles#4743"
                }
            }
        ]
    }
    url = WinWebhook if (TradeValues[1]-TradeValues[0])>0 else LoseWebhook
    #This ends up looking like this https://gyazo.com/9e27e8579b3e9a8f33bc71ea16e8b64c
    requests.post(url,json=data) #Posts the webhook

def rolimonitemupdater():
    tempdata = {} #Makes an empty dict, this is where all our itemdetails will be added
    x = requests.get("https://www.rolimons.com/itemapi/itemdetails").json()
    for i in x['items']:
        tempdata[i] = {}
        tempdata[i]["Value"] = x['items'][i][3] if x['items'][i][3] != -1 else x['items'][i][4]
        tempdata[i]["Projected"] = True if x['items'][i][7] == 1 else False #True if the projected value reads 1, False if it doesn't
    with open("RolimonsItems.json","w") as f:
        json.dump(tempdata,f,indent=4)
    print(f"Rolimon Values up to date, last checked at {datetime.datetime.now().strftime('%H:%M:%S')}")

def refresh_trades():
    with open("config.json","r") as f:
        data = json.load(f)
    mostrecenttrades = data["MostRecentTrades"] #We see what the most recent logged trades were, so we know what trades we HAVENT seen
    x = requests.get(
        "https://trades.roblox.com/v1/trades/Inbound?sortOrder=Asc&limit=10",
        cookies={".ROBLOSECURITY": cookie} 
        )
    trades = x.json()['data']
    for i in trades:
        if i['id'] in mostrecenttrades: #Basically checks to see if the id of this trade has already been checked over
            break #Break completely exits the for loop
        trade_data = requests.get(
            f"https://trades.roblox.com/v1/trades/{i['id']}", #Getting the info of the specific trade 
            cookies={".ROBLOSECURITY": cookie}
            )
        sendnotif(trade_data.json())
    data["MostRecentTrades"] = [i['id'] for i in trades] #Sets the value in the json to the most recent IDS
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)
    print(f"Trades up to date, last checked at {datetime.datetime.now().strftime('%H:%M:%S')}") #I mainly use this for debugging, and to see if the programs running.

while True:
    rolimonitemupdater()
    for i in range(30): #Loop this x amount times, then update rolimons values.. then loop back! (This means we're getting new rolimons values every 5 minutes)
        try:
            refresh_trades()
        except:
            pass
        time.sleep(10) #Sleeps for 10 seconds, as we're just sending a single get request this isn't going to be excessive
