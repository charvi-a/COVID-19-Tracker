from flask import Flask,render_template
import pandas as pd
import numpy as np
import folium
import csv
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
import requests

url = "https://api.covid19api.com/summary"
payload={}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload)
jsonResponse = response.json()

csv_columns = ['Country','TotalConfirmed','CountryCode', 'NewDeaths', 'Date', 'TotalDeaths', 'NewConfirmed', 'Slug', 'NewRecovered', 'Premium', 'ID', 'TotalRecovered']
country_data = jsonResponse["Countries"]
csv_file = "data.csv"

#convert JSON data into a csv file
try:
    with open(csv_file, 'w') as csvfile:
    	writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    	writer.writeheader()
    	for i in range(len(country_data)):
            writer.writerow(country_data[i])
except IOError:
    print("I/O error")

file = pd.read_csv("data.csv", encoding = 'unicode_escape', engine ='python')

def get_top_10(file):
#getting the data based on the countries.
	countries = file.groupby('Country').sum()[['TotalConfirmed']]
#get the top 10 countries with the largest number of confirmed cases.
	country_df = countries.nlargest(10,'TotalConfirmed')[['TotalConfirmed']]
	return country_df

country_df = get_top_10(file)

rows = []
for country,Confirmed in zip(country_df.index,country_df['TotalConfirmed']):
	rows.append((country,Confirmed))

map_countries=folium.Map(location=[34.223334,-82.461707],tiles='CartoDB positron',zoom_start=3)

#get the latitude and longitude for each of the countries
latitudes = []
longitudes = []
def get_geolocation(country):
	try:
		geolocator = Nominatim(user_agent="COVID-19 Project")
		return geolocator.geocode(country)
	except GeocoderTimedOut:
		return get_geolocation(country)
	
map_countries=folium.Map(location=[34.223334,-82.461707], tiles='CartoDB positron', zoom_start=3)

for ele in file["Country"]:
	if get_geolocation(ele):
		location = get_geolocation(ele)
		longitudes.append(location.longitude)
		latitudes.append(location.latitude)
	#location not found
	else:
		longitudes.append(np.nan)
		latitudes.append(np.nan)
		
file["Longitude"] = longitudes
file["Latitude"] = latitudes

def create_circle(ele):
	folium.Circle(location=[ele[0],ele[1]], radius=ele[2],fill = True,
                    popup=f'{ele[4]} New Confirmed Cases {ele[2]} Total Confirmed Cases {ele[3]}', color='red').add_to(map_countries)

file = file.dropna(subset=['Latitude','Longitude','NewConfirmed','TotalConfirmed','Country'])
file[['Latitude','Longitude','NewConfirmed','TotalConfirmed','Country']].apply(lambda ele:create_circle(ele),axis=1)
html_map=map_countries._repr_html_()


app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html",cmap=html_map,table=country_df,rows=rows)

if __name__ == "__main__":
	app.run(debug = False)

