import os
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import io
from io import BytesIO
import base64
from flask import Flask, render_template, flash, redirect, request, session
from flask_session import Session
import sqlite3

app = Flask(__name__)

# Configure the secret key for Flask session
app.secret_key = os.urandom(24)


# Configure the Flask session to store data in the local filesystem
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)


# Define the home page route
@app.route('/')
def index():
    
    return render_template('index.html')





def generate_heatmap():
    # Load the US shapefile
    us = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    us = us[us.name != 'Antarctica']

    # Load the data
    conn = sqlite3.connect('rnalytics.db')
    df = pd.read_sql_query("SELECT * FROM contracts", conn)

    # Clean up the pay_rate column
    df['pay_rate'] = df['pay_rate'].str.replace('$', '').str.replace(',', '')
    df['pay_rate'] = pd.to_numeric(df['pay_rate'], errors='coerce')

    # Compute the aggregate pay rate by location
    data = df.groupby('location').agg({'pay_rate': 'mean'})

    # Merge the data with the shapefile
    merged = pd.merge(us, data, how='left', left_on='name', right_on='location')

    # Create the choropleth map
    fig, ax = plt.subplots(1, figsize=(10, 6))
    merged.plot(column='pay_rate', cmap='YlOrRd', linewidth=0.8, ax=ax, edgecolor='0.8')
    ax.axis('off')
    ax.set_title('Average Travel RN Pay Rates by State')

    # Save the map to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')

    # Encode the buffer as a base64 string
    img_data = base64.b64encode(buf.getvalue()).decode()

    # Close the plot and database connections
    plt.close()
    conn.close()

    # Return the encoded image as a base64 string
    return img_data


    
# Define the maps page route
@app.route('/maps')
def maps():
    # Get the encoded heatmap image
    heatmap = generate_heatmap()

    # Pass the heatmap image to the template
    return render_template('maps.html', heatmap=heatmap)
    

# Define the graphs page route
@app.route('/graphs')
def graphs():
    graph = generate_heatmap()
    return render_template('graphs.html', graph=graph)


# Define the raw data page route
@app.route('/raw_data')
def raw_data():
    # Connect to the database
    conn = sqlite3.connect('rnalytics.db')
    cursor = conn.cursor()

    # Retrieve the data from the database
    cursor.execute('SELECT * FROM contracts')
    contracts = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Pass the data to the template
    return render_template('raw_data.html', contracts=contracts)


@app.route('/chart_data', methods=['POST'])
def chart_data():
    # Get the chart type from the request
    chart_type = request.json['chartType']

    # Connect to the database
    conn = sqlite3.connect('rnalytics.db')
    cursor = conn.cursor()

    # Determine the SQL query to use based on the chart type
    if chart_type == "location":
        query = """
            SELECT facility_name, location, pay_rate
            FROM contracts
            ORDER BY location
        """
    elif chart_type == "season":
        # TODO: add SQL query for season chart
        pass
    elif chart_type == "specialty":
        # TODO: add SQL query for specialty chart
        pass
    elif chart_type == "shift":
        # TODO: add SQL query for shift chart
        pass
    elif chart_type == "contract-length":
        # TODO: add SQL query for contract-length chart
        pass

    # Execute the SQL query and retrieve the data
    cursor.execute(query)
    data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Return the data as a JSON response
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
