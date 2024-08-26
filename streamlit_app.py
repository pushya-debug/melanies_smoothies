# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Customize and order your smoothie:
    """)

# Input for name on order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on Smoothie will be:', name_on_order)

# Checkbox to mark the order as filled or not filled
# This is for editing existing orders, it’s set to False by default for new orders
order_filled = st.checkbox('Mark as filled', value=False)

# Get Snowflake session
session = get_active_session()

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
        
        # Determine if the order is filled based on the checkbox
        order_filled_value = 'TRUE' if order_filled else 'FALSE'
        
        # Construct the SQL query
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string}', '{name_on_order}', {order_filled_value})
        """
        st.write(my_insert_stmt)  # For debugging: shows the query that will be executed
        # st.stop()  # Uncomment to stop execution and view query

        # Execute the query
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
    else:
        st.error('Please enter a name and select at least one ingredient.', icon="❌")
