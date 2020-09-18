from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply)

from Aplicacion.BaseDatos.GestorBBDD import GestorBBDD
from Aplicacion.ClasesBase.Usuario import Usuario
from Aplicacion.Scraper.TestCredenciales import TestCredenciales


class RegistroHandler():
    def __init__(self):

        # Declaración de estados
        self.STATUS1, self.STATUS2, self.STATUS3, self.STATUS4,\
        self.STATUS5, self.STATUS6 = range(6)

        self.handler = ConversationHandler(
            entry_points=[CommandHandler(
                'registrarse', self.iniciar_registro)],
            states={
                self.STATUS1: [MessageHandler(~Filters.command, self.recoge_codigo_pregunta_cuenta)],
                self.STATUS2: [MessageHandler(~Filters.command, self.recoge_cuenta_pide_mail_o_cp)],
                self.STATUS3: [MessageHandler(~Filters.command, self.recoge_mail_pide_password)],
                self.STATUS4: [MessageHandler(~Filters.command, self.recoge_password_pide_mensaje)],
                self.STATUS5: [MessageHandler(~Filters.command, self.recoge_mensaje_pide_codigo_postal)],
                self.STATUS6: [MessageHandler(~Filters.command, self.recoge_codigo_postal_probar_credenciales)],
            },

            fallbacks=[CommandHandler(
                'cancelar_registro', self.cancelar_registro)]
        )

    def iniciar_registro(self, update, context):
        # Si ya tiene cuenta, no dejo que se registre.
        gestorBBDD = GestorBBDD()
        id_telegram = update.message.from_user.id
        if(gestorBBDD.existeUsuario(id_telegram)):
            update.message.reply_text("Ya tienes una cuenta, no puedes añadir otra. Puedes borrar la previamente introducida con /borrar_cuenta. ")
            return ConversationHandler.END
        # Si no, pido código de invitación.
        else:
            print(f"[TELEGRAM] usuario {id_telegram} empieza a registrarse.")
            update.message.reply_text("Introduce código de invitación o usa /cancelar_registro en cualquier momento para cancelar el registro: ", reply_markup=ForceReply())
            return self.STATUS1

    def recoge_codigo_pregunta_cuenta(self, update, context):
        condigo_invitacion = update.message.text
        if(condigo_invitacion.lower() == "gii_uah"):
            id_telegram = update.message.from_user.id
            print(f"[TELEGRAM] Usuario {id_telegram} mete el código.")
            reply_keyboard = [['Añadir cuenta', 'No añadir cuenta']]
            texto = "Código valido. ¿Quieres utilizar tu cuenta de wallapop para enviar mensajes automáticamente, o no introducirla y sólamente ser notificado de los nuevos anuncios?: "
            update.message.reply_text(texto, reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True))
            return self.STATUS2
        else:
            id_telegram = update.message.from_user.id
            update.message.reply_text("Código inválido. Registro cancelado. ")
            return ConversationHandler.END

    def recoge_cuenta_pide_mail_o_cp(self, update, context):
        contestacion = update.message.text
        if(contestacion.lower() == "añadir cuenta"):
            context.user_data["tiene_cuenta"] = True
            id_telegram = update.message.from_user.id
            print(f"[TELEGRAM] Usuario {id_telegram} va a añadir cuenta.")
            update.message.reply_text(
                "¿Cuál es el email de tu cuenta de wallapop?: ", reply_markup=ForceReply())
            return self.STATUS3
        elif(contestacion.lower() == "no añadir cuenta"):
            id_telegram = update.message.from_user.id
            context.user_data["tiene_cuenta"] = False
            print(f"[TELEGRAM] Usuario {id_telegram} solo va a añadir código postal.")
            update.message.reply_text(
                "¿Cuál es tu código postal?: ", reply_markup=ForceReply())
            return self.STATUS6
        else:
            update.message.reply_text("Utiliza el teclado para responder. ", )
            return ConversationHandler.END

    def recoge_mail_pide_password(self, update, context):
        email = update.message.text
        if("@" in email):
            id_telegram = update.message.from_user.id
            print(f"[TELEGRAM] Usuario {id_telegram} mete correo: {email}.")
            update.message.reply_text(
                "Correo valido. ¿Cuál es la contraseña de tu cuenta de wallapop?: ", reply_markup=ForceReply())
            context.user_data["email"] = email
            return self.STATUS4
        else:
            update.message.reply_text(
                "Correo erróneo. Lanza /registro cuando sepas escribir. ", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

    def recoge_password_pide_mensaje(self, update, context):
        password = update.message.text
        context.user_data["pass_wallapop"] = password
        id_telegram = update.message.from_user.id
        print(f"[TELEGRAM] Usuario {id_telegram} mete password: {password}.")
        update.message.reply_text(f"Cuenta guardada. Introduce el mensaje automático que se enviará para los artículos: ", reply_markup=ForceReply())
        return self.STATUS5

    def recoge_mensaje_pide_codigo_postal(self, update, context):
        mensaje = update.message.text
        id_telegram = update.message.from_user.id
        print(f"[TELEGRAM] Usuario {id_telegram} mete mensaje: {mensaje}.")
        context.user_data["mensaje_wallapop"] = mensaje
        update.message.reply_text(
            f"Introduce código postal para las búsquedas: ", reply_markup=ForceReply())
        return self.STATUS6

    def recoge_codigo_postal_probar_credenciales(self, update, context):
        codigo_postal = update.message.text
        id_telegram = update.message.from_user.id
        correcto = False
        print(f"[TELEGRAM] Usuario {id_telegram} mete codigo postal: {codigo_postal}.")
        try:
            ccaa = int(codigo_postal[:2])
            if(ccaa in range(1,53) and len(codigo_postal) == 5):
                correcto = True
        except:
            pass

        if(not(correcto)):
            update.message.reply_text("Código postal incorrecto. Registro cancelado. ")
            return ConversationHandler.END
        else:
            context.user_data["codigo_postal"] = codigo_postal

        # Si introduce cuenta de wp, pruebo credenciales.
        if(context.user_data["tiene_cuenta"]):
            texto = "Código postal guardado. Vamos a probar tu cuenta. Esto puede durar unos segundos..."
            update.message.reply_text(texto)
            usuario = Usuario(update.message.from_user.id,
                              context.user_data["email"],
                              context.user_data["pass_wallapop"],
                              context.user_data["codigo_postal"],
                              context.user_data["mensaje_wallapop"])
            bot = TestCredenciales(usuario, ejecucion_en_background=True)
            if(bot.probarCredenciales()):
                # Registro al usuario en la BBDD
                gestorBBDD = GestorBBDD()
                gestorBBDD.insertarUsuario(usuario)

                # Muestro datos guardados.
                texto = f"""Credenciales correctos. Cuenta guardada:
                - Email: {context.user_data["email"]}
                - Password: {context.user_data["pass_wallapop"]}
                - Mensaje automático: {context.user_data["mensaje_wallapop"]}
                - Código postal: {context.user_data["codigo_postal"]}
                """
                update.message.reply_text(texto)

                # Logueo
                id_telegram = update.message.from_user.id
                if(gestorBBDD.existeUsuario(usuario.id_telegram)):
                    print(f"[TELEGRAM] Usuario {id_telegram} registrado con éxito.")
            else:
                update.message.reply_text("Credenciales erróneos. Registro cancelado y datos borrados. ")
                self.limpiar_datos(context)
        # Si no tiene cuenta
        else:
            # Solo le inserto en la bbdd
            usuario = Usuario(update.message.from_user.id,
                              None,
                              None,
                              context.user_data["codigo_postal"],
                              None)
            gestorBBDD = GestorBBDD()
            gestorBBDD.insertarUsuario(usuario)
            update.message.reply_text("Registrado como usuario sin cuenta en la BBDD.")
            print(f"[TELEGRAM] Usuario {id_telegram} registrado como usuario sin cuenta con éxito.")
        return ConversationHandler.END


    def cancelar_registro(self, update, context):
        self.limpiar_datos(context)
        update.message.reply_text(
            'Registro cancelado. ', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


    def limpiar_datos(self, context):
        context.user_data["tiene_cuenta"] = False
        context.user_data["email"] = ""
        context.user_data["pass_wallapop"] = ""
        context.user_data["mensaje_wallapop"] = ""
        context.user_data["codigo_postal"] = ""