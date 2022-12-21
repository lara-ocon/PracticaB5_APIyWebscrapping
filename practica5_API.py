

# Practica 5 - Parte 1
# Exraer datos de una API:


# cargamos las librerias necesarias
import requests
import json
import pandas as pd
import fpdf

# extraccion de datos
def extract():

    # leemos la key que hemos guardado en un fichero json
    key = json.load(open('fichero.json'))['cod']

    # cargamos las APIS que vamos a usar
    standings = requests.get(
        f'https://api.sportsdata.io/v3/nba/scores/json/Standings/2023?key={key}').json()
    players = requests.get(
        f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/LAL?key={key}').json()

    return standings, players

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

    print(lakers_df)
    print(lakers_players_df)

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


def crear_pdf(lakers_df, lakers_players_df):
    # ahora creamos el pdf, primero mostramos la tabla de los lakers
    # y en otra pagina la tabla con los jugadores
    pdf = fpdf.FPDF()
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
    pdf.image('images/lakers_logo.png', 150, 10, 50, 30) # imagen, x, y, ancho, alto


    # ahora saltamos de pagina para hablar acerca de los jugadores
    pdf.add_page()
    pdf.set_font('Arial', 'B', 20) # fuente, negrita, tamaño
    pdf.cell(40, 10, 'Los Angeles Lakers') # ancho, alto, texto
    pdf.ln(10) # salto de linea
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(30, 10, 'Season 2022-2023 Players')
    pdf.ln(30) # salto de linea

    # ahora creamos la tabla2 con el dataframe lakers_players_df,
    # primero ponemos la cabecera, todas las celdas estaran
    # con su borde, y el fondo en naranja claro

    pdf.set_font('Arial', 'B', 7)
    pdf.set_fill_color(255, 184, 51) # naranja claro
    # ahora creamos la cabecera y centramos el texto
    # añadimos una celda vacia para que quede mas centrado
    pdf.cell(15, 7, '')
    pdf.cell(30, 7, 'Jugador', border=True, fill=True, align='C') # ancho, alto, texto

    print(list(lakers_players_df.columns))
    print(list(lakers_players_df.index))

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


    # añadimos una imagen a la derecha y arriba (logo lakers)
    pdf.image('images/lakers_logo.png', 150, 10, 50, 30) # imagen, x, y, ancho, alto

    # cargamos el pdf en un fichero
    pdf.output('lakers.pdf', 'F')
    


team_season_stats, players = extract()
load_to_json(team_season_stats, 'team_season_stats.json')
load_to_json(players, 'players.json')
lakers_df, lakers_players_df = transform(team_season_stats, players)
crear_pdf(lakers_df, lakers_players_df)

