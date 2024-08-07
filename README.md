# ProjectName
> A brief description of the project.

## Table of Contents

* [Introduction](#introduction)
* [Installation](#installation)
* [Code](#code)

---

### Introduction

This is the backend for the visualization page of node-red. It contains a MQTT client that creates dynamically figure on the fly

### Installation
To run this project you need to have python 3 or higher installed in your computer. You can download python from [this link](https://www.python.org/downloads/). Then you can install the required packages using pip by running the following command:
```bash
pip install -r requirements.txt
```

### Code

#### controller.py

This Python script implements a MQTT controller for the visualization page.

The script defines several methods related to creating different types of visualizations (e.g., scatter plots, histograms, world maps, timelines), as well as initializing data tables and information tables. These methods are called with the `create_` prefix followed by the type of visualization (e.g., `create_scatter_plot`, `create_hist_plot`, etc.).

Here's a breakdown of the code:

1. The first section imports necessary libraries: `paho.mqtt.client` for MQTT, `json` for JSON serialization, and "Invalid arguments" is likely a string literal.
2. The `VisualizationController` class defines several methods:
	* `create_scatter_plot`: Creates a scatter plot with specified x and y columns.
	* `create_hist_plot`: Creates a histogram plot for the specified column.
	* `init_datatable`: Initializes the data table.
	* `init_infotable`: Initializes the information table.
	* `create_world_map`: Creates a world map visualization.
	* `create_timeline`: Creates a timeline visualization.
	* `create_defaults_plots`: Creates default plots based on a list of basic plots.
3. The `on_publish` method is a callback function that prints a message when a message is published.
4. The `run` method:
	* Connects to the MQTT broker using the `connect` method.
	* Starts two threads: one for the MQTT controller and another for the Flask server.
	* Calls the `loop_forever` method on the MQTT controller thread, which runs indefinitely.
5. The script defines several instance variables:
	* `controller`: an MQTT client object.
	* `server`: a Flask server object.
	* `data_table`, `info_table`, and `map`: objects that represent data tables, information tables, and maps, respectively.
6. Finally, the script creates an instance of the `VisualizationController` class and runs it using the `run` method.

In summary, this script is part of a larger application that uses MQTT to handle messaging between different components. It provides methods for creating various types of visualizations and initializing data tables and information tables.

---

#### flask_server.py

This is a Python script that defines a class `FlaskServer` for creating and managing multiple Dash applications (which are web-based visualizations) using Flask as the web server.

Here's a breakdown of the code:

**Initialization**

The `__init__` method initializes the `FlaskServer` object with an optional parameter `size`, which determines how many Dash apps to create. The default size is 20.

It sets up several instance variables:

* `default_layout`: a basic HTML layout for all Dash apps.
* `server`: the Flask server.
* `apps`: a dictionary of Dash app objects, indexed by their IDs (0 to `size-1`).
* `apps_available`: a list of available app IDs (i.e., those that are not currently running).
* `apps_running`: a list of currently running app IDs.

**Initializing the Flask Server**

The `init_flask_server` method creates the Flask server and initializes it with the following:

* Creates a Flask server with the name "Visualization Server".
* For each app ID from 0 to `size-1`, creates a new Dash app with that ID, sets its layout to the default layout, and adds it to the `apps` dictionary.
* Sets up several routes (URLs) for the Flask server:
	+ `/`: returns a basic HTML page with links to all available apps.
	+ `/apps`: lists all available apps, including their IDs and whether they are running or not.
	+ `/apps/shutdown`: shuts down an app by resetting its layout and removing it from the `apps_running` list. It also adds the ID to the `apps_available` list if necessary.

**Getting an Available App**

The `get_available_app` method returns an available Dash app (i.e., one that is not currently running). If no apps are available, it returns the first app in the list (which will be reset when run).

---

This is a Python script that defines two functions and a class, all related to working with TSV (Tab-Separated Values) files. Here's a breakdown of the code:

**Functions**

1. `find_tsv_files(path)`:
	* Iterates through a directory tree starting from the given `path`.
	* Checks if each file is a TSV file (ending with `.tsv`) and adds its path to an empty list `tsv_files` if it is.
	* If a file is a ZIP archive containing a TSV file, extracts the inner file's path and adds it to the list as well. The format of these paths will be `zip_file:inner_file.tsv`.
	* Returns the list of TSV files found.
2. `load_dataframe(path)`:
	* Initializes a `CustomDataFrame` object with the given `path`.
	* Converts all column names to lowercase using the `str.lower()` method.
	* Drops the first row of the DataFrame (assuming it's unnecessary metadata).
	* Iterates through each column in the DataFrame and checks if the first value is marked as numeric (`'[f]'`). If so, converts the entire column to a numeric type using `pd.to_numeric()`.
	* Checks if any columns contain specific keywords (`'object_'`, but not `'id'` or `'label'`) and adds them to an empty list `metadatas_of_interest`. These are likely metadata columns of interest.
	* Returns the loaded DataFrame, its length, and the list of metadatas of interest.

**Class**

1. `CustomDataFrame(pd.DataFrame)`:
	* Defines a custom DataFrame class that inherits from Pandas' built-in `pd.DataFrame` class.
	* Adds three attributes: `path`, `name`, and `zip`. These are used to store metadata about the DataFrame, such as its file path and whether it was loaded from a ZIP archive.
	* Overloads the `__init__()` method to initialize the custom DataFrame with optional parameters `path` and `**kwargs`.
	* If a `path` is provided, checks if it's a ZIP file containing an inner TSV file. If so, reads the TSV file from the ZIP archive using `zipfile.ZipFile`. Otherwise, reads the TSV file directly using `pd.read_csv()`.
	* Sets the `zip` attribute to `True` if the DataFrame was loaded from a ZIP archive and `False` otherwise.
	* Sets the `path` and `name` attributes accordingly.

**Example usage**

In the last block of code, the script demonstrates how to use the two functions by finding all TSV files in a directory and printing their paths.

---

#### utils.py

This is a Python script that defines two functions and a class, all related to working with TSV (Tab-Separated Values) files. Here's a breakdown of the code:

**Functions**

1. `find_tsv_files(path)`:
	* Iterates through a directory tree starting from the given `path`.
	* Checks if each file is a TSV file (ending with `.tsv`) and adds its path to an empty list `tsv_files` if it is.
	* If a file is a ZIP archive containing a TSV file, extracts the inner file's path and adds it to the list as well. The format of these paths will be `zip_file:inner_file.tsv`.
	* Returns the list of TSV files found.
2. `load_dataframe(path)`:
	* Initializes a `CustomDataFrame` object with the given `path`.
	* Converts all column names to lowercase using the `str.lower()` method.
	* Drops the first row of the DataFrame (the one filled with [t] and [f]).
	* Iterates through each column in the DataFrame and checks if the first value is marked as numeric (`'[f]'`). If so, converts the entire column to a numeric type using `pd.to_numeric()`.
	* Checks if any columns contain specific keywords (`'object_'`, but not `'id'` or `'label'`) and adds them to an empty list `metadatas_of_interest`. These are likely metadata columns of interest.
	* Returns the loaded DataFrame, its length, and the list of metadatas of interest.

**Class**

1. `CustomDataFrame(pd.DataFrame)`:
	* Defines a custom DataFrame class that inherits from Pandas' built-in `pd.DataFrame` class.
	* Adds three attributes: `path`, `name`, and `zip`. These are used to store metadata about the DataFrame, such as its file path and whether it was loaded from a ZIP archive.
	* Overloads the `__init__()` method to initialize the custom DataFrame with optional parameters `path` and `**kwargs`.
	* If a `path` is provided, checks if it's a ZIP file containing an inner TSV file. If so, reads the TSV file from the ZIP archive using `zipfile.ZipFile`. Otherwise, reads the TSV file directly using `pd.read_csv()`.
	* Sets the `zip` attribute to `True` if the DataFrame was loaded from a ZIP archive and `False` otherwise.
	* Sets the `path` and `name` attributes accordingly.

---

#### Charts

The provided code demonstrates how to create various types of visualizations:

* **World Map**: Displays a world map with markers representing datasets.
* **Timeline**: Datasets over time.
* **Data Table**: Presents object metadata in a tabular format.
* **Info Table**: Similar to a data table but displays metadata about the project.
* **Scatter Plot**: Plots data points on a 2D coordinate system (x-y axis) to show relationships between variables.
* **Hist Plot**: Displays the distribution of data values over a range of intervals or bins.

**Structure**

Each chart follows a similar structure:

1. **Data Preparation**: Create a new Pandas DataFrame (df) if it is needed to transform the data given in input of the class that represent the tsv file
2. **Creation of Plotly Layout**: Define the appearance of the figure, including colors, fonts, backgrounds, and more.
3. **Creation of Dash App**: Contain the Plotly figure and add HTML/CSS elements with custom Python code to enhance the visualization and add dynamic interactions with the user.

**Key Components**

The code uses several key components:

* **Dash App Framework**: Manages the web application.
* **Plotly Figures**: Used to create visualizations, including world maps, timelines, data tables, and more.
* **Callback Functions**: Handle user interactions (e.g., clicks on the world map) and update the visualization accordingly.

