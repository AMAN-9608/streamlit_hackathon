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

# @st.cache_data
# def generate_response(sys_message, human_message):
#   chat = ChatOpenAI(temperature=0.8,openai_api_key=openai.api_key)
#   return chat([
#     SystemMessage(content=sys_message),
#     HumanMessage(content=human_message)
#    ]).content


st.title('Welcome to your Travel Planning app!')

col1, col2 = st.columns(2)



# using form so that changing a data point does not rerun
# the entire script 


preference_dict = {
   "filter_1":"Outdoor Activities",
   "filter_2":"Socializing & Nightlife",
   "filter_3":"Arts & Culture",
   "filter_4":"Food",
   "filter_5":"Festivals and Events"

}

with st.form("my_form"):
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
   
   preferences_list = []
   
   with st.expander("Select activities you are interested in"):
      filter_1 = st.checkbox('Outdoor Activities')
      filter_2 = st.checkbox('Socializing & Nightlife')
      filter_3 = st.checkbox('Arts & Culture')
      filter_4 = st.checkbox('Food')
      filter_5 = st.checkbox('Festivals and Events')
      
      for i in range(1,6):
         if(eval("filter_"+str(i))):
            preferences_list.append(preference_dict["filter_"+str(i)])
   who_filter = "Friends"
   with st.expander("Who do you plan on travelling with"):
      who_filter = st.radio(
    "Who do you plan on travelling with",
    ["Solo", "Family", "Couple","Friends"],label_visibility="hidden")
      
   # filter_1 = st.slider('On a scale of 0 to 5, how much do you enjoy Outdoor Activities?', 0, 5,key='pref1')
   # filter_2 = st.slider('On a scale of 0 to 5, how much do you enjoy Socializing & Nightlife?', 0, 5,key='pref2')
   # filter_3 = st.slider('On a scale of 0 to 5, how much do you enjoy Arts & Culture?', 0, 5, key='pref3')
   # filter_4 = st.slider('On a scale of 0 to 5, how much do you enjoy Food?', 0, 5,key='pref4')
   # filter_5 = st.slider('On a scale of 0 to 5, Pace of activities?', 0, 5,key='pref5')

   submit_button = st.form_submit_button('Submit')


def generate_response(sys_message, human_message):
#   llm = OpenAI(temperature=0.8,openai_api_key=openai.api_key)
#   st.info(llm(sys_message))

  chat = ChatOpenAI(temperature=0.2,openai_api_key=openai.api_key, model='gpt-4')
  return chat([
    SystemMessage(content=sys_message)
      ]).content



# ref = {"Art and culture":filter_3,
#        "Food":filter_4,
#        "Socializing and nightlife":filter_2,
#        "Outdoor Activities":filter_1,
#        "Pace of activities": filter_5          
# }

if submit_button:
   system_prompt = f"""
   You are a virtual travel planner, assisting users with their travel plans by providing information based on their inputs.
   Offer tailored recommendations based on the user's responses to help them have a memorable and enjoyable trip. Below is some more context on their responses.
   ###
   Context:
   1. You are planning a trip to {city}, {country} from {start_date} to {end_date}. 
   2. {preferences_list} is a list of activities that a user wants to be included in their travel plan.
      a. if the list contains 'Outdoor Activities', prioritise recommending outdoor activities like hiking etc.
      b. if the list contains 'Socializing & Nightlife', prioritise recommending social activies and clubs, dancing etc.
      c. if the list contains 'Arts & Culture', prioritise recommending museums, art galleries, etc.
      d. if the list contains 'Food', prioritise recommending good restaurants.
      e. if the list contains one or more of these activities, mix and match the recommendations.       
   3. User will be travelling in a {who_filter} setting. So make sure you tailor your reccomendation based on this attribute, ie:
      a. if the value is couple, prioritise recommending romantic things to do.
      b. if the value is family, prioritise recommending more family oriented activities.
      c. if the value is friends, prioritise recommending suited to a friend group.
      d. if the value is solo, prioritise recommending good solo activities.
   4. Include the time duration range for each output on the intinerary, e.g. if you recommend the explore Louvre in Paris you should also give a time range like [30 minutes - 120 minutes ]
   ###

   Recommend atleast three places to visit for each day.
   Be sure to include web links to the places that you recommend. e.g. if you recommend the Louvre in Paris, include a hyperlink to its website in your response.
   
   ###
   Format your response in the following format:
   Day 1: 
   <Recommendation 1>
   .
   .
   Day 2:
   <Recommendation 1>
   .
   .
   and so on
   ###

   Your response:
   """

   # prompt = PromptTemplate(template=system_prompt, input_variables=['start_date','end_date','country','city','filter_1','filter_2','filter_3','filter_4'])
   sys_message = system_prompt
   # sys_message = "You are a travel advising AI bot that helps the user in planning itinerary for a user. the user will also provide their preferences for the following attributes {} with a score in the range 0-5. Where an attribute with a low score should be given a very low priotiy in the itinerary and  an attribute with a high value like 5 should be given high priority while planning the itinerary ".format(list(ref.keys()))
   human_message = "Hi Can you plan a travel for me to {},{} from {} to {} given the following qualities and their scores".format(city,country,start_date,end_date)
   basic_sys_message = f"""
   Can you find the the values of the following variables for {country}:
   1.Currency
   2.Capital
   3.Electricity port type
   4.Best form of transport
   5.Time zone
   Give me the output of this query as a python dictionary, the keys should be the variables 
   as stated above and the values should be the response you come up with, 
   if you are not able to find an the value of a key the value should be None
   The returned dictionary should not have any text outside curly braces"""
   basic_information_response = generate_response(basic_sys_message,human_message)
   st.write(basic_information_response)
   tab1, tab2, tab3,tab4 = st.tabs(["Basic Information", "Weather", "Safety Guidelines","Crime Stats"])

   with tab1:
      st.header("Basic Information")
     
         
      basic_info_dict = eval(basic_information_response)
      print(basic_info_dict)
      df_basic_info = pd.DataFrame(basic_info_dict,index = [0])
      st.table(df_basic_info)
      # except:
      #    st.write("No response")

   with tab2:
      st.header("Safety Guidelines")
      st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

   with tab3:
      st.header("Crime Stats")
      st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
   st.write(generate_response(sys_message,human_message))

