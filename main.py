def sendnotif(tradejson):
    with open("RolimonsItems.json","r") as f: #I open this every time I start the subroutine because I want the most up-to-date values
        rolivalues = json.load(f)
    TradeValues = [0,0]
    for a,v in enumerate(tradejson['offers']): #This bit iterates through the offers, and calculates the final values
        for i in v['userAssets']:
            TradeValues[a] += rolivalues[str(i['assetId'])]['Value']
        TradeValues[a] += v['robux']
    OurRobux = tradejson['offers'][0]['robux']
    TheirRobux = tradejson['offers'][1]['robux']
    if OurRobux != 0:
        OurRobux = f"\nRobux: {tradejson['offers'][0]['robux']} ({(tradejson['offers'][0]['robux']//10)*7})"
    else:
        OurRobux = ""
    if TheirRobux != 0:
        TheirRobux = f"\nRobux: {tradejson['offers'][1]['robux']} ({(tradejson['offers'][1]['robux']//10)*7})"
    else:
        TheirRobux = ""
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
                        "value": "\n".join(f"{':warning: ' if rolivalues[str(i['assetId'])]['Projected'] else ''}[{i['name']}](https://www.roblox.com/catalog/{i['assetId']}) ({rolivalues[str(i['assetId'])]['Value']:,d})" for i in tradejson['offers'][0]['userAssets'])+f"{OurRobux}\n\n**Total Value:** {TradeValues[0]:,d}"
                    },
                    {
                        "name": "Offering",
                        "value": "\n".join(f"{':warning: ' if rolivalues[str(i['assetId'])]['Projected'] else ''}[{i['name']}](https://www.roblox.com/catalog/{i['assetId']}) ({rolivalues[str(i['assetId'])]['Value']:,d})" for i in tradejson['offers'][1]['userAssets'])+f"{TheirRobux}\n\n**Total Value:** {TradeValues[1]:,d}"
                    },
                    {
                        "name": "Evaluation",
                        "value": f"Value {'Gain' if (TradeValues[1]-TradeValues[0])>0 else 'Loss'}: {abs(TradeValues[1]-TradeValues[0]):,d} ({'+' if (TradeValues[1]-TradeValues[0])>=0 else '-'}{round(abs(((TradeValues[0]-TradeValues[1])/TradeValues[1])*100),2)}%)\nItem {'Gain' if len(tradejson['offers'][1]['userAssets'])-len(tradejson['offers'][0]['userAssets'])>0 else 'Loss'}: {abs(len(tradejson['offers'][1]['userAssets'])-len(tradejson['offers'][0]['userAssets'])):,d}" 
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
