from part1 import *
import cohere
import numpy as np
import pandas as pd
from annoy import AnnoyIndex
from flask import Flask, render_template, request, jsonify
import warnings
warnings.filterwarnings('ignore')
pd.set_option('display.max_colwidth', None)

app = Flask(__name__, static_url_path="/static", static_folder='static')

# top_results = jsonify({'unique_links':list()})

@app.route('/')
def index():
    return render_template('altsearch.html')

@app.route('/process', methods=['POST'])
def process():
    results = list()
    rlinks = list()
    query=request.form['user_input']

    get_dataset(query, 80, results, rlinks)

    model_name = "embed-english-v3.0"
    api_key = "2gtPSdrP4OQqJppvccnSVAb7n92eQO65qO25bKUr"
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
    similar_item_ids = search_index.get_nns_by_vector(query_embed[0],150,
                                                    include_distances=True)
    # Format the results
    query_results = pd.DataFrame(data={'links': [rlinks[index] for index in similar_item_ids[0]], 
                                'distance': similar_item_ids[1],
                                'phrase': [results[index] for index in similar_item_ids[0]]})


    print(f"Query:'{query}'\nNearest neighbors:")
    print(query_results) # NOTE: Your results might look slightly different to ours.
    uniq_links = query_results['links'].unique()
    # global top_results
    # return render_template('altsearch.html', output=jsonify({ "unique_links" : list(query_results['links'].unique()) }))
    top_results = jsonify({ "unique_links" : list(uniq_links) })
    return render_template('altsearch.html', output1=uniq_links[0], output2=uniq_links[1], output3=uniq_links[2], output4=uniq_links[3], output5=uniq_links[4], output6=uniq_links[5],) #output7=uniq_links[6], output8=uniq_links[7], output9=uniq_links[8], output10=uniq_links[9], output11=uniq_links[10], output12=uniq_links[11], output13=uniq_links[12], output14=uniq_links[13], output15=uniq_links[14])#, output16=uniq_links[15], output17=uniq_links[16], output18=uniq_links[17], output19=uniq_links[18], output20=uniq_links[19])

# @app.route('/get_results', methods = ['GET'])
# def get_results():
#     return top_results

if __name__ == '__main__':
    app.run()