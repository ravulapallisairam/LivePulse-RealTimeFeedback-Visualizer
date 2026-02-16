from textblob import TextBlob

if st.button("Analyze Sentiments"):
    feedback_data["Sentiment"] = feedback_data["Comment"].apply(
        lambda x: TextBlob(str(x)).sentiment.polarity
    )
    st.line_chart(feedback_data["Sentiment"])