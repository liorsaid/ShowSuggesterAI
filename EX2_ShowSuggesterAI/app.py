import pandas as pd
from openai import OpenAI
import json
import pickle
from fuzzywuzzy import process
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


client = OpenAI(api_key="my_api_key")

# Read the xlsx file and convert it to a list of directory which contains the contents of the file


def read_tv_shows_xlsx(file_path):
    try:
        tv_shows_df = pd.read_excel(file_path)
        tv_shows_data = tv_shows_df.to_dict(orient='records')
        return tv_shows_data
    except Exception as e:
        print(f"Error reading the Excel file: {e}")
        return []


# Create a list of dict' from the tv_shows Excel file
xlsx_file_path = 'imdb_tvshows.xlsx'
tv_shows_data = read_tv_shows_xlsx(xlsx_file_path)

# Convert the list of dict' into a list of Titles' names
column_list = [row['Title'] for row in tv_shows_data]

# return the correct show name, using Fuzzy string matching


def match_user_shows(show_name):
    return process.extractOne(show_name, column_list)[0]

# Return a list of the correct shows' names using match_user_shows func


def get_correct_show_list(shows_list):
    tv_shows_match = []
    for show in shows_list:
        tv_shows_match.append(match_user_shows(show))
    return tv_shows_match


# Goes over all the shows and make embedding api call, extract the result to a new file
# data = {}
# for show in tv_shows_data:
#     response = client.embeddings.create(
#         input=show['Description'],
#         model="text-embedding-ada-002"
#     )
#     # Save the embedding into a dictionary
#     data.update({f"{show['Title']}": response.data[0].embedding})

# # Save the dictionary of embedding vectors into a pickle file

# with open('embedding_data.pickle', 'wb') as file:
#     pickle.dump(data, file)

with open('embedding_data.pickle', 'rb') as file:
    embedding_data = pickle.load(file)

# Goes over the corrected tv shows names and insert each show's vector to a list


def extract_vectors_by_show_name(tv_shows_list, tv_shows_match):
    vectors_list = []
    for show in tv_shows_list:
        vectors_list.append(embedding_data[f"{show}"])
    print(get_average_vector(vectors_list, tv_shows_match))
    return vectors_list

# The function check if the tv_shows which the user gave are separated with comma and |tv_shows| >=2
# After that if it goes through the check succefully, It creates and returns a String with the correct names of the user's shows


def get_favorites_shows(tv_shows):
    # Split the input into words using commas as the delimiter
    words = tv_shows.split(',')

    # Check if there is more than one word
    if len(words) > 1:
        # Check if each part is a valid word
        for word in words:
            if word.strip() == "":
                return "You should enter at least two TV shows, separated by a comma"
    tv_shows_match = get_correct_show_list(words)
    extract_vectors_by_show_name(tv_shows_match, tv_shows_match)
    str_tv_shows = ', '.join(tv_shows_match)
    final_tv_shows = "Just to make sure, do you mean " + \
        str_tv_shows + "?(y/n)"
    return final_tv_shows


def get_5_most_similar_shows(average_vector, tv_shows_match):

    temp_embedding = {**embedding_data}
    for show_name in tv_shows_match:
        del (temp_embedding[show_name])

    shows_vectors = list(temp_embedding.values())
    # Calculate cosine similarity between average vector and each show vector
    similarities = cosine_similarity([average_vector], shows_vectors)[0]

    # Combine similarities with show indices for sorting
    show_distances = list(zip(range(len(similarities)), similarities))

    # Sort shows based on distances (shortest distance first)
    sorted_shows = sorted(show_distances, key=lambda x: x[1])

    # Select the top 5 shows (excluding the input shows)
    top_5_shows = sorted_shows[0:5]

    # Output the results
    for idx, distance in top_5_shows:
        # Assuming higher similarity corresponds to a higher percentage
        percentage_similarity = 100 * (1 - distance)
        print(
            f"{list(temp_embedding.keys())[idx]}: ({percentage_similarity:.2f}%)")


# Calculate the average vector
def get_average_vector(vectors_list, tv_shows_match):
    num_vectors = len(vectors_list)
    average_vector = [sum(x) / num_vectors for x in zip(*vectors_list)]
    get_5_most_similar_shows(average_vector, tv_shows_match)
    return average_vector


get_favorites_shows("gem of throns, lupan, witcher")
