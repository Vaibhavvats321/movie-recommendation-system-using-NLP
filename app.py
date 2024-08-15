import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch movie data from TMDB
def fetch_movie_data(movie_id):
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=2edb1b578d2a521cd31bcf366dacde00&language=en-US')
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching movie data: {e}")
        return None

# Function to fetch movie poster from TMDB
def fetch_poster(poster_path):
    return f"https://image.tmdb.org/t/p/w500{poster_path}"

# Function to recommend movies based on similarity
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:16]
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_data = fetch_movie_data(movie_id)
        recommended_movie_names.append(movie_data['title'])
        recommended_movie_posters.append(fetch_poster(movie_data['poster_path']))
        recommended_movie_ids.append(movie_id)
    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids

# Load movie data
movies_list = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_list)

# Load similarity matrix
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit app interface

st.title('Movie Recommender Using NLP')

selected_movie = st.selectbox("Select Movie From The List", movies['title'].values)

if st.button("Recommend"):
    names, posters, movie_ids = recommend(selected_movie)
    
    # Display selected movie in a large frame
    st.header("Selected Movie")
    selected_movie_id = movies[movies['title'] == selected_movie].iloc[0].movie_id
    selected_movie_data = fetch_movie_data(selected_movie_id)
    if selected_movie_data:
        st.subheader(selected_movie_data['title'])
        st.image(fetch_poster(selected_movie_data['poster_path']), use_column_width=True)
        st.write(f"**Overview**: {selected_movie_data['overview']}")
        st.write(f"**Genres**: {', '.join([genre['name'] for genre in selected_movie_data['genres']])}")
        st.write(f"**Release Date**: {selected_movie_data['release_date']}")
        st.write(f"**Runtime**: {selected_movie_data['runtime']} minutes")
        st.write(f"**IMDb Rating**: {selected_movie_data['vote_average']}")
        st.write(f"**Vote Count**: {selected_movie_data['vote_count']}")

    st.header("Recommended Movies")
    for i in range(0, len(names), 5):
        cols = st.columns(5)
        for j, col in enumerate(cols):
            if i + j < len(names):
                with col:
                    st.image(posters[i + j])
                    st.text(names[i + j])

st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .movie-poster {
        border-radius: 15px;
    }
    .movie-title {
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
