from Aplicacion.BaseDatos.GestorBBDD import GestorBBDD
from Aplicacion.BotTelegram.AddBusquedaHandler import AddBusquedaHandler
from Aplicacion.BotTelegram.BorrarBusquedaHandler import BorrarBusquedaHandler
from Aplicacion.BotTelegram.BorrarCuentaHandler import BorrarCuentaHandler
from Aplicacion.BotTelegram.RegistroHandler import RegistroHandler
from Aplicacion.BotTelegram.WallascraperBot import Wallascraper

TOKEN = "INSERTA TU TOKEN AQUÍ"

if __name__ == "__main__":
    gestorBBDD = GestorBBDD()
    registroHandler = RegistroHandler()
    borrarCuentaHandler = BorrarCuentaHandler()
    addBusquedaHandler = AddBusquedaHandler()
    borrarBusquedaHandler = BorrarBusquedaHandler()
    bot = Wallascraper(TOKEN)
    bot.addHandler(registroHandler.handler)
    bot.addHandler(addBusquedaHandler.handler)
    bot.addHandler(borrarBusquedaHandler.handler)
    bot.addHandler(borrarCuentaHandler.handler)
    bot.run()
