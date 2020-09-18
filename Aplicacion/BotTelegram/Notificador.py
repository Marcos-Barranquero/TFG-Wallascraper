#from Aplicacion.BotTelegram.WallascraperBot import TOKEN

import telegram

class Notificador:
    def __init__(self, TOKEN):
        self.bot = telegram.Bot(TOKEN)

    def notificarChollo(self, id_usuario, articulo, busqueda):
        texto = f"¡El artículo {articulo.titulo} por {articulo.precio} de tu búsqueda {busqueda.keywords} es un posible chollo! Échale un vistazo: {articulo.enlace}"
        self.bot.sendMessage(id_usuario, text=texto)#, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    def notificarAnuncio(self, id_usuario, articulo, busqueda):
        texto = f"¡Nuevo {articulo.titulo} por {articulo.precio}!, de tu búsqueda {busqueda.keywords}. Échale un vistazo: {articulo.enlace}"
        self.bot.sendMessage(id_usuario, text=texto)#, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))