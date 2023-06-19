import os
import discord
import handler
from quickchart import QuickChart
import ast
import random

from discord.ui import Button , View

TOKEN = os.environ.get('DISCORD_TOKEN')
bot = discord.Bot()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Capitaliser"))
    print('Logged on as {0}!'.format(bot.user))

bot.load_extension('mechanics')
bot.load_extension('Cogs.Other.CogMission')

@bot.slash_command(name="aide",description="Obtenir de l'aide à propos des différentes commandes disponibles")
async def aide(ctx):   
    embed = discord.Embed(color=0x79c6c6, title="🌐 Page d'aide aux commandes")
    embed.add_field(name="**🏛 Bourse**", value="`/bourse` - Affiche les valeurs des différentes agences.\n`/acheter` - Achète des parts d'une agence donnée.\n`/vendre` - Vend des parts d'une agence donnée.\n`/actionnaires` - Affiche les actionnaires d'une agence.\n`/topagences` - Affiche les 5 agences les mieux côtées.\n`/setup` - Fait côter en bourse une agence.\n`/topbourse` - Affiche les cours des trois agences les mieux côtées.",inline = False)
    embed.add_field(name="**💵 Economie**", value="`/solde` - Affiche votre solde bancaire\n`/virement` - Vire de l'argent à quelqu'un\n`/topargent` - Affiche les 5 membres les plus riches.\n`/depot` - Dépose de l'argent dans le compte de votre agence.\n`/retrait` - Retire de l'argent de votre compte d'agence.", inline=False)
    embed.add_field(name="**🚀 Missions**", value="`/lancement` - Effectue le lancement d'une mission spatiale.\n`/mission` - Calcule le prix et lance une mission spatiale.")
    embed.add_field(name="**📚 Divers**", value="`/aide` - Affiche cette page d'aide aux commandes.")
    await ctx.respond(embed=embed)

@bot.slash_command(name="bourse", description="Afficher le cours d'une agence")
async def embed(ctx, ticker: discord.Option(str, required=True)):
    embed = discord.Embed(color=0x79c6c6, title=f"Cotation de {ticker.upper()}")
    value = float(list(handler.getAgencyValue(ticker.upper())[0])[0])
    embed.add_field(name="Valeur actuelle", value=f"`{'{:,}'.format(value).replace(',', ' ')} EUR`", inline=True)
    v = handler.getAgencyPastValues(ticker.upper())[0][0]
    v = ast.literal_eval(v)
    v0 = float(v[-2])
    v1 = float(v[-1])
    percent = round(((v1-v0)/v0)*100, 2)
    if percent>=0:
        sign = "+"
        emoji = "📈"
    elif percent<0:
        sign = ""
        emoji = "📉"
    embed.add_field(name=f"{emoji} Variations 24h", value=f"`{sign}{percent}%`", inline=True)
    v0 = float(v[0])
    v1 = float(v[-1])
    percent = round(((v1-v0)/v0)*100, 2)
    if percent>=0:
        sign = "+"
        emoji = "📈"
    elif percent<0:
        sign = ""
        emoji = "📉"
    embed.add_field(name=f"{emoji} Variations 7j", value=f"`{sign}{percent}%`", inline=True)
    qc = QuickChart()
    qc.width = 500
    qc.height = 300
    qc.background_color = "rgba(47,48,54,255)"
    qc.config = """{
        type: 'line',
        data:{
            labels: ['J-7', 'J-6', 'J-5', 'J-4', 'J-3', 'J-2', 'J-1' ],
            datasets: [{
                label: 'Valeur',
                data: """ + str(list(handler.getAgencyPastValues(ticker.upper())[0])[0]) + """,
                lineTension: 0.4
            }]
        },
        options: {
            legend: {
                display:false
            }
        }
    }
    """
    embed.add_field(name="Parts en ciruclation", value=int(float(handler.getAgencyParts(ticker.upper())[1])), inline=True)
    embed.set_image(url=qc.get_url())
    await ctx.respond(embed=embed)

@bot.slash_command(name="solde", description="Afficher votre solde bancaire actuel")
async def solde(ctx):
    embed = discord.Embed(color=0x79c6c6, title=f"💰 Solde bancaire de {ctx.author.name}")
    money = handler.getUserBalance(ctx.author.id)
    if money:
        amount = handler.getUserBalance(ctx.author.id)
        embed.add_field(name="Compte courant", value=f"`{round(float('{:,}'.format(amount).replace(',', ' ')),2)} EUR`")
        acquisitions = handler.getAcquisitions(ctx.author.id)
        actions = ""
        for each in acquisitions:
            if int(each[2]) != 0:
                actions = actions + f"`{each[1]}` - `{each[2]} parts`\n"
        embed.add_field(name="Portefeuille en actions", value=actions)
    else:
        handler.createAccount(ctx.author.id)
        embed = discord.Embed(color=0x79c6c6, title="💰 Compte bancaire créée", description="Votre compte bancaire est désormais ouvert. Vous pouvez dès maintenant consulter votre solde.")
    await ctx.respond(embed=embed)

@bot.slash_command(name="virement", description="Virer de l'argent à la personne de votre choix.")
async def virement(ctx, montant: discord.Option(int, required=True), destinataire: discord.Option(str, required=True), raison: discord.Option(str, required=False)):
    destinataire = destinataire[2:-1]
    if float(handler.getUserBalance(ctx.author.id))<float(montant):
        embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Solde insuffisant", description="Vous n'avez pas le solde suffisant pour procéder à cette opération.")
    else:
        embed = discord.Embed(color=0x79c6c6, title=f"💸 Virement effectué", description=f"Vous avez envoyé {montant} EUR à <@{destinataire}>\n")
        if raison is not None:
            embed.add_field(name="Raison", value=f"{raison}")
        hasAccount = handler.getUserAccount(destinataire)
        if hasAccount:
            handler.transferMoney(ctx.author.id, destinataire, montant)
        else:
            handler.createAccount(destinataire)
            handler.transferMoney(ctx.author.id, destinataire, montant)

    await ctx.respond(embed=embed)

@bot.slash_command(name="setup", description="Faire côter votre agence en bourse")
async def setup(ctx, nom: discord.Option(str, required=True), ticker: discord.Option(str, required=True)):
    if float(handler.getUserBalance(ctx.author.id))>1000.0:
        if len(ticker) == 3:
            embed = discord.Embed(color=0x79c6c6, title="✅ Agence introduite en bourse", description=f"1000 EUR ont été déduits de votre compte bancaire.\nL'agence `{nom}` est désormais côtée en bourse sous le ticker `{ticker}`")
            handler.createAgency(ctx.author.id, nom.upper(), ticker.upper(), 1000)
        else:
            embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Ticker invalide", description="Le ticker saisi est invalide. Un ticker doit faire 3 caractères et représentra votre agence à l'avenir sur les marchés boursiers.")
    else:
        embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Solde insuffisant", description="Vous n'avez pas le solde suffisant pour procéder à cette opération.")
    await ctx.respond(embed=embed)

@bot.slash_command(name="topagences", description="Afficher les agences les plus côtées dans le monde")
async def topagences(ctx):
    embed = discord.Embed(color=0x79c6c6, title="💰 Agences les mieux côtées")
    agtop = list(handler.getAgtop())
    
    for n in range(len(agtop)):
        if n == 5: break
        money = float(list(agtop)[n][0])
        embed.add_field(name = "", value=f"`#{n+1}` `{str(list(agtop)[n][1]).upper()}` - `{'{:,}'.format(money).replace(',', ' ')} EUR`", inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(name="topargent", description="Afficher les joueurs les plus riches du monde.")
async def topargent(ctx):
    embed = discord.Embed(color=0x79c6c6, title="💰 Joueurs les plus riches")
    baltop = list(handler.getBaltop())
    
    for n in range(len(baltop)):
        if n == 5: break
        money = float(list(baltop)[n][0])
        usermention = "<@" + str(list(baltop)[n][1]) + ">"
        embed.add_field(name = "", value=f"`#{n+1}` {usermention} - `{'{:,}'.format(money).replace(',', ' ')} EUR`", inline=False)
    await ctx.respond(embed=embed)

@bot.slash_command(name="acheter", description="Acheter des parts d'agences.")
async def acheter(ctx, ticker: discord.Option(str, required=True), parts: discord.Option(int, required=True)):
    if handler.getUserBalance(ctx.author.id)>float(handler.getAgencyParts(ticker.upper())[0])/float(handler.getAgencyParts(ticker.upper())[1])*parts:
        if float(handler.getAgencyParts(ticker.upper())[1])>=float(parts):
            unitPrice = round(float(handler.getAgencyParts(ticker.upper())[0]), 2) #/float(handler.getAgencyParts(ticker.upper())[1])
            totalCost = round(parts*unitPrice, 2)
            totalCost = round(totalCost * 1.01, 2)
            fees = round(0.01*totalCost, 2)
            
            handler.refreshPartsBuy(ticker, parts)
            #handler.refreshAgencyValueBuy(ticker, totalCost-fees)
            handler.refreshBalanceBuy(ctx.author.id, totalCost-fees)
            handler.refreshPortfolioBuy(ctx.author.id, parts, ticker)
            embed=discord.Embed(color=0x79c6c6, title="📊 Achat d'actions", description=f"Agence : `{ticker.upper()}`\nNombre de parts : `{parts}`\nPrix unitaire : `{unitPrice} EUR`\nFrais (1%) : `{fees} EUR`\nCoût total : `{totalCost} EUR`")
        else:
            embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Nombre de parts insuffisant", description="Il n'y a pas assez de parts sur le marché pour procéder à cette opération.") 
    else:
        embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Solde insuffisant", description="Vous n'avez pas le solde suffisant pour procéder à cette opération.")
    await ctx.respond(embed=embed)

@bot.slash_command(name="vendre", description="Vendre des parts d'une agence")
async def vendre(ctx, ticker: discord.Option(str, required=True), parts: discord.Option(int, required=True)):
    userParts = handler.getUserParts(ctx.author.id, ticker.upper())
    if int(str(userParts[0][0])) >= parts:
        unitPrice = round(float(handler.getAgencyParts(ticker.upper())[0]), 2)
        totalCost = round(parts*unitPrice, 2)
        totalCost = round(totalCost * 0.99, 2)
        fees = round(0.01*totalCost, 2)
        
        handler.refreshPartsSell(ticker, parts)
        #handler.refreshAgencyValueSell(ticker, totalCost-fees)
        handler.refreshBalanceSell(ctx.author.id, totalCost-fees)
        handler.refreshPortfolioSell(ctx.author.id, parts, ticker)
        embed=discord.Embed(title="📊 Vente d'actions", description=f"Agence : `{ticker.upper()}`\nNombre de parts : `{parts}`\nFrais (1%) : `{fees} EUR`\nSomme totale retirée : `{totalCost} EUR`")
    else:
        embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Nombre de parts insuffisant", description="Vous n'avez pas assez de parts dans l'agence pour procéder à cette opération.")
    await ctx.respond(embed=embed)

@bot.slash_command(name="actionnaires", description="Lister les actionnaires d'une agence.")
async def actionnaires(ctx, ticker: discord.Option(str, required=True)):
    embed = discord.Embed(color=0x79c6c6, title=f"📊 Actionnaires de l'agence `{ticker.upper()}`")
    owners = handler.getOwners(ticker)
    actions = ""
    partslibres = 100
    for each in owners:
        partslibres = partslibres - int(each[2])
        actions = actions + f"<@{each[0]}> - `{each[2]}%`\n"
    if actions == "":
        actions = "Pas d'actionnaires pour l'instant."
    embed.add_field(name=f"{partslibres} parts libres", value=actions)
    await ctx.respond(embed=embed)

@bot.slash_command(name="topbourse", description="Afficher les courbes boursières des 3 meilleures agences.")
async def topbourse(ctx):
    embed = discord.Embed(color=0x79c6c6, title="📊 Indice boursier international")
    
    agenciesInfo = handler.getAllAgenciesValues()
    allTickers = []
    allPastValues = []
    for n in agenciesInfo:
        allTickers.append(n[1])
        allPastValues.append(n[3])
    qc = QuickChart()
    qc.width = 500
    qc.height = 300
    qc.background_color = "rgba(47,48,54,255)"
    qc.config = """{
        type: 'line',
        data:{
            labels: ['J-7', 'J-6', 'J-5', 'J-4', 'J-3', 'J-2', 'J-1' ],
            datasets: [{
                label: '""" + str(allTickers[0]) + """',
                data: """ + str(ast.literal_eval(allPastValues[0])) + """,
                lineTension: 0.4,
                fill: false
            },
            {
                label: '""" + str(allTickers[1]) + """',
                data: """ + str(ast.literal_eval(allPastValues[1])) + """,
                lineTension: 0.4,
                fill: false
            },
            {
                label: '""" + str(allTickers[2]) + """',
                data: """ + str(ast.literal_eval(allPastValues[2])) + """,
                lineTension: 0.4,
                fill: false
            }]
        },
        options: {
            
        }
    }
    """
    embed.set_image(url=qc.get_url())
    await ctx.respond(embed=embed)

@bot.slash_command(name="soldeagence", description="Afficher le solde du compte de votre agence")
async def soldeagence(ctx):
    isUserAgencyChief = handler.isUserChief(ctx.author.id)[0]
    if isUserAgencyChief:
        agency = isUserAgencyChief[2]
        money = isUserAgencyChief[4]
        embed = discord.Embed(color=0x79c6c6, title=f"💰 Solde bancaire de l'agence {agency}", description=f"`{money} EUR`")
    else:
        embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Erreur de grade", description="Vous n'êtes le chef d'aucune agence spatiale.")
    await ctx.respond(embed=embed)

@bot.slash_command(name="depot", description="Déposer de l'argent dans le compte de votre agence.")
async def depot(ctx, montant: discord.Option(float, required=True)):
    isUserAgencyChief = handler.isUserChief(ctx.author.id)[0]
    if isUserAgencyChief:
        if float(handler.getUserBalance(ctx.author.id))>montant:
            ticker = handler.isUserChief(ctx.author.id)[0][2]
            money = float(handler.isUserChief(ctx.author.id)[0][4])+montant
            handler.updateAgencyBalance(ticker, money)
            embed = discord.Embed(color=0x79c6c6, title=f"💸 Dépôt effectué", description=f"Vous avez déposé `{montant} EUR` sur le compte de l'agence `{ticker}`")
        else:
            embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Solde insuffisant", description="Vous ne disposez pas du solde requis pour procéder à cette opération.")
    else:
        embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Erreur de grade", description="Vous n'êtes le chef d'aucune agence spatiale.")
    await ctx.respond(embed=embed)

@bot.slash_command(name="retrait", description="Retirer de l'argent du compte de votre agence.")
async def retrait(ctx, montant: discord.Option(float, required=True)):
    isUserAgencyChief = handler.isUserChief(ctx.author.id)[0]
    if isUserAgencyChief:
        if float(handler.isUserChief(ctx.author.id)[0][4])>montant:
            ticker = handler.isUserChief(ctx.author.id)[0][2]
            money = float(handler.isUserChief(ctx.author.id)[0][4])-montant
            handler.updateAgencyBalance(ticker, money)
            embed = discord.Embed(color=0x79c6c6, title=f"💸 Retrait effectué", description=f"Vous avez retiré `{montant} EUR` sur le compte de l'agence `{ticker}`")
        else:
            embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Solde insuffisant", description="Votre agence ne dispose pas du solde requis pour procéder à cette opération.")
    else:
        embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Erreur de grade", description="Vous n'êtes le chef d'aucune agence spatiale.")
    await ctx.respond(embed=embed)

@bot.slash_command(name="lancement", description="Lancer une mission spatiale.")
async def lancement(ctx, lieu: discord.Option(str, required=True), carburant: discord.Option(str, required=True)):
    """
    Effectue le lancement d'une mission spatiale en prenant en compte la météo du lieu de lancement ainsi que le carburant de l'engin.

    :param lieu: (str) lieu du lancement
    :param carburant: (str) carburant de la fusée
    """
    weather = {"☀️ Ensoleillé":0.0,"☁️ Nuageux":0.0, "🌧️ Pluvieux":0.25, "🍃 Grand vent":0.10, "⚡ Orageux":0.75, "🌨️ Neigeux":0.80, "💨 Tempête":0.95, "🌪️ Ouragan":0.90} #float = chances d'échec
    actualWeather, actualFailProbability = random.choice(list(weather.items()))

    class YesNoButtons(discord.ui.View):

        @discord.ui.button(label="Oui", style=discord.ButtonStyle.success, emoji="🚀")
        async def yesbutton_callback(self, button, interaction):
            if random.random()>actualFailProbability:
                embed = discord.Embed(color=0x2c7ef2, title="✅ Lancement réussi", description="La météo s'est éclaircie en dernière minute, le lancement a réussi !")
            else:
                embed = discord.Embed(color=0xb02c3a, title=f"⛔️ Météo capricieuse", description="Malheureusement, la météo a été capricieuse aujourd'hui et le lancement a échoué. La fusée est irrécupérable.")
            await interaction.response.edit_message(embed=embed, view=None)

        @discord.ui.button(label="Non", style=discord.ButtonStyle.danger, emoji="❎")
        async def nobutton_callback(self, button, interaction):
            embed = discord.Embed(color=0xb02c3a, title="⛔️ Lancement annulé")
            await interaction.response.edit_message(embed=embed, view=None)

    embed = discord.Embed(color=0x2c7ef2, title="📌 Météo actuelle", description=f"La météo du moment sur votre pas de tir est : `{actualWeather}`\nSouhaitez-vous continuer ?")
    await ctx.respond(embed=embed, view=YesNoButtons())

bot.run(TOKEN)