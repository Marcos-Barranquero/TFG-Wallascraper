import sqlite3

from Aplicacion.ClasesBase.Articulo import Articulo
from Aplicacion.ClasesBase.PreciosArticulo import PreciosArticulo
from Aplicacion.ClasesBase.BusquedaWallapop import BusquedaWallapop
from Aplicacion.ClasesBase.ExclusionesBusqueda import ExclusionesBusqueda

from Aplicacion.ClasesBase.Usuario import Usuario

PRUEBAS = False


class GestorBBDD:
    def __init__(self):
        database = "C:/Users/marco/PycharmProjects/TFG/Aplicacion/BaseDatos/datosArticulos.db"
        self.conexion = sqlite3.connect(database)

    def instanciarEsquemaBBDD(self):
        # Nombre de la base de datos
        DB_NAME = "datosArticulos.db"

        # Archivo SQL con la definicion de las tablas
        SQL_File_Name = "CrearTablas.sql"

        # Se carga el archivo SQL a una variable y se eliminan los saltos de linea
        TableSchema = ""
        with open(SQL_File_Name, 'r') as SchemaFile:
            TableSchema = SchemaFile.read().replace('\n', '')

        # Se crea la nueva base de datos
        conn = sqlite3.connect(DB_NAME)
        curs = conn.cursor()

        # Se lanza la consulta de creacion de tablas
        sqlite3.complete_statement(TableSchema)

        curs.executescript(TableSchema)

        # Se cierra la conexion con la base de datos
        curs.close()
        conn.close()

        print("[GESTORBBDD] Base de datos creada con éxito.")

    def __insertarEnBBDD(self, query, args):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(query, args)
            self.conexion.commit()
            cursor.close()
        except sqlite3.Error as error:
            print("Error al insertar en BBDD: ", error)

    def __recuperarEnBBDD(self, query):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(query)
            self.conexion.commit()
            datos = cursor.fetchall()
            cursor.close()

            return datos
        except sqlite3.Error as error:
            print("Error al recuperar de la BBDD: ", error)

    # Gestión de usuarios
    def insertarUsuario(self, usuario):
        """ Inserta un usuario nuevo en la BBDD """

        id_telegram = usuario.id_telegram
        email = usuario.email
        password = usuario.password
        codigo_postal = usuario.codigo_postal
        mensaje = usuario.mensaje
        query = "INSERT INTO 'Usuarios' VALUES(?, ?, ?, ?, ?)"
        args = (id_telegram, email, password, codigo_postal, mensaje)

        self.__insertarEnBBDD(query, args)

    def existeUsuario(self, id_telegram):
        """ Devuelve true si existe usuario asociado a ese mail"""

        existe = False
        query = f"Select * from Usuarios WHERE id_telegram = '{id_telegram}'"
        datos_recuperados = self.__recuperarEnBBDD(query)
        if(len(datos_recuperados) > 0):
            existe = True
        return existe

    def recuperarUsuario(self, id_telegram):
        query = f"Select * from 'Usuarios' WHERE id_telegram = '{id_telegram}'"
        usuario_devuelto = None
        if(self.existeUsuario(id_telegram)):
            datos_recuperados = self.__recuperarEnBBDD(query)[0]

            email = str(datos_recuperados[1])
            password = str(datos_recuperados[2])
            codigo_postal = str(datos_recuperados[3])
            mensaje = str(datos_recuperados[4])
            usuario_devuelto = Usuario(
                id_telegram, email, password, codigo_postal, mensaje)

        return usuario_devuelto

    def borrarUsuario(self, id_telegram):
        query = f"DELETE FROM 'Usuarios' WHERE id_telegram = {id_telegram}"
        self.__recuperarEnBBDD(query)

    # Gestión de artículos

    def getMaxIdArticulo(self):
        max_id = self.__recuperarEnBBDD(
            "select MAX(id_articulo) from 'Articulos';")[0][0]
        if(max_id == None):
            max_id = 0
        return max_id

    def insertarArticulo(self, articulo):
        """ Inserta un artículo nuevo no estudiado en la BBDD """
        query = "INSERT INTO 'Articulos' VALUES(?, ?, ?, ?, ?, ?)"
        args = [articulo.id_articulo,
                articulo.id_busqueda,
                articulo.titulo,
                articulo.descripcion,
                articulo.precio,
                articulo.enlace]
        self.__insertarEnBBDD(query, args)

    def existeArticulo(self, id_articulo, id_busqueda):
        """ Devuelve true si existe articulo asociado"""
        existe = False
        query = f"SELECT * FROM 'Articulos' WHERE id_articulo = {id_articulo} and id_busqueda = {id_busqueda}"
        datos_recuperados = self.__recuperarEnBBDD(query)
        if(len(datos_recuperados) > 0):
            existe = True
        return existe

    def borrarArticulosBusqueda(self, id_busqueda):
        query = f"DELETE FROM 'Articulos' WHERE id_busqueda = {id_busqueda}"
        query2 = f"DELETE FROM 'PreciosArticulos' WHERE id_busqueda = {id_busqueda}"
        self.__recuperarEnBBDD(query)
        self.__recuperarEnBBDD(query2)

    def recuperarArticulo(self, id_articulo, id_busqueda):
        """ Devuelve el artículo con la ID introducida de la BBDD. """
        query = f"SELECT * FROM Articulos WHERE id_articulo = {id_articulo} and id_busqueda = {id_busqueda}"
        articulo_devuelto = None
        if(self.existeArticulo(id_articulo, id_busqueda)):
            datos_recuperados = self.__recuperarEnBBDD(query)[0]
            id_busqueda = datos_recuperados[1]
            titulo = datos_recuperados[2]
            descripcion = datos_recuperados[3]
            precio = datos_recuperados[4]
            enlace = datos_recuperados[5]
            articulo_devuelto = Articulo(
                id_articulo, id_busqueda, titulo, descripcion, precio, enlace)

        return articulo_devuelto

    def recuperarArticulosBusqueda(self, id_busqueda):
        query = f"SELECT * FROM Articulos where id_busqueda = {id_busqueda}"
        datos = self.__recuperarEnBBDD(query)
        articulos_recuperados = []

        for dato in datos:
            id_articulo = dato[0]
            articulos_recuperados.append(
                self.recuperarArticulo(id_articulo, id_busqueda))
        return articulos_recuperados

    # Gestión de precios de artículos tras estudiarlos
    def insertarPreciosArticulo(self, precios_articulo, id_busqueda):
        """ Inserta un artículo nuevo no estudiado en la BBDD """
        query = "INSERT INTO 'PreciosArticulos' VALUES(?, ?, ?, ?, ?)"

        # Convierto listas a str separando elementos con |
        precios_wp = "|".join([str(val)
                               for val in precios_articulo.precios_wp])
        precios_cc = "|".join([str(val)
                               for val in precios_articulo.precios_cc])
        precios_cex = "|".join([str(val)
                                for val in precios_articulo.precios_cex])

        args = [precios_articulo.id_articulo,
                id_busqueda,
                precios_wp,
                precios_cc,
                precios_cex]

        self.__insertarEnBBDD(query, args)

    def existePreciosArticulo(self, id_articulo, id_busqueda):
        """ Devuelve true si existe articulo asociado"""
        existe = False
        query = f"SELECT * FROM 'PreciosArticulos' WHERE id_articulo = {id_articulo} and id_busqueda = {id_busqueda}"
        datos_recuperados = self.__recuperarEnBBDD(query)
        if(len(datos_recuperados) > 0):
            existe = True
        return existe

    def recuperarPreciosArticulo(self, id_articulo, id_busqueda):
        """ Devuelve el la tabla de precios asociada al artículo con la ID introducida de la BBDD. """
        query = f"SELECT * FROM 'PreciosArticulos' WHERE id_articulo = {id_articulo} and id_busqueda = {id_busqueda}"
        precios_articulo_devuelto = None
        if(self.existePreciosArticulo(id_articulo)):
            datos = self.__recuperarEnBBDD(query)[0]
            precios_wp = [float(valor) for valor in datos[1].split("|")]
            precios_cc = [float(valor) for valor in datos[2].split("|")]
            precios_cex = [float(valor) for valor in datos[3].split("|")]
            precios_articulo_devuelto = PreciosArticulo(
                id_articulo, precios_wp, precios_cc, precios_cex)
        return precios_articulo_devuelto

    # Gestión de exclusiones

    def insertarExclusion(self, id_busqueda, exclusion):
        query = "INSERT INTO 'Exclusiones' VALUES(?, ?, ?, ?, ?, ?, ?)"
        lista_keywords_titulo_excluyentes = "|".join(
            exclusion.lista_keywords_titulo_excluyentes)
        lista_keywords_descripcion_excluyentes = "|".join(
            exclusion.lista_keywords_descripcion_excluyentes)
        lista_keywords_descripcion_reincluyentes = "|".join(
            exclusion.lista_keywords_descripcion_reincluyentes)
        multiplicador_maximo = exclusion.multiplicador_maximo
        multiplicador_minimo = exclusion.multiplicador_minimo
        porcentaje_considerado_chollo = exclusion.porcentaje_considerado_chollo

        args = (id_busqueda,
                lista_keywords_titulo_excluyentes,
                lista_keywords_descripcion_excluyentes,
                lista_keywords_descripcion_reincluyentes,
                multiplicador_maximo, multiplicador_minimo,
                porcentaje_considerado_chollo)

        self.__insertarEnBBDD(query, args)

    def existeExclusion(self, id_busqueda):
        """ Devuelve true si existe exclusion asociada"""
        existe = False
        query = f"SELECT * FROM 'Exclusiones' WHERE id_busqueda = {id_busqueda}"
        datos_recuperados = self.__recuperarEnBBDD(query)
        if(len(datos_recuperados) > 0):
            existe = True
        return existe

    def recuperarExclusion(self, id_busqueda):
        """ Devuelve el artículo con la ID introducida de la BBDD. """
        query = f"SELECT * FROM 'Exclusiones' WHERE id_busqueda = {id_busqueda}"
        exclusion = None
        if(self.existeExclusion(id_busqueda)):
            datos_recuperados = self.__recuperarEnBBDD(query)[0]
            lista_keywords_titulo_excluyentes = [
                valor for valor in datos_recuperados[1].split("|")]
            lista_keywords_descripcion_excluyentes = [
                valor for valor in datos_recuperados[2].split("|")]
            lista_keywords_descripcion_reincluyentes = [
                valor for valor in datos_recuperados[3].split("|")]
            multiplicador_maximo = float(datos_recuperados[4])
            multiplicador_minimo = float(datos_recuperados[5])
            porcentaje_considerado_chollo = float(datos_recuperados[6])
            exclusion = ExclusionesBusqueda(lista_keywords_titulo_excluyentes,
                                            lista_keywords_descripcion_excluyentes,
                                            lista_keywords_descripcion_reincluyentes,
                                            multiplicador_maximo, multiplicador_minimo,
                                            porcentaje_considerado_chollo)

        return exclusion

    # Gestión de búsquedas
    def insertarBusqueda(self, busquedaWallapop):
        """ Inserta un artículo nuevo no estudiado en la BBDD """

        id_busqueda = self.getMaxIdBusqueda() + 1
        id_telegram = busquedaWallapop.id_telegram
        exclusiones = busquedaWallapop.exclusiones
        comparar_automaticamente = busquedaWallapop.comparar_automaticamente
        enviar_mensaje_auto = busquedaWallapop.enviar_mensaje_auto
        keywords = busquedaWallapop.keywords
        precio_min = busquedaWallapop.precio_min
        precio_max = busquedaWallapop.precio_max
        radio_km = busquedaWallapop.radio_km
        order_by = busquedaWallapop.order_by

        query = "INSERT INTO 'BusquedasWallapop' VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        args = [id_telegram, id_busqueda, keywords,
                comparar_automaticamente, enviar_mensaje_auto,
                precio_min, precio_max,
                radio_km, order_by]
        self.__insertarEnBBDD(query, args)
        print(f"Búsqueda insertada con id asignada: {id_busqueda}")

        self.insertarExclusion(id_busqueda, exclusiones)

    def getMaxIdBusqueda(self):
        max_id = self.__recuperarEnBBDD(
            "select MAX(id_busqueda) from 'BusquedasWallapop';")[0][0]
        if(max_id == None):
            max_id = 0
        return max_id

    def existeBusqueda(self, id_busqueda):
        """ Devuelve true si existe exclusion asociada"""
        existe = False
        query = f"SELECT * FROM 'BusquedasWallapop' WHERE id_busqueda = {id_busqueda}"
        datos_recuperados = self.__recuperarEnBBDD(query)
        if(len(datos_recuperados) > 0):
            existe = True
        return existe

    def recuperarBusqueda(self, id_busqueda):
        """ Devuelve la búsqueda con la ID introducida de la BBDD. """
        query = f"SELECT * FROM 'BusquedasWallapop' WHERE id_busqueda = {id_busqueda}"
        busqueda = None
        if(self.existeBusqueda(id_busqueda)):
            datos_recuperados = self.__recuperarEnBBDD(query)[0]
            id_telegram = int(datos_recuperados[0])
            exclusiones = self.recuperarExclusion(id_busqueda)
            keywords = datos_recuperados[2]
            comparar_automaticamente = bool(datos_recuperados[3])
            enviar_mensaje_auto = bool(datos_recuperados[4])
            precio_min = float(datos_recuperados[5])
            precio_max = float(datos_recuperados[6])
            radio = int(datos_recuperados[7])
            order_by = datos_recuperados[8]
            busqueda = BusquedaWallapop(id_telegram, id_busqueda, exclusiones,
                                        keywords, enviar_mensaje_auto,
                                        comparar_automaticamente,
                                        precio_min, precio_max,
                                        radio, order_by)

        return busqueda

    def recuperarBusquedasUsuario(self, id_telegram):
        """ Devuelve la búsqueda con la ID introducida de la BBDD. """
        query = f"SELECT id_busqueda FROM 'BusquedasWallapop' WHERE id_telegram = {id_telegram}"
        busquedas = []
        if(self.existeUsuario(id_telegram)):
            ids = self.__recuperarEnBBDD(query)
            for id_busqueda in ids:
                busquedas.append(self.recuperarBusqueda(id_busqueda[0]))
        return busquedas

    def borrarBusqueda(self, id_busqueda):
        query = f"DELETE FROM 'BusquedasWallapop' WHERE id_busqueda = {id_busqueda}"
        query2 = f"DELETE FROM 'Exclusiones' WHERE id_busqueda = {id_busqueda}"
        self.__recuperarEnBBDD(query)
        self.__recuperarEnBBDD(query2)
        self.borrarArticulosBusqueda(id_busqueda)


# Tests
if __name__ == "__main__":

    bbdd = GestorBBDD()
    bbdd.instanciarEsquemaBBDD()
    if(PRUEBAS):

        # Pruebas con usuarios...

        usuario = Usuario(25, "pedrito_sanchez@mail.com",
                          "1234f", "28030", "ola guapa que tal stas")
        usuario2 = Usuario(21, "", "", "28030", "")
        bbdd.insertarUsuario(usuario)
        bbdd.insertarUsuario(usuario2)

        print(f"usuario existe: {bbdd.existeUsuario(25)}")
        print(f"usuario existe: {bbdd.existeUsuario(21)}")
        print(f"usuario3 existe: {bbdd.existeUsuario(34)}")

        print(
            f"usuario recuperado: {bbdd.recuperarUsuario(usuario.id_telegram)}")
        print(
            f"usuario2 recuperado: {bbdd.recuperarUsuario(usuario2.id_telegram)}")
        # Pruebas con articulos
        articulo = Articulo(1, 25, "Titulo", "Descripcion",
                            "25€", "http://www....")
        articulo2 = Articulo(
            2, 25, "Titulo", "Descripcion", 13, "http://www....")
        bbdd.insertarArticulo(articulo)
        bbdd.insertarArticulo(articulo2)
        print(f"articulo existe: {bbdd.existeArticulo(articulo.id_articulo)}")
        print(
            f"articulo2 existe: {bbdd.existeArticulo(articulo2.id_articulo)}")
        print(f"articulo3 existe: {bbdd.existeArticulo(55)}")
        print(
            f"articulo recuperado: {bbdd.recuperarArticulo(articulo.id_articulo)}")
        print(
            f"articulo2 recuperado: {bbdd.recuperarArticulo(articulo2.id_articulo)}")
        print(f"articulo2 recuperado: {bbdd.recuperarArticulo(55)}")
        articulos = bbdd.recuperarArticulosBusqueda(25)
        print("articulos", articulos)

        # Pruebas con preciosArticulo
        preciosArticulo = PreciosArticulo(12, [1, 2, 3], [4, 5, 6], [7, 8, 9])
        preciosArticulo2 = PreciosArticulo(
            15, [10, 11, 12], [4.4, 5.5, 6.6], [72, 83, 94])
        bbdd.insertarPreciosArticulo(preciosArticulo)
        bbdd.insertarPreciosArticulo(preciosArticulo2)
        print(
            f"preciosarticulo existe: {bbdd.existePreciosArticulo(preciosArticulo.id_articulo)}")
        print(preciosArticulo)
        print(
            f"preciosarticulo2 existe: {bbdd.existePreciosArticulo(preciosArticulo2.id_articulo)}")
        print(f"preciosarticulo3 existe: {bbdd.existePreciosArticulo(76563)}")
        print(
            f"preciosarticulo recuperado: {bbdd.recuperarPreciosArticulo(preciosArticulo.id_articulo)}")
        print(
            f"preciosarticulo recuperado: {bbdd.recuperarPreciosArticulo(preciosArticulo2.id_articulo)}")
        Pruebas con exclusiones y busquedas
        exclusiones1 = ExclusionesBusqueda(["lite"], [], [], 1.5, 0.8, 0.20)
        busqueda1 = BusquedaWallapop(
            25, None, exclusiones1, "xiaomi", False, False, 60, 120, 25)
        exclusiones2 = ExclusionesBusqueda(["lite"], [], [], 1.5, 0.8, 0.20)
        busqueda2 = BusquedaWallapop(
            25, None, exclusiones2, "samsung", False, False, 60, 120, 25)
        exclusiones3 = ExclusionesBusqueda(["lite"], [], [], 1.5, 0.8, 0.20)
        busqueda3 = BusquedaWallapop(
            25, None, exclusiones3, "huawei", False, False, 60, 120, 25)
        bbdd.insertarBusqueda(busqueda1)
        bbdd.insertarBusqueda(busqueda2)
        bbdd.insertarBusqueda(busqueda3)
        print("Busquedas: ")
        busq = bbdd.recuperarBusquedasUsuario(25)
        for bus in busq:
            print(bus.getURL())
            print(bus.exclusiones)
            print(bus.enviar_mensaje_auto, bus.comparar_automaticamente)
    else:
        pass
