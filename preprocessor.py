import re
import pandas as pd

def preprocessor(data):
    pattern = r'\d{1,2}\/\d{1,2}\/\d{2},\s\d{1,2}:\d{2}\s(?:am|pm)\s-\s'

    messages = re.split(pattern, data)[1:]

    dates = re.findall(pattern, data)
    dates = [d.replace('\u202f', ' ') for d in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # convert message_date type explicitly into
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p - ')  # '%d/%m/%Y, %H:%M - '

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)  # spliting on basis of :-  Pratham Harer: ---> ([\w\W]+?):\s

        if entry[1:]:  # If username exists
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append(
                'group_notification')  # the message that doesn't contain a semicolon, like ( Messages to yourself are end-to-end encrypted... )
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages

    df.drop(columns=['user_message'], inplace=True)  # No longer needed coz unstructure so dropped

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    period_order = []  # NEW: keep hour as numeric for sorting
    for hour in df[['day_name', 'hour']]['hour']:
        hour = int(hour)  # ensure it's an integer

        if hour == 23:
            period.append(f"{hour}-00")  # wrap around for 23
        else:
            period.append(f"{hour}-{hour + 1}")  # normal case

        period_order.append(hour)  # store numeric hour

    # new col.
    df['period'] = period
    df['period_order'] = period_order  # use this for sorting when plotting

    return df
