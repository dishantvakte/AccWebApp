import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from haversine import haversine, Unit
from geopy.distance import geodesic
import geopy.distance
import folium
from streamlit_folium import st_folium, folium_static 
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import requests


#Setting the title for the page
st.set_page_config(page_title = "Find Facilities Nearby", page_icon = ":office_building:U+1F3E2", layout="wide")

#Creating containers
header = st.container()
subheader1 = st.container()
dataset = st.container()
#selection_display = st.container()
result_display = st.container()


#ce=reating Headers
with subheader1:
    st.subheader("Enter the Address or Zipcode you want to search for")

with header:
    st.title("KO Storage")
    


def load_data(path):
    return pd.read_csv(path)
    
    
#Taking inputs
with dataset:
    zipcodes = load_data(r"US Zip Codes from 2013 Government Data.csv")
    fac_info = load_data(r"Fac_info.csv")
    
    
    sel_col, disp_col, disp_col2, disp_col3 = st.columns([2.5,2.5,1,2.5])
    
    with sel_col:
    
        new_address = sel_col.text_input("Search by Address", '')
        radius = sel_col.slider('Select the Radius of the Search', min_value = 5, max_value = 300, value = 100, step = 5)

    with disp_col:
        new_zip = disp_col.number_input("Search by Zipcode", value = 55305)
        
        st.markdown(f"<p style='font-size:15px;border-collapse: collapse;padding: 0; margin: 0;'>Zipcode will be ignored if address is entered</p>", unsafe_allow_html=True)

###################################################### Adding extra here #####################################
    
#    with disp_col3:
#        test_display = st.container()    

#        test_col1,test_col2 = st.columns(2)
#        with test_col1:
#            numb_of_disp1 = st.number_input("Enter number of rows to be displayed", value = 5,)
    

#       if st.button('Calculate Time'):
#            st.write(df_2.head(numb_of_disp1))
#        #else:
#        st.markdown(f"<p style='font-size:15px;border-collapse: collapse;padding: 0; margin: 0;'>Calculating drive time can be computationally heavy</p>", unsafe_allow_html=True) 
    
#Definining a function to calculate the distance
#@st.cache_data    
def calculate_distance(row):
    coord1 = (row['latitude'], row['longitude'])
    coord2 = LAT, LNG
    return geodesic(coord1, coord2).miles
    

#df_2 = pd.DataFrame()

#If neither address nor zipcode is entered
if not new_address and not new_zip:
    with result_display:

        result_display_sub = st.container()

        with result_display_sub:
            display_sub1, display_sub2 =st.columns(2)
            with display_sub1:
                st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>Enter address or Zipcode</p>", unsafe_allow_html=True)

    
        result_col1, result_col2 = st.columns(2)
    
    
        m = folium.Map(location=[44.972155552614254, -93.41025401521466], 
                    zoom_start=7, control_scale=True)


        with result_col1:
            #st_data = result_col1.st_folium(m, width=900)
            folium_static(m, width=870)    




#If only zipcode is entered
elif not new_address and new_zip:  
    new_zip = int(new_zip)
    zip_code_lookup1 = zipcodes[zipcodes['ZIP'] == new_zip]

    if(len(zip_code_lookup1) == 1):
        #Extracting the Lat Long of the Zip code 
        LAT = zip_code_lookup1.iloc[0,1]
        LNG = zip_code_lookup1.iloc[0,2]



        #Creating a copy and calculating the distance
        facilities_list_copy = fac_info.copy(deep = True)
        facilities_list_copy['distance'] = facilities_list_copy.apply(calculate_distance, axis=1)

        #Filteirng based on the input radius
        df = facilities_list_copy[facilities_list_copy['distance'] <= radius]
        df_2 = df[['name', 'state', 'postal', 'distance', 'flag', 'Status']]
        df_2.sort_values(by = 'distance', inplace = True)
        df_2['distance'] = round(df_2['distance'],2)

        #Removing "KO Storage of" from the name to make it more readable
        df_2['Facility'] = df_2['name'].str.replace(r"KO Storage of ", '')


        #Getting the name of the datasets to match
        zip_code_lookup1.rename(columns ={'ZIP':'name', 'LAT':'latitude', 'LNG':'longitude'}, inplace = True)


        df3 = pd.concat([df[['name','latitude','longitude', 'Status', 'flag']],zip_code_lookup1])
        df3.fillna('Location', inplace = True)


    if(len(zip_code_lookup1) == 1):
        with result_display:

            result_display_sub = st.container()

            with result_display_sub:
                display_sub1, display_sub2 =st.columns(2)
                with display_sub1:
                    st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>Searching for Facilities in {radius} miles range for Zipcode {zip_code_lookup1.iloc[0,0]}</p>", unsafe_allow_html=True)

    
            result_col1, blank_col, result_col2 = st.columns([5,2,5])
    
    
            m = folium.Map(location=[LAT, LNG], 
                        zoom_start=7, control_scale=True)

            #Loop through each row in the dataframe
            
            if (len(df3)>1):
                for i,row in df3.iterrows():
                    #Setup the content of the popup
                    iframe = folium.IFrame(str(row["name"]))
    
                    #Initialise the popup using the iframe
                    popup = folium.Popup(iframe, min_width=170, max_width=170)
    
                    if (row['Status'] == "Location"):
                        #Add each row to the map
                        folium.Marker(location=[row['latitude'],row['longitude']],
                                popup = popup, icon=folium.Icon(color='red', prefix='fa', icon = '')).add_to(m)
                                
                    elif (row['Status'] == "Upcoming"):
                        #Add each row to the map
                        folium.Marker(location=[row['latitude'],row['longitude']],
                                popup = popup, icon=folium.Icon(color='lightgray', prefix='fa', icon = '')).add_to(m)
                    
                    else:
                        folium.Marker(location=[row['latitude'],row['longitude']],
                                popup = popup, c=row['name']).add_to(m)
            else:
                folium.Marker(location=[LAT,LNG],
                                icon=folium.Icon(color='red', prefix='fa', icon = '')).add_to(m)
                

            with result_col1:
            #st_data = result_col1.st_folium(m, width=900)
                folium_static(m, width=870)
    
            with result_col2:
                df_2.reset_index(inplace = True)
                df_2.drop(columns = ['index'], inplace = True)
                fig = ff.create_table(df_2[['Facility','distance','state','postal','Status']])
                fig.update_annotations()
            # Make text size larger
                for i in range(len(fig.layout.annotations)):
                    fig.layout.annotations[i].font.size = 15


                st.write(fig)
        with result_display_sub:
            with display_sub1:
                st.markdown(f"<p style='font-size:30px;border-collapse: collapse;padding: 0; margin: 0;'><b>{len(df_2)} Facilities Found</b></p>", unsafe_allow_html=True)
       

    else:
        with result_display:

            result_display_sub = st.container()

            with result_display_sub:
                display_sub1, display_sub2 =st.columns(2)
                with display_sub1:
                    st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>Could not find the Zipcode</p>", unsafe_allow_html=True)

    
            result_col1, result_col2 = st.columns(2)
    
    
            m = folium.Map(location=[44.972155552614254, -93.41025401521466], 
                        zoom_start=7, control_scale=True)


            with result_col1:
                #st_data = result_col1.st_folium(m, width=900)
                folium_static(m, width=870)


########################################################################################################
  

       
        
    



elif new_address:
    
    #Here API for geolocation
    # Here.com API endpoint
    endpoint = "https://geocode.search.hereapi.com/v1/geocode"
    
    # Here.com API key
    api_key = st.secrets["api_key"]
    
    
    query = new_address
    
    # Request parameters
    params = {
        "q": query,
        "apiKey": api_key,
    }
    
    flag = 0
    
    # Send request to Here.com API
    response = requests.get(endpoint, params=params)
    
    try:
    
        # Check if request was successful
        if response.status_code == 200:
    
        
            # Parse response JSON
            response_json = response.json()
    
            # Extract latitude and longitude of first result
            result = response_json["items"][0]
            LAT = result["position"]["lat"]
            LNG = result["position"]["lng"]
            
            flag = 1
        
########################### Added an indentation here ##################################
        
            facilities_list_copy = fac_info.copy(deep = True)
    
            facilities_list_copy['distance'] = facilities_list_copy.apply(calculate_distance, axis=1)
    
            df = facilities_list_copy[facilities_list_copy['distance'] <= radius]
        
        
            
    
            origin_coord = str(LAT) +','+str(LNG)
    
            api_key_dt = st.secrets["api_key_dt"]
    
            with_distance = pd.DataFrame()
    
    
            for index, row in df.iterrows(): 
                sub_df = pd.DataFrame()
                dest_coord = str(row['latitude']) +','+str(row['longitude'])   
                url =   f"https://router.hereapi.com/v8/routes?transportMode=car&origin={origin_coord}&destination={dest_coord}&return=summary&apikey={api_key_dt}"
                sub_df["name"] = row['name']
                sub_df['state'] = row['state']
                response = requests.get(url)
        
                if response.status_code == 200:
                    # Parse response JSON
                    response_json = response.json()
                    sub_df['Drive Time'] = response_json['routes'][0]['sections'][0]['summary']['duration']/3600
                    sub_df_mins = response_json['routes'][0]['sections'][0]['summary']['duration']/60
                    sub_df['Drive Distance'] = round(response_json['routes'][0]['sections'][0]['summary']['length']*0.00062137,2)
            
            
                    if sub_df_mins>= 60:
                        sub_df_time = str(int(sub_df_mins//60)) + ' hrs ' +  str(int(sub_df_mins%60)) + ' mins'
                        sub_df = pd.DataFrame(data = [[row['name'],row['state'], response_json['routes'][0]['sections'][0]['summary']['duration']/3600, round(response_json['routes'][0]['sections'][0]['summary']['length']*0.00062137,2),sub_df_time, row['Status']]], columns = ["name", "state","Drive Time", "Drive Distance", "Time", "Status"])
        
                    else:    
                        sub_df_time = str(int(sub_df_mins%60)) + 'mins'
                        sub_df = pd.DataFrame(data = [[row['name'],row['state'], response_json['routes'][0]['sections'][0]['summary']['duration']/3600, round(response_json['routes'][0]['sections'][0]['summary']['length']*0.00062137,2),sub_df_time, row['Status']]], columns = ["name", "state","Drive Time", "Drive Distance", "Time", "Status"])


                    with_distance = pd.concat([with_distance, sub_df])
            
            
                else:
                # Request was unsuccessful
                    sub_df = pd.DataFrame(data = [[row['name'],row['state'], "Process Failed", "Process Failed","Process Failed", row['Status']]], columns = ["name", "state","Drive Time", "Drive Distance","Time", "Status"])
                    with_distance = pd.concat([with_distance, sub_df])
            
    
            df_2 = with_distance.copy(deep = True)
            df_2['Facility'] = df_2['name'].str.replace(r"KO Storage of ", '')
    

            #Sorting Based on Distance    
            df_2.sort_values(by = 'Drive Distance', inplace = True)
    
    
            #Adding address to the lat long df
            name = new_address
            address_df = pd.DataFrame([[name,LAT, LNG]], columns =['name', 'latitude','longitude'])
            
            
            df3 = pd.concat([df[['name','latitude','longitude','Status']],address_df])
            df3.fillna('Location', inplace = True)
    
    ##################################Till here###################################
            if(len(address_df) == 1):
                with result_display:

                    result_display_sub = st.container()

                    with result_display_sub:
                        display_sub1, display_sub2 =st.columns(2)
                        with display_sub1:
                            st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>Searching for Facilities in {radius} miles range for {new_address}</p>", unsafe_allow_html=True)

    
                    result_col1, blank_col, result_col2 = st.columns([5,2,5])
    
    
                    m = folium.Map(location=[LAT, LNG], 
                        zoom_start=7, control_scale=True)

                    #Loop through each row in the dataframe
                    
                    if (len(df3)>=1):
                        for i,row in df3.iterrows():
                            #Setup the content of the popup
                            iframe = folium.IFrame(str(row["name"]))
    
                        #Initialise the popup using the iframe
                            popup = folium.Popup(iframe, min_width=170, max_width=170)
                    
                    
                    ######################################################
    
                            if (row['Status'] == 'Location'):
                                #Add each row to the map
                                folium.Marker(location=[row['latitude'],row['longitude']],
                                        popup = popup, icon=folium.Icon(color='red', prefix='fa', icon = '')).add_to(m)
 

                            if (row['Status'] == 'Upcoming'):
                                #Add each row to the map
                                folium.Marker(location=[row['latitude'],row['longitude']],
                                        popup = popup, icon=folium.Icon(color='gray', prefix='fa', icon = '')).add_to(m)
                                        
 
                            else:
                                folium.Marker(location=[row['latitude'],row['longitude']],
                                        popup = popup, c=row['name']).add_to(m)
    
                    else:
                    #Display the point only
                        folium.Marker(location=[LAT,LNG],
                                        icon=folium.Icon(color='red', prefix='fa', icon = '')).add_to(m)
                    
                    with result_col1:
                        #st_data = result_col1.st_folium(m, width=900)
                        folium_static(m, width=870)
            
            
                    with result_col2:
                        df_2.reset_index(inplace = True)
                        df_2.drop(columns = ['index'], inplace = True)
                        fig = ff.create_table(df_2[['Facility','Time','Drive Distance','state','Status']])
                        fig.update_annotations()
                    # Make text size larger
                        for i in range(len(fig.layout.annotations)):
                            fig.layout.annotations[i].font.size = 15


                        st.write(fig)
                #with result_display_sub:
                #    with display_sub2:
                #        st.markdown(f"<p style='font-size:30px;text-align:left;border-collapse: collapse;padding: 0; margin: 0;'>{len(df_2)} Facilities Found</p>", unsafe_allow_html=True)

                with result_display_sub:
                    with display_sub1:
                        st.markdown(f"<p style='font-size:30px;border-collapse: collapse;padding: 0; margin: 0;'><b>{len(df_2)} Facilities Found</b></p>", unsafe_allow_html=True)
        else:
            with result_display:

                result_display_sub = st.container()

                with result_display_sub:
                    display_sub1, display_sub2 =st.columns(2)
                    with display_sub1:
                    #if len(df3):
                        st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>0 Could not find {new_address} on the map ELSE</p>", unsafe_allow_html=True)
   #                 else:
   #                     st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>Could not find {new_address} on the map</p>", unsafe_allow_html=True)

    
    
    except:
    
        # Check if request was successful
        try:
    
        
            # Parse response JSON
            response_json = response.json()
    
            # Extract latitude and longitude of first result
            result = response_json["items"][0]
            LAT = result["position"]["lat"]
            LNG = result["position"]["lng"]
            
            with result_display:

                result_display_sub = st.container()

                with result_display_sub:
                    display_sub1, display_sub2 =st.columns(2)
                    with display_sub1:
                        #if len(df3):
                        st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>No Facilities found near {new_address}</p>", unsafe_allow_html=True)
   #                 else:
   #                     st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>Could not find {new_address} on the map</p>", unsafe_allow_html=True)

    
                result_col1, result_col2 = st.columns(2)
    
    
                m = folium.Map(location=[LAT, LNG], 
                            zoom_start=7, control_scale=True)

                

                with result_col1:
                #st_data = result_col1.st_folium(m, width=900)
                    folium_static(m, width=870)    
                    
                    
        except:

            # Parse response JSON
            
            with result_display:

                result_display_sub = st.container()

                with result_display_sub:
                    display_sub1, display_sub2 =st.columns(2)
                    with display_sub1:
                        #if len(df3):
   #                     st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>No Facilities found near {new_address}</p>", unsafe_allow_html=True)
   #                 else:
                        st.markdown(f"<p style='font-size:20px;border-collapse: collapse;padding: 0; margin: 0;'>Could not find {new_address} on the map</p>", unsafe_allow_html=True)

    
                result_col1, result_col2 = st.columns(2)
    
    
                m = folium.Map(location=[44.972155552614254, -93.41025401521466], 
                            zoom_start=7, control_scale=True)


                with result_col1:
                #st_data = result_col1.st_folium(m, width=900)
                    folium_static(m, width=870)             
