from Aplicacion.BaseDatos.GestorBBDD import GestorBBDD
from Aplicacion.BotTelegram.AddBusquedaHandler import AddBusquedaHandler
from Aplicacion.BotTelegram.BorrarBusquedaHandler import BorrarBusquedaHandler
from Aplicacion.BotTelegram.BorrarCuentaHandler import BorrarCuentaHandler
from Aplicacion.BotTelegram.RegistroHandler import RegistroHandler
from Aplicacion.BotTelegram.WallascraperBot import Wallascraper

TOKEN = "AÑADE TU TOKEN AQUI"

if __name__ == "__main__":
    # Creo handlers de conversaciones
    registroHandler = RegistroHandler()
    borrarCuentaHandler = BorrarCuentaHandler()
    addBusquedaHandler = AddBusquedaHandler()
    borrarBusquedaHandler = BorrarBusquedaHandler()

    # Creo bot
    bot = Wallascraper(TOKEN)

    # Añado handlers
    bot.addHandler(registroHandler.handler)
    bot.addHandler(addBusquedaHandler.handler)
    bot.addHandler(borrarBusquedaHandler.handler)
    bot.addHandler(borrarCuentaHandler.handler)

    # Lo pongo a correr en IDLE
    bot.run()
