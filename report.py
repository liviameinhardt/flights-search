#%%
from turtle import width
import pandas as pd 
import plotly.graph_objects as go
from datetime import date, time

today = date.today()

azul = pd.read_csv(f'output\coleta_azul_{today}.csv') 
gol = pd.read_csv(f'output\coleta_gol_{today}.csv')
latam = pd.read_csv(f'output\coleta_latam_{today}.csv') 

# #azul
azul['Hour'] = pd.to_datetime(azul['Hour'],format="%H:%M").dt.time
azul['Date'] = pd.to_datetime(azul['Date'],format="%Y-%m-%d")
azul = azul[azul['Stops']=='Direto']
azul = azul[azul['Hour']>time(19)]
azul = azul.rename(columns={'Price':"Azul"})
azul = azul.groupby('Date')[['Azul']].mean()

# #gol 
gol['Date'] = pd.to_datetime(gol['Date'],format="%Y-%m-%d")
gol['Hour'] = pd.to_datetime(gol['Hour'],format="%H:%M:%S").dt.time
gol = gol[gol['Stops']==0]
gol = gol[gol['Hour']>time(19)]
gol = gol.rename(columns={'LIGHT':"Gol"})
gol = gol.groupby('Date')[['Gol']].mean()


# #latam
latam['Date'] = pd.to_datetime(latam['Date'],format="%d/%m/%Y")
latam['Hour'] = pd.to_datetime(latam['Hour'],format="%H:%M").dt.time
latam = latam[latam['Stops']=="Direto"]
latam = latam[latam['Hour']>time(19)]
latam = latam.rename(columns={'Price':"Latam"})
latam = latam.groupby('Date')[['Latam']].mean()

#compare
data = latam.join(azul,how='outer').join(gol,how='outer').dropna()
fig= go.Figure()

color_list=["#1D57A5","#00B5E2","#b8b6b6",
     "#e30b0b","#141414"," #fca605", "#0ac200",'#4285F4','#A6771E', '#F4B400', '#0F9D58',
     '#185ABC', '#B31412', '#EA8600', '#137333',
      '#d2e3fc', '#ceead6']

for color, col in enumerate(data.columns):
    fig.add_trace(go.Scatter(x=data.index,y=data[col],line=dict(width=3,color=color_list[color]),name=col))

date_min = str(data.index.min().date())
date_max = str(data.index.max().date())

fig.update_layout(autosize=False,width=1500,height=700, showlegend=True, 
    paper_bgcolor='#fafafa',
    plot_bgcolor='#fafafa',
    title=f'<b>Preço passagens áreas GRU -> SDU</b> | Average Price after 19PM<br><sup>{date_min} - {date_max}',
    title_font_size=21,font_size=18) 

fig.show()