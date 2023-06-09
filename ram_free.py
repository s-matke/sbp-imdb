import pandas as pd
import psutil
import json
import time

DATA_DIR = "./data_small/"

name_basics_file       = "ImdbName.csv"
title_akas_file        = "ImdbTitleAkas.csv"
title_basics_file      = "ImdbTitleBasics.csv"
title_crew_file        = "ImdbTitleCrew.csv"
title_episode_file     = "ImdbTitleEpisode.csv"
title_principals_file  = "ImdbTitlePrincipals.csv"
title_ratings_file     = "ImdbTitleRatings.csv"

name_basics         = DATA_DIR + name_basics_file
title_akas          = DATA_DIR + title_akas_file
title_basics        = DATA_DIR + title_basics_file
title_crew          = DATA_DIR + title_crew_file
title_episode       = DATA_DIR + title_episode_file
title_principals    = DATA_DIR + title_principals_file
title_ratings       = DATA_DIR + title_ratings_file


# ---- LOAD TITLES ----
print("Loading titles...")
basics_df = pd.read_csv(title_basics, low_memory=False)

basics_df['genres'] = basics_df['genres'].str.split(",")
basics_df.set_index(basics_df['tconst'], inplace=True)
start = time.time()
recnik = basics_df.to_dict('index')

for key, value in recnik.items():
    if recnik[key]['titleType'] in ['tvSeries', 'tvMiniSeries']:
        recnik[key]['episodes'] = []

print("len of recnik:", len(recnik))
print("Time taken loading titles: ", time.time() - start)


# ---- LOAD RATING ----
print("\nLoading ratings...")
start = time.time()
ratings_df = pd.read_csv(title_ratings, low_memory=True)

for row in ratings_df.itertuples():
    if not recnik.get(row.tconst):
        continue
    recnik[row.tconst]['rating'] = {
        "avgRating": row.averageRating,
        "numVotes": row.numVotes
    }

print("Time taken loading ratings:", time.time() - start)
del ratings_df

# ---- LOAD EPISODES ----
print("\nLoading episodes...")
start = time.time()
episode_df = pd.read_csv(title_episode, low_memory=True)

for row in episode_df.itertuples():
    if not recnik.get(row.parentTconst):
        continue
    if not recnik.get(row.tconst):
        continue
    epizoda_info = recnik[row.tconst]
    epizoda_info['seasonNumber'] = row.seasonNumber
    epizoda_info['episodeNumber'] = row.episodeNumber
    recnik[row.parentTconst]['episodes'].append(epizoda_info)
    recnik.pop(row.tconst)

print("time taken loading episodes: ", time.time() - start)
del episode_df

# ---- LOAD HUMANS ----
print("\nLoading humans...")
start = time.time()
principals_df = pd.read_csv(title_principals, low_memory=True)

principals_df = principals_df[principals_df['tconst'].isin(basics_df['tconst'])]
del basics_df

name_df = pd.read_csv(name_basics, low_memory=True)
principals_df = principals_df[principals_df['nconst'].isin(name_df['nconst'])]

principals_df = principals_df.groupby(['tconst', 'nconst']).agg({'category': lambda x: ', '.join(set(x))}).reset_index()

principals_df['category'] = principals_df['category'].str.split(',')

joined_df = pd.merge(name_df, principals_df, on='nconst')
del name_df
del principals_df

joined_df.drop(['primaryProfession', 'knownForTitles'], axis=1, inplace=True)

cast = (
    joined_df.groupby('tconst')
    .apply(lambda x: x[['nconst', 'primaryName', 'birthYear', 'deathYear', 'category']].to_dict('records'))
    .reset_index()
    .set_index('tconst')
    .rename(columns={0: 'cast'})
    .to_dict('index')
)

for key, value in cast.items():
    if not recnik.get(key):
        continue
    recnik[key]['cast'] = value['cast']

print("Time taken loading humans: ", time.time() - start)
# print("Skipped: ", skipped)

print("free mem nakon dodavanja castova: ", psutil.virtual_memory().free/1000000000)


start = time.time()
json_output = json.dumps(recnik)

with open("test.json", "w") as outfile:
    outfile.write(json_output)
