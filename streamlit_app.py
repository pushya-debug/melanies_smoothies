# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on Smoothie will be:', name_on_order)

# Get Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Allow user to select fruits
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Display information and handle form submission
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        st.subheader(f'{fruit_chosen} Nutrition Information')
        try:
            # API call to Fruityvice
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}")
            fruityvice_response.raise_for_status()  # Raise an exception for HTTP errors
            fruityvice_data = fruityvice_response.json()  # Convert response to JSON

            # Create DataFrame from the API response and display
            fv_df = pd.DataFrame([fruityvice_data])
            st.dataframe(fv_df, use_container_width=True)
        except requests.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}", icon="❌")
        except ValueError as e:
            st.error(f"Error processing data for {fruit_chosen}: {e}", icon="❌")

    # Insert order into Snowflake
    if st.button('Submit Order'):
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        st.write(my_insert_stmt)  # For debugging: shows the query that will be executed
        # Execute the query
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
