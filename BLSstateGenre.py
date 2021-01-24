# -*- coding: utf-8 -*- 
"""
Created on Sun Jan 24 15:05:18 2021

@author: Jose
"""
import json
import requests
import pandas as pd


# List goes to 56
seriesNumbers = list(range(254466901,254466957))

"""
Delete the seriesID that do not exist
254466903 -> index 2
254466907 -> index 6
254466911 -> index 10 (district of columbia is not a state, it is just the capital)
254466914 -> index 13
254466943 -> index 42
254466952 -> index 51
"""
removeList = [2,6,10,13,42,51]
seriesNumbers = [i for j, i in enumerate(seriesNumbers) if j not in removeList]

#Transform int list to str list
seriesNumbers = [str(number) for number in seriesNumbers]

#Add prefix to obtain complete seriesId for men
seriesIdMen = ["LEU0" + number for number in seriesNumbers]

#Create same list for Women
seriesIdWomen = [value.replace('69', '70') for value in seriesIdMen]

EmploymentStateGenre = pd.DataFrame()

#------------------------------------------------------#
############## Create the request ######################
def bls_request(series, EmploymentStateGenre):
    headers = {'Content-type': 'application/json'}
    pload = json.dumps ({"seriesid": series, "startyear":"2012", "endyear":"2020",
                     "catalog": 'true', "aspects":'true', "registrationkey":'2621eaef43214baea5bc3bfc92917562'})

    r = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data = pload, headers=headers)
    json_data = json.loads(r.text)
    #print (r.text)

    data = dict()
    data['seriesId'] = []
    data['laborForceStatus'] = []
    data['year'] = []
    data['period'] = []
    data['periodName'] = []
    data['state'] =[]
    data['genre'] = []
    data['value'] = []

    for i in range(0, len(json_data['Results']['series'])):
        for j in range(0, len(json_data['Results']['series'][i]['data'])):
            data['seriesId'].append(json_data['Results']['series'][i]['seriesID'])
            data['laborForceStatus'].append(json_data['Results']['series'][i]['catalog']['cps_labor_force_status'])
            data['year'].append(json_data['Results']['series'][i]['data'][j]['year'])
            data['period'].append(json_data['Results']['series'][i]['data'][j]['period'])
            data['periodName'].append(json_data['Results']['series'][i]['data'][j]['periodName'])
            series_title = json_data['Results']['series'][i]['catalog']['series_title']
            first, *middle, last = series_title.split()
            data['state'].append(last) # the state is the last word of the field
            data['genre'].append(json_data['Results']['series'][i]['catalog']['demographic_gender'])
            data['value'].append(json_data['Results']['series'][i]['data'][j]['value'])

    Employment_Level = pd.DataFrame([data])
    Employment_Levell = Employment_Level.apply(pd.Series.explode).reset_index(drop=True)
    print(Employment_Levell.head(5))
    EmploymentStateGenre = EmploymentStateGenre.append(Employment_Levell,ignore_index=True)

    return EmploymentStateGenre

# Call requests for both men and women
EmploymentStateGenre = bls_request(seriesIdWomen,EmploymentStateGenre)
EmploymentStateGenre = bls_request(seriesIdMen,EmploymentStateGenre)
