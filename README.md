# PracticaB5
## Practica Bloque 5: API y Webscrapping
### Hecho por: Lara Ocón Madrid

Esta práctica consiste en dos ETL que extraen informacion importante de un equipo de la NBA (en mi caso he decidido hacerlo de Los Angeles Lakers), analizan dicha informacion y la cargan o bien por pantalla o en formato pdf para visualizar las estadísticas más relevantes del equipo en la temporada 2022-2023.

Antes de hacer nada es necesario ejecutar el comando: 'pip install -r requirements.txt' para tener instaladas todas las librerías necesarias.

1) La primera ETL (ETL_API.py) extrae datos de distintas API, accediendo a la informacion de los lakers, y cargando dicha informacion en formato pdf. La primera página del pdf contiene información a nivel de equipo, mientras que la segunda página habla acerca de sus jugadores.

Para ejecutar dicha ETL es necesario introducir el siguiente comando: 'python3 ETL_API.py'.

2) La segunda ETL (ETL_Webscrapping) accede a una pagina web donde se muestran las cuotas para los proximos partidos de la NBA y muestra por pantalla solo aquellas del equipo que nos interese (mediante un input preguntamos el equipo del cual mostrar las cuotas, esto lo he hecho dado que en un principio solo mostraba las de los Lakers, pero a fecha 3 de enero, en la pagina no se mostraban partidos para los lakers de forma que el programa no mostraba nada).

Para ejecutar la segunda ETL es necesario introducir el siguiente comando: 'python3 ETL_Webscrapping.py'.


