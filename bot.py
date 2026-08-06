import os
import discord
from discord.ext import tasks
from datetime import datetime, time
from zoneinfo import ZoneInfo

# ─── CONFIGURATION (lue depuis les variables Railway) ─────────────
TOKEN = os.environ["TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
CIBLE = datetime(2027, 4, 25, 12, 0, tzinfo=ZoneInfo("Europe/Brussels"))
HEURE_ENVOI = time(hour=23, minute=32, tzinfo=ZoneInfo("Europe/Brussels"))
# ──────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def jours_restants():
    maintenant = datetime.now(ZoneInfo("Europe/Brussels"))
    delta = CIBLE - maintenant
    return delta.days


@tasks.loop(time=HEURE_ENVOI)
async def envoi_quotidien():
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel introuvable — vérifie CHANNEL_ID.")
        return

    jours = jours_restants()
    if jours > 1:
        await channel.send(f"⏳ Plus que **{jours} jours** avant le 25 avril 2027 !")
    elif jours == 1:
        await channel.send("⏳ Plus qu'**1 jour** avant le 25 avril 2027 !")
    elif jours == 0:
        await channel.send("🎉 C'est aujourd'hui : **25 avril 2027** !")
    # après la date : n'envoie plus rien


@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")
    if not envoi_quotidien.is_running():
        envoi_quotidien.start()


client.run(TOKEN)
