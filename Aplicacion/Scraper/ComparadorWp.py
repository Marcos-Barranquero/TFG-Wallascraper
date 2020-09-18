# Imports de selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from Aplicacion.ClasesBase.Articulo import Articulo
from Aplicacion.Scraper.Paths import *

# Import del sleep
from time import sleep

# Importo gestor del chromedriver directamente para no tener que pasar el path
from webdriver_manager.chrome import ChromeDriverManager

# Import de los xpaths para las webs...
from Aplicacion.Scraper.Paths import *

class ComparadorWp:
    def __init__(self, options, codigo_postal, recursos="altos"):
        self.codigo_postal = codigo_postal

        # Si el host es un ordenador con bajos recursos, abrirá ventanas de una en una cerrándolas
        # en lugar de varias de golpe
        if(recursos == "bajos"):
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        else:
            caps = DesiredCapabilities().CHROME
            caps["pageLoadStrategy"] = "eager"
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=caps, options=options)

        options = webdriver.ChromeOptions()

    def compararArticuloWallapop(self, articulo, busqueda, precios_float):
        """ Extrae la media y mediana de los artículos en wallapop con título similar al artículo dado """


        # Cargo la URL
        self.driver.get("https://es.wallapop.com/search?")

        # Acepto cookies
        aceptarCookies(self.driver)

        # Cambio ubicación
        cambiarUbicacion(self.driver, self.codigo_postal)


        # Umbral de minimo y máximo en la comparación
        precio_minimo_aceptable = float(articulo.precio) * busqueda.exclusiones.multiplicador_minimo
        precio_maximo_aceptable = float(articulo.precio) * (1+busqueda.exclusiones.multiplicador_maximo)

        print(f"[Comp-WP] Comparando {articulo.titulo} contra Wallapop en rango [{precio_minimo_aceptable},{precio_maximo_aceptable}]... ")

        # Preparo URL
        url = self.__getURL(articulo, busqueda)

        # Cargo búsqueda
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(url)

        # Recupero artículos
        articulos_a_comparar = self.recuperarArticulosWallapop(busqueda)
        articulos_no_excluidos = []
        for articulo_a_comparar in articulos_a_comparar:
            if(not(articulo_a_comparar.estaExcluido(busqueda))):
                articulos_no_excluidos.append(articulo_a_comparar)
        print(f"[Comp-WP] Excluidos {len(articulos_a_comparar) - len(articulos_no_excluidos)} artículos.")


        # Extraigo precios
        ignorados = 0
        for articulo_estudiado in articulos_no_excluidos:
            # No debería hacer falta pero a wallapop le da igual la query...
            if(articulo_estudiado.precio > precio_minimo_aceptable and articulo_estudiado.precio < precio_maximo_aceptable):
                precios_float.append(articulo_estudiado.precio)
            else:
                ignorados += 1

        print(f"[Comp-WP] Finalizada comparación de {articulo.titulo} en Wp. ")
        # Finalizo este driver.
        self.driver.quit()




    def recuperarArticulosWallapop(self, busqueda):
        """ Una vez cargada la URL, devuelve los últimos 40 artículos subidos. """
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
                # print("[Comp-WP] Error: ", end="")
                # print(e)
        print(f"[Comp-WP] Ignorados {anuncios} anuncios. ")
        return articulos

    def __getURL(self, articulo, busqueda):

        # Umbral de minimo y máximo en la comparación
        precio_minimo_aceptable = float(articulo.precio) * busqueda.exclusiones.multiplicador_minimo
        precio_maximo_aceptable = float(articulo.precio) * (1+busqueda.exclusiones.multiplicador_maximo)

        # Preparo url a scrapear
        url = f"https://es.wallapop.com/search?distance={busqueda.radio_km*1000}&keywords={articulo.titulo}&order_by={busqueda.order_by}&min_sale_price={precio_minimo_aceptable}&max_sale_price={precio_maximo_aceptable}"
        return url