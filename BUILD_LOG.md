# Build Log

> Question 1 — Genre Breakdown: What's the distribution of genres among the movies that were rated? (Movies can have multiple genres; explain how you handle that before you count anything.)  

**Counting method:** Count each distinct `movie_id` once in every genre listed, splitting tags at `|`. A Comedy–Romance movie counts once in both genres, regardless of how many ratings it received. Each percentage uses all **1,682 rated movies** as its denominator, so percentages exceed 100% when added together.

From [movie_ratings.csv]:

| Genre | Movies | % of rated movies |
|---|---:|---:|
| Drama | 725 | 43.10% |
| Comedy | 505 | 30.02% |
| Action | 251 | 14.92% |
| Thriller | 251 | 14.92% |
| Romance | 247 | 14.68% |
| Adventure | 135 | 8.03% |
| Children | 122 | 7.25% |
| Crime | 109 | 6.48% |
| Sci-Fi | 101 | 6.00% |
| Horror | 92 | 5.47% |
| War | 71 | 4.22% |
| Mystery | 61 | 3.63% |
| Musical | 56 | 3.33% |
| Documentary | 50 | 2.97% |
| Animation | 42 | 2.50% |
| Western | 27 | 1.61% |
| Film-Noir | 24 | 1.43% |
| Fantasy | 22 | 1.31% |
| Unknown | 2 | 0.12% |

**Drama is the most common genre, followed by Comedy.** There are 849 movies with multiple genres, producing 2,893 total genre assignments. Unknown tags are retained explicitly.

>what chart type would best represent this question?

A **horizontal bar chart, sorted from most to least common**, best represents this distribution.

- **Y-axis:** Genre.
- **X-axis:** Number of distinct rated movies.
- **Bar labels:** Movie count and percentage of rated movies.
- **Footnote:** “Movies can belong to multiple genres and are counted once in each. Percentages may total more than 100%.”

Horizontal bars make the 19 genre labels easy to read and compare. Avoid a pie or donut chart because genres overlap rather than forming mutually exclusive parts of a whole.

>rememeber to represent each question with the best chart type moving forward.

I’ll pair each question with the chart type that best fits the data and comparison, and explain any counting assumptions before calculating.

>Question 2 — Genre Satisfaction: Which genres have the highest average rating? Which have the lowest?

**Method:** Each rating contributes to every genre tagged on its movie. A genre’s average is the sum of those ratings divided by their count, so more frequently rated movies carry more weight.

A **sorted horizontal bar chart** makes the genre ranking easy to compare. Calculated from [movie_ratings.csv]:

**Highest:** Film-Noir (3.92), War (3.82), and Drama (3.69). **Lowest known genres:** Fantasy (3.22), Horror (3.29), and Children (3.35). “Unknown” averages 3.20, but represents only 10 ratings across two movies.

>Question 3 — Ratings Over Time: How has the mean rating changed across movie release years?

**Method:** Group ratings by **movie release year**, then average all ratings within each year. More frequently rated movies carry more weight. Exclude 30 ratings across five movies with missing release years.

A **line chart** best shows the chronological trend; gaps indicate years with no movies in the data. Source: [movie_ratings.csv].

**Newer releases generally have lower mean ratings**, with fluctuations: 1980 averages **3.87**, 1990 **3.58**, and 1998 **3.30**. The peak is **1942 at 4.40**, based on only two movies; the minimum is **1926 at 3.00**, based on just two ratings.

This compares release-year groups, not how audience ratings changed over time. The older movies represented may be a selective set of enduring favorites, so the trend alone does not establish declining movie quality.

>Question 4 — Best Movies, With a Floor: What are the top 5 best-rated movies, once you only count movies with at least 50 ratings? What changes if you raise that floor to 150?

**Method:** Group by movie ID, calculate each movie’s mean and rating count, then keep movies meeting the inclusive threshold (≥50 or ≥150). Rank by unrounded mean.

**Two sorted horizontal bar charts with a shared scale** show both rankings clearly. Results come from [movie_ratings.csv].

Raising the floor reduces eligible movies from **603 to 203**. **A Close Shave, The Wrong Trousers, and Wallace & Gromit** drop out because they have fewer than 150 ratings. **The Shawshank Redemption, Rear Window, and The Usual Suspects** enter, making **Schindler’s List** the new leader. Individual movie averages remain unchanged; only eligibility changes.

>Build the four charts for Streamlit.   
>main file path: app.py     
>A straightforward layout is:   
>- Chart 1: Sorted horizontal bar chart of movie counts by genre.
>- Chart 2: Sorted horizontal bar chart of average ratings by genre.
>- Chart 3: Line chart of average rating by release year, ordered chronologically.
>- Chart 4: Horizontal bar chart of the top five eligible movies.
>For Chart 4, display rating counts alongside averages so the minimum-count rule is easy to verify. If fewer than five movies qualify, show the available movies.
>Add working interactive controls.
>Two useful controls are:
>- A minimum-rating-count selector with options 50 and 150, controlling Chart 4.
>- A release-year range slider, controlling Chart 3.    
>Label which chart each control affects. Switching between 50 and 150 must let you compare the two required top-five results.   
>Run and check the app      
>Anything used like Streamlit, pandas, and Plotly, list those packages in requirements.txt

Built all four charts in [app.py], with:

- Chart 3’s release-year slider.
- Chart 4’s 50/150 selector, averages, and rating counts.
- Handling for fewer than five eligible movies.

Dependencies are in [requirements.txt].

**Running:** [Open dashboard](http://127.0.0.1:8501)

All six automated tests passed. Browser visual inspection was unavailable; Streamlit widget tests and server health checks passed.

>Update my existing MovieLens Streamlit dashboard to meet these requirements. Use movie_ratings.csv and preserve any working features.     
>Include all four required charts:      
>1. Genre Breakdown: Show the distribution of genres among movies that were rated using a sorted bar chart. Count each unique movie once per genre, splitting pipe-separated genres. Explain this approach to me before implementing it.    
>2. Genre Satisfaction: Show the average rating for each genre using a sorted bar chart. Use individual ratings, with each rating contributing to every genre associated with its movie.   
>3. Ratings Over Time: Show mean rating by movie release year using a line chart. Use the year column, not the rating timestamp.   
>4. Best Movies, With a Floor: Show the five highest-rated movies after filtering to movies with at least 50 ratings. Allow switching to at least 150 ratings so I can compare the results. Display each movie’s average rating and rating count.  
>Add two working interactive controls:  
>- A release-year range slider that updates Chart 3.  
>- A minimum-rating-count selector with options of 50 and 150 that updates Chart 4. Apply this threshold before selecting the top five movies.    
>Label the controls clearly so users know which chart they affect. Give every chart a clear title and labeled axes. Handle empty results gracefully.    
>Do not include an embedded write-up or audit section. That belongs in next week’s notebook, not this dashboard.    
>Provide the updated app.py, any necessary changes to requirements.txt, and brief instructions for running the app and checking that both controls work.    

Updated [app.py] to preserve all four charts and both controls, add explicit bar-chart axis labels, and remove the embedded write-up. Empty-result handling and rating counts remain intact.

[requirements.txt] already includes Streamlit, pandas, and Plotly; no changes were needed. All six automated tests passed.

Run from the project folder:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m streamlit run app.py
```

Check the controls:

- **Chart 3:** Select **1990–1998**; only its line chart should change.
- **Chart 4:** Switch **50 → 150**; the leader changes from **A Close Shave** to **Schindler’s List**. Switch back to restore the original ranking.
- Select **1923–1925** to verify Chart 3’s empty-result message.