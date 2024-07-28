# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize your smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie:
    """
)

name_on_order = st.text_input("Name on smoothie:")
st.write("The name on your smoothie will be: ", name_on_order)

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("fruit_name"))
st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'choose up to five ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit in ingredients_list:
        ingredients_string += fruit + " "
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
