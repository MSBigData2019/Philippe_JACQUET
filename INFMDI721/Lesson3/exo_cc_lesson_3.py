###########################################################################################

from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

###########################################################################################

def get_top_cities():

    INSEE_url = "https://www.insee.fr/fr/statistiques/1906659?sommaire=1906743"

    res = requests.get(INSEE_url)

    top_cities = []

    if res.status_code == 200:
        html_doc = res.text
        soup = BeautifulSoup(html_doc,"html.parser")
        table = soup.find("table", id = "produit-tableau-T16F014T4")
        t_body = table.find("tbody")
        for tr in t_body.findAll("tr"):
            top_cities += [tr.findAll("th")[1].text]

    return top_cities

###########################################################################################

def get_distances_matrix(cities):
    
    key = "AIzaSyDe0IYNjx3GnU-A7B7qY6tW5u_RCCVF9iU"
    distances_matrix = []
    origins = "|".join(cities)
    destinations = origins
    
    api_url = f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metrics" +\
              f"&origins={origins}&destinations={destinations}&key={key}"
    
    res = requests.get(api_url)
    
    if res.status_code == 200:
        json_data = json.loads(res.content)
        distances_matrix = list(map(lambda row: list(map(lambda element: element['distance']['text'], row['elements'])), json_data['rows']))
    
    return distances_matrix

###########################################################################################

if __name__ == '__main__':

    top_ten_cities = get_top_cities()[0:10]

    distance_matrix_df = pd.DataFrame(get_distances_matrix(top_ten_cities),
                                      index = top_ten_cities,
                                      columns = top_ten_cities
                                      )
    print(distance_matrix_df)
    
###########################################################################################
