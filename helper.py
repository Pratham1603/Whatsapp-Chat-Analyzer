from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import re
import emoji

extract = URLExtract()

# Function to Statistics Area
def fetch_stats(selected_user,df):

    if selected_user != "Overall":
        # consideration will be for Overall and if not then df will be changed according to user
        df = df[df['user'] == selected_user]

    # 1. Fetch the total no. of messages
    num_messages = df.shape[0]

    # 2. Fetch the total no. of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # 3. Fetch the total no. of media file
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # 3. Fetch the total no. of media file
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

# Function to find Most Busy Users
def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'product'})
    return x, df

# Function to Create WordCloud
def create_wordcloud(selected_user,df):

    # reading stop_hinglish.txt
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    print(stop_words)

    if selected_user != "Overall":
        # consideration will be for Overall and if not then df will be changed according to user
        df = df[df['user'] == selected_user]

    # remove group notification messages
    temp = df[df['user'] != 'group_notification']
    # remove media omitted messages
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):

        # remove URLs
        message = re.sub(r'http\S+|www\S+', '', message)

        # remove html tags
        message = re.sub(r'<.*?>', '', message)

        # remove non letters
        message = re.sub(r'[^a-zA-Z\s]', '', message)

        y = []
        for word in message.lower().split():
            if word not in stop_words and len(word) > 2:
                y.append(word)

        return ' '.join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))

    return df_wc

# Function to Create Most Common Words barchart
def most_common_words(selected_user, df):

    # reading stop_hinglish.txt
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    print(stop_words)

    if selected_user != "Overall":
        # consideration will be for Overall and if not then df will be changed according to user
        df = df[df['user'] == selected_user]

    # remove group notification messages
    temp = df[df['user'] != 'group_notification']
    # remove media omitted messages
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        # remove html tags
        message = re.sub(r'<.*?>', '', message)

        # keep only alphabets
        message = re.sub(r'[^a-zA-Z\s]', '', message)

        # remove punctuation & symbols
        message = re.sub(r'[^\w\s]', '', message)

        # remove numbers from entire message
        message = re.sub(r'\d+', '', message)

        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(25))

    return most_common_df

# Function Emoji Analysis
def emoji_helper(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emoji_list = []
    for message in df['message']:
        emoji_list.extend(emoji.distinct_emoji_list(message))

    # Make a clean dataframe with proper column names
    emoji_df = pd.DataFrame(
        Counter(emoji_list).most_common(25),
        columns=['emoji', 'count']  # <-- important!
    )

    return emoji_df

# Function for Monthly Timeline
def monthly_timeline(selected_user, df):

    if selected_user != "Overall":
        # consideration will be for Overall and if not then df will be changed according to user
        df = df[df['user'] == selected_user]


    # Group messages by year and month
    # Count number of messages per (year, month)
    timeline = (
        df.groupby(['year', 'month_num', 'month'])['message']
          .count()
          .reset_index()
    )

    # Create a combined "Month-Year" column for plotting (e.g., Jan-2023)
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)

    return timeline

# Function for Daily Timeline
def daily_timeline(selected_user, df):

    if selected_user != "Overall":
        # consideration will be for Overall and if not then df will be changed according to user
        df = df[df['user'] == selected_user]

    dailys_timeline = df.groupby('only_date').count()['message'].reset_index()

    return dailys_timeline

# Function for Weekly Active days
def week_activity_map(selected_user, df):
    # Filter by user if not Overall
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Count messages per day
    busy_day = df['day_name'].value_counts()

    # Ensure all weekdays are present in correct order
    week_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    busy_day = busy_day.reindex(week_order, fill_value=0)

    return busy_day

# Function for Month Active days
def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    # Count messages per month
    busy_month = df['month'].value_counts()

    # Ensure all months are present in correct order
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    busy_month = busy_month.reindex(month_order, fill_value=0)

    return busy_month

# Function for Active hours on Active days
def activity_heatmap(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    heatmap_data = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)

    return heatmap_data