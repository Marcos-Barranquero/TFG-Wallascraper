class Usuario():
    def __init__(self, id_telegram, email, password, codigo_postal, mensaje):
        # Id del usuario de telegram
        self.id_telegram = id_telegram

        # Credenciales
        self.email = email
        self.password = password

        #
        self.codigo_postal = codigo_postal

        # Mensaje que se envía automáticamente si se detecta chollo
        self.mensaje = mensaje

    def __str__(self):
        return f"[ID: {self.id_telegram}] - [LOGIN: {self.email}:{self.password}] - [MENSAJE: {self.mensaje}]"
