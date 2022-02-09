import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid")

# Initialize the matplotlib figure
f, ax = plt.subplots(figsize=(6, 15))

# Load the example car crash dataset
df_gt = pd.read_csv("../../outputs/google_trends/results.csv")
df_gt = df_gt[df_gt['Time period'] == "12 months"]
df_gs = pd.read_csv("../../outputs/google/front_page_analysis.csv")
df_gs = pd.merge(df_gs, df_gt, left_on='term', right_on='Search term')


def viable_plot(df):
    df_counts = df.copy()
    df_counts['viable_count'] = [1 if x == 'Yes' else 0 for x in df['Viable']]
    df_counts = df_counts.groupby(['Domain', 'Level', 'Viable']).agg({'viable_count': ['sum']}).reset_index()
    df_counts.columns = ['domain', 'level', 'viable', 'count']

    df_counts_viable = df_counts[df_counts['viable'] == 'Yes']

    df_counts_viable = pd.pivot_table(data=df_counts_viable, index=['domain'], columns=['level'],
                                      values='count').fillna(0)
    column_order = ['Low level', 'Medium level', 'High level']
    df_counts_viable = df_counts_viable[column_order]
    df2 = pd.DataFrame([[0, 0, 0], [0, 0, 0]], columns=column_order,
                       index=['Housing, Planning and Local Services', 'Travel, Transport and Tourism'])
    df_counts_viable = df_counts_viable.append(df2)

    df_counts_viable.sort_index(inplace=True)
    df_counts_viable.index = ['AEE', 'BTID', 'CES', 'CS', 'E', 'HSC', 'HPLS', 'LMW', 'PS', 'TTT']

    level_colours = ['#AAC9DD', '#78AED3', '#4F77AA']

    ax_ = df_counts_viable.plot(kind='bar', stacked=True, color=level_colours, grid=False,
                                title="Number of Viable search terms")
    ax_.set_xlabel("Domain")
    ax_.set_ylabel("Count")
    plt.tight_layout()
    plt.show()


def data_or_statistics_plot(df):
    df_counts = df.copy()
    df_counts[['pre', 'suff']] = df['Search term'].str.rsplit(' ', 1, expand=True)
    df_counts = df_counts.loc[(df_counts['suff'].isin(['statistics', 'data']))]
    df_counts_mask = df_counts.pre.duplicated(keep=False)
    df_counts = df_counts[df_counts_mask]
    df_counts['viable_count'] = [1 if x == 'Yes' else 0 for x in df_counts['Viable']]
    df_counts['data_count'] = [1 if x is True else 0 for x in df_counts['data']]
    df_counts['statistics_count'] = [1 if x is False else 0 for x in df_counts['data']]
    df_counts_nv = df_counts.copy()
    df_counts_nv = df_counts_nv[df_counts_nv['Domain'] != 'Cross-cutting']

    df_counts = df_counts[df_counts['viable_count'] == 1]

    df_counts = df_counts.groupby(['Domain']).agg({'data_count': ['sum'], 'statistics_count': ['sum']}).reset_index()
    df_counts_nv = df_counts_nv.groupby(['Domain']).agg(
        {'data_count': ['sum'], 'statistics_count': ['sum']}).reset_index()

    df_counts = df_counts.set_index('Domain')
    df_counts.columns = ['Data', 'Statistics']

    df_counts_nv = df_counts_nv.set_index('Domain')
    df_counts_nv.columns = ['Data', 'Statistics']

    column_order = ['Data', 'Statistics']
    df_counts = df_counts[column_order]
    df2 = pd.DataFrame([[0, 0], [0, 0], [0, 0], [0, 0]], columns=column_order,
                       index=['Economy', 'Housing, Planning and Local Services', 'Health and Social Care',
                              'Travel, Transport and Tourism'])
    df_counts = df_counts.append(df2)

    df2 = pd.DataFrame([[0, 0]], columns=column_order, index=['Housing, Planning and Local Services'])
    df_counts_nv = df_counts_nv.append(df2)

    df_counts.sort_index(inplace=True)
    df_counts.index = ['AEE', 'BTID', 'CES', 'CS', 'E', 'HSC', 'HPLS', 'LMW', 'PS', 'TTT']

    df_counts_nv.sort_index(inplace=True)
    df_counts_nv.index = ['AEE', 'BTID', 'CES', 'CS', 'E', 'HSC', 'HPLS', 'LMW', 'PS', 'TTT']

    df_counts = (df_counts / df_counts_nv) * 100

    level_colours = ['#AAC9DD', '#4F77AA']

    ax_ = df_counts.plot(kind='bar', color=level_colours, grid=False,
                         title="Number of Viable search terms")
    ax_.set_xlabel("Domain")
    ax_.set_ylabel("Percentage")
    plt.show()


def trusted_webpages_plot(df):
    df_counts = df.copy()

    df_counts['trusted_count'] = [1 if x is True else 0 for x in df['trusted_url']]

    df_counts = df_counts.groupby(['Domain', 'term', 'Level'])['trusted_count'].sum().reset_index()
    df_counts = df_counts.set_index(['Domain', 'term'])
    df_counts = df_counts.loc[~(df_counts == 0).all(axis=1)]

    df_counts = df_counts.sort_values('trusted_count')

    level_colours = ['#AAC9DD', '#78AED3', '#4F77AA']

    df_counts = pd.pivot_table(data=df_counts, index=df_counts.index, columns=['Level'], values='trusted_count').fillna(
        0)

    column_order = ['Low level', 'Medium level', 'High level']

    df_counts['total'] = df_counts['High level'] + df_counts['Low level'] + df_counts['Medium level']
    df_counts = df_counts.sort_values(by=['total'])
    df_counts = df_counts.drop(['total'], axis=1)
    df_counts = df_counts[column_order]

    df_counts.index = ['Open university statistics (CES)',
                       'Jobs statistics (LMW)',
                       'Religion statistics (PS)',
                       'Literacy rate (CES)',
                       'Parks statistics (HPLS)',
                       'Manufacturing statistics (BTID)',
                       'Inflation statistics (E)',
                       'Allowance statistics (LMW)',
                       'Mortgage statistics (HPLS)',
                       'EU trade statistics (BTID)',
                       'Health statistics (HSC)',
                       'Obesity statistics (HSC)',
                       'Pensions statistics (E)',
                       'Benefit statistics (LMW)',
                       'Police statistics (CS)',
                       'Social care statistics (HSC)',
                       'Transport statistics (TTT)',
                       'Adult health statistics (HSC)']

    ax_ = df_counts.plot(kind='bar', color=level_colours, stacked=True, grid=False,
                         title='Number of trusted websites from Google for each search term')
    ax_.set_ylabel("Count")
    plt.tight_layout()

    plt.show()


viable_plot(df_gt)
data_or_statistics_plot(df_gt)
trusted_webpages_plot(df_gs)
