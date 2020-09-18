from telegram.ext import (Updater, CommandHandler)

from Aplicacion.BotTelegram.Notificador import Notificador

from Aplicacion.BaseDatos.GestorBBDD import GestorBBDD
from Aplicacion.Scraper.ScraperWallapop import ScraperWallapop
from Aplicacion.Scraper.TareaPeriodica import TareaPeriodica

class Wallascraper():
    def __init__(self, TOKEN):
        self.TOKEN = TOKEN
        self.handlers = [CommandHandler('start', self.start),
                         CommandHandler('iniciar', self.iniciar),
                         CommandHandler('ayuda', self.ayuda),
                         CommandHandler('detener', self.detener)]
        self.updater = Updater(self.TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.diccionario_scrapers = {}

    def addHandler(self, handler):
        self.handlers.append(handler)

    def start(self, update, context):
        id_telegram = update.message.from_user.id
        nombre_usuario = update.message.from_user.username
        print(f"[TELEGRAM] Usuario {id_telegram} lanza /start. ")
        gestorBBDD = GestorBBDD()
        context.user_data["tiene_cuenta"] = gestorBBDD.existeUsuario(update.message.from_user.id)
        context.user_data["email"] = ""
        context.user_data["password"] = ""
        context.user_data["mensaje"] = ""
        context.user_data["codigo_postal"] = ""
        bienvenida = f'¡Hola {nombre_usuario}! Soy un bot para actualizarte con los nuevos anuncios que se suban en Wallapop. Utiliza /ayuda para ver los comandos disponibles.'
        update.message.reply_text(bienvenida)

    def ayuda(self, update, context):
        texto = "Están disponibles los siguientes comandos: \n"
        texto += "- Utiliza /registrarse para registrarte con el bot. Puedes añadir tu cuenta de wallapop o solamente tu código postal.\n\n"
        texto += "- Utiliza /borrar_cuenta para borrar la cuenta que hayas registrado en el bot. Después puedes registrarte de nuevo.\n\n"
        texto += "- Utiliza /add_busqueda para añadir una búsqueda, una vez te hayas registrado.\n"
        texto += "- Utiliza /borrar_busqueda para ver y poder borrar una búsqueda que hayas introducido previamente.\n\n"
        texto += "- Utiliza /iniciar para iniciar el scrapeo de tus búsquedas.\n\n"
        texto += "- Utiliza /detener para detener el scrapeo previamente iniciado. \n\n"
        update.message.reply_text(texto)


    def iniciar(self, update, context):
        id_telegram = update.message.from_user.id
        print(f"[TELEGRAM] Usuario {id_telegram} lanza /iniciar. ")
        gestorBBDD = GestorBBDD()
        if(gestorBBDD.existeUsuario(id_telegram) and len(gestorBBDD.recuperarBusquedasUsuario(id_telegram)) > 0):
            if(self.diccionario_scrapers.get(id_telegram) == None):
                usuario = gestorBBDD.recuperarUsuario(id_telegram)
                busquedas_usuario = gestorBBDD.recuperarBusquedasUsuario(id_telegram)
                for busqueda in busquedas_usuario:
                    # Si está activada la autocomparación, borro artículos anteriores
                    # y relleno con los nuevos desde scraperwallapop, de forma que
                    # solo se van comparando los artículos nuevos subidos.
                    if(busqueda.comparar_automaticamente == True):
                        print(f"[TELEGRAM] Borro artículos previos de la búsqueda {busqueda.keywords} del usuario {id_telegram} porque tiene autocomparación. ")
                        gestorBBDD.borrarArticulosBusqueda(busqueda.id_busqueda)

                notificador = Notificador(self.TOKEN)
                tarea = TareaPeriodica(10, ScraperWallapop, usuario, notificador, ejecucion_en_background=False)
                update.message.reply_text("Iniciando scrapeo. ")
                self.diccionario_scrapers[id_telegram] = tarea
                tarea.start()
            else:
                update.message.reply_text("Ya se está scrapeando, utiliza /detener para detener el scrapeo.")

        else:
            update.message.reply_text("Debes tener una cuenta y al menos una búsqueda para iniciar el scrapeo. ")

    def detener(self, update, context):
        id_telegram = update.message.from_user.id
        try:
            print(f"[TELEGRAM] Usuario {id_telegram} lanza /detener. ")
            tarea = self.diccionario_scrapers.pop(id_telegram)
            update.message.reply_text("Deteniendo scrapeo. ")
            tarea.stop()
        except:
            update.message.reply_text("No hay ningún scrapeo corriendo en este momento. ")


    def run(self):
        print(f"[TELEGRAM] Iniciando bot. ")

        for handler in self.handlers:
            print(f"[TELEGRAM] Añado handler. ")
            self.dispatcher.add_handler(handler)

        # Lanzo el bot
        self.updater.start_polling()
        print("[TELEGRAM] Lanzo bot.")

        # Lo dejo en idle
        print("[TELEGRAM] Se queda en idle. ")
        self.updater.idle()


