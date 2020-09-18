class PreciosArticulo():
    def __init__(self, id_articulo, precios_wp, precios_cc, precios_cex):
        self.id_articulo = id_articulo
        self.precios_wp = precios_wp
        self.precios_cc = precios_cc
        self.precios_cex = precios_cex

    def __str__(self):
        cadena = f"Precios de {self.id_articulo}:\n" \
                 f"Wallapop: {self.precios_wp},\n" \
                 f"Cash Converters: {self.precios_cc}\n" \
                 f"Cex: {self.precios_cex}"

        return cadena

if __name__ == "__main__":
    precios = PreciosArticulo(5,
                             [1,2,3,4],
                             [5,6,7,8],
                             [9,10,11,12]
                             )
    print(precios)