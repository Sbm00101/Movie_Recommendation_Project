import streamlit as st
import pickle
import requests
from requests.exceptions import RequestException
import time

# Load data
new_df = pickle.load(open('movies.pkl', 'rb'))
movies_list = new_df['title'].values.tolist()
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movies Recommendation - SBM')

Selected_movie = st.selectbox(
    "Choose your Movie",
    movies_list)

st.write("Your Movie:", Selected_movie)

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    attempts = 3
    while attempts > 0:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path', '')
            if poster_path:
                full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
                return full_path
            else:
                return None
        except RequestException as e:
            attempts -= 1
            time.sleep(1)  # Wait for 1 second before retrying
            if attempts == 0:
                st.error(f"Failed to fetch poster for movie ID {movie_id}. Error: {e}")
                return None

def reccomend(Selected_movie):
    recommended_movies = []
    recommended_movies_posters = []
    movie_index = new_df[new_df['title'] == Selected_movie].index[0]
    distances = similarity[movie_index]
    output = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]
    for i in output:
        movie_title = new_df.iloc[i[0]].title
        poster_url = fetch_poster(new_df.iloc[i[0]].movie_id)
        recommended_movies.append(movie_title)
        recommended_movies_posters.append(poster_url)
    return recommended_movies, recommended_movies_posters

if st.button("Recommend Movies"):
    recommendations, posters = reccomend(Selected_movie)
    cols = st.columns(5)
    for col, movie, poster in zip(cols, recommendations, posters):
        with col:
            st.text(movie)
            if poster:
                st.image(poster)
            else:
                st.write("No poster available")
