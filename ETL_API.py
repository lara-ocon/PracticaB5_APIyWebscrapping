"""
Practica Bloque 5 - Parte 1 - ETL API
En esta primera parte de la práctica, vamos a extraer datos de una API de la NBA, para así transformar los datos que nos interesan
y más tarde cargar chicos datos en un pdf donde se ilustren las estadisticas del equipo y su informacion mas importante de forma visual.

"""

# cargamos las librerias necesarias
import requests
import json
import pandas as pd
from fpdf import FPDF
import os
import regex as re

# guardamos los colores que vamos a usar al imprimir por pantalla el progreso de la ETL
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# extraccion de datos
def extract():

    # leemos la key que hemos guardado en un fichero txt
    key = eval(open('config.txt', 'r').read())['hash']

    # cargamos las APIS que vamos a usar
    standings = requests.get(
        f'https://api.sportsdata.io/v3/nba/scores/json/Standings/2023?key={key}').json()
    players = requests.get(
        f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/LAL?key={key}').json()
    players_photos = requests.get(
        f'https://api.sportsdata.io/v3/nba/scores/json/Players?key={key}').json()

    return standings, players, players_photos

# pasamos los datos a ficheros json para poder trabajar con ellos
def load_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def transform(team_season_stats, players):
    # Primero vamos a hacer una tabla con los datos de los lakers de la season
    # copiamos esta tabla (https://www.google.com/search?q=conference+rank+nba&oq=conference+rank+nba&aqs=chrome..69i57j0i22i30l7.3546j0j7&sourceid=chrome&ie=UTF-8#cobssid=s&sie=lg;/g/11rp7bmb2v;3;/m/05jvx;st;fp;1;;;)
    # pasamos el json a un dataframe con la informacion importante, para ello
    # buscamos el diccionario que nos interesa
    for team in team_season_stats:
        if team['Key'] == 'LAL':
            lakers = team

    # ahora creamos el dataframe con los datos que vamos a usar
    lakers_df = crear_df_lakers(lakers)

    # ahora recreamos la tabla de google con los jugadores de los lakers
    # https://www.espn.com/nba/team/stats/_/name/lal/los-angeles-lakers

    lakers_players_df = crear_df_players(players)

    return lakers_df, lakers_players_df

def crear_df_lakers(lakers):
    # vamos a hacer un dataframe donde el nombre del indice sea 'Equipo' y el 
    # primer valor sea 'Los Angeles Lakers'
    lakers_df = pd.DataFrame()
    lakers_df['Equipo'] = ['Los Angeles Lakers']
    # lo establecemos como el index
    lakers_df.set_index('Equipo', inplace=True)

    # primero añadimos la columna V
    lakers_df['V'] = lakers['Wins']
    # ahora añadimos la columna D
    lakers_df['D'] = lakers['Losses']
    # ahora añadimos la columna %
    lakers_df['%'] = lakers['Percentage']
    # ahora añadimos la columna PD (Points Differential)
    lakers_df['PD'] = lakers['GamesBack']
    # ahora añadimos la columna Conf
    lakers_df['Conf'] = f"{lakers['ConferenceWins']}-{lakers['ConferenceLosses']}"
    # ahora añadimos la columna casa
    lakers_df['Casa'] = f"{lakers['HomeWins']}-{lakers['HomeLosses']}"
    # ahora añadimos la columna fuera
    lakers_df['Fuera'] = f"{lakers['AwayWins']}-{lakers['AwayLosses']}"
    # ahora la columna U10
    lakers_df['U10'] = f"{lakers['LastTenWins']}-{lakers['LastTenLosses']}"
    # ahora la columna Racha (Streak)
    lakers_df['Racha'] = lakers['StreakDescription']

    return lakers_df

def crear_df_lakers2(lakers):
    # pasamos directamente el diccionario a un dataframe
    lakers_df = pd.DataFrame(lakers, index=[0])
    lakers_df.set_index('Name', inplace=True)
    # ahora nos quedamos solo con las columna interesantes
    interesting_columns = ['Wins', 'Losses', 'Percentage', 'GamesBack']
    lakers_df = lakers_df[interesting_columns]
    return lakers_df


def crear_df_players(players):
    # primero creamos un df con el index como el nombre de los jugadores
    lakers_players_df = pd.DataFrame(players)
    lakers_players_df.set_index('Name', inplace=True) # ponemos que el index sean los nombres
    # para cada jugador nos quedamos con solo la informacion importante
    # y renombramos las columnas
    column_names = {'Position': 'POS', 'Games': 'GP', 'Minutes': 'MIN', 'Points': 'PTS', 'OffensiveReboundsPercentage': 'OR', 'DefensiveReboundsPercentage': 'DR', 'TotalReboundsPercentage': 'REB', 'AssistsPercentage': 'AST', 'StealsPercentage': 'STL', 'BlocksPercentage': 'BLK', 'TurnOversPercentage': 'TO', 'PersonalFouls': 'PF'}
    # despues añadiremos otra columna que sera 'AST/TO', relacion entre asistencias y perdidas por juego
    lakers_players_df = lakers_players_df[list(column_names.keys())]
    lakers_players_df.rename(columns=column_names, inplace=True)
    # ahora añadimos la columna 'AST/TO', con 2 decimales
    lakers_players_df['AST/TO'] = (lakers_players_df['AST'] / lakers_players_df['TO']).round(2)


    # ordenamos el df por puntos
    lakers_players_df.sort_values(by='PTS', ascending=False, inplace=True)
    
    return lakers_players_df


def load_lakers_logo():
    # cargamos la imagen del logo de los lakers
    if not os.path.exists('lakers_logo.png'):
        # si no existe la descargamos
        with open('lakers_logo.png', 'wb') as f:
            f.write(requests.get('https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Los_Angeles_Lakers_logo.svg/1200px-Los_Angeles_Lakers_logo.svg.png').content)

def load_images(players_photos, players):
    if not os.path.exists('player_images'):
        os.mkdir('player_images')

    # aqui cargamos las fotos de perfil de los 5 mejores jugadores en cada categoria para despues
    # incluirlas en el pdf
    for player in players:
        found = False
        for player_info in players_photos:

            if re.search(player['player'], player_info['DraftKingsName'], re.I):
                found = True
                # si encontramos el jugador en la lista de fotos, guardamos la imagen png en una carpeta
                with open(f"player_images/{player['player']}.png", 'wb') as f:
                    f.write(requests.get(player_info['PhotoUrl']).content)
                break
        if not found:
            # si no encontramos la foto, ponemos una por defecto
            with open(f"player_images/{player['player']}.png", 'wb') as f:
                f.write(requests.get('https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/480px-No_image_available.svg.png').content)
                


def crear_pdf(lakers_df, lakers_players_df, players_photos):
    # ahora creamos el pdf, primero mostramos la tabla de los lakers
    # y en otra pagina la tabla con los jugadores
    pdf = FPDF()

    # Pagina 1 ======================================================#
    pdf.add_page()
    pdf.set_font('Arial', 'B', 20) # fuente, negrita, tamaño
    pdf.cell(40, 10, 'Los Angeles Lakers') # ancho, alto, texto
    pdf.ln(10) # salto de linea
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(30, 10, 'Season 2022-2023') 
    pdf.ln(30) # salto de linea

    # ahora creamos la tabla1 con el dataframe lakers_df,
    # primero ponemos la cabecera, todas las celdas estaran
    # con su borde, y el fondo en naranja claro

    pdf.set_font('Arial', 'B', 8)
    pdf.set_fill_color(255, 184, 51) # naranja claro
    # ahora creamos la cabecera y centramos el texto
    # añadimos una celda vacia para que quede mas centrado
    pdf.cell(15, 10, '')
    pdf.cell(20, 10, 'Equipo', border=True, fill=True, align='C') # ancho, alto, texto
    for column in lakers_df.columns:
        pdf.cell(15, 10, column, border=True, fill=True, align='C')
    pdf.ln(10)

    # comenzamos a rellenar la tabla con los datos
    # primero ponemos el nombre del equpo que será la unica celda que
    # pondremos con fondo morado
    pdf.set_fill_color(135, 24, 253) # morado
    pdf.cell(15, 10, '')
    pdf.cell(20, 10, 'Lakers', border=True, fill=True, align='C')

    for column in lakers_df.columns:
        pdf.cell(15, 10, str(lakers_df[column][0]), border=True, align='C')

    # añadimos una imagen a la derecha y arriba (logo lakers)
    load_lakers_logo()
    pdf.image('lakers_logo.png', 150, 10, 50, 30) # imagen, x, y, ancho, alto


    # Pagina 2 ======================================================#

    # ahora saltamos de pagina para hablar acerca de los jugadores
    pdf.add_page()
    pdf.set_font('Arial', 'B', 20) # fuente, negrita, tamaño
    pdf.cell(40, 10, 'Los Angeles Lakers') # ancho, alto, texto
    pdf.ln(10) # salto de linea
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(30, 10, 'Season 2022-2023 Players')
    pdf.ln(30) # salto de linea

    # añadimos una imagen a la derecha y arriba (logo lakers)
    pdf.image('lakers_logo.png', 150, 10, 50, 30) # imagen, x, y, ancho, alto

    # ahora creamos la tabla2 con el dataframe lakers_players_df,
    # primero ponemos la cabecera, todas las celdas estaran
    # con su borde, y el fondo en naranja claro

    pdf.set_font('Arial', 'B', 7)
    pdf.set_fill_color(255, 184, 51) # naranja claro
    # ahora creamos la cabecera y centramos el texto
    # añadimos una celda vacia para que quede mas centrado
    pdf.cell(15, 7, '')
    pdf.cell(30, 7, 'Jugador', border=True, fill=True, align='C') # ancho, alto, texto


    for column in list(lakers_players_df.columns):
        pdf.cell(10, 7, column, border=True, fill=True, align='C')
    pdf.ln(7)

    pdf.set_fill_color(180, 110, 253) # morado
    for player in lakers_players_df.index:
        pdf.cell(15, 7, '')
        pdf.cell(30, 7, player, border=True, align='C', fill=True)
        for column in lakers_players_df.columns:
            pdf.cell(10, 7, str(lakers_players_df[column][player]), border=True, align='C')
        pdf.ln(7)
    

    # ahora hablamos de los lideres
    # primero una celda con el lider en puntos
    # pondremos Puntos en pequeño arriba a la izquierda
    # debajo la foto del jugador, y a su derecha su nombre y sus puntos
    pdf.ln(20)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(15, 7, '')
    pdf.cell(30, 10, 'Líderes')
    pdf.ln(10)

    tops = {'PTS': 'Puntos', 'REB': 'Rebotes', 'AST': 'Asistencias', 'STL': 'Robos', 'BLK': 'Bloqueos'}
    bests = {}
    for top, category in tops.items():
        best_player = lakers_players_df[top].idxmax()
        bests[category] = {"player" : best_player,
                            "points" : str(lakers_players_df[top][best_player])
                            }

    # 1) Ponemos la letra en arial , negrita, tamaño 6, color = gris
    pdf.set_font('Arial', 'B', 6)
    pdf.set_text_color(128, 128, 128)

    pdf.cell(15, 5, '')
    for top in tops.values():
        # ponemos la caracteristica del lider (puntos, rebotes...) y ponemos 
        # linea de celda solo izquierda, arriba y a la dereca
        pdf.cell(32, 5, top, border='LTR', align='L')
    pdf.ln(5)

    #2) Ponemos el nombre del jugador debajo de estas celdas y 
    # centramos el texto a la izquierda
    pdf.set_font('Arial', 'B', 6)
    pdf.set_text_color(0, 0, 0)

    pdf.cell(15, 5, '')
    for top in tops.values():
        pdf.cell(32, 5, bests[top]['player'], border='LR', align='R')
    pdf.ln(5)

    # 3) Añadimos los puntos en grande debajo de cada nombre de jugador
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(15, 5, '')
    for top in tops.values():
        pdf.cell(32, 5, bests[top]['points'], border='LRB', align='R')
    pdf.ln(5)

    # 4) Añadimos las imagenes de los jugadores en sus lugares correspondientes, para ello accedemos 
    # al df donde tenemos los perfiles de los juagdores y cogemos la url de la imagen
    load_images(players_photos, bests.values()) # cargamos las fotos de perfil de los jugadores
    pdf.cell(15, 5, '')
    for player in bests.values():
        pdf.image(f'player_images/{player["player"]}.png', pdf.get_x()+1, pdf.get_y()-11, 10, 10)
        pdf.cell(32, 5, '')


    # guardamos el pdf
    pdf.output('lakers.pdf')


if __name__ == '__main__':

    # Extraemos los datos de la API
    # imprimimos en azul para que se vea que se esta ejecutando
    print(bcolors.OKBLUE + '\nExtrayendo datos de la API...\n' + bcolors.ENDC)
    team_season_stats, players, players_photos = extract()
    print(bcolors.OKGREEN + 'Datos extraidos correctamente\n' + bcolors.ENDC)
    print('\n')

    # Cargamos los datos en un json para poder tenerlos en local
    load_to_json(team_season_stats, 'team_season_stats.json')
    load_to_json(players, 'players.json')
    load_to_json(players_photos, 'players_photos.json')

    # Transformamos los datos obteniendo la informacion que nos interesa
    print(bcolors.OKBLUE + '\nTransformando datos...\n' + bcolors.ENDC)
    lakers_df, lakers_players_df = transform(team_season_stats, players)
    print(bcolors.OKGREEN + 'Datos transformados correctamente\n' + bcolors.ENDC)
    print('\n')

    # Cargamos los datos en un pdf
    print(bcolors.OKBLUE + '\nCargando datos en un pdf...\n' + bcolors.ENDC)
    crear_pdf(lakers_df, lakers_players_df, players_photos)
    print(bcolors.OKGREEN + 'Datos cargados correctamente en el pdf\n' + bcolors.ENDC)

