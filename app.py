import streamlit as st
import os
import pandas as pd
from glob import glob
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title='Spotify Data Exploration', layout='wide')

st.title('Spotify Data Exploration')
st.success("Get a deeper dive into your Spotify listening habits with our data exploration app! Simply request and upload your Extended streaming history JSON files from Spotify's privacy page and see your music consumption like never before. Enhance your Spotify experience and learn more about your personal music preferences.  \n Try it out now! https://www.spotify.com/us/account/privacy/")

st.sidebar.header('Upload JSON Data')
uploaded_files = st.sidebar.file_uploader("", accept_multiple_files=True)
number_of_bands = st.sidebar.slider('Number of TOP bands to analyze', min_value=1, max_value=50, value=5)

if st.sidebar.button('Analyze Data!'):
    ind_df = (pd.read_json(f) for f in uploaded_files)
    df_raw = pd.concat(ind_df, ignore_index=True)

    df = df_raw[['ts', 'ms_played', 'master_metadata_track_name', 'master_metadata_album_album_name', 'master_metadata_album_artist_name']]
    df.columns = ['ts', 'ms_played', 'track_name', 'album_name', 'artist_name']

    bands_num_songs = df[['artist_name']].value_counts(['artist_name']).to_frame()
    bands_time = df[['artist_name', 'ms_played']].groupby('artist_name').sum().sort_values('ms_played', ascending=False)
    bands_time['ms_played'] = bands_time['ms_played']/(60*60*1000)
    bands_time['ms_played'] = bands_time['ms_played'].round(2)
    bands_time = bands_time.rename(columns = {'ms_played':'hrs_played'})
    stats = bands_time.join(bands_num_songs, on='artist_name', how='inner').reset_index()
    stats.columns = ['artist_name', 'hrs_played', 'tracks']

    fig = px.scatter(stats.head(10), x='tracks', y='hrs_played', text='artist_name')
    fig.update_traces(textposition='middle center', mode='text', textfont_size=15, textfont_color='rgb(0, 150, 255)')
    fig.update_layout(xaxis=dict(range=[680, 3600]), height=600, title_x=0.5, title_text='Top 10 Artists - Based on number of tracks and total hours played', xaxis_title='Number of tracks', yaxis_title='Total hours played')
    st.plotly_chart(fig)

    df2020 = df[(df['ts'] > '2020-01-01T00:00:00Z') & (df['ts'] < '2021-01-01T00:00:00Z')].sort_values('ts', ascending=True)
    df2021 = df[(df['ts'] > '2021-01-01T00:00:00Z') & (df['ts'] < '2022-01-01T00:00:00Z')].sort_values('ts', ascending=True)
    df2022 = df[(df['ts'] > '2022-01-01T00:00:00Z') & (df['ts'] < '2023-01-01T00:00:00Z')].sort_values('ts', ascending=True)

    hours2022 = df2022.groupby('artist_name').sum().sort_values('ms_played', ascending=False)/(60*60*1000)
    hours2022 = hours2022.round(2)
    tracks2022 = df2022.value_counts(['artist_name']).to_frame()
    stats2022 = hours2022.join(tracks2022, on='artist_name', how='inner').reset_index()
    stats2022.columns = ['artist_name', 'hrs_played_2022', 'tracks_2022']

    hours2021 = df2021.groupby('artist_name').sum().sort_values('ms_played', ascending=False)/(60*60*1000)
    hours2021 = hours2021.round(2)
    tracks2021 = df2021.value_counts(['artist_name']).to_frame()
    stats_3years = stats2022.join(hours2021, on='artist_name', how='outer')
    stats_3years = stats_3years.join(tracks2021, on='artist_name', how='outer')
    stats_3years = stats_3years.sort_values('hrs_played_2022', ascending=False)
    stats_3years.columns = ['artist_name', 'hrs_played_2022', 'tracks_2022', 'hrs_played_2021', 'tracks_2021']

    hours2020 = df2020.groupby('artist_name').sum().sort_values('ms_played', ascending=False)/(60*60*1000)
    hours2020 = hours2020.round(2)
    tracks2020 = df2020.value_counts(['artist_name']).to_frame()
    stats_3years = stats_3years.join(hours2020, on='artist_name', how='outer')
    stats_3years = stats_3years.join(tracks2020, on='artist_name', how='outer')
    stats_3years = stats_3years.sort_values('hrs_played_2022', ascending=False)
    stats_3years.columns = ['artist_name', 'hrs_played_2022', 'tracks_2022', 'hrs_played_2021', 'tracks_2021', 'hrs_played_2020', 'tracks_2020']

    fig = go.Figure()
    bands = stats_3years['artist_name'].head(20).values.tolist()
    hours2020 = stats_3years['hrs_played_2020'].head(20).values.tolist()
    hours2021 = stats_3years['hrs_played_2021'].head(20).values.tolist()
    hours2022 = stats_3years['hrs_played_2022'].head(20).values.tolist()
    fig.add_trace(go.Bar(x=bands, y=hours2022, name='2022', marker_color='rgb(17, 103, 177)'))
    fig.add_trace(go.Bar(x=bands, y=hours2021, name='2021', marker_color='rgb(42, 157, 244)'))
    fig.add_trace(go.Bar(x=bands, y=hours2020, name='2020', marker_color='rgb(160, 200, 255)'))
    fig.update_layout(
        height=600,
        title_x=0.5,
        title_text='Top 20 Artists - Total hours played each year',
        yaxis_title='Total hours played',
        legend=dict(x=0,y=1.0, bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'),
        barmode='group',
        bargap=0.2,
        bargroupgap=0.05)
    st.plotly_chart(fig)

    fig = px.histogram(x=df['ts'], nbins=38)
    fig.update_traces(marker_color='rgb(17, 103, 177)')
    fig.update_xaxes(title=False)
    fig.update_layout(
        title_x=0.5,
        title_text='All Time - Number of tracks monthly',
        xaxis_title=None,
        yaxis_title='Number of Tracks',
        bargap=0.5,)
    st.plotly_chart(fig)

    def band(number_of_bands):
        for i in range(number_of_bands):
            Band = df[df['artist_name'] == stats_3years.loc[list(stats_3years.index)[i],'artist_name']]
            fig = px.histogram(x=Band['ts'], nbins=38)
            fig.update_traces(marker_color='rgb(42, 157, 244)')
            fig.update_xaxes(title=False)
            fig.update_layout(
                title_x=0.5,
                title_text= 'TOP '
                + str(i+1)
                + ' Artist - '
                + stats_3years.loc[list(stats_3years.index)[i],'artist_name']
                + ' (first listened on '
                + str(pd.to_datetime(Band['ts'].min()).date())
                + ')',
                xaxis_title=None,
                yaxis_title='Tracks',
                bargap=0.3,)
            st.plotly_chart(fig)

    band(number_of_bands)

if st.sidebar.button('Load example data'):
    df_raw = pd.read_json('data.json')

    df = df_raw[['ts', 'ms_played', 'master_metadata_track_name', 'master_metadata_album_album_name', 'master_metadata_album_artist_name']]
    df.columns = ['ts', 'ms_played', 'track_name', 'album_name', 'artist_name']

    bands_num_songs = df[['artist_name']].value_counts(['artist_name']).to_frame()
    bands_time = df[['artist_name', 'ms_played']].groupby('artist_name').sum().sort_values('ms_played', ascending=False)
    bands_time['ms_played'] = bands_time['ms_played']/(60*60*1000)
    bands_time['ms_played'] = bands_time['ms_played'].round(2)
    bands_time = bands_time.rename(columns = {'ms_played':'hrs_played'})
    stats = bands_time.join(bands_num_songs, on='artist_name', how='inner').reset_index()
    stats.columns = ['artist_name', 'hrs_played', 'tracks']

    fig = px.scatter(stats.head(10), x='tracks', y='hrs_played', text='artist_name')
    fig.update_traces(textposition='middle center', mode='text', textfont_size=15, textfont_color='rgb(0, 150, 255)')
    fig.update_layout(xaxis=dict(range=[680, 3600]), height=600, title_x=0.5, title_text='Top 10 Artists - Based on number of tracks and total hours played', xaxis_title='Number of tracks', yaxis_title='Total hours played')
    st.plotly_chart(fig)

    df2020 = df[(df['ts'] > '2020-01-01T00:00:00Z') & (df['ts'] < '2021-01-01T00:00:00Z')].sort_values('ts', ascending=True)
    df2021 = df[(df['ts'] > '2021-01-01T00:00:00Z') & (df['ts'] < '2022-01-01T00:00:00Z')].sort_values('ts', ascending=True)
    df2022 = df[(df['ts'] > '2022-01-01T00:00:00Z') & (df['ts'] < '2023-01-01T00:00:00Z')].sort_values('ts', ascending=True)

    hours2022 = df2022.groupby('artist_name').sum().sort_values('ms_played', ascending=False)/(60*60*1000)
    hours2022 = hours2022.round(2)
    tracks2022 = df2022.value_counts(['artist_name']).to_frame()
    stats2022 = hours2022.join(tracks2022, on='artist_name', how='inner').reset_index()
    stats2022.columns = ['artist_name', 'hrs_played_2022', 'tracks_2022']

    hours2021 = df2021.groupby('artist_name').sum().sort_values('ms_played', ascending=False)/(60*60*1000)
    hours2021 = hours2021.round(2)
    tracks2021 = df2021.value_counts(['artist_name']).to_frame()
    stats_3years = stats2022.join(hours2021, on='artist_name', how='outer')
    stats_3years = stats_3years.join(tracks2021, on='artist_name', how='outer')
    stats_3years = stats_3years.sort_values('hrs_played_2022', ascending=False)
    stats_3years.columns = ['artist_name', 'hrs_played_2022', 'tracks_2022', 'hrs_played_2021', 'tracks_2021']

    hours2020 = df2020.groupby('artist_name').sum().sort_values('ms_played', ascending=False)/(60*60*1000)
    hours2020 = hours2020.round(2)
    tracks2020 = df2020.value_counts(['artist_name']).to_frame()
    stats_3years = stats_3years.join(hours2020, on='artist_name', how='outer')
    stats_3years = stats_3years.join(tracks2020, on='artist_name', how='outer')
    stats_3years = stats_3years.sort_values('hrs_played_2022', ascending=False)
    stats_3years.columns = ['artist_name', 'hrs_played_2022', 'tracks_2022', 'hrs_played_2021', 'tracks_2021', 'hrs_played_2020', 'tracks_2020']

    fig = go.Figure()
    bands = stats_3years['artist_name'].head(20).values.tolist()
    hours2020 = stats_3years['hrs_played_2020'].head(20).values.tolist()
    hours2021 = stats_3years['hrs_played_2021'].head(20).values.tolist()
    hours2022 = stats_3years['hrs_played_2022'].head(20).values.tolist()
    fig.add_trace(go.Bar(x=bands, y=hours2022, name='2022', marker_color='rgb(17, 103, 177)'))
    fig.add_trace(go.Bar(x=bands, y=hours2021, name='2021', marker_color='rgb(42, 157, 244)'))
    fig.add_trace(go.Bar(x=bands, y=hours2020, name='2020', marker_color='rgb(160, 200, 255)'))
    fig.update_layout(
        height=600,
        title_x=0.5,
        title_text='Top 20 Artists - Total hours played each year',
        yaxis_title='Total hours played',
        legend=dict(x=0,y=1.0, bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'),
        barmode='group',
        bargap=0.2,
        bargroupgap=0.05)
    st.plotly_chart(fig)

    fig = px.histogram(x=df['ts'], nbins=38)
    fig.update_traces(marker_color='rgb(17, 103, 177)')
    fig.update_xaxes(title=False)
    fig.update_layout(
        title_x=0.5,
        title_text='All Time - Number of tracks monthly',
        xaxis_title=None,
        yaxis_title='Number of Tracks',
        bargap=0.5,)
    st.plotly_chart(fig)

    def band(number_of_bands):
        for i in range(number_of_bands):
            Band = df[df['artist_name'] == stats_3years.loc[list(stats_3years.index)[i],'artist_name']]
            fig = px.histogram(x=Band['ts'], nbins=38)
            fig.update_traces(marker_color='rgb(42, 157, 244)')
            fig.update_xaxes(title=False)
            fig.update_layout(
                title_x=0.5,
                title_text= 'TOP '
                + str(i+1)
                + ' Artist - '
                + stats_3years.loc[list(stats_3years.index)[i],'artist_name']
                + ' (first listened on '
                + str(pd.to_datetime(Band['ts'].min()).date())
                + ')',
                xaxis_title=None,
                yaxis_title='Tracks',
                bargap=0.3,)
            st.plotly_chart(fig)

    band(number_of_bands)