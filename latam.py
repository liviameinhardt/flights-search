#%%
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

op = webdriver.ChromeOptions()
op.add_argument('headless') #do not display driver UI

from datetime import date
from time import sleep
import pandas as pd
from pandas.tseries.offsets import DateOffset

def load_page(driver,day,origin,destination):
    
    url = f"https://www.latamairlines.com/br/pt/oferta-voos?origin={origin}&inbound=null&outbound={day}T15%3A00%3A00.000Z&destination={destination}&adt=1&chd=0&inf=0&trip=OW&cabin=Economy&redemption=false&sort=RECOMMENDED"
    driver.get(url)
    
    sleep(5)
    
    # accept cookies
    try:
        element = WebDriverWait(driver, 30).until( EC.presence_of_element_located((By.CSS_SELECTOR, "button")))
        driver.find_element(By.ID, 'cookies-politics-button').click() 
    except: print('')
    
    sleep(5)

    #waits
    flights =  "/html/body/div/div/main/div/div/div/div/ol"
    element = WebDriverWait(driver, 30).until( EC.presence_of_element_located((By.XPATH, flights)))
    available_flights = driver.find_element(By.XPATH, flights)

    element = WebDriverWait(driver, 30).until( EC.presence_of_element_located((By.XPATH, '//*[@id="WrapperCardFlight0"]/div/div[2]/div[2]/div/div/div/span/span[2]')))
    
    return available_flights

def get_flight_info(flights_list, day):
    
    latam = pd.DataFrame(columns=['Data','Hora','Paradas','Preco'])
    
    number = 0
    for  flight in flights_list.find_elements(By.CSS_SELECTOR,'li'):
        if flight.get_attribute("class") == "sc-fQfKYo hqsges":
            
            price_str = f'//*[@id="WrapperCardFlight{number}"]/div/div[2]/div[2]/div/div/div/span'
            stops_str = f'//*[@id="itinerary-modal-{number}-dialog-open"]/span'
            hour_str = f'//*[@id="WrapperCardFlight{number}"]/div/div[1]/div[2]/div[1]/div[1]/span[1]'
            
            price = flight.find_element(By.XPATH,price_str).get_attribute("aria-label")
            price = price.replace(' Reais brasileiros','').replace(',','.')
            
            stops = flight.find_element(By.XPATH,stops_str).text
            
            hour = flight.find_element(By.XPATH,hour_str).text
            
            new_row = pd.Series({'Date': day, 'Price': price,'Stops':stops,'Hour':hour})
            latam = pd.concat([latam, new_row.to_frame().T], ignore_index=True)
    
            number+=1
    
    return latam
            
if __name__ == "__main__":
    
    date_range = pd.date_range(start=date.today(), end=date.today()+ DateOffset(months=4))
    date_range = [str(i.date()) for i in date_range if (i.weekday() == 2 ) or (i.weekday() == 4 )]

    driver = webdriver.Chrome(options=op) 
    data_latam = pd.DataFrame(columns=['Date','Hour','Stops','Price'])
    
    origin = "GRU"
    destination = "SDU"
    
    for  day in date_range:
        
        print("Getting data for: ",day)
        
        lista_voos = load_page(driver,day,origin,destination)
        
        temp_df = get_flight_info(lista_voos,day)
        data_latam = pd.concat([data_latam,temp_df])
            
        
    driver.quit()
    data_latam.to_csv(f'output/coleta_latam_{str(date.today())}_{origin}_{destination}.csv',index=False)
