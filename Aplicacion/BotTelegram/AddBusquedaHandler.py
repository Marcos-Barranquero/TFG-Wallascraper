from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply)

from Aplicacion.BaseDatos.GestorBBDD import GestorBBDD
from Aplicacion.ClasesBase.BusquedaWallapop import BusquedaWallapop
from Aplicacion.ClasesBase.ExclusionesBusqueda import ExclusionesBusqueda

class AddBusquedaHandler():
    def __init__(self):

        # Declaración de estados
        self.STATUS1, self.STATUS2, self.STATUS3, self.STATUS4, \
        self.STATUS5, self.STATUS6, self.STATUS7, self.STATUS8,\
        self.STATUS9, self.STATUS10, self.STATUS11, self.STATUS12 = range(12)

        self.handler = ConversationHandler(
            entry_points=[CommandHandler(
                'add_busqueda', self.add_busqueda)],
            states={
                self.STATUS1: [MessageHandler(~Filters.command, self.add_busqueda_uno)],
                self.STATUS2: [MessageHandler(~Filters.command, self.add_busqueda_dos)],
                self.STATUS3: [MessageHandler(~Filters.command, self.add_busqueda_tres)],
                self.STATUS4: [MessageHandler(~Filters.command, self.add_busqueda_cuatro)],
                self.STATUS5: [MessageHandler(~Filters.command, self.add_busqueda_cinco)],
                self.STATUS6: [MessageHandler(~Filters.command, self.add_busqueda_seis)],
                self.STATUS7: [MessageHandler(~Filters.command, self.add_busqueda_siete)],
                self.STATUS8: [MessageHandler(~Filters.command, self.add_busqueda_ocho)],
                self.STATUS9: [MessageHandler(~Filters.command, self.add_busqueda_nueve)],
                self.STATUS10: [MessageHandler(~Filters.command, self.add_busqueda_diez)],
                self.STATUS11: [MessageHandler(~Filters.command, self.add_busqueda_once)],
                self.STATUS12: [MessageHandler(~Filters.command, self.add_busqueda_doce)]
            },

            fallbacks=[CommandHandler(
                'cancelar_add_busqueda', self.cancelar_add_busqueda)]
        )

    def iniciar_diccionario_busqueda(self, update, context):
        context.user_data["keywords"] = ""
        context.user_data["precio_min"] = ""
        context.user_data["precio_max"] = ""
        context.user_data["radio_km"] = ""
        context.user_data["lista_keywords_titulo_excluyentes"] = ""
        context.user_data["lista_keywords_descripcion_excluyentes"] = ""
        context.user_data["lista_keywords_descripcion_reincluyentes"] = ""
        context.user_data["multiplicador_maximo"] = ""
        context.user_data["multiplicador_minimo"] = ""
        context.user_data["porcentaje_considerado_chollo"] = ""
        context.user_data["comparar_automaticamente"] = ""
        context.user_data["enviar_mensaje_auto"] = ""



    def add_busqueda(self, update, context):
        gestorBBDD = GestorBBDD()
        id_telegram = update.message.from_user.id
        if(gestorBBDD.existeUsuario(id_telegram)):
            print(f"[TELEGRAM] Usuario {id_telegram} comienza a registrar búsqueda. ")
            self.iniciar_diccionario_busqueda(update, context)
            update.message.reply_text("Introduce las keywords de tu búsqueda o utiliza en cualquier momento /cancelar_add_busqueda para cancelar.",reply_markup=ForceReply())
            return self.STATUS1
        else:
            update.message.reply_text("Necesitas registrarte para poder añadir una búsqueda. Usa /registrarse .")


    def add_busqueda_uno(self, update, context):
        keywords = update.message.text
        context.user_data["keywords"] = keywords
        update.message.reply_text("¿Cuál es el precio mínimo? ",reply_markup=ForceReply())
        return self.STATUS2

    def add_busqueda_dos(self, update, context):
        precio_min = update.message.text
        context.user_data["precio_min"] = precio_min
        update.message.reply_text("¿Cuál es el precio máximo? ",reply_markup=ForceReply())
        return self.STATUS3

    def add_busqueda_tres(self, update, context):
        precio_max = update.message.text
        context.user_data["precio_max"] = precio_max
        update.message.reply_text("¿Cuál es el radio, en km, de la búsqueda? ",reply_markup=ForceReply())
        return self.STATUS4

    def add_busqueda_cuatro(self, update, context):
        radio_km = update.message.text
        context.user_data["radio_km"] = radio_km
        update.message.reply_text("Introduce, separando por comas, las palabras o conjuntos de palabras que quieras que se excluyan de los títulos. Si no quieres añadir ninguna, introduce sólamente ',' : ",reply_markup=ForceReply())
        return self.STATUS5

    def add_busqueda_cinco(self, update, context):
        lista_keywords_titulo_excluyentes = update.message.text
        context.user_data["lista_keywords_titulo_excluyentes"] = lista_keywords_titulo_excluyentes.split(", ")
        update.message.reply_text("Introduce, separando por comas, las palabras o conjuntos de palabras que quieras que se excluyan de las descripciones. Si no quieres añadir ninguna, introduce sólamente ',' : ",reply_markup=ForceReply())
        return self.STATUS6

    def add_busqueda_seis(self, update, context):
        lista_keywords_descripcion_excluyentes = update.message.text
        context.user_data["lista_keywords_descripcion_excluyentes"] = lista_keywords_descripcion_excluyentes.split(", ")
        update.message.reply_text("Introduce, separando por comas, las palabras o conjuntos de palabras que quieras que se reincluyan en las descripciones. Si no quieres añadir ninguna, introduce sólamente ',' : ",reply_markup=ForceReply())
        return self.STATUS7

    def add_busqueda_siete(self, update, context):
        # Recojo keywords
        lista_keywords_descripcion_reincluyentes = update.message.text
        context.user_data["lista_keywords_descripcion_reincluyentes"] = lista_keywords_descripcion_reincluyentes.split(", ")

        # Habilito comparación solo si el usuario ha metido su cuenta de WP en la BBDD.
        gestorBBDD = GestorBBDD()
        id_telegram = update.message.from_user.id
        usuario = gestorBBDD.recuperarUsuario(id_telegram)
        tiene_cuenta = (usuario.email != "None" and usuario.password != "None")

        if(tiene_cuenta):
            keyboard= ReplyKeyboardMarkup([["Si"],["No"]], one_time_keyboard=True)
            texto = "La autocomparación hace que se estudien todos los anuncios nuevos, y solo se te avise de los anuncios que se consideren chollos. Si no la activas, se te avisarán de todos los anuncios. ¿Deseas activar la autocomparación?"
            update.message.reply_text(texto,reply_markup=keyboard)
            return self.STATUS8
        else:
            # Si no tiene cuenta, relleno los campos restantes con valores por defecto,
            # teniendo en cuenta que no se van a utilizar.
            context.user_data["multiplicador_minimo"] = 0.4
            context.user_data["multiplicador_maximo"] = 0.6
            context.user_data["porcentaje_considerado_chollo"] = 0.2

            context.user_data["comparar_automaticamente"] = False
            context.user_data["enviar_mensaje_auto"] = False
            texto = "Muy bien. Guardando búsqueda... "
            update.message.reply_text(texto)
            self.guardarBusqueda(id_telegram, update, context)
            return ConversationHandler.END


    def add_busqueda_ocho(self, update, context):
        if(update.message.text.lower() == "si"):
            context.user_data["comparar_automaticamente"] = True
            texto = "Al comparar, cada artículo se compara en base a su propio precio en un rango de precios. Elige el multiplicador para determinar el precio mínimo de este rango. (Por ej. 0.4 sería hasta un 40% por debajo del precio del artículo.): "
            update.message.reply_text(texto,reply_markup=ForceReply())
            return self.STATUS9
        else:
            context.user_data["multiplicador_minimo"] = 0.4
            context.user_data["multiplicador_maximo"] = 0.6
            context.user_data["porcentaje_considerado_chollo"] = 0.2
            context.user_data["comparar_automaticamente"] = False
            context.user_data["enviar_mensaje_auto"] = False
            id_telegram = update.message.from_user.id
            self.guardarBusqueda(id_telegram, update, context)
            return ConversationHandler.END


    def add_busqueda_nueve(self, update, context):
        multiplicador_minimo = update.message.text
        context.user_data["multiplicador_minimo"] = multiplicador_minimo
        texto = "Al comparar, cada artículo se compara en base a su propio precio en un rango de precios. Elige el multiplicador para determinar el precio máximo de este rango. (Por ej. 0.6 sería hasta un 60% por encima del precio del artículo.): "
        update.message.reply_text(texto,reply_markup=ForceReply())
        return self.STATUS10


    def add_busqueda_diez(self, update, context):
        multiplicador_maximo = update.message.text
        context.user_data["multiplicador_maximo"] = multiplicador_maximo
        texto = "Al comparar, la alerta saltara si un artículo está por debajo de un porcentaje de la media de precios de artículos similares. Introduce el porcentaje de precio bajo el cual se considera chollo. (Por ej. 0.2 sería a partir de un 20% más barato que el resto.): "
        update.message.reply_text(texto,reply_markup=ForceReply())
        return self.STATUS11

    def add_busqueda_once(self, update, context):
        porcentaje_considerado_chollo = update.message.text
        context.user_data["porcentaje_considerado_chollo"] = porcentaje_considerado_chollo
        texto = "¿Quieres que se envíe el mensaje automático a los chollos encontrados?"
        keyboard= ReplyKeyboardMarkup([["Si"],["No"]], one_time_keyboard=True)
        update.message.reply_text(texto,reply_markup=keyboard)
        return self.STATUS12


    def add_busqueda_doce(self, update, context):
        if(update.message.text.lower() == "si"):
            context.user_data["enviar_mensaje_auto"] = True
        else:
            context.user_data["enviar_mensaje_auto"] = False

        texto = "Muy bien. Guardando búsqueda... "
        update.message.reply_text(texto)

        id_telegram = update.message.from_user.id
        self.guardarBusqueda(id_telegram, update, context)
        return ConversationHandler.END


    def guardarBusqueda(self, id_telegram, update, context):
        gestorBBDD = GestorBBDD()
        try:
            exclusiones = ExclusionesBusqueda(
                list(context.user_data["lista_keywords_titulo_excluyentes"]),
            list(context.user_data["lista_keywords_descripcion_excluyentes"]),
            list(context.user_data["lista_keywords_descripcion_reincluyentes"]),
            float(context.user_data["multiplicador_maximo"]),
            float(context.user_data["multiplicador_minimo"]),
            float(context.user_data["porcentaje_considerado_chollo"])
            )

            busqueda = BusquedaWallapop(id_telegram,None, # Porque la id de búsqueda se asigna dentro de insertar búsqueda.
                                        exclusiones,
                                        str(context.user_data["keywords"]),
                                        bool(context.user_data["enviar_mensaje_auto"]),
                                        bool(context.user_data["comparar_automaticamente"]),
                                        float(context.user_data["precio_min"]),
                                        float(context.user_data["precio_max"]),
                                        int(context.user_data["radio_km"]),
                                        )
            gestorBBDD.insertarBusqueda(busqueda)
            update.message.reply_text("¡Búsqueda guardada!")
            print(f"[TELEGRAM] Usuario {id_telegram} registra búsqueda: ")
            print(f"[TELEGRAM] {gestorBBDD.recuperarBusqueda(gestorBBDD.getMaxIdBusqueda())}")
            self.limpiarBusqueda(context)
        except:
            update.message.reply_text("No se ha podido crear la búsqueda. ¿Seguro que has introducido bien los parámetros? Recuerda que los porcentajes se deben poner con un punto, por ej. 0.4.")
            self.limpiarBusqueda(context)



    def cancelar_add_busqueda(self, update, context):
        self.limpiarBusqueda(context)
        update.message.reply_text(
            'Introducción de búsqueda cancelada.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def limpiarBusqueda(self, context):
        context.user_data["keywords"] = ""
        context.user_data["precio_min"] = ""
        context.user_data["precio_max"] = ""
        context.user_data["radio_km"] = ""
        context.user_data["lista_keywords_titulo_excluyentes"] = ""
        context.user_data["lista_keywords_descripcion_excluyentes"] = ""
        context.user_data["lista_keywords_descripcion_reincluyentes"] = ""
        context.user_data["multiplicador_minimo"] = ""
        context.user_data["multiplicador_maximo"] = ""
        context.user_data["porcentaje_considerado_chollo"] = ""
        context.user_data["comparar_automaticamente"] = ""
        context.user_data["enviar_mensaje_auto"] = ""


