import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.header("📊 Live Feedback Dashboard")

# Load feedback data
df = load_feedback()  # make sure you already have a load_feedback() function

if not df.empty:
    # -------------------------------
    # 🟢 EMOJI SUMMARY SECTION
    # -------------------------------
    st.subheader("😀 Live Emoji Summary")

    emoji_counts = {
        "😊 Happy": (df['Sentiment'] > 0).sum(),
        "😐 Neutral": (df['Sentiment'] == 0).sum(),
        "😢 Sad": (df['Sentiment'] < 0).sum()
    }

    # Show colored emojis with counts
    st.markdown(
        f"<p style='color:green;font-size:18px;'>😊 Happy: {emoji_counts['😊 Happy']}</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='color:orange;font-size:18px;'>😐 Neutral: {emoji_counts['😐 Neutral']}</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='color:red;font-size:18px;'>😢 Sad: {emoji_counts['😢 Sad']}</p>",
        unsafe_allow_html=True
    )

    # Divider line
    st.markdown("---")

    # -------------------------------
    # 🎨 SENTIMENT PIE CHART SECTION
    # -------------------------------
    st.subheader("💬 Sentiment Distribution Pie Chart")

    labels = ['😃 Happy', '😐 Neutral', '😔 Sad']
    sizes = [emoji_counts['😊 Happy'], emoji_counts['😐 Neutral'], emoji_counts['😢 Sad']]
    colors = ['#4CAF50', '#FFC107', '#F44336']  # Green, Yellow, Red

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        shadow=True,
        textprops={'color': 'white', 'fontsize': 11}
    )

    ax.set_title("Sentiment Analysis", fontsize=14, color='#333', pad=20)
    plt.setp(autotexts, size=11, weight="bold")

    st.pyplot(fig)
else:
    st.info("No feedback yet to display reactions or sentiment.")