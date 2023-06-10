import pandas as pd
import time
import json
import inspect
import warnings
import numpy as np

warnings.filterwarnings("ignore")


# RAM_CHECKUP = 0

# if RAM_CHECKUP:
#     import psutil

# ---------------------------------------------------
DATA_DIR = "../data/"

name_basics_file       = "ImdbName.csv"
title_akas_file        = "ImdbTitleAkas.csv"
title_basics_file      = "ImdbTitleBasics.csv"
title_crew_file        = "ImdbTitleCrew.csv"
title_episode_file     = "ImdbTitleEpisode.csv"
title_principals_file  = "ImdbTitlePrincipals.csv"
title_ratings_file     = "ImdbTitleRatings.csv"

name_basics_path         = DATA_DIR + name_basics_file
title_akas_path          = DATA_DIR + title_akas_file
title_basics_path        = DATA_DIR + title_basics_file
title_crew_path          = DATA_DIR + title_crew_file
title_episode_path       = DATA_DIR + title_episode_file
title_principals_path    = DATA_DIR + title_principals_file
title_ratings_path       = DATA_DIR + title_ratings_file

output_path = DATA_DIR + 'output.json'
# ---------------------------------------------------

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        print(f"[{func.__name__}] took {execution_time} seconds to execute.")

        # signature = inspect.signature(func)
        # bound_args = signature.bind(*args, **kwargs)
        # bound_args.apply_defaults()
        # params = bound_args.arguments
        
        # param_info = ", ".join(f"{name}={value}" for name, value in params.items() if name != "recnik")

        # print(f"Parameters: {param_info}")
        return result
    return wrapper

def filter_dataframe(df_a, column_name, df_b) -> pd.DataFrame:
    return df_a[df_a[column_name].isin(df_b[column_name])]

def convert_to_numeric(column_names, df):
    if isinstance(column_names, list):
        for column_name in column_names:
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
            df[column_name].replace(np.nan, None, inplace=True)
    else:
        df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
        df[column_name].replace(np.nan, None, inplace=True)

def load_data_into_dataframe(file_path) -> pd.DataFrame:
    return pd.read_csv(file_path, low_memory=True)

@measure_time
def initial_dictionary(file_path=None) -> dict:
    if not file_path:
        raise("Require file_path, got 'None'")
    
    df = load_data_into_dataframe(file_path=file_path)

    convert_to_numeric(['isAdult', 'startYear', 'endYear', 'runtimeMinutes'], df)
    df['isAdult'] = df['isAdult'].astype(bool)

    df['genres'] = df['genres'].str.split(",")
    df.set_index(df['tconst'], inplace=True)
    recnik = df.to_dict('index')

    for key, value in recnik.items():
        if recnik[key]['titleType'] in ['tvSeries', 'tvMiniSeries']:
            recnik[key]['episodes'] = []
    
    del df
    return recnik
    
@measure_time
def insert_ratings(file_path, recnik):
    rating_df = load_data_into_dataframe(file_path=file_path)
    convert_to_numeric(['averageRating', 'numVotes'], rating_df)

    for row in rating_df.itertuples():
        if not recnik.get(row.tconst):
            continue
        recnik[row.tconst]['rating'] = {
            "avgRating": row.averageRating,
            "numVotes": row.numVotes
        }
    
    del rating_df

@measure_time
def insert_episodes(file_path, recnik):
    episode_df = load_data_into_dataframe(file_path=file_path)
    convert_to_numeric(['episodeNumber', 'seasonNumber'], episode_df)

    for row in episode_df.itertuples():
        if not recnik.get(row.parentTconst) or not recnik.get(row.tconst):
            continue
        episode_info = recnik[row.tconst]
        episode_info['seasonNumber'] = row.seasonNumber
        episode_info['episodeNumber'] = row.episodeNumber
        recnik[row.parentTconst]['episodes'].append(episode_info)
        recnik.pop(row.tconst)
    
    del episode_df

@measure_time
def insert_cast(title_info_file, cast_info_file, principal_info_path, recnik):
    basic_df = load_data_into_dataframe(title_info_file)
    principal_df = load_data_into_dataframe(principal_info_path)

    principal_df = filter_dataframe(principal_df, 'tconst', basic_df)
    
    del basic_df

    cast_df = load_data_into_dataframe(cast_info_file)
    
    principal_df = filter_dataframe(principal_df, 'nconst', cast_df)
    
    principal_df = principal_df.groupby(['tconst', 'nconst']).agg({'category': lambda x: ', '.join(set(x))}).reset_index()
    principal_df['category'] = principal_df['category'].str.split(',')

    joined_df = pd.merge(cast_df, principal_df, on='nconst')
    
    del cast_df, principal_df

    joined_df.drop(['primaryProfession', 'knownForTitles'], axis=1, inplace=True)
    convert_to_numeric(['birthYear', 'deathYear'], joined_df)

    cast = (
        joined_df.groupby('tconst')
        .apply(lambda x: x[['nconst', 'primaryName', 'birthYear', 'deathYear', 'category']].to_dict('reconrds'))
        .reset_index()
        .set_index('tconst')
        .rename(columns={0: 'cast'})
        .to_dict('index')
    )

    for key, value in cast.items():
        if not recnik.get(key):
            continue
        # value = {k: v for k, v in value.items() if v is not None}
        recnik[key]['cast'] = value['cast']

@measure_time
def export_json(recnik, output_file_name):
    # json_output = json.dumps(recnik)
    with open(output_file_name, "w") as output_file:
        for _, value in recnik.items():
            json_object = json.dumps(value)
            output_file.write(json_object + "\n")

if __name__ == "__main__":
    recnik = initial_dictionary(title_basics_path)
    insert_ratings(title_ratings_path, recnik)
    insert_episodes(title_episode_path, recnik)
    insert_cast(title_basics_path, name_basics_path, title_principals_path, recnik)
    export_json(recnik, output_path)