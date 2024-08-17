import matplotlib.pyplot as plt
import pandas as pd

# Read data from a CSV file
df = pd.read_csv('stats.csv')
columns = ['User_IP_Address','Hostname','Timestamp']
df.columns = columns
# Convert 'Timestamp' column to datetime
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Group data by Timestamp and Hostname columns
daily_stats = df.groupby([df['Timestamp'].dt.date, 'Hostname']).size().unstack()
weekly_stats = df.groupby([df['Timestamp'].dt.to_period('W'), 'Hostname']).size().unstack()
monthly_stats = df.groupby([df['Timestamp'].dt.to_period('M'), 'Hostname']).size().unstack()

website_visits = df['Hostname'].value_counts()

# Create a pie chart with number of vists to different websites
plt.figure(figsize=(8, 8))
plt.pie(website_visits, labels=website_visits.index, autopct=lambda pct: f'{int(pct * sum(website_visits)/100)}\n{pct:.1f}%')
plt.title('Count and Percentage of Different Websites Visited')
plt.axis('equal') 
plt.show()

# To plot daily/weekly/monthly statistics of different websites visited
plt.figure(figsize=(20, 6))
for stats, period in zip([daily_stats, weekly_stats, monthly_stats], ['Daily', 'Weekly', 'Monthly']):
    stats.plot(kind='bar', ax=plt.gca())
    plt.title(f'Website Visits - {period}')
    plt.xlabel('Date' if period == 'Daily' else 'Week' if period == 'Weekly' else 'Month')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Number of Visits')
    plt.legend(title='Hostname')
    plt.show()