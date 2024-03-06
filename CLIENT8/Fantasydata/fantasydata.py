import requests
from datetime import date

import pandas as pd
# URL de la demande
def dataframe_fantasydata():
    url = "https://fantasydata.com/NBA_Projections/Projections_Read"
    # En-têtes de la demande
    headers = {    
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "fr,fr-FR;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "_omappvp=zBX5tX55FXAP8lxYGzYrUFzUQmc63hjxNpHrCY1uc8IcPimKcHa7cQFptyyzKY9AQwaH7P3UHqjtI5xMXMQcRn6PmROpCQuW; usprivacy=1YNY; ccuid=ab3f5a39-8232-4585-ab63-1032e3eee3fd; _gid=GA1.2.1632321436.1709228201; _lr_geo_location_state=QC; _lr_geo_location=CA; __gads=ID=c4cb390c4ffb3e7d:T=1708912132:RT=1709228207:S=ALNI_MaMfkoRPyiqJklrJs5LVeIPD8lrLw; __gpi=UID=00000dc439f0eb49:T=1708912132:RT=1709228207:S=ALNI_MY-GtQcrqeJ2ACvy2RUeHrHeJLEsg; __eoi=ID=a13f0a1bfa9915c2:T=1708912132:RT=1709228207:S=AA-AfjbJBdaqHotGhujeeEfM2-6W; _lr_hashed_pid=93c8ff26fcc68a6fc4beef3c071da612f3cbcb3893baf95c5de7ff5df6b17ad1; AMZN-Token=v2FweLxGMGl0SFpRZjdlL3RjU2gyN05QMC81bjRqTittSDF5K2FLVTFjQjlrTzBWMmVaS2h0Qk9pVllPa2RndTlCc3NQdHhDN0xxdDNUY0dYTFUrRmU4Z21oRzZ6eFF4S21mN1BVUmhQeG1NRUJqb05xTHU1b2ZUK0ppUk9YMlVDZTBYMzVoZG12eUUyYkdqdHVOKzZBL2dHVGVzUXQ0UUhWcTRaaVZvSG44Lzl4bTU5VGJ2L0JsLzJMMkxuVmd3PWJrdgFiaXZ4IEhoQk5YZSsvdmUrL3ZXanZ2NzN2djcwTDc3Kzk3Nys5/w==; _lr_optout=%2F; ASP.NET_SessionId=pshtdkyttq0htbch31qfdi3q; ks03ndsapqq84662kglvmcya009273nhdkwsn=43abb972-352f-4490-a601-d3a084bf475c; mp_e1c710649cc8ff18c0c4d5d58433be69_mixpanel=%7B%22distinct_id%22%3A%20107655%2C%22%24device_id%22%3A%20%2218de317f6fd861-0c8b582abf2d3c-4c657b58-240000-18de317f6fd861%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%20107655%7D; _ga=GA1.2.1289497982.1708912015; _gat_gtag_UA_43845809_1=1; __adblocker=false; _ga_ZZN4SP5R2G=GS1.1.1709267588.4.1.1709267603.0.0.0",
        "Origin": "https://fantasydata.com",
        "Sec-Ch-Ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Microsoft Edge\";v=\"122\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "X-Requested-With": "XMLHttpRequest",
    }
    # Obtenir la date du jour
    today_date = date.today()
    formatted_date = today_date.strftime("%m-%d-%Y")  # Formate la date en MM-DD-YYYY

    # Corps de la demande
    data = {
        "sort": "FantasyPoints-desc",
        "pageSize": 300,
        "group": "",
        "filter": "",
        "filters.scope": 2,
        "filters.subscope": "",
        "filters.season": 2024,
        "filters.seasontype": 1,
        "filters.team": "",
        "filters.conference": 1,
        "filters.position": "",
        "filters.searchtext": "",
        "filters.scoringsystem": "",
        "filters.exportType": "",
        "filters.date": formatted_date,
        "filters.dfsoperator": "",
        "filters.dfsslateid": "",
        "filters.dfsslategameid": "",
        "filters.dfsrosterslot": "",
        "filters.showfavs": "",
        "filters.teamkey": "",
        "filters.oddsstate": "",
        "filters.showall": "",
    }
    # Envoyer la requête POST
    response = requests.post(url, headers=headers, data=data)
    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Extraire les données JSON de la réponse
        json_data = response.json()['Data']  # Assurez-vous que le chemin d'accès à 'Data' est correct

        # Transformer les données JSON en DataFrame
        df = pd.json_normalize(json_data)

        # Sélectionner et renommer les colonnes selon les titres fournis
        columns_mapping = {
            "Name": "NAME",
            "Team": "TEAM",
            "Position": "POS",
            "Opponent": "OPP",
            "Points": "PTS",
            "Rebounds": "REB",
            "Assists": "AST",
            "BlockedShots": "BLK",
            "Steals": "STL",
            "FieldGoalsPercentage": "FG%",
            "FreeThrowsPercentage": "FT%",
            "ThreePointersPercentage": "3P%",
            "FreeThrowsMade": "FTM",
            "TwoPointersMade": "2PM",
            "ThreePointersMade": "3PM",
            "Turnovers": "TO",
            "Minutes": "MIN",
            "FantasyPoints": "FPTS"
        }
        df = df.rename(columns=columns_mapping)
        df = df[list(columns_mapping.values())]
        print("DataFrame fantasydata created successfully.")
        return df
    else:
        print(f"Échec de la requête: {response.status_code}")