import os
import random
import discord
from discord.ext import tasks, commands
from datetime import datetime, date, time
from zoneinfo import ZoneInfo


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

TOKEN = os.environ["TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])

ZONE = ZoneInfo("Europe/Brussels")

CIBLE = datetime(
    2027,
    4,
    25,
    12,
    0,
    tzinfo=ZONE
)

HEURE_ENVOI = time(
    hour=10,
    minute=10,
    tzinfo=ZONE
)

DOSSIER_IMGS = "imgs"
EXT_IMAGES = (".png", ".jpg", ".jpeg", ".gif", ".webp")


# ─────────────────────────────────────────────
# RAPPELS
# ─────────────────────────────────────────────

RAPPELS = [
    (date(2027, 3, 25), "Shinkansen via Smart-EX"),
    (date(2026, 12, 25), "Shibuya Sky"),
    (date(2027, 3, 10), "Musée Ghibli (Mitaka)"),
    # (date(2027, 4, 20), "confirmer la réservation resto"),
]

EXAM = [
    (date(2026, 8, 19), "Examen d'aless : Irlande"),
    (date(2026, 8, 19), "Examen d'aless : Histoire"),
    (date(2026, 8, 21), "Examen d'aless : Stage"),
]


# ─────────────────────────────────────────────
# DISCORD
# ─────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="$",
    intents=intents
)


# ─────────────────────────────────────────────
# CALCUL DU NOMBRE DE JOURS
# ─────────────────────────────────────────────

def jours_restants():
    maintenant = datetime.now(ZONE)
    delta = CIBLE - maintenant

    return delta.days


# ─────────────────────────────────────────────
# CONSTRUCTION DES RAPPELS
# ─────────────────────────────────────────────

def texte_rappels(events):
    """
    Construit le bloc de rappels encore valides.
    Retourne une chaîne vide s'il n'y a aucun rappel.
    """

    aujourdhui = datetime.now(ZONE).date()
    lignes = []

    for date_limite, quoi in events:

        jours = (date_limite - aujourdhui).days

        # Date passée → on ne l'affiche plus
        if jours < 0:
            continue

        jour_txt = "jour" if jours in (0, 1) else "jours"
        d = date_limite.strftime("%d/%m")

        if jours == 0:
            lignes.append(
                f"⚠️ Rappel : **aujourd'hui** ({d}) pour {quoi}"
            )
        else:
            lignes.append(
                f"Rappel : **{jours} {jour_txt}** avant le {d} pour {quoi}"
            )

    if not lignes:
        return ""

    separateur = "\n-----------------------------------------------\n"

    return separateur + "\n".join(lignes)


# ─────────────────────────────────────────────
# IMAGE ALÉATOIRE
# ─────────────────────────────────────────────

def image_aleatoire():
    """
    Retourne une image Discord au hasard.
    Retourne None si aucune image n'est disponible.
    """

    if not os.path.isdir(DOSSIER_IMGS):
        print(f"Dossier '{DOSSIER_IMGS}' introuvable.")
        return None

    fichiers = [
        f
        for f in os.listdir(DOSSIER_IMGS)
        if f.lower().endswith(EXT_IMAGES)
    ]

    if not fichiers:
        print(f"Aucune image dans '{DOSSIER_IMGS}'.")
        return None

    choix = random.choice(fichiers)

    return discord.File(
        os.path.join(DOSSIER_IMGS, choix)
    )


# ─────────────────────────────────────────────
# ENVOI DU MESSAGE
# ─────────────────────────────────────────────

async def envoyer_message(channel):
    """
    Construit et envoie le message du compte à rebours.
    Cette fonction est utilisée :
    - par l'envoi automatique quotidien
    - par la commande $japon
    """

    jours = jours_restants()

    # ─── Compte à rebours ─────────────────────

    if jours > 1:

        texte = (
            f"⏳ Plus que **{jours} jours** "
            f"avant le 25 avril 2027 !"
        )

    elif jours == 1:

        texte = (
            "⏳ Plus qu'**1 jour** "
            "avant le 25 avril 2027 !"
        )

    elif jours == 0:

        texte = (
            "🎉 C'est aujourd'hui : "
            "**25 avril 2027** !"
        )

    else:

        # Le voyage est passé
        return


    # ─── Rappels Japon ─────────────────────────

    texte += texte_rappels(RAPPELS)


    # ─── Examens ───────────────────────────────

    texte += texte_rappels(EXAM)


    # ─── Image ─────────────────────────────────

    image = image_aleatoire()


    # ─── Envoi ─────────────────────────────────

    if image is not None:

        await channel.send(
            content=texte,
            file=image
        )

    else:

        await channel.send(
            content=texte
        )


# ─────────────────────────────────────────────
# ENVOI AUTOMATIQUE À 11H14
# ─────────────────────────────────────────────

@tasks.loop(time=HEURE_ENVOI)
async def envoi_quotidien():

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:

        print(
            "Channel introuvable — "
            "vérifie CHANNEL_ID."
        )

        return

    await envoyer_message(channel)


# ─────────────────────────────────────────────
# COMMANDE $japon
# ─────────────────────────────────────────────

@bot.command()
async def japon(ctx):

    await envoyer_message(ctx.channel)


# ─────────────────────────────────────────────
# BOT PRÊT
# ─────────────────────────────────────────────

@bot.event
async def on_ready():

    print(
        f"Connecté en tant que "
        f"{bot.user}"
    )

    if not envoi_quotidien.is_running():

        envoi_quotidien.start()

        print(
            "Envoi quotidien activé "
            f"à {HEURE_ENVOI.strftime('%H:%M')}."
        )


# ─────────────────────────────────────────────
# LANCEMENT DU BOT
# ─────────────────────────────────────────────

bot.run(TOKEN)
