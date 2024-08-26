# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Customize and order your smoothie:")

# Input for name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on Smoothie will be:', name_on_order)

# Checkbox to mark the order as filled or not filled
order_filled = st.checkbox('Mark as filled', value=False)

# Get Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch the available fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
pd_df = my_dataframe.to_pandas()

# Display the fruit options in a dataframe
st.dataframe(pd_df)

# Allow user to select fruits for their smoothie
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Handle form submission
if st.button('Submit Order'):
    if ingredients_list and name_on_order:
        # Create the ingredients string
        ingredients_string = ' '.join(ingredients_list)
        
        # Display nutrition information for each selected fruit
        for fruit_chosen in ingredients_list:
            st.subheader(f"{fruit_chosen} Nutrition Information")
            try:
                # API call to Fruityvice
                fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}")
                fruityvice_response.raise_for_status()  # Raise an exception for HTTP errors
                fruityvice_data = fruityvice_response.json()  # Convert response to JSON
                
                # Extract relevant details from API response
                fruit_name = fruityvice_data.get('name', 'Unknown')
                calories = fruityvice_data.get('nutritions', {}).get('calories', 'Unknown')
                fat = fruityvice_data.get('nutritions', {}).get('fat', 'Unknown')
                sugar = fruityvice_data.get('nutritions', {}).get('sugar', 'Unknown')
                carbs = fruityvice_data.get('nutritions', {}).get('carbohydrates', 'Unknown')
                protein = fruityvice_data.get('nutritions', {}).get('protein', 'Unknown')

                # Display formatted nutrition information
                st.write(f"**Fruit Name:** {fruit_name}")
                st.write(f"**Calories:** {calories} kcal")
                st.write(f"**Fat:** {fat} g")
                st.write(f"**Sugar:** {sugar} g")
                st.write(f"**Carbohydrates:** {carbs} g")
                st.write(f"**Protein:** {protein} g")
            except requests.RequestException as e:
                st.error(f"Error fetching data for {fruit_chosen}: {e}", icon="❌")
            except ValueError as e:
                st.error(f"Error processing data for {fruit_chosen}: {e}", icon="❌")
        
        # Determine if the order is filled based on the checkbox
        order_filled_value = 'TRUE' if order_filled else 'FALSE'
        
        # Construct the SQL query
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string}', '{name_on_order}', {order_filled_value})
        """
        st.write(my_insert_stmt)  # For debugging: shows the query that will be executed
        # Uncomment to stop execution and view query
        # st.stop()

        # Execute the query
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
    else:
        st.error('Please enter a name and select at least one ingredient.', icon="❌")
