#%%
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

op = webdriver.ChromeOptions()
op.add_argument('headless') #do not display driver UI

from datetime import date
import pandas as pd
from pandas.tseries.offsets import DateOffset
from time import sleep


if __name__ == "__main__":
        
    date_range = pd.date_range(start=date.today(), end=date.today()+ DateOffset(months=1))
    date_range = [i.date().strftime('%m/%d/%Y') for i in date_range if (i.weekday() == 2 ) or (i.weekday() == 4 )]

    driver = webdriver.Chrome(options=op) 
    data_azul = pd.DataFrame(columns=['Date','Hour','Stops','Price'])
    
    origin = 'GRU'
    destination = 'SDU'

    for day in date_range:
            
        url = f"https://www.voeazul.com.br/br/pt/home/selecao-voo?c[0].ds={origin}&c[0].std={day}&c[0].as={destination}&p[0].t=ADT&p[0].c=1&p[0].cp=false&f.dl=3&f.dr=3&cc=BRL"
        driver.get(url)
        
        #wait
        element = WebDriverWait(driver, 30).until( EC.presence_of_element_located((By.CSS_SELECTOR, 'section.card-list')))
        
        #get flights
        for  flight in element.find_elements(By.CSS_SELECTOR,'div.flight-card'):
            
            price = flight.find_element(By.CSS_SELECTOR,'h4.current').text
            price = price.replace('R$','').replace('.','').replace(',','.')
            
            stops = flight.find_element(By.CSS_SELECTOR,'p.flight-leg-info').text
            stops = stops.split(' ')[-1]
            
            hour = flight.find_element(By.CSS_SELECTOR,'h4.departure').text
            hour = hour.split(origin)[0].strip()
        
            new_row = pd.Series({'Date': day, 'Price': price,'Stops':stops,'Hour':hour})
            data_azul = pd.concat([data_azul, new_row.to_frame().T], ignore_index=True)
        
    driver.quit()

    data_azul['Date'] = pd.to_datetime(data_azul['Date'],format='%m/%d/%Y')
    data_azul.to_csv(f'output/coleta_azul_{str(date.today())}_{origin}_{destination}.csv',index=False)
        
