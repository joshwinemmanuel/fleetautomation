import pandas as pd

def apply_common_filters(data_df):
    # Define columns to exclude zeros
    columns_to_exclude_zeros = ['Autononous driving mileage (km)', 'Manual driving mileage (km)',
                                 'Autononous driving time (hr)', 'Manual driving time (hr)',
                                 'Total driving time (hr)', 'D gear time (hr)']

    # Exclude rows with zeros in specified columns
    for col in columns_to_exclude_zeros:
        data_df = data_df[data_df[col] != 0]

    return data_df

def process_eu_data(filter_df, data_df):
    # """Process EU-specific data."""
    # Create an empty dictionary to store test data
    test_data = {}

    # Iterate over each row in the filter DataFrame
    for index, row in filter_df.iterrows():
        hostname = row['Hostname']
        # Iterate over each date column
        for column in filter_df.columns[1:]:
            date = column
            test = row[column]
            # Check if the cell is not empty
            if pd.notnull(test):
                # Filter data_df by date and hostname
                filtered_df = data_df[(data_df['Date'] == date) & (data_df['Hostname'] == hostname)]

                if not filtered_df.empty:
                    # Add filtered data to the dictionary for the respective test
                    if test not in test_data:
                        test_data[test] = filtered_df
                    else:
                        test_data[test] = pd.concat([test_data[test], filtered_df])

    return test_data

def calculate_summary_data(df):
    numeric_cols = df.select_dtypes(include='number')
    averages = numeric_cols.mean()

    if not averages.empty:
        # Perform calculations
        averages['Average Total driving time (min)'] = averages['Activate time (hr)'] * 60
        averages['Average D gear time (min)'] = averages['D gear time (hr)'] * 60
        averages['D/total time'] = averages['D gear time (hr)'] / averages['Activate time (hr)'] * 100
        averages['Auto/total km'] = (averages['Autononous driving mileage (km)'] / averages['Total mileage (km)']) * 100

    summary = [
        averages.get('Average Total driving time (min)', None),
        averages.get('Activate time (hr)', None),
        averages.get('Average D gear time (min)', None),
        averages.get('D gear time (hr)', None),
        averages.get('D/total time', None),
        averages.get('Total mileage (km)', None),
        averages.get('Autononous driving mileage (km)', None),
        averages.get('Auto/total km', None),
        averages.get('Takeover', None)
    ]

    return summary

def generate_summary_eu(test_data_eu):
    try:
        summary_data = {}

        for test, df in test_data_eu.items():
            summary_data[test] = calculate_summary_data(df)

        summary_df = pd.DataFrame(summary_data, index=[
            'average total online time (min)',
            'average total online time (hr)',
            'average total D drive time (min)',
            'average total D drive time (hr)',
            'D/total time (%)',
            'average total km/day',
            'average Autononous km/day',
            'auto/total km (%)',
            'average takeover No.'
        ])

        summary_df.to_csv('eu_summary daily.csv', index=True)

    except Exception as e:
        print("Error generating EU summary:", str(e))

def process_specific_hostnames(data_df):
    # Define hostnames and their corresponding labels
    hostname_labels = {
        'S580-BBSQ3142': 'ATGB1',
        'BBSQ5098': 'ATGB2',
        'BBQS3816': 'ATGB4',
        'S580-BBQS3685': 'ATGB6',
        'S580-BBQS4364': 'ATGB8',
        'S580-BBQS4597': 'ATGB9',
        'S580-BBQS3817': 'ATGB10',
        'S580-BBQS7149': 'ATGB11',
        'S580-BBQS3823': 'ATGB12',
        'S580-BBQS3696': 'ATGB13',
        'BBQS4702': 'ATGB14',
        'BBQS7150': 'ATGB15',
        'BBOR7404': '223-4',
        'BBOR7405': '223-5',
        'S450-BBQS5622': 'Tiger',
        'S450L-BBSQ3150': 'Koala',
        'S580-BBQS3499': 'Shark'
    }

    columns_to_keep = ['Total mileage (km)', 'Autononous driving mileage (km)', 'Activate time (hr)', 'Total driving time (hr)']

    # Filter the DataFrame to keep only the specified columns
    filtered_df = data_df[['Hostname'] + columns_to_keep]

    # Convert relevant columns to numeric (if necessary)
    filtered_df.loc[:, columns_to_keep] = filtered_df.loc[:, columns_to_keep].apply(pd.to_numeric, errors='coerce')

    # Drop rows with missing values
    filtered_df = filtered_df.dropna()

    # Calculate averages for 'D/total time' and 'auto/total km'
    averages = filtered_df.groupby('Hostname').mean()
    averages['D/total time'] = averages['Total driving time (hr)'] / averages['Activate time (hr)'] * 100
    averages['auto/total km (%)'] = (averages['Autononous driving mileage (km)'] / averages['Total mileage (km)']) * 100

    # Extract labels that have corresponding hostnames present in the DataFrame
    available_labels = [label for hostname, label in hostname_labels.items() if hostname in averages.index]

    # Create a DataFrame for the required columns with available labels
    result_df = pd.DataFrame(index=available_labels, columns=['D/total time', 'auto/total km (%)'])

    # Update the DataFrame with calculated averages where available
    for hostname, label in hostname_labels.items():
        if hostname in averages.index:
            result_df.loc[label, 'D/total time'] = averages.loc[hostname, 'D/total time']
            result_df.loc[label, 'auto/total km (%)'] = averages.loc[hostname, 'auto/total km (%)']

    # Check if result_df is not empty
    if not result_df.empty:
        # Save the result to a new CSV file
        result_df.to_csv('specific_hostnames_summary.csv')

def process_data():
    # Read the CSV files into pandas DataFrames
    filter_df = pd.read_csv('filter_data.csv')
    data_df = pd.read_csv('042524.csv')

    # Convert date column in 412_421.csv to match the format in filter_data.csv
    data_df['Date'] = pd.to_datetime(data_df['Date']).dt.strftime('%Y-%m-%d')

    # Apply common filters
    data_df = apply_common_filters(data_df)

    
    # Process EU-specific data
    test_data_eu = process_eu_data(filter_df, data_df)

    # Save each test data to a separate CSV file in the filtered_results directory
    for test, df in test_data_eu.items():
        df.to_csv(f'filtered_results/output_data_EU_{test}.csv', index=False)

    # Save the results to a new CSV file in the filtered_results directory
    results = pd.DataFrame(columns=['Test', 'Hostname'])
    for test in test_data_eu.keys():
        for hostname in test_data_eu[test]['Hostname'].unique():
            results = pd.concat([results, pd.DataFrame({'Test': [test], 'Hostname': [hostname]})], ignore_index=True)

            
    results.to_csv('filtered_results/filtered_results.csv', index=False)

    return data_df, test_data_eu

# Call the function to process the data
data_df, test_data_eu = process_data()

# Generate EU daily summary data
generate_summary_eu(test_data_eu)

# Process specific hostnames and generate summary
process_specific_hostnames(data_df)
