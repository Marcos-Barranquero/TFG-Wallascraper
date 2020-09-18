# Imports de selenium
from itertools import combinations

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from Aplicacion.Scraper.Paths import *

# Import del sleep
from time import sleep

# Importo gestor del chromedriver directamente para no tener que pasar el path
from webdriver_manager.chrome import ChromeDriverManager

# Import de los xpaths para las webs...
from Aplicacion.Scraper.Paths import *

class ComparadorCex:
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

    def __getURL(self, keywords, precio_min, precio_max):
        keywords = keywords.replace(" ", "%20").replace(" ", "/")

        url = f"https://es.webuy.com/search?stext={keywords}&maxPrice={precio_max}&minPrice={precio_min}"

        return url

    def __existeElemento(self, xpath):
        return (len(self.driver.find_elements_by_xpath(xpath)) > 0)

    def __existeElementoPorNombreClase(self, nombre_clase):
        return (len(self.driver.find_elements_by_class_name(nombre_clase)) > 0)

    # Gestión de comparaciones...
    def __generarPermutaciones(self, articulo, busqueda):

        # TODO: si hay muchas permutaciones, meter 3 opciones
        #    - continuar como si nada
        #    - comparar contra keywords de la busqueda
        #    - comparar manualemtne con las palabras que meta el usuario

        keys = articulo.titulo.lower().split(" ")

        # Si el título del artículo no contiene la keyword y no penaliza en exceso el rendimiento, lo añado
        if(len(keys) < 6):
            for keyword in busqueda.keywords.split(" "):
                if(not(keyword in keys)):
                    keys.append(keyword)

        # Elimino basicos
        caracteres_especiales = "?¿/-€"
        for caracter in caracteres_especiales:
            if(caracter in keys):
                keys.remove(caracter)

        # Genero las permutaciones
        todos_los_combos = []
        combos_str = []
        for i in range(len(keys) + 1):
            combinations_object = combinations(keys, i)
            combinations_list = list(combinations_object)
            todos_los_combos += combinations_list

        for combo in todos_los_combos:
            if(len(combo) > 1):
                cadena = " ".join(combo)
                for keyword in busqueda.keywords:
                    if(keyword in cadena):
                        combos_str.append(cadena)
                        break
        print(f"[Comp-CX] Generadas {len(combos_str)} permutaciones. ")
        if(len(combos_str) > 40):
            print(f"[Comp-CX] Se han generado demasiadas permutaciones. Se probará solo con el título. ")
            combos_str = [articulo.titulo]

        return combos_str

    def __generarDiccionarioCex(self, articulo, combinaciones, busqueda):

        diccionario_resultados = {}
        # dicc[clave] = valor

        # Abro el rango en búsqueda en combinaciones...
        precio_max = articulo.precio *((1+busqueda.exclusiones.multiplicador_maximo) * 2)
        precio_min = articulo.precio * (busqueda.exclusiones.multiplicador_minimo / 2)

        # Pruebo con todas las combinaciones
        for combinacion in combinaciones:
            url = self.__getURL(combinacion, precio_min, precio_max)

            # Abro ventana
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.execute_script('window.open("about:blank", "_blank");')
            self.driver.switch_to.window(self.driver.window_handles[-1])

            # Cargo búsqueda
            self.driver.get(url)

        # Ahora voy de atrás hacia adelante
        combinaciones.reverse()

        for combinacion in combinaciones:

            self.driver.switch_to.window(self.driver.window_handles[-1])

            # Si sale el rollo del sorteo, lo cierro.
            if(self.__existeElemento(path_sorteo_cex)):
                getByXpath(self.driver, path_sorteo_cex).click()

            try:
                path_resultados = '/html/body/div[1]/div[2]/div[5]/div[1]/div[2]/div/div[1]/p/span[1]'

                # Espero hasta que el botón esté renderizado
                espera = WebDriverWait(self.driver, 180)
                espera.until(EC.visibility_of_element_located(
                    (By.XPATH, path_resultados)))

                # Recupero resultados
                valor = int(self.driver.find_element_by_xpath(
                    path_resultados).text)

                # Añado al dict si es distinto de 0
                if(valor > 0):
                    diccionario_resultados[combinacion] = valor
            except Exception as e:
                pass
            self.driver.execute_script('''window.close();''')

        return diccionario_resultados

    def compararArticuloCex(self, articulo, busqueda, precios_float):

        # Umbral de minimo y máximo en la comparación
        precio_minimo_aceptable = float(articulo.precio) * busqueda.exclusiones.multiplicador_minimo
        precio_maximo_aceptable = float(articulo.precio) * (1+busqueda.exclusiones.multiplicador_maximo)


        precio_max = precio_maximo_aceptable * 2
        precio_min = precio_minimo_aceptable / 2

        print(f"[Comp-CX] Comparando artículo {articulo.titulo} contra Cex en rango [{precio_minimo_aceptable},{precio_maximo_aceptable}]... ")

        combinaciones = self.__generarPermutaciones(articulo, busqueda)

        diccionario = self.__generarDiccionarioCex(articulo, combinaciones, busqueda)

        if(len(diccionario) > 0):
            menor_combinacion = min(diccionario, key=diccionario.get)


            # Cargo la web con menor cantidad de resultados =! 0, es decir
            # la que más se aproxima al titulo del artículo estudiado

            url = self.__getURL(menor_combinacion, precio_min, precio_max)

            # Cargo búsqueda
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(url)

            # Extraigo precios

            espera = WebDriverWait(self.driver, 20)
            espera.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "priceTxt")))
            precios = self.driver.find_elements_by_class_name("priceTxt")

            for precio in precios:
                precio_texto = precio.text.lower()
                if("vendemos" in precio_texto):
                    precio_float = float(precio_texto.replace(
                        "vendemos", "").replace("€", ""))
                    if(precio_float > precio_minimo_aceptable and precio_float < precio_maximo_aceptable):
                        precios_float.append(precio_float)

        print(f"[Comp-CX] Finalizada comparación de {articulo.titulo} en Cex. ")
        # Finalizo este driver.
        self.driver.quit()



