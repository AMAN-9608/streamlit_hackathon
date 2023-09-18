import streamlit as st
import pandas as pd
import datetime
import geonamescache
import openai
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os



st.set_page_config(layout="wide")
openai.api_key = st.text_input('Streamlit Api Key')
@st.cache_data
def geo_data():
   #  geonames_df = pd.read_csv('cities15000.txt', sep='\t', header=None, names=['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature class', 'feature code', 'country code', 'cc2', 'admin1 code', 'admin2 code', 'admin3 code', 'admin4 code', 'population', 'elevation', 'dem', 'timezone', 'modification date'])
    city_to_country_dict = {}
    gc = geonamescache.GeonamesCache()
    for i, j in gc.get_cities().items():
      if j['countrycode'] in gc.get_countries():
         if j['countrycode'] in city_to_country_dict:
               city_to_country_dict[j['countrycode']].append(j['name'])
         else:
               city_to_country_dict[j['countrycode']] = [j['name']]
    city_to_country_dict2 = {}
    tmp = gc.get_countries()
    for i,j in city_to_country_dict.items():
       if i in gc.get_countries():
          city_to_country_dict2[tmp[i]['name']] = j

    return city_to_country_dict2

@st.cache_data
def generate_response(sys_message, human_message):
  chat = ChatOpenAI(temperature=0.8,openai_api_key=openai.api_key)
  st.info(chat([
    SystemMessage(content=sys_message),
    HumanMessage(content=human_message)
]
))


st.title('Welcome to your Travel Planning app!')

col1, col2 = st.columns(2)

with col1:
   col3, col4 = st.columns(2)
   today = datetime.date.today()
   tomorrow = today + datetime.timedelta(days=1)
   with col3:
      start_date = st.date_input('Start date', value=today,min_value=today,max_value=today + datetime.timedelta(days=90))
   with col4:
      end_date = st.date_input('End date', value=tomorrow,min_value=tomorrow,max_value=start_date + datetime.timedelta(45))
   if start_date>end_date:
      st.error('Error: End date must fall after start date.')

with col2:
   col5, col6 = st.columns(2)
   gc = geonamescache.GeonamesCache()
   list_countries = sorted(list(gc.get_countries_by_names().keys()))
   with col5:
      country = st.multiselect("Select the country you'd like to visit", options=list_countries,default=None,max_selections=1)
      if len(country) >= 1:
         with col6:
            list_cities = geo_data()
            list_cities = sorted(list_cities[country[0]])
            city = st.multiselect("Select the city you'd like to visit", options=list_cities,default=None)

with st.sidebar:
   filter_1 = st.slider('On a scale of 0 to 5, how much do you enjoy Outdoor Activities?', 0, 5,key='pref1')
   filter_2 = st.slider('On a scale of 0 to 5, how much do you enjoy Socializing & Nightlife?', 0, 5,key='pref2')
   filter_3 = st.slider('On a scale of 0 to 5, how much do you enjoy Arts & Culture?', 0, 5, key='pref3')
   filter_4 = st.slider('On a scale of 0 to 5, how much do you enjoy Food?', 0, 5,key='pref4')
   filter_5 = st.slider('On a scale of 0 to 5, Pace of activities?', 0, 5,key='pref5')




def generate_response(sys_message, human_message):
  chat = ChatOpenAI(temperature=0.8,openai_api_key=openai.api_key)
  st.info(chat([
    SystemMessage(content=sys_message),
    HumanMessage(content=human_message)
]
))

# def get_text(input):
#     completion = openai.ChatCompletion.create(
#                     model="gpt-3.5-turbo",
#                     messages=[
#                     {"role": "system", "content": "You are a helpful assistant."},
#                     {"role": "user", "content": input}]
#                     )
    
#     return completion.choices[0].message

ref = {"Art and culture":filter_3,
       "Food":filter_4,
       "Socializing and nightlife":filter_2,
       "Outdoor Activities":filter_1,
       "Pace of activities": filter_5          
}
system_prompt = f"""
You are a virtual travel planner, assisting users with their travel plans by providing information based on their inputs.
Offer tailored recommendations based on the user's responses to help them have a memorable and enjoyable trip. Below is some more context on their responses.
1. You are planning a trip to {city}, {country} from {start_date} to {end_date}. 
2. {filter_1} tells you how much the user likes Outdoor Activites; with a score of 1 being not interested, 2 being neutral, and 3 indicating that they really enjoy that activity.
3. {filter_2} tells you how much the user likes Socializing & Nightlife; with a score of 1 being not interested, 2 being neutral, and 3 indicating that they really enjoy that activity.
4. {filter_3} tells you how much the user likes Arts & Culture; with a score of 1 being not interested, 2 being neutral, and 3 indicating that they really enjoy that activity.
5. {filter_4} tells you how much the user likes Food; with a score of 1 being not interested, 2 being neutral, and 3 indicating that they really enjoy that activity.

Make sure to factor in a user's score for a category into your response. e.g. if the user says {filter_4} is 1 or 2, then do not provide restaurant recommendations.

Also make sure to include links if possible to the places that you recommend. e.g. if you recommend the Louvre in Paris, include a hyperlink to its website in your response.
"""

# prompt = PromptTemplate(template=system_prompt, input_variables=['start_date','end_date','country','city','filter_1','filter_2','filter_3','filter_4'])
sys_message = system_prompt
# sys_message = "You are a travel advising AI bot that helps the user in planning itinerary for a user. the user will also provide their preferences for the following attributes {} with a score in the range 0-5. Where an attribute with a low score should be given a very low priotiy in the itinerary and  an attribute with a high value like 5 should be given high priority while planning the itinerary ".format(list(ref.keys()))
human_message = "Hi Can you plan a travel for me to {},{} from {} to {} given the following qualities and their scores {}".format(city,country,start_date,end_date,ref)
st.write(generate_response(sys_message,human_message))

