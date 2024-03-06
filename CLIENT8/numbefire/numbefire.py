import requests
from bs4 import BeautifulSoup
import pandas as pd 
def dataframe_numbefire() :
    url = "https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "fr,fr-FR;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Referer": "https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections",
    }

    # Obtenir la réponse du site Web
    response = requests.get(url, headers=headers)
    player_df = extract_player_data(response.text)
    return player_df

# Analyser le contenu HTML et extraire les données
def extract_player_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Définir les noms des colonnes pour le DataFrame
    fieldnames = ['Name', 'Position', 'Team', 'FP', 'Min', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO', '3PM']
    # Initialiser une liste vide pour stocker les données extraites
    player_data = []
    
    player_rows = soup.find_all('tr', {'data-player-id': True})
    
    for row in player_rows:
        player_name = row.find('a', class_='full').text.strip()
        position = row.find('span', class_='player-info--position').text.strip()
        team = row.find('div', class_='player-info--game-info').find_all('span', class_='team-player__team')[0].text.strip()
        opponent = row.find('div', class_='player-info--game-info').find_all('span', class_='team-player__team')[1].text.strip()
        gametime = row.find('span', class_='gametime').text.strip()
        fp = row.find('td', class_='fp').text.strip()
        stats = row.find_all('td')[4:]  # Assuming the first four td elements are not stats

        # Collecting stats data
        stats_data = [stat.text.strip() for stat in stats]
        
        player_data.append({
            'Name': player_name,
            'Position': position,
            'Team': f"{team} vs {opponent}",
            'FP': fp,
            'Min': stats_data[0],
            'PTS': stats_data[1],
            'REB': stats_data[2],
            'AST': stats_data[3],
            'STL': stats_data[4],
            'BLK': stats_data[5],
            'TO': stats_data[6],
            '3PM': stats_data[7]
        })
    df = pd.DataFrame(player_data, columns=fieldnames)
    numeric_columns = ['Min', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO', '3PM']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Arrondir toutes les colonnes numériques à deux décimales
    df[numeric_columns] = df[numeric_columns].round(2)    
    return df

