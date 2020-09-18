# Imports de selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


# Import del sleep
from time import sleep

# Importo gestor del chromedriver directamente para no tener que pasar el path
from webdriver_manager.chrome import ChromeDriverManager

# Import de los xpaths para las webs...
from Aplicacion.Scraper.Paths import *

class ComparadorCC:
    def __init__(self, options, recursos="altos"):

        # Si el host es un ordenador con bajos recursos, abrirá ventanas de una en una cerrándolas
        # en lugar de varias de golpe
        if(recursos == "bajos"):
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        else:
            caps = DesiredCapabilities().CHROME
            caps["pageLoadStrategy"] = "eager"
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=caps, options=options)

        options = webdriver.ChromeOptions()

    def compararArticuloCC(self, articulo, busqueda, precios_float):
        """ En el cash converters, si solo aparece un articulo
        como resultado, carga directamente ese artículo en lugar
        de mostrar la misma web que si hubiese varios. """
        # Umbral de minimo y máximo en la comparación
        precio_minimo_aceptable = float(articulo.precio) * busqueda.exclusiones.multiplicador_minimo
        precio_maximo_aceptable = float(articulo.precio) * (1+busqueda.exclusiones.multiplicador_maximo)

        print(f"[Comp-CC] Comparando {articulo.titulo} contra Cash Converters en rango [{precio_minimo_aceptable},{precio_maximo_aceptable}]... ")

        unico_articulo = False
        sin_resultados = False

        # Cargo búsqueda
        url = self.__getURL(articulo.titulo)
        self.driver.get(url)
        sleep(3)

        if(existeElemento(self.driver, path_cookies_cc)):
            print("[Comp-CC] Encuentro el botón de las cookies")
            getByXpath(self.driver, path_cookies_cc).click()

        # Si saliese algo de un sorteo, lo cierro
        if(existeElemento(self.driver, path_sorteo_cc)):
            print("[Comp-CC] Cierro sorteo...")
            getByXpath(self.driver, path_sorteo_cc).click()

        # Compruebo si hay resultados. Si no los hay,
        # devolveré la lista vacía.
        if(self.__existeElementoPorNombreClase('section-header-nohits')):
            print("[Comp-CC] No hay resultados. ")
            sin_resultados = True


        # Compruebo si es único artículo
        if(not(sin_resultados)):
            unico = self.driver.find_elements_by_id('product-details')
            if(len(unico) > 0):
                unico_articulo = True

            if(unico_articulo):
                print("[Comp-CC] Solo hay un artículo. ")

                # Extraigo precio y finalizo
                precio = self.driver.find_elements_by_css_selector(selector_css_cc)[0].text
                precio_float = float(precio.replace(",", ".").replace("€", ""))
                precios_float.append(precio_float)

            if(not(unico_articulo)):
                print("[Comp-CC] Hay varios artículos. ")

                # Cargo toda la página
                pausa_entre_scroll = 0.5
                ultima_altura = self.driver.execute_script(
                    "return document.body.scrollHeight")
                nueva_altura = 0

                # Si es un nombre de artículo genérico (p.e. "móvil"),
                # pongo que haya un tope de scroll para no gastar el tiempo
                # renderizando una página infinita.
                scroll_tope = 10

                while nueva_altura != ultima_altura and scroll_tope > 0:
                    scroll_tope -= 1

                    # Mientras quede pagina por scrollear, scrolleo
                    ultima_altura = nueva_altura
                    # Hago scroll hacia abajo
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")

                    # Espero a que cargue la página
                    sleep(pausa_entre_scroll)

                    # Saco altura en la que estoy para comparar con la anterior
                    nueva_altura = self.driver.execute_script(
                        "return document.body.scrollHeight")

                # Extraigo títulos y precios
                #titulos = self.driver.find_elements_by_css_selector(
                #    "a[class='product-title']")

                precios = self.driver.find_elements_by_css_selector(selector_css_cc)

                for precio in precios:
                    precio_procesado = float(
                        precio.text.replace(".","").replace(",", ".").replace("€", ""))
                    if(precio_procesado > precio_minimo_aceptable and precio_procesado < precio_maximo_aceptable):
                        precios_float.append(precio_procesado)

        print(f"[Comp-CC] Finalizada comparación de {articulo.titulo} en Cash Converters. ")
        # Finalizo este driver.
        self.driver.quit()

    def __getURL(self, keywords):
        keywords = keywords.replace(" ", "+")
        str_keywords = ""
        for keyword in keywords:
            # El cash converters redirige a la web de venta si pone vendo o algo así.
            excluidas = ["vendo","venta","vender"]
            if(not(keyword in excluidas)):
                str_keywords += keyword + "%20"

        url = f"https://www.cashconverters.es/es/es/search/?q={keywords}&lang=es"
        return url

    def __existeElementoPorNombreClase(self, nombre_clase):
        return (len(self.driver.find_elements_by_class_name(nombre_clase)) > 0)