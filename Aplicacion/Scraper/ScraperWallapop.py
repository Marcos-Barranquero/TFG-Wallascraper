# Imports de selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Import del sleep
from time import sleep

# Import de estadísticas
import statistics as stats

# Import del artículo
from Aplicacion.BaseDatos.GestorBBDD import GestorBBDD
from Aplicacion.BotTelegram.Notificador import Notificador
from Aplicacion.ClasesBase.Articulo import Articulo
from Aplicacion.ClasesBase.PreciosArticulo import PreciosArticulo

# Importo gestor del chromedriver directamente para no tener que pasar el path
from webdriver_manager.chrome import ChromeDriverManager

# Import de los xpaths para las webs...
from Aplicacion.ClasesBase.Usuario import Usuario
from Aplicacion.Scraper.Paths import *

# Import de comparadores
from Aplicacion.Scraper.ComparadorCC import ComparadorCC
from Aplicacion.Scraper.ComparadorCex import ComparadorCex
from Aplicacion.Scraper.ComparadorWp import ComparadorWp

# Import de los threads
from threading import Thread


class ScraperWallapop:
    def __init__(self, usuario, notificador, recursos="altos", ejecucion_en_background=False):

        # Cargo el notificador
        self.notificador = notificador

        # Recupero usuario y veo si tiene cuenta
        self.usuario = usuario
        self.tiene_cuenta = (self.usuario.email != None) and (self.usuario.password != None)

        # Recupero búsquedas de la BBDD
        gestorBBDD = GestorBBDD()
        self.lista_busquedas = gestorBBDD.recuperarBusquedasUsuario(self.usuario.id_telegram)

        # Ajustes de configuración del webdriver
        self.recursos = recursos
        self.ejecucion_en_bakcground = ejecucion_en_background

        # Ignoro errores de certificado
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument("--start-maximized")
        self.options.add_argument("log-level=3")
        self.options.add_argument("--silent")

        # Configuro ventana para su ejecución en segundo plano
        if(ejecucion_en_background):
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--headless')
            self.options.add_argument("--window-size=1920x1080")

        # Si el host es un ordenador con bajos recursos, abrirá ventanas de una en una cerrándolas
        # en lugar de varias de golpe
        if(self.recursos == "bajos"):
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.options)

        else:
            caps = DesiredCapabilities().CHROME
            caps["pageLoadStrategy"] = "eager"
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=caps, options=self.options)

        # Lanzo el bot
        self.iniciarBot()

    def iniciarBot(self):
        """ Carga la web, acepta las cookies y establece la ubicación. """

        # Cargo la URL
        self.driver.get("https://es.wallapop.com/search?")

        # Acepto cookies
        aceptarCookies(self.driver)

        # Cambio ubicación
        cambiarUbicacion(self.driver, self.usuario.codigo_postal)

        # Inicio sesión si el usuario tiene cuenta
        if(self.tiene_cuenta):
            login(self.driver, self.ejecucion_en_bakcground, self.usuario.email, self.usuario.password)
            print(f"[SCRAPER] Usuario {self.usuario.id_telegram} logueado con éxito.  ")
        else:
            print(f"[SCRAPER] El usuario {self.usuario.id_telegram} no tiene cuenta ingresada.  ")

        # Dejo que la web cargue un poco de tiempo
        sleep(3)

        # Scrapeo
        self.scrapearBusquedas(self.lista_busquedas)

    # Funcionalidad adicional
    def enviarMensaje(self, articulo):
        """ Envía el mensaje predefinido por el usuario
        al vendedor del artículo pasado """

        # Cargo el enlace
        url = articulo.enlace
        self.driver.get(url)

        # Pulso sobre el botón de hablar
        getByXpath(self.driver, path_boton_chat).click()

        # Cambio de ventana
        self.driver.switch_to.window(self.driver.window_handles[-1])

        # Escribo el mensaje en el chat
        getByXpath(self.driver, path_chat_textarea).send_keys(self.usuario.mensaje)

        # Envío el mensaje
        getByXpath(self.driver, path_boton_enviar_chat).click()

    # Gestión de búsquedas
    def scrapearBusquedas(self, lista_busquedas_usuario):
        gestorBBDD = GestorBBDD()
        try:
            for busqueda in lista_busquedas_usuario:
                # Verifico si es la primera vez que se realiza la búsqueda
                articulos = gestorBBDD.recuperarArticulosBusqueda(busqueda.id_busqueda)
                no_hay_articulos = len(articulos) == 0

                # Si es la primera vez, añado artículos de una búsqueda inicial, para no notificar de los anuncios ya existentes.
                if(no_hay_articulos):
                    print(f"[SCRAPER] La búsqueda {busqueda.id_busqueda} se lanza por primera vez. Scrapeo artículos iniciales.  ")
                    self.scrapeoInicial(busqueda)

                if(self.tiene_cuenta):
                    self.scrapearBusqueda(busqueda)
                else:
                    self.scrapearBusquedaSinCuenta(busqueda)

            print(f"[SCRAPER] Scrapeo de todas las búsquedas del usuario {self.usuario.id_telegram} finalizado.")
        except Exception as e:
            print(f"[SCRAPER] Error scrapeando las búsquedas de {self.usuario.id_telegram}: {e}. Se aborta el scrapeo...")
        finally:
            self.notificador.notificarFinScrapeo(self.usuario.id_telegram)

            # Cierro el driver y con ello el navegador.
            self.driver.quit()

    def scrapearBusqueda(self, busqueda):

        print(f"[SCRAPER] Recuperando artículos de búsqueda '{busqueda.keywords}'")
        articulos_recuperados = self.recuperarArticulosWallapop(busqueda)

        gestorBBDD = GestorBBDD()

        for articulo in articulos_recuperados:
            # Si no está en la base de datos, no está estudiado para esta búsqueda.
            excluido = articulo.estaExcluido(busqueda)
            existe = gestorBBDD.existeArticulo(articulo.id_articulo, busqueda.id_busqueda)

            if(not(excluido) and not(existe)):

                # Lo añado a la base de datos.
                gestorBBDD.insertarArticulo(articulo)

                # Si está activada la autocomparación, pues comparo.
                if(busqueda.comparar_automaticamente):

                    preciosArticulo = self.__extraerPreciosArticulo(articulo, busqueda)
                    chollo = self.__esChollo(articulo, busqueda, preciosArticulo)

                    if(chollo):
                        print(f"[SCRAPER] El usuario {self.usuario.id_telegram} ha encontrado un chollo: {articulo.titulo} - {articulo.precio} [{articulo.enlace}]")
                        self.notificador.notificarChollo(self.usuario.id_telegram,articulo,busqueda)
                        if(busqueda.enviar_mensaje_auto):
                            self.enviarMensaje(articulo)
                    else:
                        print(f"[SCRAPER] El usuario {self.usuario.id_telegram} ha analizado {articulo.titulo} - {articulo.precio}, pero no es un chollo...")
                # Si no está activada la autocomparación, solo notifico.
                else:
                    self.notificador.notificarAnuncio(self.usuario.id_telegram,articulo,busqueda)
        print(f"[SCRAPER] Scrapeo de la búsqueda {busqueda.id_busqueda} del usuario {self.usuario.id_telegram} finalizado.")

    def scrapearBusquedaSinCuenta(self, busqueda):

        print(f"[SCRAPER] Recuperando artículos de búsqueda '{busqueda.keywords}' del usuario {self.usuario.id_telegram}")
        articulos_recuperados = self.recuperarArticulosWallapop(busqueda)

        gestorBBDD = GestorBBDD()

        for articulo in articulos_recuperados:
            # Si no está en la base de datos, no está estudiado para esta búsqueda.
            excluido = articulo.estaExcluido(busqueda)
            existe = gestorBBDD.existeArticulo(articulo.id_articulo, busqueda.id_busqueda)

            # Solo notifico
            if(not(excluido) and not(existe)):
                self.notificador.notificarAnuncio(self.usuario.id_telegram,articulo,busqueda)

            # Finalmente, lo añado a la base de datos.
            gestorBBDD.insertarArticulo(articulo)
        print(f"[SCRAPER] Scrapeo de la búsqueda {busqueda.id_busqueda} del usuario {self.usuario.id_telegram} finalizado.")

    def scrapeoInicial(self, busqueda):
        gestorBBDD = GestorBBDD()
        articulos = self.recuperarArticulosWallapop(busqueda)
        for articulo in articulos:
            if(not(articulo.estaExcluido(busqueda))):
                gestorBBDD.insertarArticulo(articulo)



    def __esChollo(self, articulo, busqueda, preciosArticulo):
        # Doy por hecho que no es chollo
        chollo = False

        # Preparo medias
        media_wp, media_cx, media_cc = float("inf"), float("inf"), float("inf")

        # Calculo medias
        if(len(preciosArticulo.precios_wp) > 0):
            media_wp = stats.mean(preciosArticulo.precios_wp)
        if(len(preciosArticulo.precios_cc) > 0):
            media_cc = stats.mean(preciosArticulo.precios_cc)
        if(len(preciosArticulo.precios_cex) > 0):
            media_cx = stats.mean(preciosArticulo.precios_cex)

        print(f"[SCRAPER] Media WP [{media_wp}] | Media CC [{media_cc}] | Media CX [{media_cx}]")


        debajo_media_wp = articulo.precio < media_wp
        debajo_media_cc = articulo.precio < media_cc
        debajo_media_cx = articulo.precio < media_cx

        # Si está por debajo de todas las medias, saco una media total
        if(debajo_media_cc and debajo_media_cx and debajo_media_wp):
            print("[SCRAPER] El precio del artículo analizado está por debajo de la media, puede ser un chollo...")
            medias = [media_cc, media_wp, media_cx]
            numero_medias = len(medias)

            # Si no se han extraido precios de aguna web, la borro
            while (float ("inf") in medias):
                medias.remove(float("inf"))
                numero_medias -= 1

            media_total = 0
            for media in medias:
                media_total+=(media/numero_medias)

            # Genero el precio a partir del cual se considera chollo en base a las exclusiones
            precio_considerado_chollo = (media_total - (media_total*busqueda.exclusiones.porcentaje_considerado_chollo))

            # Si está por debajo, es un chollo.
            if(articulo.precio < precio_considerado_chollo):
                chollo = True
        return chollo

    def __extraerPreciosArticulo(self, articulo, busqueda):

        # Lanzo comparadores
        comparador_wp = ComparadorWp(self.options, self.usuario.codigo_postal,self.recursos)
        comparador_cc = ComparadorCC(self.options, self.recursos)
        comparador_cx = ComparadorCex(self.options, self.recursos)

        # Lanzo listas de recogida
        precios_wp, precios_cx, precios_cc = [], [], []

        # Preparo hilos de comparaciones
        t1 = Thread(target=comparador_wp.compararArticuloWallapop, args=(articulo, busqueda, precios_wp))
        t2 = Thread(target=comparador_cc.compararArticuloCC, args=(articulo, busqueda, precios_cc))
        t3 = Thread(target=comparador_cx.compararArticuloCex, args=(articulo, busqueda, precios_cx))

        # Lanzo hilos
        print(f"[SCRAPER] Comparando {articulo.titulo} por {articulo.precio}€ ... ")
        t1.start()
        t2.start()
        t3.start()

        # Uno todos antes de continuar
        t1.join(140)
        t2.join(140)
        t3.join(140)

        print(f"[SCRAPER] Resultados de la comparación de {articulo.titulo} por {articulo.precio}€...")
        print(f"[SCRAPER] Precios wp: {precios_wp}")
        print(f"[SCRAPER] Precios cc: {precios_cc}")
        print(f"[SCRAPER] Precios cx: {precios_cx}")
        precios_articulo = PreciosArticulo(articulo.id_articulo, precios_wp, precios_cc, precios_cx)
        return precios_articulo

    def recuperarArticulosWallapop(self, busqueda):
        """ Una vez cargada la URL, devuelve los últimos 40 artículos subidos. """

        # Cargo búsqueda
        self.driver.get(busqueda.getURL())

        articulos = []
        anuncios = 0
        sleep(5)
        cards = self.driver.find_elements_by_xpath(path_cardboard_articulos)[0]
        for i in range(2, 46):
            try:
                titulo = cards.find_element_by_xpath(path_titulo_articulos(i)).text
                descripcion = cards.find_element_by_xpath(path_descripcion_articulos(i)).text
                precio = cards.find_element_by_xpath(path_precio_articulos(i)).text
                enlace = cards.find_element_by_xpath(path_enlace_articulos(i)).get_attribute("href")
                id_articulo = enlace.split("-")[-1]
                articulo = Articulo(id_articulo, busqueda.id_busqueda, titulo, descripcion,
                                    precio, enlace)
                articulos.append(articulo)
            except Exception as e:
                anuncios += 1
                # print("Error: ", end="")
                # print(e)
        print(f"[SCRAPER] Ignorados {anuncios} anuncios. ")
        return articulos





