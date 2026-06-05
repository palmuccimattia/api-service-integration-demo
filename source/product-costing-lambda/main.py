# from config_scripts.aws_secret_loader import get_secret
from datetime import datetime, date
from utility import *
from alici import *
from amatriciana import *
from margherita import *
from capricciosa import *
from carciofi import *
from cipolla import *
from cotto_scamorza import *
from crudo_rucola_grana_stracciatella import *
from crudo_rucola_grana import *
from funghi_bianca import *
from funghi_cotto import *
from funghi_salsiccia import *
from funghi import *
from grasselli import *
from ortolana import *
from parmigiana import *
from patate_cotto import *
from patate_pancetta import *
from patate_porcini import *
from patate_salsiccia import *
from patate_wurstel import *
from patate import *
from peperoni import *
from piccante import *
from pomodoro import *
from quattro_formaggi import *
from rosmarino import *
from salsarosa_gamberetti import *
from salsiccia import *
from spinaci_salsiccia import *
from sushi import *
from tartufata import *
from tartufo_porcini import *
from tartufo_salsiccia import *
from tonno_pomodorini_rucola import *
from vegana import *
from wurstel import *
from zucchine_cotto import *
from zucchine_pancetta import *
from zucchine_pomodorini import *
from zucchine_salsiccia import *
from zucchine import *

def lambda_handler(event, context):
    
    start_data = date(2024, 1, 1).strftime("%Y-%m-%d")
    end_data = datetime.now().strftime("%Y-%m-%d")

    df, engine = get_data_margherita(start_data, end_data)
    df.to_sql(name = "Margherita", con=engine, if_exists='replace', index=False)    

    df, eng = get_data_alici(start_data, end_data)
    df.to_sql(name = "Alici", con=engine, if_exists='replace', index=False)

    df, eng = get_data_amatriciana(start_data, end_data)
    df.to_sql(name = "Amatriciana", con=engine, if_exists='replace', index=False)

    df, eng = get_data_capricciosa(start_data, end_data)
    df.to_sql(name = "Capricciosa", con=engine, if_exists='replace', index=False)

    df, eng = get_data_carciofi(start_data, end_data)
    df.to_sql(name = "Carciofi", con=engine, if_exists='replace', index=False)

    df, eng = get_data_cipolla(start_data, end_data)
    df.to_sql(name = "Cipolla", con=engine, if_exists='replace', index=False)

    df, eng = get_data_cottoscamorza(start_data, end_data)
    df.to_sql(name = "CottoScamorza", con=engine, if_exists='replace', index=False)

    df, eng = get_data_crudorucolagranastracciatella(start_data, end_data)
    df.to_sql(name = "CrudoRucolaGranaStracciatella", con=engine, if_exists='replace', index=False)

    df, eng = get_data_crudorucolagrana(start_data, end_data)
    df.to_sql(name = "CrudoRucolaGrana", con=engine, if_exists='replace', index=False)

    df, eng = get_data_funghibianca(start_data, end_data)
    df.to_sql(name = "FunghiBianca", con=engine, if_exists='replace', index=False)

    df, eng = get_data_funghicotto(start_data, end_data)
    df.to_sql(name = "FunghiCotto", con=engine, if_exists='replace', index=False)

    df, eng = get_data_funghisalsiccia(start_data, end_data)
    df.to_sql(name = "FunghiSalsiccia", con=engine, if_exists='replace', index=False)

    df, eng = get_data_funghi(start_data, end_data)
    df.to_sql(name = "Funghi", con=engine, if_exists='replace', index=False)   

    df, eng = get_data_grasselli(start_data, end_data)
    df.to_sql(name = "Grasselli", con=engine, if_exists='replace', index=False)

    df, eng = get_data_ortolana(start_data, end_data)
    df.to_sql(name = "Ortolana", con=engine, if_exists='replace', index=False)

    df, eng = get_data_parmigiana(start_data, end_data)
    df.to_sql(name = "Parmigiana", con=engine, if_exists='replace', index=False)

    df, eng = get_data_patatecotto(start_data, end_data)
    df.to_sql(name = "PatateCotto", con=engine, if_exists='replace', index=False)

    df, eng = get_data_patatepancetta(start_data, end_data)
    df.to_sql(name = "PatatePancetta", con=engine, if_exists='replace', index=False)

    df, eng = get_data_patateporcini(start_data, end_data)
    df.to_sql(name = "PatatePorcini", con=engine, if_exists='replace', index=False)

    df, eng = get_data_patatesalsiccia(start_data, end_data)
    df.to_sql(name = "PatateSalsiccia", con=engine, if_exists='replace', index=False)

    df, eng = get_data_patatewurstel(start_data, end_data)
    df.to_sql(name = "PatateWurstel", con=engine, if_exists='replace', index=False)

    df, eng = get_data_patate(start_data, end_data)
    df.to_sql(name = "Patate", con=engine, if_exists='replace', index=False)

    df, eng = get_data_peperoni(start_data, end_data)
    df.to_sql(name = "Peperoni", con=engine, if_exists='replace', index=False)

    df, eng = get_data_piccante(start_data, end_data)
    df.to_sql(name = "Piccante", con=engine, if_exists='replace', index=False)

    df, eng = get_data_pomodoro(start_data, end_data)
    df.to_sql(name = "Pomodoro", con=engine, if_exists='replace', index=False)

    df, eng = get_data_quattroformaggi(start_data, end_data)
    df.to_sql(name = "QuattroFormaggi", con=engine, if_exists='replace', index=False)

    df, eng = get_data_rosmarino(start_data, end_data)
    df.to_sql(name = "Rosmarino", con=engine, if_exists='replace', index=False)

    df, eng = get_data_salsarosagamberetti(start_data, end_data)
    df.to_sql(name = "SalsarosaGamberetti", con=engine, if_exists='replace', index=False)

    df, eng = get_data_salsiccia(start_data, end_data)
    df.to_sql(name = "Salsiccia", con=engine, if_exists='replace', index=False)

    df, eng = get_data_spinacisalsiccia(start_data, end_data)
    df.to_sql(name = "SpinaciSalsiccia", con=engine, if_exists='replace', index=False)

    df, eng = get_data_sushi(start_data, end_data)
    df.to_sql(name = "Sushi", con=engine, if_exists='replace', index=False)

    df, eng = get_data_tartufata(start_data, end_data)
    df.to_sql(name = "Tartufata", con=engine, if_exists='replace', index=False)

    df, eng = get_data_tartufoporcini(start_data, end_data)
    df.to_sql(name = "TartufoPorcini", con=engine, if_exists='replace', index=False)

    df, eng = get_data_tartufosalsiccia(start_data, end_data)
    df.to_sql(name = "TartufoSalsiccia", con=engine, if_exists='replace', index=False)

    df, eng = get_data_tonnopomodorinirucola(start_data, end_data)
    df.to_sql(name = "TonnoPomodoriniRucola", con=engine, if_exists='replace', index=False)

    df, eng = get_data_vegana(start_data, end_data)
    df.to_sql(name = "Vegana", con=engine, if_exists='replace', index=False)

    df, eng = get_data_wurstel(start_data, end_data)
    df.to_sql(name = "Wurstel", con=engine, if_exists='replace', index=False)

    df, eng = get_data_zucchinecotto(start_data, end_data)
    df.to_sql(name = "ZucchineCotto", con=engine, if_exists='replace', index=False)

    df, eng = get_data_zucchinepancetta(start_data, end_data)
    df.to_sql(name = "ZucchinePancetta", con=engine, if_exists='replace', index=False)

    df, eng = get_data_zucchinepomodorini(start_data, end_data)
    df.to_sql(name = "ZucchinePomodorini", con=engine, if_exists='replace', index=False)

    df, eng = get_data_zucchinesalsiccia(start_data, end_data)
    df.to_sql(name = "ZucchineSalsiccia", con=engine, if_exists='replace', index=False)

    df, eng = get_data_zucchine(start_data, end_data)
    df.to_sql(name = "Zucchine", con=engine, if_exists='replace', index=False)
    
    return {
        'statusCode': 200,
        'body': "Dati delle prodotti aggiornati con successo!"
    }

if __name__ == "__main__":
    lambda_handler({}, {})