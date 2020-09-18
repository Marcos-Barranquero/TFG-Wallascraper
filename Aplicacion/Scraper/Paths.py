from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Cookies
path_boton_cookies = '/html/body/div[1]/div/div/div/div/div/div[3]/button[2]'

# Ubicacion
path_boton_ubicacion = '//*[@id="quick-filters"]/div/div[2]/div[4]/div[1]/div[2]'
path_campotexto_ubicacion = '//*[@id="quick-filters"]/div/div[2]/div[4]/div[2]/div[2]/div/div[1]/div/div[1]/input'
path_resultados_busqueda_ubicacion = '/html/body/div[3]/div/div[2]/div[4]/div[2]/div[2]/div/div[1]/div/div[2]/div/div'
path_aplicar_ubicacion = '/html/body/div[3]/div/div[2]/div[4]/div[2]/div[3]/div/button[2]'
path_aplicar_ubicacion = '/html/body/div[8]/div/div[2]/div[4]/div[2]/div[3]/div/button[1]'


# Login
path_primer_boton_login = '/html/body/header/div[2]/div[4]/button'
path_primer_boton_login_headless = '/html/body/div[5]/div/div[5]'
path_segundo_boton_login = '/html/body/div[2]/div/div[2]/div[1]/div[3]/div/a[1]'
path_segundo_boton_login_dos = '/html/body/div[6]/div/div[2]/div[1]/div[3]/div/a[1]'
path_segundo_boton_login_tres = '/html/body/div[5]/div/div[2]/div[1]/div[3]/div/a[1]'

path_input_usuario_login = '/html/body/div[2]/div/div[2]/div[1]/form/div[1]/div/input'
path_input_usuario_login = '/html/body/div[2]/div/div[2]/div[1]/form/div[1]/div/input'
path_input_password_login = '/html/body/div[2]/div/div[2]/div[1]/form/div[2]/div/input'
path_tercer_boton_login = '/html/body/div[2]/div/div[2]/div[1]/form/div[3]/button'

# Probar login
path_zona = '/html/body/tsl-root/tsl-topbar/div[2]/a[3]/span'

# Envio de mensaje automático...
path_boton_chat = '/html/body/div[3]/div[2]/div[2]/div[2]/div[1]/div[1]/div/div[2]/a[2]'
path_chat_textarea = '/html/body/tsl-root/tsl-chat/div/div[2]/tsl-current-conversation/div/div[1]/div/div[3]/tsl-input/form/div/div[1]/textarea'
path_boton_enviar_chat = '/html/body/tsl-root/tsl-chat/div/div[2]/tsl-current-conversation/div/div[1]/div/div[3]/tsl-input/form/div/div[2]/a'

# Paths artículos wp...
path_cardboard_articulos = '//*[@id="main-search-container"]'


def path_titulo_articulos(i):
    path_titulo_articulos = f'//*[@id="main-search-container"]/div[{i}]/a/div/div[2]/span'
    return path_titulo_articulos

def path_descripcion_articulos(i):
    path_descripcion_articulos = f'//*[@id="main-search-container"]/div[{i}]/a/div/div[2]/p'
    return path_descripcion_articulos

def path_precio_articulos(i):
    path_precio_articulos = f'//*[@id="main-search-container"]/div[{i}]/a/div/div[2]/div/span'
    return path_precio_articulos

def path_enlace_articulos(i):
    path_enlace_articulos = f'//*[@id="main-search-container"]/div[{i}]/a'
    return path_enlace_articulos



# Paths comparación cash converters
path_cookies_cc = '/html/body/div[2]/div[3]/div/button'

selector_css_cc = "span[class='price-sales price']"

path_sorteo_cc = '/html/body/div[2]/div[1]/button'


# Paths comparación del CEX
path_sorteo_cex = '/html/body/div[1]/div[2]/div[1]/button'
class_sorteo_cex = 't039-button t039-close'

def getByXpath(driver, full_xpath):
    """ Devuelve el elemento asociado al xpath"""
    espera = WebDriverWait(driver, 15)
    elemento = espera.until(
        EC.visibility_of_element_located((By.XPATH, full_xpath)))

    return elemento




def aceptarCookies(driver):
    """ Acepta las cookies para poder renderizar por completo la web """
    # Cliqueo el botón de las cookies
    getByXpath(driver, path_boton_cookies).click()

def  cambiarUbicacion(driver, codigo_postal):
    """ Aunque envía la latitud y longitud por URL, no se puede cambiar a menos
    que se meta manualmente en su caja de búsqueda en la web. """
    getByXpath(driver, path_boton_ubicacion).click()
    getByXpath(driver, path_campotexto_ubicacion).send_keys(codigo_postal)
    #self.__getByXpath(path_resultados_busqueda_ubicacion).click()
    getByXpath(driver, "//label[@for='id-0-locationsSuggester']").click()
    #self.__getByXpath(path_aplicar_ubicacion).click()
    botones = driver.find_elements_by_xpath("//button[@class='QuickFilter__button QuickFilter__button--primary']")
    for boton in botones:
        if(boton.text.lower() == "aplicar"):
            boton.click()

def login(driver, ejecucion_en_bakcground, email, password):
        """ Se loguea con el usuario proporcionado en la web. """

        getByXpath(driver, path_primer_boton_login).click()

        # Pulso sobre el botón de login de la ventana emergente
        driver.find_elements_by_class_name('Welcome__btn-go-login-form')[0].click()

        # Escribo usuario
        getByXpath(driver, "//input[@name='email']").send_keys(email)

        # Escribo contraseña...
        getByXpath(driver, "//input[@name='password']").send_keys(password)

        # Pulso el botón de inicio de sesión
        getByXpath(driver, "//button[@id='sign-in-wallapop']").click()

def existeElemento(driver, xpath):
    return (len(driver.find_elements_by_xpath(xpath)) > 0)