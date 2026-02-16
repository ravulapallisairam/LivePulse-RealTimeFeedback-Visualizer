# app.py
import streamlit as st
import pandas as pd
import os
from textblob import TextBlob
import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px

# --- Page setup ---
st.set_page_config(page_title="LivePulse", layout="wide")

# --- Basic Styling ---
st.markdown("""
<style>
    h1, h2, h3 { color: #1E90FF; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius:10px; }
    .stMetric { text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- File paths ---
CSV_FILE = "feedback.csv"
COLUMNS = ["timestamp", "name", "rating", "emoji", "comment", "sentiment"]
STUDENTS_FILE = "students.csv"

# --- Load student data ---
if os.path.exists(STUDENTS_FILE):
    students = pd.read_csv(STUDENTS_FILE)
else:
    students = pd.DataFrame(columns=["regno", "name", "department", "year"])

# --- CSV helper functions ---
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)

def save_feedback(name, rating, emoji, comment, sentiment):
    ensure_csv()
    df = pd.DataFrame([{
        "timestamp": datetime.datetime.now().isoformat(timespec='seconds'),
        "name": name,
        "rating": rating,
        "emoji": emoji,
        "comment": comment,
        "sentiment": sentiment
    }])
    df.to_csv(CSV_FILE, mode='a', header=False, index=False)

def load_feedback():
    ensure_csv()
    try:
        df = pd.read_csv(CSV_FILE)
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def analyze_sentiment(text):
    if not text or str(text).strip() == "":
        return 0.0
    try:
        return TextBlob(str(text)).sentiment.polarity
    except Exception:
        return 0.0


# --- Sidebar: Student Login ---
st.sidebar.header("🎓 Student Login (Optional)")
regno = st.sidebar.text_input("Enter Register Number (e.g., 2021CS1001)")

student_info = None
if regno:
    match = students[students['regno'].astype(str) == regno.strip()]
    if not match.empty:
        student_info = match.iloc[0].to_dict()
        st.sidebar.success(f"Welcome, {student_info['name']}!")
        st.sidebar.write(f"**Dept:** {student_info['department']}")
        st.sidebar.write(f"**Year:** {student_info['year']}")
    else:
        st.sidebar.warning("RegNo not found. Continue anonymously?")


# --- Main UI ---
st.title("⚡ LivePulse — Real-Time Feedback Visualizer")
st.write("Collect live feedback and show instant charts to presenters.")

col1, col2 = st.columns([1, 1])

# --- Feedback Form ---
with col1:
    st.header("Give Feedback")
    
    if student_info:
        st.write(f"**Logged in as:** {student_info['name']} ({student_info['regno']})")
        name = student_info['name']
    else:
        name = st.text_input("Your name (optional)")
    
    rating = st.slider("Rate this session (1 = worst, 5 = best)", 1, 5, 4)
    emoji = st.selectbox("How do you feel right now?", ["😊 Happy", "😐 Neutral", "😞 Sad"])
    comment = st.text_area("Write a short comment (optional)", max_chars=250)
    
    if st.button("Submit Feedback"):
        polarity = analyze_sentiment(comment)
        name_to_save = name or "Anonymous"
        save_feedback(name_to_save, rating, emoji, comment, polarity)
        st.success("✅ Feedback submitted — thank you!")
        st.balloons()


# --- Quick Stats ---
with col2:
    st.header("Quick Stats")
    df = load_feedback()
    total = len(df)
    st.metric("Total feedbacks", total)
    
    if total > 0:
        avg_rating = round(df["rating"].mean(), 2)
        st.metric("Average rating", avg_rating)
        pos = (df["sentiment"] > 0.1).sum()
        neg = (df["sentiment"] < -0.1).sum()
        neu = total - pos - neg
        st.write(f"Sentiment → 👍 {pos}  |  😐 {neu}  |  👎 {neg}")

# --- Overall Mood Display ---
if not df.empty:
    avg_sentiment = df["sentiment"].mean()
    if avg_sentiment > 0.2:
        color, mood = "green", "😊 Positive"
    elif avg_sentiment < -0.2:
        color, mood = "red", "😞 Negative"
    else:
        color, mood = "gray", "😐 Neutral"
    st.markdown(f"""
    <div style='background-color:{color};padding:10px;border-radius:10px;text-align:center;'>
    <b>Overall Mood:</b> {mood}
    </div>
    """, unsafe_allow_html=True)


# --- Live Dashboard ---
st.markdown("---")
st.header("📊 Live Dashboard")

df = load_feedback()

if df.empty:
    st.info("No feedback yet — ask users to submit feedback from the left panel.")
else:
    # Ratings Distribution
    st.subheader("Ratings distribution")
    ratings_count = df['rating'].value_counts().sort_index()
    st.bar_chart(ratings_count)

    # Interactive Chart
    st.subheader("⭐ Interactive Ratings Chart")
    fig = px.bar(df, x='rating', color='emoji', title="Ratings per Emoji", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    # Emoji Reactions
    st.subheader("Emoji reactions")
    emoji_counts = df['emoji'].value_counts()
    st.write(emoji_counts.to_frame("count"))

    # Recent Comments (Table)
    st.subheader("Recent comments")
    recent = df.sort_values("timestamp", ascending=False).head(10)[
        ["timestamp", "name", "rating", "emoji", "comment", "sentiment"]
    ]
    st.table(recent)

    # Chat-Style Comments
    st.subheader("💬 Live Comments Feed")
    for _, row in df.sort_values("timestamp", ascending=False).head(10).iterrows():
        st.markdown(
            f"**{row['name']} ({row['emoji']})**: {row['comment']}  "
            f"<br><small>⭐ {row['rating']} | 🕒 {row['timestamp']}</small>", 
            unsafe_allow_html=True)

    # Word Cloud
    st.subheader("🧠 Audience Word Cloud")
    text = " ".join(df["comment"].dropna().astype(str))
    if text.strip():
        wc = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

    # Download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download All Feedback (CSV)", csv, "livepulse_feedback.csv", "text/csv")

    # Insights
    st.subheader("Simple Insights")
    st.write(f"Average sentiment: {round(df['sentiment'].mean(),3)}")


st.markdown("---")
st.write("© LivePulse — Enhanced Version with Advanced Visuals & Student Login")