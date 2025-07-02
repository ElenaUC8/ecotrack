# Ecotrack

La plicación consta de un backend desarrollado con Flask y un frontend construido con React y Vite.

## Ejecución backend

Primero, es necesario instalar Flask, dentro del directorio backend/app con el siguiente comando:

```
pipenv install Flask 
```
Después, se ejecuta en backendcon el siguiente comando:

```
pipenv run python app.py
```

## Ejecución frontend

Una vez tenemos el backend corriendo, en otra terminal, accedemos al directorio del frontend y ejecutamos: 

```
npm install
```
Y después ejecutamos el frontend con el siguiente comando:

```
npm run dev
```
Ahora accedemos a http://localhost:5173/, que es donde está almacenada la aplicación.

## Productos a buscar
Esta es la lista de los productos que se encuentran almacenados en la base de datos y sus códigos de barras para poder añadirlos a la lista de favoritos:

-111035002175 agua

-5449000000996 cocacola

-6111266962187 leche

-6111242106949 yogur

-7622210449283 galletas principe

-3017620425035 nutella

-6111184004129 mayonesa

-20724696 almendras

-8445290615350 salsa tomate

-5000157024671 judias

-6111203001467 mantequilla

-8715035110106 salsa de soja

-80052760 kinder

-3256540000698 pan leche

-50457250 ketchup

 Para añadir más productos a la base de datos, buscar en https://world.openfoodfacts.org/ y coger el código de barras del producto a añadir. Después, con el backend en ejecución, buscar la siguiente dirección: http://127.0.0.1:5000/api/products/search?barcode=(codigo de barras del producto a añadir)
 Ejemplo: Ejemplo: http://127.0.0.1:5000/api/products/search?barcode=5449000000996

 ## Emisiones CO2
 En la región a buscar las emisiones de CO2, hay que poner explícitamente "C.A. de Euskadi", ya que ésta es la única comunidad que existe en el archivo CSV y, por tanto, en la base de datos.
