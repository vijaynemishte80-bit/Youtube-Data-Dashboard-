import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import plotly.express as px

# YouTube API setup
API_KEY = "AIzaSyAmbR-mZiykk6jsVkzDG81kNlTjKpzJ56A"
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Streamlit UI
st.set_page_config(page_title="YouTube Data Dashboard", layout="wide")
st.title("📊 YouTube Data Dashboard")

channel_id = st.text_input("🔹 Enter YouTube Channel ID:", "")

if channel_id:
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()

    if not response['items']:
        st.warning("⚠️ Invalid Channel ID. Please check again.")
    else:
        channel_data = response['items'][0]
        channel_name = channel_data['snippet']['title']
        subs = int(channel_data['statistics']['subscriberCount'])
        views = int(channel_data['statistics']['viewCount'])
        videos = int(channel_data['statistics']['videoCount'])

        st.subheader(f"🎬 Channel: {channel_name}")
        st.write(f"👥 Subscribers: *{subs:,}*")
        st.write(f"📺 Videos: *{videos}*")
        st.write(f"👀 Views: *{views:,}*")

        uploads_playlist_id = channel_data['contentDetails']['relatedPlaylists']['uploads']
        video_request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=30
        )
        video_response = video_request.execute()

        video_ids = [v['contentDetails']['videoId'] for v in video_response['items']]
        stats_request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        stats_response = stats_request.execute()

        videos_data = []
        for v in stats_response['items']:
            videos_data.append({
                'Title': v['snippet']['title'],
                'Views': int(v['statistics'].get('viewCount', 0)),
                'Likes': int(v['statistics'].get('likeCount', 0)),
                'Comments': int(v['statistics'].get('commentCount', 0))
            })

        df = pd.DataFrame(videos_data)

        st.subheader("📈 Top 10 Videos by Views")
        st.dataframe(df.sort_values('Views', ascending=False).head(10))

        # Charts
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(df.sort_values('Views', ascending=False).head(10),
                          x='Title', y='Views', title='Top 10 Videos by Views')
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.scatter(df, x='Views', y='Likes', size='Comments',
                              title='Likes vs Views (Bubble = Comments)',
                              hover_name='Title')
            st.plotly_chart(fig2, use_container_width=True)

        # Additional charts
        st.subheader("📊 Comments & Correlation Insights")
        fig3 = px.bar(df.sort_values('Comments', ascending=False).head(10),
                      x='Title', y='Comments', title='Top 10 Videos by Comments')
        st.plotly_chart(fig3, use_container_width=True)

        corr = df[['Views', 'Likes', 'Comments']].corr()
        fig4 = px.imshow(corr, text_auto=True, color_continuous_scale='Blues',
                         title='Correlation between Views, Likes & Comments')
        st.plotly_chart(fig4, use_container_width=True)

        st.success("✅ Dashboard Loaded Successfully!")