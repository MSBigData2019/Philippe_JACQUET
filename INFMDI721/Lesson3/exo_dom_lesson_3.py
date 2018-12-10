###########################################################################################

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
from multiprocessing.dummy import Pool as ThreadPool

###########################################################################################

def get_github_top_users():
    
    users = []
    url = "https://gist.github.com/paulmillr/2657075"

    res = requests.get(url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text,"html.parser");
        t_body = soup.find("tbody")
        for tr in t_body.findAll("tr"):
            user = tr.find("td").text.split(" ")[0]
            users += [user]
    
    return users

###########################################################################################

def get_mean_stars_for_user(user):
    
    headers = {'Authorization': "token %s" % "42fdf2bf67271519c5a4849d0722a5bbf5fa6dcb"}
    url_format = "https://api.github.com/users/" + user + "/repos?page=%d&per_page=100"
    stars = []
    repos_number = 0
    
    i = 1

    while(True):

        url = url_format % i
        res = requests.get(url, headers=headers);
        
        if res.status_code != 200: 
            print(user + "\n\n" + str(res.headers) + "\n\n")
            break
            
        if res.status_code == 200:
            
            json_data = json.loads(res.text)
            if (len(json_data)) == 0:
                break
            repos_number += len(json_data)    
            stars += list(map(lambda x : x["stargazers_count"], json_data))

        i += 1
    
    mean_stars = np.mean(np.array(stars))
    
    return (user, np.round(mean_stars, 1), repos_number)

###########################################################################################

if __name__ == '__main__':

    pool = ThreadPool(4)
    data = pool.map(get_mean_stars_for_user, get_github_top_users())
    pool.close()
    pool.join()

    df = pd.DataFrame(data, columns = ["Nom", "Moyenne", "Nombre de dépôts"])
    print(df)

###########################################################################################
