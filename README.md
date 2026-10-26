# Day 1: API Data Extraction and Transformation

## About the Project

For this project, I worked on extracting customer information from a REST API and preparing it for use by an analytics team.

The scenario was based on Duka Connect, a Nairobi-based B2B distributor that needed customer records from a partner whose directory was available through an API. The data came in a nested JSON format, so my task was to retrieve it, understand its structure, flatten it, and save it as a clean CSV file.

I used Python, the Requests library, and pandas to complete the task.

## Tools and Technologies

- Python
- Requests — to make API requests and retrieve the data
- pandas — to clean and organize the records into a DataFrame
- JSON — the format returned by the API
- CSV — the final output format
- uv — to manage the project environment and install packages
- Git and GitHub — to manage and share the project

## API Used

I used the JSONPlaceholder Users API:

https://jsonplaceholder.typicode.com/users

The API returned 10 user records. Each record contained basic information such as a name, username, email, phone number, and website, together with nested address and company information.

## What I Did

### 1. Retrieved the customer records

I used `requests.get()` to retrieve the records from the API. I added a timeout and checked the HTTP status before processing the response. I also handled common request errors and invalid JSON responses.

### 2. Explored the JSON structure

Before transforming the data, I checked the Python data types returned by the API.

The response was a list of dictionaries. Within each user record, the address and company information were stored in nested dictionaries. The address also contained a nested `geo` dictionary holding the latitude and longitude.

Some examples of the nested fields were:

- `address.city`
- `address.geo.lat`
- `address.geo.lng`
- `company.name`
- `company.catchPhrase`
- `company.bs`

This helped me understand how to access the information before flattening it.

### 3. Extracted the important fields

I created a function called `extract_core_fields()` to extract the user's ID, name, email, city, and company name.

I also accounted for missing fields so that an absent address or company would not immediately cause the function to fail.

### 4. Worked with Python data structures

I implemented `build_structures()` to create three different structures from the user records:

- A list containing the users' names.
- A list of tuples containing each user's ID and email.
- A dictionary mapping each user ID to their city.

I used list comprehensions, a dictionary comprehension, and a regular `for` loop as required by the assignment.

### 5. Flattened the nested JSON

I created a reusable function called `flatten_user()` that uses recursion to flatten nested dictionaries.

For example, `address.geo.lat` becomes `address_geo_lat`. This makes the information easier to work with in a tabular format.

The function does not depend on specific field names, so it can handle different nested dictionary structures.

### 6. Created the DataFrame

I used pandas to load the flattened records into a DataFrame.

I renamed `id` to `customer_id` and changed `company_catchPhrase` to `company_catchphrase` to match the expected output. I also converted the latitude and longitude fields to numeric values.

The final DataFrame contained 10 rows and 15 columns, arranged in the order specified in the assignment.

### 7. Exported the CSV

I exported the cleaned records to:

`output/customers_clean.csv`

The export function creates the output folder if it does not exist and saves the CSV without the pandas index. Running the script again overwrites the existing file rather than appending duplicate records.

### 8. Tested error handling

Since the assignment required the script to handle API failures, I created a separate file called `test_failures.py`.

I tested four scenarios:

- A malformed URL.
- A simulated request timeout.
- A simulated HTTP 503 response.
- A response containing invalid JSON.

All four tests passed. Each produced a clear error message and exit code `1`, without an unhandled traceback.

## Assumptions

During the implementation, I made the following assumptions:

- The API normally returns a list of user records.
- Missing text fields in the core extraction are represented by empty strings.
- A missing customer ID is represented by `None` in the core extraction.
- If an address or company dictionary is missing, it is treated as an empty dictionary.
- If a required output column is absent, it is created with missing values.
- Values that cannot be converted to numbers become missing values during numeric conversion.
- The final CSV must contain the 15 required columns in the exact order provided by the trainer.
- A successful extraction depends on the API being reachable.

## How to Run the Project

Make sure Python and uv are installed, then open PowerShell in the project directory.

### 1. Create the virtual environment

```powershell
uv venv
```

### 2. Activate it

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install the required packages

```powershell
uv pip install -r requirements.txt
```

### 4. Run the extraction script

```powershell
python extract_customers.py
```

The script will retrieve the records, process them, display the DataFrame shape and data types, and export the cleaned CSV.

### 5. Run the failure tests

```powershell
python test_failures.py
```

This runs the four tests used to check how the script handles API request failures.

## Final Output

The cleaned CSV is saved at:

`output/customers_clean.csv`

The successful run retrieved 10 user records and produced a DataFrame with 15 columns. The CSV was created successfully, and all four failure tests passed.

## What I Learned

This project helped me practise working with REST APIs, inspecting nested JSON, using Python dictionaries and comprehensions, flattening nested data with recursion, and preparing data for analysis using pandas.

I also gained experience handling request failures and testing error conditions instead of checking only whether the script works when everything goes well.
