import requests
import json
import pandas as pd
def dataframe_sportsline():
    url = 'https://www.sportsline.com/ui-gateway/v1/graphql'

    graphql_query = """
        query {
            fantasyCompetitorProjections(league: NBA) {
                columns {
                    field
                    label
                }
                expert
                league
                projections
            }
        }
    """

    payload = {
        "query": graphql_query
    }

    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://www.sportsline.com',
        'Referer': 'https://www.sportsline.com/college-basketball/expert-projections/simulation/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print('Requête réussie.')
        data = response.json()
        projections = data['data']['fantasyCompetitorProjections']['projections']
        
        # Définir les noms des colonnes
        csv_columns = ["PLAYER", "POS", "GAME", "DK", "FD", "PTS", "MIN", "FG", "FGA", "AST", "TRB", "DRB", "ORB", "BK", "ST", "TO", "FT"]
        
        # Créer un DataFrame vide avec les mêmes noms de colonnes
        df = pd.DataFrame(columns=csv_columns)
        
        # Remplir le DataFrame
        for projection in projections:
            row = {column: projection.get(column.lower(), '') for column in csv_columns}
            # Ajuster la valeur 'GAME' si nécessaire
            if 'matchup' in projection:
                game_teams = projection['matchup'].split('@')
                if len(game_teams) == 2:
                    row["GAME"] = f"{game_teams[0]}-{game_teams[1]}"
            df = df._append(row, ignore_index=True)
        
        print('DataFrame sportsline created successfully')
        # Définir les noms des colonnes
        csv_columns = ["PLAYER", "POS", "GAME", "DK", "FD", "PTS", "MIN", "FG", "FGA", "AST", "TRB", "DRB", "ORB", "BK", "ST", "TO", "FT"]
        df = df[csv_columns].apply(pd.to_numeric, errors='coerce').fillna(df)

        # Arrondir les colonnes numériques à deux décimales
        numeric_columns = ["DK", "FD", "PTS", "MIN", "FG", "FGA", "AST", "TRB", "DRB", "ORB", "BK", "ST", "TO", "FT"]
        df[numeric_columns] = df[numeric_columns].round(2)
        return df
    else:
        print('Échec de la requête :', response.status_code)
        print(response.text)