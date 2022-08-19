import requests
import json
import sys
import argparse
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="app")


parser = argparse.ArgumentParser()
parser.add_argument('--location','-loc', type = str, help="location of forcast")
parser.add_argument('--average', '-avg', action='store_true', help="average temperature of week")
parser.add_argument('--sum', '-sum', action='store_true', help="sum of the temperture of the week")
parser.add_argument('--day','-day', type= str, help="Day of the week and Time that the user wants")
##########################################################
parser.add_argument('--alert', '-al', action='store_true', help="if user wants active weather alerts")
parser.add_argument('--area', '-area', type=str, help="State with active weather alerts")
parser.add_argument('--point', '-p', type=str, help="enter city for a weather alert. Not compabitable with area agr")
######################################################
parser.add_argument('--save', '-s', type= str, help="the JSON file the user wants to save.")

args = parser.parse_args()

if(args.location is None and args.alert is False) or (args.location is not None and args.alert is True):
    print("Please pick between a weather forcast or weather alert")

#user selects weather alerts
elif(args.alert is True):

##all possible states
    states = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
           'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

    ##baseURL for alerts
    alertURL = "https://api.weather.gov/alerts/active?"
    
    ##if user selects area check if its a real State
    if(args.area is not None and args.point is None):
        if args.area in states:
            alertURL = alertURL + "area=" + args.area
        else:
            print("invalid state")
            sys.exit()

    ##user selects a loction for a weather alert
    elif(args.area is None and args.point is not None):
            loc = geolocator.geocode(args.point) ##Convert location into Lat and Long for request
            alertURL = alertURL + "point=" + str(round(loc.latitude, 4)) + "%2C" + str(round(loc.longitude, 4))
    elif(args.area is not None and args.point is not None):
        print("Pick state or city. Not Both")
        sys.exit()

    ##make the alert request
    alertURL= alertURL + "&urgency=Expected"
    response = requests.get(alertURL)
    if(args.save is not None):
        y= json.dumps(response.json(), indent=4)
        with open(args.save + '.json', 'w') as fp:
            fp.write(y)

    print(response.json())
    
else:
    DAYSWEEK = {"Tonight", "This Afternoon", "Monday", "Monday Night", "Tuesday", "Tuesday Night", "Wednesday","Wednesday Night", 
            "Thursday", "Thursday Night", "Friday", "Friday Night", "Saturday", "Saturday Night", "Sunday", "Sunday Night"}
    SUMTEMP = 0
    AVGTEMP = 0

    loc = geolocator.geocode(args.location) ##Convert location into Lat and Long for request

    ##print(loc.latitude, loc.longitude)

    ##make the URL for the request 
    api_url = 'https://api.weather.gov/points/' + str(loc.latitude) + ',' + str(loc.longitude)
    response = requests.get(api_url)

    ##using the request to get the url for the forcast link
    data = response.json()

    response = requests.get(data.get('properties').get("forecast"))

    data = response.json()

    ##Calculate Sum and Avg of temps
    tempDumps = data.get('properties').get('periods')
    for item in tempDumps: 
        SUMTEMP = SUMTEMP + item.get("temperature")
    AVGTEMP = SUMTEMP // 14 


    ##Print the average/sum if user wants it 
    if(args.average is True):
        print(AVGTEMP)
    if(args.sum is True):
        print(SUMTEMP)

    ##if no day is selected, Print all weahter forcast
    if(args.day is None):
        print(data.get('properties').get('periods'))

    ##if user wants to save the forcast as JSON file
        if(args.save is not None):
            tempData = data.get("properties").get("periods")
            if(args.average):
                tempData.append({"avgTemp": AVGTEMP})
            if(args.sum):
                tempData.append({"sumTemp": SUMTEMP})
            y = json.dumps(tempData, indent=4)
            with open(args.save + '.json', 'w') as fp:
                fp.write(y)

    else:
    ##Check to see if user gave a proper day
        if(args.day in DAYSWEEK):
            data = data.get('properties').get('periods')

            ##check if the day the user gave is too far in the future
            listDayDict = [value for elem in data for value in elem.values()]
            if args.day in listDayDict:
        
                dayForcast = next(item for item in data if item["name"] == args.day)
                print(dayForcast)
                ##check if user wants to save the json file
                if(args.save is not None):
                    y = json.dumps(dayForcast, indent=4)
                    with open(args.save + '.json', 'w') as fp:
                        fp.write(y)
            else:
                print("day to far ahead in time")
        else:
            print("Invaild Day/Time")
