"""Run with: python -m unittest discover -s tests -v."""

import json
from pathlib import Path
import unittest
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest

import app


def render_app():
    import app
    app.main()


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = app.load_data()
        cls.genres, cls.years, cls.movies = app.summarize(cls.data)

    def test_data_and_aggregations(self):
        self.assertEqual(len(self.data), 100000)
        self.assertEqual(len(self.movies), 1682)
        genres = self.genres.set_index("genre")
        self.assertEqual(genres.loc["Drama", "movie_count"], 725)
        self.assertEqual(genres["movie_count"].sum(), 2893)
        self.assertAlmostEqual(genres.loc["Film-Noir", "mean_rating"], 3.9215233699)
        self.assertEqual(self.years["rating_count"].sum(), 99970)
        self.assertAlmostEqual(self.years.set_index("year").loc[1942, "mean_rating"], 4.39846743295)

    def test_threshold_rankings(self):
        for floor, count, ids in [
            (50, 603, [408, 318, 169, 483, 114]),
            (150, 203, [318, 483, 64, 603, 12]),
        ]:
            result = app.eligible_movies(self.movies, floor)
            self.assertEqual(len(result), count)
            self.assertEqual(result.head(5)["movie_id"].tolist(), ids)
            self.assertTrue((result["rating_count"] >= floor).all())

    def test_inclusive_floor_and_short_results(self):
        sample = pd.DataFrame({
            "movie_id": [1, 2, 3], "title": ["One", "Two", "Three"],
            "mean_rating": [5, 4, 3], "rating_count": [49, 50, 150],
        })
        self.assertEqual(app.eligible_movies(sample, 50)["movie_id"].tolist(), [2, 3])
        self.assertEqual(app.eligible_movies(sample, 150)["movie_id"].tolist(), [3])
        self.assertTrue(app.eligible_movies(sample, 151).empty)

    def test_year_gaps_and_single_year(self):
        figure = app.year_chart(self.years, 1922, 1926)
        self.assertEqual(list(figure.data[0].x), [1922, 1923, 1924, 1925, 1926])
        self.assertTrue(pd.isna(figure.data[0].y[1]))
        self.assertFalse(figure.data[0].connectgaps)
        self.assertEqual(list(app.year_chart(self.years, 1998, 1998).data[0].x), [1998])

    def test_interactive_controls(self):
        at = AppTest.from_file(str(Path(app.__file__)), default_timeout=30).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.get("plotly_chart")), 4)
        self.assertEqual(at.dataframe[0].value["Rating count"].tolist(), [112, 298, 118, 243, 67])
        original_charts = [chart.proto.spec for chart in at.get("plotly_chart")]
        at.selectbox(key="minimum_ratings").select(150).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.dataframe[0].value["Rating count"].tolist(), [298, 243, 283, 209, 267])
        self.assertEqual([chart.proto.spec for chart in at.get("plotly_chart")][:3], original_charts[:3])
        top_chart = at.get("plotly_chart")[3].proto.spec
        at.slider(key="release_year_range").set_range(1990, 1998).run()
        self.assertEqual(len(at.exception), 0)
        charts = at.get("plotly_chart")
        self.assertEqual(json.loads(charts[2].proto.spec)["data"][0]["x"], list(range(1990, 1999)))
        self.assertEqual(charts[3].proto.spec, top_chart)
        self.assertEqual([chart.proto.spec for chart in charts][:2], original_charts[:2])
        at.selectbox(key="minimum_ratings").select(50).run()
        self.assertEqual(at.dataframe[0].value["Rating count"].tolist(), [112, 298, 118, 243, 67])
        at.slider(key="release_year_range").set_range(1923, 1925).run()
        self.assertEqual(len(at.exception), 0)
        self.assertTrue(any("No movies have release years" in message.value for message in at.info))

    def test_short_and_empty_top_five_ui(self):
        sample = self.data.loc[self.data["movie_id"].isin([408, 318])]
        with patch.object(app, "load_data", return_value=sample):
            at = AppTest.from_function(render_app, default_timeout=30).run()
            self.assertEqual(len(at.exception), 0)
            self.assertEqual(len(at.dataframe[0].value), 2)
            at.selectbox(key="minimum_ratings").select(150).run()
            self.assertEqual(len(at.dataframe[0].value), 1)
        with patch.object(app, "load_data", return_value=self.data.head(10)):
            at = AppTest.from_function(render_app, default_timeout=30).run()
            self.assertEqual(len(at.exception), 0)
            self.assertTrue(any("No movies meet" in message.value for message in at.info))


if __name__ == "__main__":
    unittest.main()
