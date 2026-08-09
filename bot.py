import os
import random
import discord
from discord.ext import tasks
from datetime import datetime, date, time
from zoneinfo import ZoneInfo

# ─── CONFIGURATION (lue depuis les variables Railway) ─────────────
TOKEN = os.environ["TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
CIBLE = datetime(2027, 4, 25, 12, 0, tzinfo=ZoneInfo("Europe/Brussels"))
HEURE_ENVOI = time(hour=12, minute=10, tzinfo=ZoneInfo("Europe/Brussels"))
DOSSIER_IMGS = "imgs"                    # dossier des images dans le repo
EXT_IMAGES = (".png", ".jpg", ".jpeg", ".gif", ".webp")

# ─── RAPPELS SUPPLÉMENTAIRES ──────────────────────────────────────
# Ajoute/retire des lignes ici. Format :
#   (date_limite, "ce pour quoi il faut réserver / faire qqch")
# Le nombre de jours est calculé automatiquement.
# Un rappel disparaît tout seul une fois sa date passée.
RAPPELS = [
    (date(2027, 3, 25), "Shinkansen via Smart-EX"),
    (date(2026, 12, 25),  "Shibuya Sky"),
    (date(2027,3,10), "Musée Ghibli (Mitaka)"),
    # (date(2027, 4, 20), "confirmer la réservation resto"),
]
# ──────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def jours_restants():
    maintenant = datetime.now(ZoneInfo("Europe/Brussels"))
    delta = CIBLE - maintenant
    return delta.days


def texte_rappels():
    """Construit le bloc de rappels encore valides, ou '' si aucun."""
    aujourdhui = datetime.now(ZoneInfo("Europe/Brussels")).date()
    lignes = []
    for date_limite, quoi in RAPPELS:
        jours = (date_limite - aujourdhui).days
        if jours < 0:
            continue  # date passée → on n'affiche plus ce rappel
        jour_txt = "jour" if jours in (0, 1) else "jours"
        d = date_limite.strftime("%d/%m")
        if jours == 0:
            lignes.append(f"⚠️ Rappel : **aujourd'hui** ({d}) pour {quoi}")
        else:
            lignes.append(f"Rappel : **{jours} {jour_txt}** avant le {d} pour {quoi}")
    if not lignes:
        return ""
    separateur = "\n-----------------------------------------------\n"
    return separateur + "\n".join(lignes)


def image_aleatoire():
    """Retourne un objet discord.File pour une image au hasard, ou None si aucune."""
    if not os.path.isdir(DOSSIER_IMGS):
        print(f"Dossier '{DOSSIER_IMGS}' introuvable.")
        return None
    fichiers = [f for f in os.listdir(DOSSIER_IMGS)
                if f.lower().endswith(EXT_IMAGES)]
    if not fichiers:
        print(f"Aucune image dans '{DOSSIER_IMGS}'.")
        return None
    choix = random.choice(fichiers)
    return discord.File(os.path.join(DOSSIER_IMGS, choix))


@tasks.loop(time=HEURE_ENVOI)
async def envoi_quotidien():
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel introuvable — vérifie CHANNEL_ID.")
        return

    jours = jours_restants()
    if jours > 1:
        texte = f"⏳ Plus que **{jours} jours** avant le 25 avril 2027 !"
    elif jours == 1:
        texte = "⏳ Plus qu'**1 jour** avant le 25 avril 2027 !"
    elif jours == 0:
        texte = "🎉 C'est aujourd'hui : **25 avril 2027** !"
    else:
        return  # après la date : n'envoie plus rien

    texte += texte_rappels()  # ajoute les rappels sous le message (et sous la photo)

    image = image_aleatoire()
    if image is not None:
        await channel.send(content=texte, file=image)
    else:
        await channel.send(content=texte)  # pas d'image → juste le texte


@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")
    if not envoi_quotidien.is_running():
        envoi_quotidien.start()


client.run(TOKEN)
