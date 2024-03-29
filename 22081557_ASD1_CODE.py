# -*- coding: utf-8 -*-
"""Clustering and Fitting.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1B-InBiTIOCqEwi-rO81FUc2IG0CFBmIY

# **Importing** **Libraries**
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from scipy.optimize import curve_fit
import statsmodels.api as sm
from sklearn.metrics import silhouette_score

"""# **Function Definitions**

**`Function to Read File`**
"""

def readFile(filename):
    """
    Read data from a CSV file into a Pandas DataFrame, remove metadata, and
    return two DataFrames.

    Parameters:
    - filename (str): Path to the CSV file.

    Returns:
    - df and Transposed DataFrame as countries_data.
    """
    # Load data into a Pandas DataFrame and drop the last column
    try:
        df = pd.read_csv(filename,skiprows=4).iloc[:, :-1]
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at {filename}. Please provide a valid file path.")

     # Create a dataset with countries as columns and drop unnecessary columns
    df.drop(["Country Code", "Indicator Code"], axis=1, inplace=True)

    # Create a dataset with countries as columns and drop unnecessary column
    country_data = df.set_index(["Country Name", "Indicator Name"])


    # Transpose the countries dataframe
    country_data = country_data.T

    return df, country_data

"""# **Data Description & Statistics**"""

#To describe data and dipslay statistics
def describe_Data(df):

  df.head()
  df.info()
  df.columns
  df.describe()

  #Display categorical features
  categorical_features = (df.select_dtypes(include=['object']).columns.values)
  categorical_features

  #Display numerical features
  numerical_features = df.select_dtypes(include = ['float64', 'int64']).columns.values
  numerical_features

"""# **Data Extraction**"""

#define the list of indicators relevant to the analysis
indicators_list = [

    'Electricity production from coal sources (% of total)',
    'Electricity production from oil sources (% of total)',
    'Electricity production from natural gas sources (% of total)',
    'Electricity production from nuclear sources (% of total)',
    'Electricity production from hydroelectric sources (% of total)',
    'Electricity production from renewable sources, excluding hydroelectric (% of total)',
    'Electric power consumption (kWh per capita)',
    'CO2 emissions (kt)',
    'Total greenhouse gas emissions (kt of CO2 equivalent)',
    'Access to electricity (% of population)',
    'Renewable energy consumption (% of total final energy consumption)',
    'Renewable electricity output (% of total electricity output)',
]

# Extracting data for relevant indicators
def extract_data(df,indicators_list):
  """
    Extract data from a DataFrame based on a list of relevant indicators.

    Parameters:
    - df (pd.DataFrame): Input DataFrame containing the data.
    - indicator_list (list): List of indicator names to extract.

    Returns:
    - pd.DataFrame: DataFrame with data only for the specified indicators.

    """
  filtered_df = df[df["Indicator Name"].isin(indicators_list)]

  return filtered_df

"""## **Data Preprocessing**"""

# Handle missing values (Replace missing values with 0 )
def preprocess(df):

  df.fillna(0, inplace=True)

  return df

# Dropping all world records
def drop_world(df):

  index = df[df["Country Name"] == "World"].index
  df.drop(index, axis=0, inplace=True)
  df.reset_index(drop=True, inplace=True)

  return df

"""# **Cluster Tools**"""

def map_corr(df, size=6):
    """Function creates a heatmap of the correlation matrix for each pair of
    columns in the DataFrame.

    Input:
        df: pandas DataFrame
        size: vertical and horizontal size of the plot (in inch)

    The function does not have a plt.show() at the end so that the user
    can save the figure.
    """

    corr = df.corr()
    plt.figure(figsize=(size, size))
    plt.matshow(corr, cmap='coolwarm', aspect='auto')

    # setting ticks to column names
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)

    plt.colorbar()

# Function to estimate confidence ranges
def err_ranges(fit_params, covariance_matrix, x_data, func, alpha=0.05):
    n = len(x_data)
    p = len(fit_params)
    dof = max(0, n - p)  # Degrees of freedom

    t_value = abs(t.ppf(alpha / 2, dof))

    err = np.sqrt(np.diag(covariance_matrix))

    lower_bounds = fit_params - t_value * err
    upper_bounds = fit_params + t_value * err

    return lower_bounds, upper_bounds

""" Tools to support clustering: correlation heatmap, normaliser and scale
(cluster centres) back to original scale, check for mismatching entries """


def map_corr(df, size=6):
    """Function creates heatmap of correlation matrix for each pair of
    columns in the dataframe.

    Input:
        df: pandas DataFrame
        size: vertical and horizontal size of the plot (in inch)

    The function does not have a plt.show() at the end so that the user
    can savethe figure.
    """

    corr = df.corr()
    plt.figure(figsize=(size, size))
    # fig, ax = plt.subplots()
    plt.matshow(corr, cmap='coolwarm', location="bottom")
    # setting ticks to column names
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)

    plt.colorbar()
    plt.show()

"""# **Main Function**"""

if __name__ == "__main__":
  df, country_data = readFile('API_19_DS2_en_csv_v2_6300757.csv')
  df = extract_data(df, indicators_list)
  df = preprocess(df)

# Filtering data for the "CO2 emissions (kt)" indicator, dropping unnecessary columns
df_co2 = df[(df["Indicator Name"] == "CO2 emissions (kt)") & (df["Country Name"] == "World")].iloc[:, :-2]

# Calculating the mean of CO2 emissions for each year and plotting the results
df_co2.iloc[:, 32:].mean().plot(kind="line", figsize=(14, 5))

plt.xlabel('Year')
plt.ylabel('CO2 emissions (kt)')

plt.title("World Average CO2 Emission\n1990 - 2020", fontsize=18)
plt.show()

# Selecting data for a specific year (e.g., 2015)
target_year = '2015'

indicators = [

    'Electricity production from coal sources (% of total)',
    'Electricity production from oil sources (% of total)',
    'Electricity production from natural gas sources (% of total)',
    'Electricity production from nuclear sources (% of total)',
    'Electricity production from hydroelectric sources (% of total)',
    'Electricity production from renewable sources, excluding hydroelectric (% of total)',
    ]

#Selecting world data
world_data = df[df["Country Name"] == "World"]

#Extracting relevant indicators
filtered_df = world_data[world_data["Indicator Name"].isin(indicators)]

# Create a dictionary mapping long names to short forms
short_labels = {
    'Electricity production from coal sources (% of total)': 'Coal',
    'Electricity production from oil sources (% of total)': 'Oil',
    'Electricity production from natural gas sources (% of total)': 'Natural Gas',
    'Electricity production from nuclear sources (% of total)':'Nuclear',
    'Electricity production from hydroelectric sources (% of total)':'Hydroelectric',
    'Electricity production from renewable sources, excluding hydroelectric (% of total)':'Renewable',
}

# Replace labels with short forms
filtered_df['Short Indicator'] = filtered_df['Indicator Name'].map(short_labels)
labels = filtered_df['Short Indicator']
sizes = filtered_df[target_year]

# Plotting the pie chart
plt.figure(figsize=(10, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['#ff9999', '#66b3ff', '#99ff99'])
plt.title(f'Electricity Production Sources (% of Total) - World ({target_year})')
plt.show()

# List of countries to keep in the dataset
countries = [
      'United States',
      'China',
      'India',
      'Russian Federation',
      'United Kingdom',
      'France',
      'Germany',
      'Japan',
      'Brazil',
      'Canada',
      'Australia',
      'South Korea',
      'Italy',
      'Spain',
      'Mexico',
      'Indonesia',
      'Turkey',
      'Nigeria',
      'Saudi Arabia',
      'Iceland',
      'Pakistan',
      'Kuwait',
      'Sweden',
      'Norway',
      'Denmark',
      'Finland',
      'New Zealand',
      'Austria',
      'Switzerland',
      ]

# Assuming df is your DataFrame
df_countries = df[df['Country Name'].isin(countries)]

# Selecting data for coal production
coal_data = df_countries[df_countries["Indicator Name"] == "Electricity production from coal sources (% of total)"]

# Sorting by coal production in descending order
sorted_coal_data = coal_data.sort_values(by='2015', ascending=False)

# Taking the top 5 countries
top_5_coal_countries = sorted_coal_data.head(10)

# Data for the bar chart
countries = top_5_coal_countries['Country Name']
coal_percentages = top_5_coal_countries['2015']

# Plotting the bar chart
plt.figure(figsize=(13, 6))
plt.bar(countries, coal_percentages, color='grey')
plt.xlabel('Country')
plt.ylabel('Electricity Production from Coal (%)')
plt.title('Top 10 Countries Generating Electricity from Coal (2015)')
plt.show()

# Selecting data for Greenhouse gas emissions
greenhouse_data = df_countries[df_countries["Indicator Name"] == "Total greenhouse gas emissions (kt of CO2 equivalent)"]

# Sorting by CO2 emissions in descending order
sorted_greenhouse_data = greenhouse_data.sort_values(by='2015', ascending=False)

# Taking the top 10 countries
top_10_greenhouse_countries = sorted_greenhouse_data.head(10)

# Data for the bar chart
countries = top_10_greenhouse_countries['Country Name']
greenhouse_emissions = top_10_greenhouse_countries['2015']/1000

# Plotting the bar chart
plt.figure(figsize=(13, 8))
plt.bar(countries, greenhouse_emissions, color='green')
plt.xlabel('Country')
plt.ylabel('Greenhouse gas emissions (kt of CO2 equivalent)')
plt.title('Top 10 Countries Producing Greenhouse Gas Emissions (kt of CO2 equivalent) (2015)')
plt.show()

# Selecting multiple years (e.g., 2010 to 2020)
years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']

# Selecting data for Renewable Energy Consumption over the years
renewable_data = df_countries[df_countries["Indicator Name"] == "Renewable energy consumption (% of total final energy consumption)"]

# Sorting by renewable energy consumption in descending order
renewable_data = renewable_data.sort_values(by=years[-1], ascending=False)

# Selecting the top 7 countries
top_7_countries = renewable_data.head(7)

# Data for the line chart
countries = top_7_countries['Country Name']
renewable_consumption_percentage_over_years = top_7_countries[years]

# Plotting the line chart
plt.figure(figsize=(15, 8))
for country in countries:
    plt.plot(years, renewable_consumption_percentage_over_years[top_7_countries['Country Name'] == country].iloc[0], label=country)

plt.xlabel('Year')
plt.ylabel('Renewable Energy Consumption\n(% of total final energy consumption)')
plt.title('Top 7 Countries for Renewable Energy Consumption')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.show()

import geopandas as gpd
import matplotlib.pyplot as plt

# Assume you have a DataFrame 'df' with the provided dataset format

# Specify the indicator name
indicator_name = 'Electric power consumption (kWh per capita)'

# Filter the DataFrame based on the indicator name
df_selected = df[df['Indicator Name'] == indicator_name]

# Load the world map shapefile
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Merge the world map with your selected data
world = world.merge(df_selected, how='left', left_on='name', right_on='Country Name')

# Plot the world map for the specified indicator
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
world.boundary.plot(ax=ax)  # Plot the country boundaries
world.plot(column='2019', ax=ax, legend=True, legend_kwds={'label': f"{indicator_name} - 2019"})
plt.title(f'Global {indicator_name} by Country - 2019')
plt.show()

# Selecting data for Greenhouse gas emissions
greenhouse_data = df_countries[df_countries["Indicator Name"] == "Electric power consumption (kWh per capita)"]

# Sorting by CO2 emissions in descending order
sorted_greenhouse_data = greenhouse_data.sort_values(by='2012', ascending=True)

# Taking the top 10 countries
top_10_greenhouse_countries = sorted_greenhouse_data.head(10)

# Data for the bar chart
countries = top_10_greenhouse_countries['Country Name']
greenhouse_emissions = top_10_greenhouse_countries['2012']/1000

# Plotting the bar chart
plt.figure(figsize=(13, 8))
plt.bar(countries, greenhouse_emissions, color='green')
plt.xlabel('Country')
plt.ylabel('Greenhouse gas emissions (kt of CO2 equivalent)')
plt.title('Top 10 Countries Producing Least Greenhouse Gas Emissions (kt of CO2 equivalent) (2015)')
plt.show()

# Selecting data for Electric power consumption
electricity_data = df_countries[df_countries["Indicator Name"] == "Electric power consumption (kWh per capita)"]

# Sorting by electric power consumption in descending order
sorted_electricity_data = electricity_data.sort_values(by='2012', ascending=False)

# Taking the top 10 countries
top_10_electricity_countries = sorted_electricity_data.head(10)

# Data for the horizontal bar chart
countries = top_10_electricity_countries['Country Name']
electricity_consumption = top_10_electricity_countries['2012']

# Specify different colors for each bar
bar_colors = ['skyblue', 'lightgreen', 'lightcoral', 'lightsalmon', 'lightsteelblue', 'lightpink', 'lightseagreen', 'lightcyan', 'lightgoldenrodyellow', 'lightblue']

# Plotting the horizontal bar chart
plt.figure(figsize=(13, 8))
plt.barh(countries, electricity_consumption, color=bar_colors)  # Use barh for horizontal bar chart
plt.xlabel('Electric Power Consumption (kWh per capita)')
plt.ylabel('Country')
plt.title('Top 10 Countries in Electric Power Consumption (kWh per capita) - 2012')
plt.show()

# Filtering data for the "Renewable enery consumption (%)" indicator, dropping unnecessary columns
df_electricity = df[(df["Indicator Name"] == "Electric power consumption (kWh per capita)") & (df["Country Name"] == "World")].iloc[:, :-8]

# Calculating the mean of CO2 emissions for each year and plotting the results
df_electricity.iloc[:, 32:].mean().plot(kind="line", figsize=(14, 5))

plt.xlabel('Year')
plt.ylabel('Electricity Consumption)')
plt.title("World Avergae Electricity Consumption\n1990 to 2020", fontsize=18)
plt.show()

# Filtering data for the world for the "Renewable energy consumption (% of total final energy consumption)" indicator
df_world_renewable = df[(df["Indicator Name"] == "Renewable energy consumption (% of total final energy consumption)") & (df["Country Name"] == "World")]

# Selecting data for all years from 1990 to 2020
years = [str(year) for year in range(1990, 2021)]
df_world_renewable_selected = df_world_renewable[years]

# Plotting the line for the world
plt.figure(figsize=(14, 5))
plt.plot(years, df_world_renewable_selected.iloc[0], marker='o', linestyle='-', color='lightgreen')

# Set x-axis ticks at a 5-year interval
plt.xticks(np.arange(0, len(years), 5), labels=years[::5])

plt.xlabel('Year')
plt.ylabel('Renewable Energy Consumption (% of total final energy consumption)')
plt.title('World Renewable Energy Consumption Over Years (1990-2020)', fontsize=18)

plt.show()

# Filtering data for the "CO2 emissions (kt)" indicator, dropping unnecessary columns
data = df[df["Indicator Name"] == "Renewable energy consumption (% of total final energy consumption)"].iloc[:, :-2]

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import numpy as np

# Selecting relevant data
df_renewable = df[df['Indicator Name'] == 'Renewable energy consumption (% of total final energy consumption)']

# Choose the columns for analysis
data = df_renewable.loc[:, '2010':'2020']

# Normalize the data
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

# Perform K-Means clustering
kmeans = KMeans(n_clusters=5, random_state=42)
clusters = kmeans.fit_predict(data_scaled)

# Calculate silhouette score
silhouette_avg = silhouette_score(data_scaled, clusters)
print(f"Silhouette Score: {round(silhouette_avg, 2)}")

# Add cluster labels to the DataFrame
df_renewable['Cluster'] = clusters

# Visualize the results
markers = ['o', 's', '^', 'D', 'v']  # Different markers for each cluster
for i in range(max(clusters) + 1):
    cluster_data = data_scaled[clusters == i]
    plt.scatter(cluster_data[:, 0], cluster_data[:, 1], label=f'Cluster {i + 1}', marker=markers[i])

plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='red', marker='X')

# Round cluster center values
cluster_centers_rounded = np.round(kmeans.cluster_centers_, 2)

plt.title("K-Means Clustering of Countries based on Renewable Energy Consumption")
plt.xlabel("Renewable Energy Consumption (Scaled)")
plt.ylabel("Other Economic Indicator (Scaled)")
plt.legend(title='Clusters')
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import t

# Choose a specific country, indicator, and years for curve fitting
country_name = 'Iceland'
indicator_name = 'Renewable energy consumption (% of total final energy consumption)'
years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']

# Extract relevant data from your DataFrame
country_data = df[(df['Country Name'] == country_name) & (df['Indicator Name'] == indicator_name)]
x_data = country_data[years].values.flatten()  # Flatten the data for curve fitting
y_data = np.arange(len(years))

# Define the model function
def simple_model(x, a, b, c):
    return a * x**2 + b * x + c

# Fit the model to the data using curve_fit
params, covariance = curve_fit(simple_model, y_data, x_data)

# Calculate confidence ranges
lower_bounds, upper_bounds = err_ranges(params, covariance, y_data, simple_model)

# Generate data for plotting the fitted curve
x_fit = np.linspace(min(y_data), max(y_data), 1000)
y_fit = simple_model(x_fit, *params)

# Plot the data, the fitted curve, and the confidence range
plt.scatter(y_data, x_data, label='Data')
plt.plot(x_fit, y_fit, color='red', label='Fitted Curve')
plt.fill_between(x_fit, simple_model(x_fit, *lower_bounds), simple_model(x_fit, *upper_bounds), color='orange', alpha=0.3, label='Confidence Range')

plt.xlabel('Year')
plt.ylabel('Your Indicator')
plt.title(f'Curve Fitting for {country_name}: {indicator_name}')
plt.legend()
plt.show()

# Assuming 'Country' is the column containing country names
# Replace 'Country' with the actual column name if it's different

# Choose one country from each cluster
selected_countries = []
for i in range(max(clusters) + 1):
    cluster_data = df_renewable[df_renewable['Cluster'] == i]
    selected_country = cluster_data.iloc[0]['Country Name']
    selected_countries.append(selected_country)

# Print the selected countries
print("Selected Countries from Each Cluster:")
for i, country in enumerate(selected_countries):
    print(f"Cluster {i + 1}: {country}")

# Choose a subset of years for visualization
selected_years = ['2010', '2012', '2015', '2018', '2020']

# Analyze and compare the selected countries within each cluster
for i, country in enumerate(selected_countries):
    cluster_data = df_renewable[df_renewable['Cluster'] == i]
    country_data = cluster_data[cluster_data['Country Name'] == country]

    # Select only the chosen years
    country_data_subset = country_data[['Country Name'] + selected_years]

    # Perform analysis and visualization for each selected country within the cluster
    # Plotting a line chart for the selected years
    plt.plot(country_data_subset.columns[1:], country_data_subset.iloc[0, 1:], label=f'{country} - Cluster {i + 1}')

# Customize the plot
plt.title("Comparison of Selected Countries within Clusters")
plt.xlabel("Year")
plt.ylabel("Renewable Energy Consumption \n(% of total final energy consumption)")

# Place the legend to the right outside the plot
plt.legend(title='Legend', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.show()