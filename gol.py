#%%
import requests
import json
from datetime import date
import pandas as pd
from pandas.tseries.offsets import DateOffset
from time import sleep

def get_token():
    url = "https://gol-auth-api.voegol.com.br/api/authentication/create-token"

    payload={}
    headers = {
      'accept': 'text/plain',
      'accept-encoding': 'gzip, deflate, br',
      'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
      'origin': 'https://b2c.voegol.com.br',
      'referer': 'https://b2c.voegol.com.br/',
      'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
      'sec-ch-ua-mobile': '?0',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-site',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
      'x-aat': 'NEUgdaCsLXoDdbB0/Jfb+d6O72lprMfUJxaW/eTW7ncXFZgMqTtFpi5mQdzidn0c0EnON6hHWtrBAshheNOhtQ=='
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)['response']['token']

def get_voos_json(token,origin, destination, data_ida):
    headers = {
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'x-sabre-cookie-encoded': '',
        'sec-ch-ua-mobile': '?0',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Referer': 'https://b2c.voegol.com.br/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'x-jsessionid': '',
        'sec-ch-ua-platform':'"Windows"'
    }

    params = (
        ('context', 'b2c'),
        ('flow', 'Issue'),
    )

    data = """{"promocodebanner":false,"destinationCountryToUSA":false,"lastSearchCourtesyTicket":false,"passengerCourtesyType":null,"airSearch":{"cabinClass":null,"currency":null,"pointOfSale":"BR","awardBooking":false,"searchType":"BRANDED","promoCodes":[""],"itineraryParts":
    [{"from":{"code":"%ORIGIN%","useNearbyLocations":false},"to":{"code":"%DESTINATION%","useNearbyLocations":false},"when":{"date":"%INBOUND%T23:00:00.000Z"},
    "selectedOfferRef":null,"plusMinusDays":null}],
    "passengers":{"ADT":1,"CHD":0,"INF":0,"UNN":0},"trendIndicator":null,"preferredOperatingCarrier":null}}"""


    data = data.replace("%ORIGIN%",origin)
    data = data.replace("%DESTINATION%",destination)
    data = data.replace("%INBOUND%",data_ida.strftime("%Y-%m-%d"))
    data = data.replace("\n  ","")

    response = requests.post('https://b2c-api.voegol.com.br/api/sabre-default/flights', headers=headers, params=params, data=data)

    return json.loads(response.text)['response']['airSearchResults']['brandedResults']['itineraryPartBrands']

def get_gol(data_ida,origin,destination):

    print(f"Rodando coleta gol do dia: {data_ida.strftime('%d %b %Y')}")

    # # Parameters:
    # origin_airports = ["GRU"]
    # destination_airports = ["SDU"]

    # Get API Token
    token = get_token()

    # Hist Dataframe
    # df_flights = pd.DataFrame()

    # for origin in origin_airports:
    #     for destination in destination_airports:
    #         if origin == destination: continue
            
    try: json_data = get_voos_json(token, origin, destination, data_ida)
    except:
        print(f"Retry {origin} -> {destination}")
        sleep(5)
        try: json_data = get_voos_json(token, origin, destination, data_ida)
        except: print(f"Error {origin} -> {destination}")

    for flight in json_data[0]:
        
        # Para faciliar > pegando o primeiro trecho como referencia
        date = flight['departure']
        stops = flight['itineraryPart']['stops']
        
        meta = {'Date':date,'Stops':stops}

        # Adicionando por oferta
        categorias = {'MX':'MAX','PL':'PLUS','LT':'LIGHT','PO':'PROMO'}
        for offer in flight['brandOffers']:
            ticket_type = categorias[offer['brandId']]
            price = offer['total']['alternatives'][0][0]['amount']
            
            meta.update({ticket_type:price})
            
        new_row = pd.Series(meta)
        df_flights = pd.concat([df_flights, new_row.to_frame().T], ignore_index=True)

    df_flights['Date'] = pd.to_datetime(df_flights['Date'])
    
    
    return df_flights

if __name__ == "__main__":
    
    date_range = pd.date_range(start=date.today(), end=date.today()+ DateOffset(months=4))
    date_range = [i.date() for i in date_range if (i.weekday() == 2 ) or (i.weekday() == 4 )]

    data_gol = pd.DataFrame()
    
    origin = "GRU"
    destination = "SDU"
    
    for day in date_range:
        temp = get_gol(day,origin,destination)
        data_gol = pd.concat([data_gol,temp])       
        sleep(5)
    
    data_gol['Hour'] = data_gol['Date'].dt.time
    data_gol['Date'] = data_gol['Date'].dt.date
        
    data_gol.to_csv(f'output/coleta_gol_{str(date.today())}_{origin}_{destination}.csv',index=False)