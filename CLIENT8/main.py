from sportsline.sportsline import dataframe_sportsline 
import pandas as pd
from rotowire.rotowire import dataframe_rotowire
from numbefire.numbefire import dataframe_numbefire
from Fantasydata.fantasydata import dataframe_fantasydata
from draftkings.draftkingsVF import dataframe_draftkings
import numpy as np
import streamlit as st
def integrate_twos_stat(df_final, df_fantasydata, df_rotowire):
    added_players = set()
    new_rows = []

    for index, row in df_final.iterrows():
        player_name = row['player']
        # Vérifie si le joueur est dans df_fantasydata et si "2's" n'a pas déjà été ajouté pour ce joueur
        if player_name in df_fantasydata['NAME'].values and player_name not in added_players:
            fd_row = df_fantasydata[df_fantasydata['NAME'] == player_name].iloc[0]
            if '2PM' in fd_row and fd_row['2PM'] != 0:
                new_row = row.copy()
                new_row['stat type'] = "2PM"
                new_row['FD'] = fd_row['2PM']
                new_row['MIN'] = fd_row['MIN']
                # Recherche du joueur dans df_rotowire pour calculer la valeur RW des "2's"
                if player_name in df_rotowire['player'].values:
                    rw_row = df_rotowire[df_rotowire['player'] == player_name].iloc[0]
                    # S'assurer que les colonnes pour FGM et 3PM existent et contiennent des valeurs non-nulles
                    if 'FGM' in rw_row and 'THREEPM' in rw_row and pd.notnull(rw_row['FGM']) and pd.notnull(rw_row['THREEPM']) and rw_row['FGM']!= 0 and rw_row['THREEPM']!= 0:
                        new_row['RW'] = rw_row['FGM'] - rw_row['THREEPM']
                    else:
                        new_row['RW'] = None
                else:
                    new_row['RW'] = None
                new_rows.append(new_row)
                added_players.add(player_name)

    df_final_with_twos = pd.concat([df_final, pd.DataFrame(new_rows)], ignore_index=True)
    return df_final_with_twos
def finaldataframe(df_rotowire, df_draftkings, df_fantasydata, df_numbefire, df_sportsline):
    df_rotowire['team(pos)'] = df_rotowire['team'] + '(' + df_rotowire['pos'] + ')'
    df_final = df_rotowire[['player', 'team(pos)', 'opp','MIN']]
    df_final = integrate_draftkings_data(df_final, df_draftkings, df_rotowire)
    df_final = integrate_fantasydata(df_final, df_fantasydata)
    df_final = integrate_numbefire(df_final, df_numbefire)
    df_final = integrate_sportsline(df_final, df_sportsline)
    # Calcul de la moyenne des projections
    cols_to_convert = ['RW', 'FD', 'NF', 'SL']
    for col in cols_to_convert:
        df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
    df_final = integrate_twos_stat(df_final, df_fantasydata, df_rotowire)
    # Conversion explicite des colonnes en float avant de calculer la moyenne
    df_final[['RW', 'FD', 'NF', 'SL', 'line']] = df_final[['RW', 'FD', 'NF', 'SL', 'line']].astype(float)

    # Calcul de la moyenne des projections en tant que float
    df_final['AVG'] = df_final[['RW', 'FD', 'NF', 'SL']].mean(axis=1)

    # Assurez-vous que 'line' est numérique et correspond au type de stat pour lequel vous faites la moyenne
    df_final['DIFF'] = df_final['AVG'] - df_final['line']

    # Calcul de la différence en pourcentage comme float
    df_final['DIFF%'] = (df_final['DIFF'] / df_final['line'].replace({0: np.nan})) * 100

    # S'assurer que les colonnes calculées sont aussi en float (au cas où les opérations précédentes n'auraient pas suffi)
    df_final[['AVG', 'DIFF', 'DIFF%']] = df_final[['AVG', 'DIFF', 'DIFF%']].astype(float)
    cols_to_round = ['MIN', 'AVG', 'DIFF', 'DIFF%', 'RW', 'FD', 'NF', 'SL', 'line']
    df_final[cols_to_round] = df_final[cols_to_round].round(2)
    df_final = df_final.dropna(subset=['stat type']) #clean the dataframe
    replacement_dict = {
        "3s": "3PM",
        "pts": "PTS",
        "reb": "REB",
        "ast": "AST",
        "PTS_REB": "PR",
        "PTS_REB_AST": "PRA",
        "PTS_AST": "PA",
        "AST_REB": "AR",
        "Steals": "STL",
        "Blocks": "BLK",
        "Steals_Blocks": "SB"
    }
    df_final['stat type'] = df_final['stat type'].replace(replacement_dict)
    return df_final
def integrate_numbefire(df_final, df_numbefire):
    new_rows = []
    for index, row in df_final.iterrows():
        player_name = row['player']
        stat_type = row['stat type']
        if player_name in df_numbefire['Name'].values:
            nf_row = df_numbefire[df_numbefire['Name'] == player_name].iloc[0]
            nf_value = calculate_Nf(stat_type, nf_row)  # Assurez-vous que calculate_Nf accepte ces paramètres
            row['NF'] = nf_value
        else:
            row['NF'] = None
        new_rows.append(row)
    
    df_final_with_nf = pd.DataFrame(new_rows)
    return df_final_with_nf
def integrate_sportsline(df_final, df_sportsline):
    new_rows = []
    for index, row in df_final.iterrows():
        player_name = row['player']
        stat_type = row['stat type']
        if player_name in df_sportsline['PLAYER'].values:
            sl_row = df_sportsline[df_sportsline['PLAYER'] == player_name].iloc[0]
            sl_value = calculate_sl(stat_type, sl_row)  # Assurez-vous que calculate_sl accepte ces paramètres
            row['SL'] = sl_value
        else:
            row['SL'] = None
        new_rows.append(row)
    df_final_with_sl = pd.DataFrame(new_rows)
    return df_final_with_sl
    
def integrate_fantasydata(df_final, df_fantasydata):
    new_rows = []
    for index, row in df_final.iterrows():
        player_name = row['player']
        stat_type = row['stat type']  # Récupération du stat type de la ligne actuelle
        # Rechercher le joueur dans df_fantasydata
        if player_name in df_fantasydata['NAME'].values:
            fd_row = df_fantasydata[df_fantasydata['NAME'] == player_name].iloc[0]
            # Calculer 'FD' en utilisant calculate_fd et en passant le stat_type et fd_row
            fd_value = calculate_fd(stat_type, fd_row)  # Assurez-vous que calculate_fd accepte ces paramètres
            row['FD'] = fd_value
        else:
            row['FD'] = None
        new_rows.append(row)
    
    df_final_with_fd = pd.DataFrame(new_rows)
    return df_final_with_fd
def integrate_draftkings_data(df_final, df_draftkings, df_rotowire):
    # Création d'un DataFrame temporaire pour stocker les nouvelles lignes
    new_rows = []
    
    for index, row in df_final.iterrows():
        player_name = row['player']
        if player_name in df_draftkings['player'].values:
            # Extraction des données de df_draftkings pour le joueur
            dk_row = df_draftkings[df_draftkings['player'] == player_name]
            # Pour chaque type de statistique disponible dans df_draftkings
            for stat_type in ['3s', 'AST_REB', 'Blocks', 'PTS_AST', 'PTS_REB_AST', 'PTS_REB', 'Steals_Blocks', 'Steals', 'ast', 'pts', 'reb']:
                # Vérification si les données existent pour ce type de statistique
                if f'{stat_type}_O_Cotes' in dk_row.columns and pd.notna(dk_row.iloc[0][f'{stat_type}_O_Cotes']):
                    # Création d'une nouvelle ligne pour ce type de statistique
                    new_row = row.copy()
                    new_row['stat type'] = stat_type
                    new_row['line'] = dk_row.iloc[0][f'{stat_type}_O_Ligne']
                    new_row['oddsO'] = dk_row.iloc[0][f'{stat_type}_O_Cotes']
                    new_row['oddsU'] = dk_row.iloc[0][f'{stat_type}_U_Cotes']
                    if player_name in df_rotowire['player'].values:
                        player_stats = df_rotowire[df_rotowire['player'] == player_name].iloc[0]
                        new_row['RW'] = calculate_rw(stat_type, player_stats)
                  
                    else:
                        new_row['RW'] = None
                    new_rows.append(new_row)

    
    # Ajout des nouvelles lignes au DataFrame df_final
    df_final_extended = pd.concat([df_final, pd.DataFrame(new_rows)], ignore_index=True)
    return df_final_extended

def calculate_rw(stat_type, player_stats):
    if stat_type == '3s':
        return player_stats['THREEPM']
    elif stat_type == 'AST_REB':
        return player_stats['AST'] + player_stats['REB']
    elif stat_type == 'Blocks':
        return player_stats['BLK']
    elif stat_type == 'PTS_AST':
        return player_stats['PTS'] + player_stats['AST']
    elif stat_type == 'PTS_REB_AST':
        return player_stats['PTS'] + player_stats['AST'] + player_stats['REB']
    elif stat_type == 'PTS_REB':
        return player_stats['PTS'] + player_stats['REB']
    elif stat_type == 'Steals_Blocks':
        return player_stats['STL'] + player_stats['BLK']
    elif stat_type == 'Steals':
        return player_stats['STL']
    elif stat_type == 'ast':
        return player_stats['AST']
    elif stat_type == 'pts':
        return player_stats['PTS']
    elif stat_type == 'reb':
        return player_stats['REB']
    else:
        return None
def calculate_sl(stat_type, player_stats):
    if stat_type == 'AST_REB':
        return player_stats['AST'] + player_stats['TRB']
    elif stat_type == 'Blocks':
        return player_stats['BK']
    elif stat_type == 'PTS_AST':
        return player_stats['PTS'] + player_stats['AST']
    elif stat_type == 'PTS_REB_AST':
        return player_stats['PTS'] + player_stats['AST'] + player_stats['TRB']
    elif stat_type == 'PTS_REB':
        return player_stats['PTS'] + player_stats['TRB']
    elif stat_type == 'Steals_Blocks':
        return player_stats['ST'] + player_stats['BK']
    elif stat_type == 'Steals':
        return player_stats['ST']
    elif stat_type == 'ast':
        return player_stats['AST']
    elif stat_type == 'pts':
        return player_stats['PTS']
    elif stat_type == 'reb':
        return player_stats['TRB']
    else:
        return None

def calculate_fd(stat_type, player_stats):
    if stat_type == '3s':
        return player_stats['3PM'] 
    elif stat_type == 'AST_REB':
        return player_stats['AST'] + player_stats['REB']
    elif stat_type == 'Blocks':
        return player_stats['BLK']
    elif stat_type == 'PTS_AST':
        return player_stats['PTS'] + player_stats['AST']
    elif stat_type == 'PTS_REB_AST':
        return player_stats['PTS'] + player_stats['AST'] + player_stats['REB']
    elif stat_type == 'PTS_REB':
        return player_stats['PTS'] + player_stats['REB']
    elif stat_type == 'Steals_Blocks':
        return player_stats['STL'] + player_stats['BLK']
    elif stat_type == 'Steals':
        return player_stats['STL']
    elif stat_type == 'ast':
        return player_stats['AST']
    elif stat_type == 'pts':
        return player_stats['PTS']
    elif stat_type == 'reb':
        return player_stats['REB']
    else:
        return None    

def calculate_Nf(stat_type, player_stats):
    if stat_type == '3s':
        return player_stats['3PM'] 
    elif stat_type == 'AST_REB':
        return player_stats['AST'] + player_stats['REB']
    elif stat_type == 'Blocks':
        return player_stats['BLK']
    elif stat_type == 'PTS_AST':
        return player_stats['PTS'] + player_stats['AST']
    elif stat_type == 'PTS_REB_AST':
        return player_stats['PTS'] + player_stats['AST'] + player_stats['REB']
    elif stat_type == 'PTS_REB':
        return player_stats['PTS'] + player_stats['REB']
    elif stat_type == 'Steals_Blocks':
        return player_stats['STL'] + player_stats['BLK']
    elif stat_type == 'Steals':
        return player_stats['STL']
    elif stat_type == 'ast':
        return player_stats['AST']
    elif stat_type == 'pts':
        return player_stats['PTS']
    elif stat_type == 'reb':
        return player_stats['REB']
    else:
        return None    

def load_data():
    # Assurez-vous que les fonctions comme dataframe_sportsline() sont définies
    # ou importées correctement
    df_sportsline = dataframe_sportsline()
    df_rotowire = dataframe_rotowire()
    df_numbefire = dataframe_numbefire()
    df_fantasydata = dataframe_fantasydata()
    df_draftkings = dataframe_draftkings()
    df_final_extended = finaldataframe(df_rotowire, df_draftkings, df_fantasydata, df_numbefire, df_sportsline)  # Assurez-vous que cette fonction est définie correctement
    return df_final_extended
def app():
    st.title('Basketball Talent Forecast: A Comparative Projection Analysis')
    
    if st.button('Run the analysis'):
        df = load_data()
        df.reset_index(drop=True, inplace=True)
        st.write('DataFrame :')
        st.dataframe(df)

if __name__ == "__main__":
    app()