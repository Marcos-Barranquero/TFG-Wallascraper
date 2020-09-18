# Imports de selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# Importo gestor del chromedriver directamente para no tener que pasar el path
from webdriver_manager.chrome import ChromeDriverManager

from Aplicacion.Scraper.Paths import *


class TestCredenciales:
    def __init__(self, usuario, ejecucion_en_background=False):

        self.ejecucion_en_bakcground = ejecucion_en_background

        # Ignoro errores de certificado que las webs luego se ponen muy pesadas
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--ignore-ssl-errors')
        self.options.add_argument("--start-maximized")
        self.options.add_argument("log-level=3")
        self.options.add_argument("--silent")

        if(ejecucion_en_background):
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--headless')
            self.options.add_argument("--window-size=1920x1080")

        self.usuario = usuario

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.options)

    def probarCredenciales(self):
        """ Método que devuelve True si los introducidos son correctos. """
        # Intento iniciar sesión, guardo resultado en exito
        exito = False

        try:
            # Cargo la URL
            self.driver.get("https://es.wallapop.com/search?")

            # Acepto cookies
            aceptarCookies(self.driver)
            print("[TESTER] Acepto cookies...")

            # Cambio ubicación
            cambiarUbicacion(self.driver, self.usuario.codigo_postal)
            print("[TESTER] Cambio ubicación...")

            login(self.driver, self.ejecucion_en_bakcground, self.usuario.email, self.usuario.password)
            print("[TESTER] Me logueo...")

            if(getByXpath(self.driver, path_zona).text == "Mi zona"):
                print("[TESTER] Credenciales correctos. ")
                exito = True
        except Exception as e:
             print("[TESTER] Error probando credenciales: ")
             print(e)
#
        finally:
            self.driver.quit()
            return exito
