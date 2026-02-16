import streamlit as st
import pandas as pd

st.title("🟢 LivePulse: Real-Time Feedback Visualizer")

# Collect feedback
name = st.text_input("Your Name")
rating = st.slider("Rate this event (1–5)", 1, 5)
comment = st.text_area("Your Comment")

if st.button("Submit"):
    data = {"Name": name, "Rating": rating, "Comment": comment}
    df = pd.DataFrame([data])
    df.to_csv("feedback.csv", mode='a', header=False, index=False)
    st.success("✅ Feedback submitted successfully!")