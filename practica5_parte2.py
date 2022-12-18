# Practica 5 - Parte 2 - Web Scraping


# importamos librerias necesarias
from bs4 import BeautifulSoup
import requests
import signal
import sys
import re

# definimos la funcion para salir del programa
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


# definimos la funcion para extraer los datos
def extract(url):
    page = requests.get(url).content
    return page


def transform(page):
    # pasamos la pagina a un objeto BeautifulSoup
    soup = BeautifulSoup(page, 'html.parser')

    # buscamos las cajitas que nos interesan donde se encuentran las
    # cuotas de los proximos partidos

    # buscamos los siguientes tags:
    # <div onclick="location.href='/cuotas/boston-celtics-orlando-magic-5705140/'" class="cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative">

    divs = soup.find_all('div', {'class': 'cursor-pointer border rounded-md mb-4 px-1 py-2 flex flex-col lg:flex-row relative'})

    # Ahora nos vamos a guardar unicamente aquellos que nos interesan, aquellos
    # donde aparecen: 'Los Angeles Lakers'

    partidos = {}

    for div in divs:
        if re.search('Los Angeles Lakers', div.text): # otra forma es decir div.get('onclick')
            fecha = div.find('span', {'class': 'text-sm text-gray-600 w-full lg:w-1/2 text-center dark:text-white'}).text.strip('\n')
            equipos = div.find('a', {'class': ''}).text.strip('\n')
            cuotas = div.find_all('span', {'class': 'px-1 h-booklogosm font-bold bg-primary-yellow text-white leading-8 rounded-r-md w-14 md:w-18 flex justify-center items-center text-base'})
            cuota1, cuota2 = float(cuotas[0].text), float(cuotas[1].text)
            equipo1, equipo2 = equipos.split(' - ')

            if cuota1 < cuota2:
                favorito = equipo1
            else:
                favorito = equipo2
            partidos[equipos] = {'fecha': fecha, 
                                    'Equipo1': equipo1, 'Equipo2': equipo2, 
                                    'Cuota1': cuota1, 'Cuota2': cuota2, 
                                    'Favorito': favorito}
    
    return partidos


def load(partidos):
    NEGRITA_AZUL = '\033[1;34m'
    NEGRITA_AMARILLO = '\033[1;33m'
    NEGRITA_BLANCO = '\033[1;37m'
    RESET = '\033[0m'

    print('\n')
    for partido in partidos:
        print(f"{NEGRITA_BLANCO}{partido} -- {partidos[partido]['fecha']} {RESET}")
        print(f"{NEGRITA_AZUL}     - {partidos[partido]['Equipo1']} -- Cuota: {partidos[partido]['Cuota1']} {RESET}")
        print(f"{NEGRITA_AZUL}     - {partidos[partido]['Equipo2']} -- Cuota: {partidos[partido]['Cuota2']} {RESET}")
        print(f"{NEGRITA_AMARILLO}     Favorito: {partidos[partido]['Favorito']} {RESET}\n")

if __name__ == '__main__':
    URL = 'https://www.sportytrader.es/cuotas/baloncesto/'
    signal.signal(signal.SIGINT, signal_handler)

    page = extract(URL)
    partidos = transform(page)
    load(partidos)

