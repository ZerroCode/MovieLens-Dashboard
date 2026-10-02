"""MovieLens: four views of movie genres, ratings, and release years."""

from pathlib import Path
from textwrap import wrap
import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


DATA_PATH = Path(__file__).resolve().parent / "data" / "movie_ratings.csv"
BLUE = "#4263EB"


@st.cache_data
def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    data = pd.read_csv(path, usecols=["movie_id", "title", "rating", "genres", "year"])
    data["rating"] = pd.to_numeric(data["rating"], errors="coerce")
    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    return data.dropna(subset=["movie_id", "rating"])


@st.cache_data
def summarize(data: pd.DataFrame):
    # Expand each rating into one row per distinct genre tag.
    tagged = data.assign(
        genre=data["genres"].fillna("unknown").map(
            lambda value: list(dict.fromkeys(
                tag.strip() for tag in value.split("|") if tag.strip()
            )) or ["unknown"]
        )
    ).explode("genre")
    genres = tagged.groupby("genre", as_index=False).agg(
        movie_count=("movie_id", "nunique"),
        mean_rating=("rating", "mean"),
        rating_count=("rating", "count"),
    )
    genres["percent"] = genres["movie_count"] / data["movie_id"].nunique() * 100
    yearly = data.dropna(subset=["year"]).groupby("year", as_index=False).agg(
        mean_rating=("rating", "mean"),
        rating_count=("rating", "count"),
        movie_count=("movie_id", "nunique"),
    )
    yearly["year"] = yearly["year"].astype(int)
    movies = data.groupby("movie_id", as_index=False).agg(
        title=("title", "first"),
        mean_rating=("rating", "mean"),
        rating_count=("rating", "count"),
    )
    return genres, yearly, movies


def eligible_movies(movies: pd.DataFrame, floor: int) -> pd.DataFrame:
    return movies.loc[movies["rating_count"] >= floor].sort_values(
        ["mean_rating", "rating_count", "movie_id"], ascending=[False, False, True]
    )


def bar_chart(frame, value, labels, text, axis_title, height=630, rating_scale=False,
              category_title="Genre"):
    figure = go.Figure(go.Bar(
        x=frame[value].tolist(), y=labels, orientation="h",
        marker_color=BLUE, text=text, textposition="auto",
        customdata=text, hovertemplate="%{y}<br>%{customdata}<extra></extra>",
    ))
    figure.update_layout(
        height=height, margin=dict(l=12, r=24, t=16, b=40),
        xaxis_title=axis_title, yaxis_title=category_title, showlegend=False,
        yaxis=dict(autorange="reversed", categoryorder="array", categoryarray=labels),
        xaxis=dict(range=[0, 5] if rating_scale else None, rangemode="tozero"),
    )
    return figure


def year_chart(yearly: pd.DataFrame, start: int, end: int):
    # Explicit missing values prevent the line from bridging absent years.
    selected = yearly.set_index("year").reindex(range(start, end + 1))
    figure = go.Figure(go.Scatter(
        x=selected.index.tolist(), y=selected["mean_rating"].tolist(),
        mode="lines+markers", connectgaps=False, line=dict(color=BLUE),
        customdata=selected[["rating_count", "movie_count"]].to_numpy(),
        hovertemplate=("Release year %{x}<br>Mean: %{y:.3f}/5"
                       "<br>%{customdata[0]:,.0f} ratings"
                       "<br>%{customdata[1]:,.0f} movies<extra></extra>"),
    ))
    figure.update_layout(
        height=420, margin=dict(l=12, r=24, t=16, b=40),
        xaxis_title="Movie release year", yaxis_title="Mean rating (1–5)",
        xaxis=dict(tickformat="d", range=[start - 0.5, end + 0.5]),
        yaxis=dict(range=[1, 5]),
    )
    return figure


def main():
    st.set_page_config(page_title="MovieLens Dashboard", page_icon="🎬", layout="wide")
    st.title("MovieLens Dashboard")
    try:
        data = load_data()
    except (OSError, ValueError) as error:
        st.error(f"Could not load the movie ratings data: {error}")
        st.stop()
    if data.empty:
        st.info("No valid movie ratings are available.")
        st.stop()
    genres, yearly, movies = summarize(data)
    st.caption(f"{len(data):,} ratings · {len(movies):,} rated movies · Ratings on a 1–5 scale")

    st.subheader("Chart 1 · Genre breakdown")
    counts = genres.sort_values(["movie_count", "genre"], ascending=[False, True])
    st.plotly_chart(bar_chart(
        counts, "movie_count", counts["genre"].tolist(),
        [f"{r.movie_count:,} movies ({r.percent:.1f}%)" for r in counts.itertuples()],
        "Distinct rated movies",
    ), width="stretch", key="genre_counts")

    st.subheader("Chart 2 · Genre satisfaction")
    satisfaction = genres.sort_values(["mean_rating", "genre"], ascending=[False, True])
    st.plotly_chart(bar_chart(
        satisfaction, "mean_rating", satisfaction["genre"].tolist(),
        [f"{r.mean_rating:.2f}/5 · {r.rating_count:,} ratings" for r in satisfaction.itertuples()],
        "Mean rating (out of 5)", rating_scale=True,
    ), width="stretch", key="genre_ratings")

    st.subheader("Chart 3 · Ratings by release year")
    if yearly.empty:
        st.info("No release years are available.")
    else:
        first, last = int(yearly["year"].min()), int(yearly["year"].max())
        if first < last:
            start, end = st.slider(
                "Chart 3 only · Release-year range", first, last, (first, last),
                step=1, key="release_year_range",
            )
        else:
            start = end = first
            st.caption(f"Only release year {first} is available.")
        if yearly["year"].between(start, end).any():
            st.plotly_chart(year_chart(yearly, start, end), width="stretch", key="year_ratings")
        else:
            st.info("No movies have release years in the selected range.")

    st.subheader("Chart 4 · Best movies, with a floor")
    floor = st.selectbox(
        "Chart 4 only · Minimum rating count", options=[50, 150], key="minimum_ratings",
    )
    eligible = eligible_movies(movies, floor)
    top = eligible.head(5)
    st.caption(f"{len(eligible):,} eligible movies · Showing {len(top)} · At least {floor} ratings each")
    if top.empty:
        st.info("No movies meet this minimum rating count.")
    else:
        labels = [
            f"{rank}. " + "<br>".join(html.escape(part) for part in wrap(str(title), 36))
            for rank, title in enumerate(top["title"], 1)
        ]
        st.plotly_chart(bar_chart(
            top, "mean_rating", labels,
            [f"{r.mean_rating:.3f}/5 · {r.rating_count:,} ratings" for r in top.itertuples()],
            "Mean rating (out of 5)", height=max(300, len(top) * 85), rating_scale=True,
            category_title="Movie",
        ), width="stretch", key="top_movies")
        st.dataframe(
            top[["title", "mean_rating", "rating_count"]].rename(columns={
                "title": "Movie", "mean_rating": "Mean rating", "rating_count": "Rating count",
            }),
            hide_index=True, width="stretch",
            column_config={"Mean rating": st.column_config.NumberColumn(format="%.4f")},
        )
    st.caption("Source: data/movie_ratings.csv")


if __name__ == "__main__":
    main()
