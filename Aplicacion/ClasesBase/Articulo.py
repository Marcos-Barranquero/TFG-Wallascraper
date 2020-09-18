class Articulo:
    def __init__(self, id_articulo, id_busqueda, titulo, descripcion, precio, enlace):
        self.id_articulo = int(id_articulo)
        self.id_busqueda = int(id_busqueda)
        self.titulo = titulo
        self.descripcion = descripcion
        if(isinstance(precio, str)):
            precio = float(precio.replace("€", "").replace(",", "."))
        self.precio = precio
        self.enlace = enlace

    def estaExcluido(self, busqueda):
        """ Devuelve true si el artículo es excluido en base a las exclusiones. """

        # Por defecto, considero que no está excluido.
        excluido_por_titulo = False
        excluido_por_descripcion = False
        fuera_de_precio = True

        # Primero, verifico el precio
        precio_maximo = busqueda.precio_max
        precio_minimo = busqueda.precio_min
        if(self.precio < precio_maximo and self.precio - precio_minimo):
            fuera_de_precio = False

        # Después, verifico el titulo:
        if(not(fuera_de_precio)):
            for titulo_excluyente in busqueda.exclusiones.lista_keywords_titulo_excluyentes:
                if titulo_excluyente.lower() in self.titulo.lower():
                    excluido_por_titulo = True
                    break

        # Después, verifico la descripción, si aún no está excluido por título
        if(not(excluido_por_titulo) and not(fuera_de_precio)):
            for descripcion_excluyente in busqueda.exclusiones.lista_keywords_descripcion_excluyentes:
                if(descripcion_excluyente.lower() in self.descripcion):
                    excluido_por_descripcion = True

        # Finalmente, verifico si debo de reincluirlo
        if(not(excluido_por_titulo) and excluido_por_descripcion and not(fuera_de_precio)):
            for descripcion_reincluyente in busqueda.exclusiones.lista_keywords_descripcion_reincluyentes:
                if(descripcion_reincluyente.lower() in self.descripcion):
                    excluido_por_descripcion = False

        # Devuelve true si está excluido por título o descripción
        return excluido_por_titulo or excluido_por_descripcion or fuera_de_precio

    def __str__(self):
        cadena = f"[{self.titulo}:{self.id_articulo}(B: {self.id_busqueda})]: {self.precio} - {self.enlace}"
        return cadena

