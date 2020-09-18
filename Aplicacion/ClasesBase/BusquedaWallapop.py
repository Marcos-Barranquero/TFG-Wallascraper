class BusquedaWallapop:
    def __init__(self, id_telegram, id_busqueda, exclusiones, keywords,
                 enviar_mensaje_auto,
                 comparar_automaticamente,
                 precio_min="", precio_max="", radio_km=10,
                 order_by="newest"):
        self.id_telegram = id_telegram
        self.id_busqueda = id_busqueda
        self.exclusiones = exclusiones
        self.keywords = keywords
        self.comparar_automaticamente = comparar_automaticamente
        self.enviar_mensaje_auto = enviar_mensaje_auto
        self.precio_min = precio_min
        self.precio_max = precio_max
        self.radio_km = radio_km
        self.order_by = order_by

    def getURL(self):
        str_keywords = ""
        keywords = self.keywords.split(" ")
        for keyword in keywords:
            str_keywords += keyword + "%20"

        url = f"https://es.wallapop.com/search?distance={int(self.radio_km)*1000}&keywords={str_keywords}&order_by={self.order_by}&min_sale_price={self.precio_min}&max_sale_price={self.precio_max}"

        return url

    def __str__(self):
        cadena = f"[{self.keywords}]:[{self.id_telegram}-{self.id_busqueda}] | Precio: [{self.precio_min},{self.precio_max}] | Radio: {self.radio_km} km | Auto: {self.comparar_automaticamente} | Mensaje: {self.enviar_mensaje_auto}"
        return cadena