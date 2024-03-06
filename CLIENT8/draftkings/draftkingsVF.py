import requests
import pandas as pd
# URL de base pour les requêtes API
BASE_URL = 'https://sportsbook-nash-caon.draftkings.com/sites/CA-ON-SB/api/v5/eventgroups/42648/categories'

# Catégories et sous-catégories à interroger
CATEGORIES = [
    {'category_id': '1215', 'subcategory_id': '12488', 'name': 'Player Points', 'index': 0},
    {'category_id': '1216', 'subcategory_id': '12492', 'name': 'Player Rebounds', 'index': 0},
    {'category_id': '1217', 'subcategory_id': '12495', 'name': 'Player Assists', 'index': 0},
    {'category_id': '1218', 'subcategory_id': '12497', 'name': 'Player Threes', 'index': 0},
    {'category_id': '1293', 'subcategory_id': '13508', 'name': 'Player Defense', 'index': 0, 'subcategory_name': 'Steals'},
    {'category_id': '1293', 'subcategory_id': '13781', 'name': 'Player Defense', 'index': 4, 'subcategory_name': 'Steals + Blocks'},
    {'category_id': '1293', 'subcategory_id': '13780', 'name': 'Player Defense', 'index': 2, 'subcategory_name': 'Blocks'},
    {'category_id': '583', 'subcategory_id': '5001', 'name': 'Player Combos', 'index': 0, 'subcategory_name': 'PTS + REB + AST'},
    {'category_id': '583', 'subcategory_id': '9976', 'name': 'Player Combos', 'index': 1, 'subcategory_name': 'PTS + REB'},
    {'category_id': '583', 'subcategory_id': '9973', 'name': 'Player Combos', 'index': 2, 'subcategory_name': 'PTS + AST'},
    {'category_id': '583', 'subcategory_id': '9974', 'name': 'Player Combos', 'index': 3, 'subcategory_name': 'AST + REB'},
]
# En-têtes HTTP nécessaires pour les requêtes
HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'fr,fr-FR;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
    'Origin': 'https://sportsbook.draftkings.com',
    'Referer': 'https://sportsbook.draftkings.com/',
}

def fetch_data(category_id, subcategory_id):
    url = f"{BASE_URL}/{category_id}/subcategories/{subcategory_id}?format=json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Échec de la requête: {response.status_code}")
        return None
def process_data_with_index(data, category, index):
    processed_data = []
    if data and 'eventGroup' in data and 'offerCategories' in data['eventGroup']:
        for category_data in data['eventGroup']['offerCategories']:
            if category_data['name'] == category['name']:  # Correspondance exacte avec le nom de la catégorie principale
                offers = category_data['offerSubcategoryDescriptors'][index]['offerSubcategory']['offers']
                for offer in offers:
                    for player_offer in offer:
                        player_name = player_offer['label'].split(' ')[0] + " " + player_offer['label'].split(' ') [1]
                        for outcome in player_offer['outcomes']:
                            line = outcome['line']
                            odds = outcome['oddsAmerican']
                            # Utilisation conditionnelle de 'subcategory_name'
                            subcategory_name = category.get('subcategory_name', category['name'])  # Fallback sur 'name' si 'subcategory_name' n'existe pas
                            processed_data.append([player_name, subcategory_name, outcome['label'], line, odds])
    return processed_data
def consolidate_data(data):
    # Mappage des noms de catégories et de types aux abréviations spécifiées
    name_mapping = {
        'Player Points': 'pts',
        'Player Rebounds': 'reb',
        'Player Assists': 'ast',
        'Player Threes': '3s',
        'Player Defense_Steals': 'stl',
        'Player Defense_Blocks': 'blk',
        'Player Defense_Steals + Blocks': 'sb',
        'Player Combos_AST + REB': 'ar',
        'Player Combos_PTS + AST': 'pa',
        'Player Combos_PTS + REB': 'pr',
        'Player Combos_PTS + REB + AST': 'pra'
    }

    # Nouveau dictionnaire pour consolider les données par joueur
    players = {}
    for entry in data:
        player_name, category, type_, line, odds = entry

        # Remplacez 'Over' et 'Under' par 'O' et 'U' dans la clé de type
        type_ = type_.replace('Over', 'O').replace('Under', 'U')

        # Construisez les noms de colonnes en utilisant l'abréviation de la catégorie et le type modifié
        base_key = name_mapping.get(category, category.replace(' + ', '_').replace(' ', '_')) + "_" + type_
        line_key = f"{base_key}_Ligne"
        odds_key = f"{base_key}_Cotes"

        # Initialisez le dictionnaire pour le joueur si nécessaire
        if player_name not in players:
            players[player_name] = {"player": player_name}

        # Ajoutez ou mettez à jour les données pour ce joueur
        players[player_name].update({
            line_key: line,
            odds_key: odds
        })

    return players

def data_to_dataframe(players):
    # Création d'une liste pour stocker les données de chaque joueur
    data_for_df = []
    
    # Les en-têtes seront déterminés dynamiquement
    fieldnames = set()
    for player_data in players.values():
        fieldnames.update(player_data.keys())
    fieldnames = ['player'] + sorted(fieldnames - {'player'})  # 'Joueur' doit être le premier champ
    
    # Remplir la liste avec les données des joueurs
    for player_data in players.values():
        data_for_df.append(player_data)
    
    # Créer le DataFrame à partir de la liste des données
    df = pd.DataFrame(data_for_df, columns=fieldnames)
    
    return df

def dataframe_draftkings():
    all_data = []
    for category in CATEGORIES:
        data = fetch_data(category['category_id'], category['subcategory_id'])
        processed_data = process_data_with_index(data, category, category['index'])
        all_data.extend(processed_data)
    # Consolidez les données pour chaque joueur
    players_data = consolidate_data(all_data)
    # Convertir les données consolidées en DataFrame
    df = data_to_dataframe(players_data)
    return df
