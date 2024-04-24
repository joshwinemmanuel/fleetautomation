import pandas as pd

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('filter_data.csv')

# Create an empty DataFrame to store the filtered results
results = pd.DataFrame(columns=['Date', 'Test', 'Hostname'])

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    hostname = row['Hostname']
    # Iterate over each date column
    for column in df.columns[1:]:
        date = column
        test = row[column]
        # Check if the cell is not empty
        if pd.notnull(test):
            # Append the data to the results DataFrame
            results = pd.concat([results, pd.DataFrame({'Date': [date], 'Test': [test], 'Hostname': [hostname]})], ignore_index=True)

# Save the results to a new CSV file
results.to_csv('filtered_results.csv', index=False)
