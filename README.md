# MovieLens Dashboard

Four interactive Streamlit charts built from `data/movie_ratings.csv`.

[Open the live Streamlit dashboard](https://zerrokid.streamlit.app/)

## Run

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m streamlit run app.py
```

Chart 3's release-year slider filters only the yearly mean rating chart.
Chart 4's minimum-count selector switches between 50 and 150 ratings.
Genre counts use distinct movies; genre and release-year means use individual
ratings. Movies with multiple genres contribute to each of their genres.

## Check

1. Set **Chart 3 only · Release-year range** to **1990–1998**. Only Chart 3
   should change, and its release years should stay within that range.
2. Switch **Chart 4 only · Minimum rating count** from **50** to **150**.
   The leader should change from **A Close Shave** (112 ratings) to
   **Schindler's List** (298 ratings). Every displayed count must meet the
   selected threshold. Switch back to 50 to restore the original ranking.
3. Select **1923–1925** in Chart 3 to check the empty-result message.

Run the automated aggregation and interaction checks:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
```
