from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply)

from Aplicacion.BaseDatos.GestorBBDD import GestorBBDD
from Aplicacion.ClasesBase.BusquedaWallapop import BusquedaWallapop
from Aplicacion.ClasesBase.ExclusionesBusqueda import ExclusionesBusqueda
from Aplicacion.ClasesBase.Usuario import Usuario
#from Aplicacion.Scraper.ScraperWallapop import BotScraperWallapop
from Aplicacion.Scraper.TestCredenciales import TestCredenciales


class BorrarBusquedaHandler():
    def __init__(self):

        # Declaración de estados
        self.STATUS1 = range(1)

        self.handler = ConversationHandler(
            entry_points=[CommandHandler(
                'borrar_busqueda', self.borrar_busqueda)],
            states={
                self.STATUS1: [MessageHandler(~Filters.command, self.borrar_busqueda_uno)],
            },

            fallbacks=[CommandHandler(
                'cancelar_borrar_busqueda', self.cancelar_borrar_busqueda)]
        )




    def borrar_busqueda(self, update, context):
        gestorBBDD = GestorBBDD()
        id_telegram = update.message.from_user.id
        opciones = []
        if(gestorBBDD.existeUsuario(id_telegram)):
            print(f"[TELEGRAM] Usuario {id_telegram} quiere borrar búsquedas. ")
            try:
                busquedas = gestorBBDD.recuperarBusquedasUsuario(id_telegram)

                if(len(busquedas) > 0):
                    texto = "¿Qué busqueda quieres borrar?"
                    contador = 1
                    for busqueda in busquedas:
                        texto+=f"\n[{contador}] - {busqueda.keywords} [{busqueda.precio_min},{busqueda.precio_max}]"
                        opciones.append([f"Borrar {contador}"])
                        contador+=1
                    texto+=f"\n Utiliza /cancelar_borrar_busqueda para cancelar el borrado. "
                    keyboard = ReplyKeyboardMarkup(opciones, one_time_keyboard=True)
                    update.message.reply_text(texto, reply_markup=keyboard)
                    return self.STATUS1
                else:
                    update.message.reply_text("No tienes ninguna búsqueda guardada.")
            except:
                update.message.reply_text("No tienes ninguna búsqueda guardada.")

        else:
            update.message.reply_text("No estás registrado. Escribe /registrarse. ")
        return ConversationHandler.END




    def borrar_busqueda_uno(self, update, context):
        # Extraigo el nº de búsqueda a borrar
        numero_busqueda_a_borrar = int(update.message.text.split(" ")[-1])
        id_telegram = update.message.from_user.id
        gestor = GestorBBDD()
        try:
            busqueda =  gestor.recuperarBusquedasUsuario(id_telegram)[numero_busqueda_a_borrar-1]
            id_busqueda = busqueda.id_busqueda
            if(gestor.existeBusqueda(id_busqueda)):
                gestor.borrarBusqueda(id_busqueda)
                print(f"[TELEGRAM] Búsqueda {id_busqueda} del usuario {id_telegram} borrada. ")
                update.message.reply_text(f"¡Busqueda '{busqueda.keywords}' borrada!")
                return ConversationHandler.END
            else:
                update.message.reply_text(f"Error, búsqueda no encontrada en la base de datos. ")
                return ConversationHandler.END
        except:
            update.message.reply_text(f"Error, búsqueda no encontrada en la base de datos. ")
            return ConversationHandler.END



    def cancelar_borrar_busqueda(self, update, context):
        update.message.reply_text(
            'Borrado de búsqueda cancelado.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END



