# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("Customize your smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie:
    """
)

name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be: ", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col("fruit_name"),col("search_on"))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#convert snowpark df to pandas df to use LOC function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)

ingredients_list = st.multiselect(
    'choose up to five ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit in ingredients_list:
        ingredients_string += fruit + " "
        # search using search_on column in pandas df
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit,' is ', search_on, '.')
        st.subheader( fruit + ' Nutrition Information' )
        # get API data
        fruityvice_response = requests.get( "https://fruityvice.com/api/fruit/" + search_on )
        fv_df = st.dataframe(data = fruityvice_response.json(), use_container_width=True)
        
    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values (
                '""" + ingredients_string + """',
                '""" + name_on_order + """'
                        )"""
    st.write(my_insert_stmt)
    time_to_insert = st.button("submit order!")
    if time_to_insert:
        if ingredients_string:
            session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered '+name_on_order+'!', icon="✅")

