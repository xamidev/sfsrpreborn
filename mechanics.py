from discord.ext import tasks, commands
import handler
import ast

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=30.0) # 1 day
    async def printer(self):

        agenciesBalances = handler.getAgenciesBalances()
        agenciesPastValues = handler.getAgenciesStockExchangeInfo()
        for agency, each in zip(agenciesBalances, agenciesPastValues):

            defaultValue = 50.0
            vault = float(agency[4])
            availparts = int(each[4])

            #print(each[3])
            if each[3] is None:
                pastValues=[defaultValue, defaultValue, defaultValue, defaultValue, defaultValue, defaultValue, defaultValue]
            else:
                pastValues = ast.literal_eval(each[3])
            #print(pastValues)
            if availparts == 0:
                stockExchangeValue = (vault*10) #to be redefined
            else: stockExchangeValue = (vault*10)/availparts
                
            #print(vault)
            #print(stockExchangeValue)
            #print(pastValues)

            pastValues.pop(0)
            #print(pastValues)
            pastValues.append(str(round(stockExchangeValue,2)))
            #print(pastValues)
            handler.updatePastValues(str(agency[2]), str(pastValues), round(stockExchangeValue,2))
            print("Agencies values refreshed!")
def setup(bot):
    bot.add_cog(MyCog(bot))