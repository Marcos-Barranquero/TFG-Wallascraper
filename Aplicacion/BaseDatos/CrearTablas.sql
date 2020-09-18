drop table if exists Articulos;
drop table if exists PreciosArticulos;
drop table if exists BusquedasWallapop;
drop table if exists Usuarios;
drop table if exists Exclusiones;

create table Usuarios
(
    id_telegram integer not null PRIMARY KEY,
    email text,
    contrasena text,
    codigo_postal text NOT NULL,
    mensaje text
);

create table Articulos
(
    id_articulo integer not null,
    id_busqueda integer not null,
    titulo text not null,
    descripcion text not null,
    precio int not null,
    enlace text not null,
    FOREIGN KEY(id_busqueda) REFERENCES BusquedasWallapop(id_busqueda)
);

create table PreciosArticulos
(
    id_articulo integer not null,
    id_busqueda integer not null,
    precios_wp text,
    precios_cc text,
    precios_cex text,
    FOREIGN KEY(id_articulo) REFERENCES Articulos(id_articulo),
    FOREIGN KEY(id_busqueda) REFERENCES BusquedasWallapop(id_busqueda)
);

create table BusquedasWallapop
(
    id_telegram integer,
    id_busqueda integer PRIMARY KEY,
    keywords text,
    comparar_automaticamente boolean,
    enviar_mensaje_auto boolean,
    precio_min int not null,
    precio_max int not null,
    radio text not null,
    order_by text not null,
    FOREIGN KEY(id_telegram) REFERENCES Usuarios(id_telegram)
);

create table Exclusiones
(
    id_busqueda integer not null PRIMARY KEY,
    lista_keywords_titulo_excluyentes text,
    lista_keywords_descripcion_excluyentes text,
    lista_keywords_descripcion_reincluyentes text,
    multiplicador_maximo float,
    multiplicador_minimo float,
    porcentaje_considerado_chollo float,
    FOREIGN KEY(id_busqueda) REFERENCES BusquedasWallapop(id_busqueda)
);