import requests
from datetime import date
import pandas as pd
# URL de la requête
def dataframe_rotowire() : 
    url = "https://www.rotowire.com/basketball/tables/projections.php"
    # Obtenir la date d'aujourd'hui
    today_date = date.today()
    # Formater la date au format AAAA-MM-JJ
    formatted_date = today_date.strftime("%Y-%m-%d")
    # Paramètres de la requête
    params = {
        "type": "daily",
        "pos": "ALL",
        "date": formatted_date,
    }

    # En-têtes de la requête
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "Accept": "*/*",
        "Cookie": "__qca=P0-242423805-1708912192943; PHPSESSID=4aea43d87177de10f6acecc69ab658d0; _gcl_au=1.1.215483635.1708912191; _fbp=fb.1.1708912191176.1075724489; cookie=6d34511e-3174-4434-973a-3086c20d56a8; _au_1d=AU1D-0100-001708912193-J1ANEKBX-RF8T; _cc_id=c854bb62c95aa4b1e6ccc4aac10e30d8; panoramaId_expiry=1709516993692; panoramaId=f91ccb8ba4d2af085c2357b79fac185ca02cb9c51a5b25ef8a326fd99fd9fb2d; panoramaIdType=panoDevice; _gid=GA1.2.2133691631.1709228271; usprivacy=1NNN"
    }
    try:
        # Envoi de la requête GET
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Cela va lever une exception pour les codes 4xx et 5xx
        
        # Charger la réponse JSON
        data = response.json()

        players_data = data  # Assurez-vous que cette ligne accède correctement à vos données réelles.
        
        # Noms des colonnes basés sur les clés JSON attendues
        csv_columns = ["player", "team", "opp", "pos", "MIN", "PTS", "REB", "AST", "STL", "BLK", "TO", "FGM", "FGA", "FGPCT", "THREEPM", "THREEPA", "THREEPPCT", "FTM", "FTA", "FTPCT", "OREB", "DREB"]
        
        # Création du DataFrame
        df = pd.DataFrame(players_data, columns=csv_columns)
        num_cols = ["MIN", "PTS", "REB", "AST", "STL", "BLK", "TO", "FGM", "FGA", "FGPCT", "THREEPM", "THREEPA", "THREEPPCT", "FTM", "FTA", "FTPCT", "OREB", "DREB"]
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

        print("DataFrame rotowire created successfully")
        return df
    except requests.RequestException as e:
        print(f"Erreur de requête: {e}")
    except ValueError:  # Cette exception est levée pour les erreurs de décodage JSON
        print("Erreur lors de la conversion de la réponse en JSON")