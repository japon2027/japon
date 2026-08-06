###### import discord

###### from discord.ext import tasks

###### from datetime import datetime, time

###### from zoneinfo import ZoneInfo

###### 

###### \# ─── CONFIGURATION ────────────────────────────────────────────────

###### TOKEN = "MTUzNTAzMTE2NjI5NjUyNjkxOA.Gy-Xdk.J\_NNGRjDsb7LMgJ0MUDPWT-1u4VoOxITpRQiuk"          # Token du bot (voir instructions)

###### CHANNEL\_ID = japon         # ID du channel où poster

###### CIBLE = datetime(2027, 4, 25, 12, 0, tzinfo=ZoneInfo("Europe/Brussels"))

###### HEURE\_ENVOI = time(hour=12, minute=0, tzinfo=ZoneInfo("Europe/Brussels"))

###### \# ──────────────────────────────────────────────────────────────────

###### 

###### intents = discord.Intents.default()

###### client = discord.Client(intents=intents)

###### 

###### 

###### def jours\_restants():

###### &#x20;   maintenant = datetime.now(ZoneInfo("Europe/Brussels"))

###### &#x20;   delta = CIBLE - maintenant

###### &#x20;   return delta.days

###### 

###### 

###### @tasks.loop(time=HEURE\_ENVOI)

###### async def envoi\_quotidien():

###### &#x20;   channel = client.get\_channel(CHANNEL\_ID)

###### &#x20;   if channel is None:

###### &#x20;       print("Channel introuvable — vérifie CHANNEL\_ID.")

###### &#x20;       return

###### 

###### &#x20;   jours = jours\_restants()

###### &#x20;   if jours > 1:

###### &#x20;       await channel.send(f"⏳ Plus que \*\*{jours} jours\*\* avant le 25 avril 2027 !")

###### &#x20;   elif jours == 1:

###### &#x20;       await channel.send("⏳ Plus qu'\*\*1 jour\*\* avant le 25 avril 2027 !")

###### &#x20;   elif jours == 0:

###### &#x20;       await channel.send("🎉 C'est aujourd'hui : \*\*25 avril 2027\*\* !")

###### &#x20;   # après la date : n'envoie plus rien

###### 

###### 

###### @client.event

###### async def on\_ready():

###### &#x20;   print(f"Connecté en tant que {client.user}")

###### &#x20;   if not envoi\_quotidien.is\_running():

###### &#x20;       envoi\_quotidien.start()

###### 

###### 

###### client.run(TOKEN)

