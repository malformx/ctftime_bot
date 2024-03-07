# This example requires the 'message_content' privileged intents

import os
from requests import get, post
from bs4 import BeautifulSoup
import discord
from discord.ext import commands, tasks
import json

base_url = "https://ctftime.org"
pe1 = "https://ctftime.org/writeup/36585" #last known writeup
pe2 = ""

async def get_writeups():
    global pe1
    global pe2

    writeup = base_url + "/writeups"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Referer": "https://ctftime.org/", "Connection": "close", "Upgrade-Insecure-Requests": "1", "Cache-Control": "max-age=0"}

    page = get(writeup, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table', id="writeups_table")
    data = table.find('tbody').find_all("tr")

    # scrap information from the page
    async def scrap_origin(url):
        page = get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        link = soup.find_all("div", {'class':'well'})[-1]

        try :
            l = link.a['href']
        except:
            l = None
        
        writer = soup.find("div", {'class':'page-header'}).find("a").string
        ctftimeuser = base_url + soup.find("div", {'class':'page-header'}).a['href']
        
        return l,writer, ctftimeuser

# make a list using the collected data
    def make_l(l):
        ctf_name = l[0].string
        event_url = base_url + l[0].a['href']
        task_name = l[1].string
        task_url = base_url + l[1].a['href']
        tag = ', '.join([x.string for x in l[2].find_all("span", {'class':'label label-info'})])
        tags = tag if tag !=None else "None"
        ctftime_writeup = base_url + l[4].a['href']
        scraper = await scrap_origin(ctftime_writeup)
        original_writeup = scraper[0]
        user_name = scraper[1]
        user_url = scraper[2]

        return ctf_name, event_url, task_name, task_url, ctftime_writeup, user_name, original_writeup, tags

    r_l = []
    g = make_l(data[0].find_all("td"))

# check if the urls are not repeating
    if pe1 != g[4]:
        pe2 = pe1
        pe1 = g[4]
        for i in data:
            d = make_l(i.find_all("td"))
            if pe2==d[4]:
                break
            send_data = discord.Embed(title=f"Writeup For **__{d[2]}__** From **__{d[0]}__**", url=d[4], description=f"Challenge Name: **{d[2]}**\nWritup Author: **{d[5]}**\nEvent Name: **{d[0]}**\nOriginal Writeup: **{d[6]}**\nChallenge Tags : **{d[7]}**", color=discord.Color.green())
            r_l.append(send_data) # make embedded links 
    return r_l

bot = commands.Bot("?", intents=discord.Intents.default())

@bot.command(name="ping", help="Alive check")
async def diss_ping(ctx):
    await ctx.send("""**Pong** mothafuka """)

#@bot.command(name="joke", help="Get random punch line jokes")
#async def get_joke(ctx):
#    r = get("")


@bot.command(name="meme", help="Get memes")
async def get_meme(ctx):
    r = get("https://meme-api.herokuapp.com/gimme")
    await ctx.send(json.loads(r.text)['url'])


channels = [897142365628825620] #justatest[writeups]

@tasks.loop(seconds=1250)
async def give_writeups():
    new_l = get_writeups.start()
    for channel_id in channels:
        message_channel = bot.get_channel(channel_id)
        print(f"Got channel {message_channel}")
        print("You made it, Sucker!")
        if new_l!=[]:
                for i in new_l:
                    await message_channel.send(embed=i)

@give_writeups.before_loop
async def before():
    await bot.wait_until_ready()

give_writeups.start()
bot.run(os.environ["DISCORD_TOKEN"])
