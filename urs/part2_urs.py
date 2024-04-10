from part1_urs import *
import cohere
import numpy as np
import re
import pandas as pd
from tqdm import tqdm
from datasets import load_dataset
import umap
import altair as alt
from sklearn.metrics.pairwise import cosine_similarity
from annoy import AnnoyIndex
import warnings
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('flask1.html')

@app.route('/process', methods=['POST'])
def process():
    warnings.filterwarnings('ignore')
    pd.set_option('display.max_colwidth', None)

    results = list()
    rlinks = list()
    
    query=request.form['user_input']
    get_dataset(query, results, rlinks)

    model_name = "embed-english-v3.0"
    api_key = "z6i4MGSuIacsbKxjHgRDfzshQHCafyFUJafnOYja"
    input_type_embed = "search_document"

    co = cohere.Client(api_key)

    embeds = co.embed(texts=results,
                      model=model_name,
                      input_type=input_type_embed).embeddings

    # print(np.array(embeds).shape[1])

    search_index = AnnoyIndex(np.array(embeds).shape[1], 'angular')
    print(search_index)

    for i in range(len(embeds)):
        search_index.add_item(i, embeds[i])
    search_index.build(10) # 10 trees

    query = "how to securely process a string"
    input_type_query = "search_query"

    # Get the query's embedding
    query_embed = co.embed(texts=[query],
                      model=model_name,
                      input_type=input_type_query).embeddings

    # Retrieve the nearest neighbors
    similar_item_ids = search_index.get_nns_by_vector(query_embed[0],10,
                                                    include_distances=True)
    # Format the results
    query_results = pd.DataFrame(data={'links': [rlinks[index] for index in similar_item_ids[0]], 
                                 'distance': similar_item_ids[1],
                                 'phrase': [results[index] for index in similar_item_ids[0]]})


    print(f"Query:'{query}'\nNearest neighbors:")
    print(query_results) # NOTE: Your results might look slightly different to ours.
    return render_template('flask1.html', output=query_results)

if __name__ == '__main__':
    app.run()