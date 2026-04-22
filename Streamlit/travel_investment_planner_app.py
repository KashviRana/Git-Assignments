import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random

st.set_page_config(page_title="Travel & Investment Planner App", page_icon="🌍", layout="centered")

# ===================================Task 1: The Setup & Header=======================================

st.title(":rainbow[PlanWise: Travel :material/globe_book: & Investment :material/account_balance: Companion]",text_alignment="center")
st.caption(""":yellow[Your all-in-one companion to plan smarter trips and investments.   
           Filter data, visualize insights, and build your future with confidence.]""", text_alignment="center")

st.write("  Welcome to **PlanWise** ⏰ --  Explore insights, *plan smarter journeys*, and make *better financial decisions*.")

if "visited" not in st.session_state:
    st.success("Welcome to PlanWise! Your planning journey starts here.. :material/travel:")
    st.session_state.visited = True

# ===================================Task 2: The Sidebar & Input Controls=============================

st.sidebar.title(":yellow[User Preferences :material/user_attributes:]", text_alignment="center")

st.sidebar.radio(":material/accessible_menu: Select your User level",("Beginner","Intermediate","Advanced"))
st.sidebar.write("")
continent = st.sidebar.selectbox(":material/globe_location_pin: Choose Target Continent",["Africa","Asia","Europe","North America", "South America", "Australia"])
st.sidebar.write("")
interests = st.sidebar.multiselect(":material/interests: Select Interests",["Tech","Finance","Travel","Food"])
if not interests:
    st.sidebar.warning("Please select at least one interest ⚠️")
st.sidebar.write("")
budget = st.sidebar.slider(":material/account_balance_wallet: Investment Budget", min_value=0, max_value=10000, value=1000)

#====================================Task 3: Temporal & Data Handling===========================================

c1,c2 = st.columns(2)

date = c1.date_input("Project Start Date",datetime.date.today())
c2.write("")
#c2.write(f"### Budget: ₹{budget}")
c2.subheader(f":material/money_bag: Budget: ₹{budget}", text_alignment="center")

st.write("")
st.write("")

st.subheader("Financial Data :material/finance_mode:", text_alignment="center")

data = pd.DataFrame({
    "Date": pd.date_range(start="2024-01-01", periods=10),
    "Category": np.random.choice(["Africa","Asia","Europe","North America", "South America", "Australia"], size=10),
    "Amount": np.random.randint(500, 5000, size=10),
    "Status": np.random.choice(["Pending","Completed"], size=10),
    "Growth": np.round(np.random.uniform(-5, 20, size=10),2)
})

df = pd.DataFrame(data)

filtered_df = df[df["Category"] == continent]

st.dataframe(filtered_df)

#============================================Task 4: Logic & Feedback=======================================

name = st.text_input("Enter your Name", placeholder="Enter your name here..")

c3,c4,c5,c6,c7 = st.columns(5)
if c5.button("**Process Report**", type="primary", icon=":material/touch_app:"):
    if budget > 0:
        daily_budget = budget / 30
        st.write(f"""
                👤 User **{name}** wants to travel to **{continent}**  
                📅 starting from {date}  
                💸 Daily Budget: ₹{daily_budget:.2f}""")
        st.balloons()
    else:
        st.warning("⚠️ Budget must be greater than 0 to process report!")

#=======================================Task 5: Refinement & Error Handling============================

if budget == 0:
    st.sidebar.info("Please set your investment budget to proceed.ℹ️")