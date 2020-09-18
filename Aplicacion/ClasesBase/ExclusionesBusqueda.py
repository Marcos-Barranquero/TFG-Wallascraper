class ExclusionesBusqueda():
    def __init__(self, lista_keywords_titulo_excluyentes,
                 lista_keywords_descripcion_excluyentes,
                 lista_keywords_descripcion_reincluyentes,
                 multiplicador_maximo,
                 multiplicador_minimo,
                 porcentaje_considerado_chollo):


        # Lista de keywords excluidas en título
        self.lista_keywords_titulo_excluyentes = lista_keywords_titulo_excluyentes
        self.lista_keywords_descripcion_excluyentes = lista_keywords_descripcion_excluyentes
        self.lista_keywords_descripcion_reincluyentes = lista_keywords_descripcion_reincluyentes

        # Multiplicador del precio del artículo (minimo, maximo) en las comparaciones
        self.multiplicador_maximo = float(multiplicador_maximo)
        self.multiplicador_minimo = float(multiplicador_minimo)
        # Porcentaje sobre el precio del producto bajo el cual se considera chollo
        self.porcentaje_considerado_chollo = float(porcentaje_considerado_chollo)

    def __str__(self):
        return f"Titulos exc: {self.lista_keywords_titulo_excluyentes}, " \
               f"Descripciones exc: {self.lista_keywords_descripcion_excluyentes}, "\
               f"Descripciones reinc: {self.lista_keywords_descripcion_reincluyentes}, "\
               f"Rango precios: [{self.multiplicador_minimo},{self.multiplicador_maximo}], "\
               f"Chollo por debajo del {float(self.porcentaje_considerado_chollo * 100)} %."

