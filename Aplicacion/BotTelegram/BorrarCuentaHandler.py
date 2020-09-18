from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply)

from Aplicacion.BaseDatos.GestorBBDD import GestorBBDD


class BorrarCuentaHandler():
    def __init__(self):
        # Declaración de estados
        self.STATUS1 = range(1)

        self.handler = ConversationHandler(
            entry_points=[CommandHandler(
                'borrar_cuenta', self.borrar_cuenta)],
            states={
                self.STATUS1: [MessageHandler(~Filters.command, self.confirmar_borrar_cuenta)],
            },
            fallbacks=[CommandHandler(
                'cancelar_borrar_cuenta', self.cancelar_borrar_cuenta)]
        )

    def borrar_cuenta(self, update, context):
        gestorBBDD = GestorBBDD()
        id_telegram = update.message.from_user.id
        print(f"[TELEGRAM] Usuario {id_telegram} va a borrar su cuenta. ")
        if(gestorBBDD.existeUsuario(id_telegram)):
            texto = "Se borrará tu cuenta y todas las búsquedas y artículos guardados asociados. Esta acción no se puede deshacer. ¿Estás seguro de que quieres continuar?"
            reply_keyboard = [["Si"],["No"]]
            keyboard = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            update.message.reply_text(texto, reply_markup = keyboard)
            return self.STATUS1
        else:
            update.message.reply_text("Debes haberte registrado para poder borrar tu cuenta.")
            return ConversationHandler.END

    def confirmar_borrar_cuenta(self, update, context):
        parametro = update.message.text.lower()
        gestorBBDD = GestorBBDD()
        id_telegram = update.message.from_user.id
        if(parametro == "si"):
            # Primero borro búsquedas y articulos contenidos
            busquedas = gestorBBDD.recuperarBusquedasUsuario(id_telegram)
            for busqueda in busquedas:
                gestorBBDD.borrarBusqueda(busqueda.id_busqueda)
            # Después, borro al usuario
            gestorBBDD.borrarUsuario(id_telegram)
            self.limpiar_datos(context)
            update.message.reply_text(f"Cuenta borrada.")
            print(f"[TELEGRAM] Usuario {id_telegram} borra su cuenta y búsquedas asociadas. ")
            return ConversationHandler.END
        else:
            update.message.reply_text("Borrado de cuenta cancelado. ")
            return ConversationHandler.END



    def cancelar_borrar_cuenta(self, update, context):
        self.limpiar_datos(context)
        id_telegram = update.message.from_user.id
        print(f"[TELEGRAM] Usuario {id_telegram} cancela el borrado de su cuenta. ")
        update.message.reply_text(
            'Borrado cancelado. ', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


    def limpiar_datos(self, context):
        context.user_data["tiene_cuenta"] = False
        context.user_data["email"] = ""
        context.user_data["pass_wallapop"] = ""
        context.user_data["mensaje_wallapop"] = ""
        context.user_data["codigo_postal"] = ""

"pip install selenium"
"pip install webdriver_manager"
"pip install pyhon-telegram-bot --upgrade"