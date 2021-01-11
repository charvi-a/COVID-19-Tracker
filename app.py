from flask import Flask,render_template
import pandas as pd
import folium

#Load the dataset.
file = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/12-31-2020.csv')

def get_top_10(file):
#getting the data based on the countries.
	countries = file.groupby('Country_Region').sum()[['Confirmed']]
#get the top 10 countries with the largest number of confirmed cases.
	country_df = countries.nlargest(10,'Confirmed')[['Confirmed']]
	return country_df

country_df = get_top_10(file)

rows = []
for country,Confirmed in zip(country_df.index,country_df['Confirmed']):
	rows.append((country,Confirmed))


map_countries=folium.Map(location=[34.223334,-82.461707],
            tiles='CartoDB positron',
            zoom_start=3)


def create_circle(ele):
	folium.Circle(location=[ele[0],ele[1]], radius=10000,fill = True,
                    popup=f'{ele[3]} Confirmed Cases {ele[2]}', color='red').add_to(map_countries)

file = file.dropna(subset=['Lat','Long_','Confirmed','Combined_Key'])
print(file)
file[['Lat','Long_','Confirmed','Combined_Key']].apply(lambda ele:create_circle(ele),axis=1)
html_map=map_countries._repr_html_()


app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html",cmap=html_map,table=country_df,rows=rows)

if __name__ == "__main__":
	app.run(debug=True)

