# Name : text_input
# City : Dropdown 
# Food preferences : multiselect
# Slider : how may times you ordered the food from the same restaurant
# Gender : radio
# DOB : calendar            2 columns : food Item, and Beverages (select)
# Audio message
# Text Area : Feedback
# Checkbox : I aggree 
# Submit button
# Message : Your Order has been successfully completed




import streamlit as st
import datetime

st.set_page_config(page_title="Food App", page_icon="😋", layout="centered")

with st.form("Food App"):
    st.title("Order Your Delicious Food !", text_alignment="center")

    name = st.text_input("Name", placeholder="Enter your name here..")

    city = st.selectbox("City", ("Vadodara","Ahmedabad","Surat","Navsari","Valsad"))

    food_pre = st.multiselect("Food Preferences", ["South Indian","Punjabi","Chinese","Kathiyawadi"])

    count = st.slider("How may times you ordered the food from the same restaurant?", min_value=1, max_value=20, value=2)

    c1,c2 = st.columns(2)
    gender = c1.radio("Gender",("Male","Female","Other"), horizontal=True)
    dob = c2.date_input("Enter your DOB", datetime.date(2005,1,24))

    c3, c4 = st.columns(2)
    food_type = c3.multiselect("Food Type", ["Breakfast","Lunch","Dinner"])
    bev = c4.multiselect("Beverages",["Hot Beverages","Cold Beverages","Alcoholic"])

    audio_msg = st.audio_input("Additional Order")
    if audio_msg:
        st.write("Your order recorded successfully.")
        st.audio(audio_msg)

    feedback = st.text_area("Give your Feedback", placeholder="Enter your text here..", height=175)

    done = st.checkbox("I Agree")

    c5,c6,c7 = st.columns(3)
    submit = c6.form_submit_button("Submit Your Order",type="primary")
    
    if submit:
        if not done:
            st.error("Please, Agree your order first.")
        else:
            st.success("Your Order has been completed successfully!")
            st.write("Name: ",name)
            st.write("City: ",city)
            st.write("Food Preferences: ",food_pre)
            st.write(f"You visit this restaurant {count} times")
            st.write("Gender: ",gender)
            st.write("Date of Birth: ",dob)
            st.write("Ordered Food: ",food_type)
            st.write("Beverages: ",bev)
            st.write("Your Feedback: ",feedback)
