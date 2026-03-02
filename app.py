import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- Centered Title ----------------
st.markdown(
    "<h1 style='text-align: center;'>📊 WhatsApp Chat Analyzer</h1>",
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------- Instructions ----------------
st.info(
    "📂 To use this app: Open the WhatsApp chat → Tap the three dots (⋮) → Select 'More' → Click 'Export Chat' → Choose 'Without Media' and upload the .txt file here."
)

# ---------------- Sidebar ----------------
st.sidebar.title('📊 WhatsApp Chat Analyzer')  # modern emoji touch
st.sidebar.markdown("Upload your exported WhatsApp chat to start analysis.")

uploaded_file = st.sidebar.file_uploader("Choose a file", type=['txt'])
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocessor(data)

    # fetch unique users (for group chat, selection of group member)
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis w.r.t", user_list)

    if st.sidebar.button("Analyze"):
        st.markdown("---")  # divider

        # ---------------- Stats Area ----------------
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.subheader("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label="💬 Total Messages", value=num_messages)
        with col2:
            st.metric(label="📝 Total Words", value=words)
        with col3:
            st.metric(label="📷 Media Shared", value=num_media_messages)
        with col4:
            st.metric(label="🔗 Links Shared", value=num_links)

        st.markdown("---")  # divider

        # ---------------- Monthly Timeline ----------------
        st.subheader("📅 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(timeline['time'], timeline['message'], marker='o', color='#2E8B57')  # prettier green
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        st.pyplot(fig)

        # ---------------- Daily Timeline ----------------
        st.subheader("📈 Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], marker='.', color='#1f77b4')  # modern blue
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        st.pyplot(fig)

        # ---------------- Weekly Activity Map ----------------
        st.subheader("🗓️ Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Week Active Day**")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.bar(busy_day.index, busy_day.values, color='skyblue')
            for i, v in enumerate(busy_day.values):
                ax.text(i, v + 0.5, str(v), ha='center', fontsize=9)
            ax.set_ylabel("Messages")
            ax.set_xlabel("Weekday")
            ax.set_title("Messages by Weekday")
            plt.xticks(rotation=45)
            plt.grid(alpha=0.3, axis='y')
            st.pyplot(fig)

        with col2:
            st.markdown("**Most Busy Month**")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.bar(busy_month.index, busy_month.values, color='mediumseagreen')
            for i, v in enumerate(busy_month.values):
                ax.text(i, v + 0.5, str(v), ha='center', fontsize=9)
            ax.set_ylabel("Messages")
            ax.set_xlabel("Months")
            ax.set_title("Messages by Month")
            plt.xticks(rotation=45)
            plt.grid(alpha=0.3, axis='y')
            st.pyplot(fig)

        # ---------------- Heatmap Activities ----------------
        st.subheader("🔥 Weekly Activity Heatmap")
        heatmap_data = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(heatmap_data, annot=True, fmt=".0f", ax=ax, cmap="YlGnBu")
        st.pyplot(fig)

        # ---------------- Most Busy Users ----------------
        if selected_user == "Overall":
            st.subheader("👥 Most Busy Users")
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()
            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values, color='#FF6F61')
                plt.xticks(rotation=45)
                plt.grid(alpha=0.3, axis='y')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # ---------------- WordCloud ----------------
        st.subheader("☁️ Most Common Messages")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # ---------------- Most Used Words ----------------
        st.subheader("🗨️ Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(most_common_df[0], most_common_df[1], color='#2ca02c')
        plt.xticks(rotation=45)
        plt.grid(alpha=0.3, axis='x')
        st.pyplot(fig)

        # ---------------- Emoji Analysis ----------------
        emoji_df = helper.emoji_helper(selected_user, df)
        st.subheader("😀 Emoji Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie(
                emoji_df['count'].head(),
                labels=emoji_df['emoji'].head(),
                autopct="%0.2f%%",
                startangle=90,
                colors=sns.color_palette("pastel")[0:len(emoji_df['count'].head())]
            )
            st.pyplot(fig)