import pandas as pd

def apply_common_filters(data_df):
    # """Apply common filters to the DataFrame."""
    # Define columns to exclude zeros
    columns_to_exclude_zeros = ['Autononous driving mileage (km)', 'Manual driving mileage (km)',
                                 'Autononous driving time (hr)', 'Manual driving time (hr)',
                                 'Total driving time (hr)', 'D gear time (hr)']

    # Apply initial filters
    data_df = data_df[(data_df['Total mileage (km)'] > 0) &
                      (data_df['Autononous driving mileage (km)'] > 0)]

    # Exclude rows with zeros in specified columns
    for col in columns_to_exclude_zeros:
        data_df = data_df[data_df[col] != 0]

    return data_df

def process_cn_data(data_df):
    # """Process CN-specific data."""
    # Apply additional filters for CN data
    excluded_cn_cities = ['斯图加特', '法兰克福', '密西根州']
    filtered_cn_df = data_df[~data_df['Car City'].isin(excluded_cn_cities)]

    # Create output_files dictionary
    output_files = {}

    # Create CSV files for CP and HNP categories in CN data
    for category in ['CP', 'HNP']:
        output_file_data_cn = f"filtered_results/output_data_CN_{category}.csv"
        category_cn_df = filtered_cn_df[filtered_cn_df['Primary Category'] == category]
        category_cn_df.to_csv(output_file_data_cn, index=False)
        output_files[category] = output_file_data_cn

    return output_files

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

def generate_summary(output_files_cn, test_data_eu):
    try:
        summary_data = {
            'EU-HNP': [None]*9,
            'CN-HNP': [None]*9,
            'EU-CP': [None]*9,
            'CN-CP': [None]*9,
        }

        # Process EU-CP data
        if 'CP' in test_data_eu:
            df_cp_eu = test_data_eu['CP']
            if not df_cp_eu.empty:
                summary_data['EU-CP'] = calculate_summary_data(df_cp_eu)

        # Process EU-HNP data
        if 'HNP' in test_data_eu:
            df_hnp_eu = test_data_eu['HNP']
            if not df_hnp_eu.empty:
                summary_data['EU-HNP'] = calculate_summary_data(df_hnp_eu)

        # Process CN-CP data
        if 'CP' in output_files_cn:
            df_cp_cn = pd.read_csv(output_files_cn['CP'])
            if not df_cp_cn.empty:
                summary_data['CN-CP'] = calculate_summary_data(df_cp_cn)

        # Process CN-HNP data
        if 'HNP' in output_files_cn:
            df_hnp_cn = pd.read_csv(output_files_cn['HNP'])
            if not df_hnp_cn.empty:
                summary_data['CN-HNP'] = calculate_summary_data(df_hnp_cn)

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

        summary_df.to_csv('summary.csv', index=True)

    except Exception as e:
        print("Error generating summary:", str(e))


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

        summary_df.to_csv('eu_summary.csv', index=True)

    except Exception as e:
        print("Error generating EU summary:", str(e))

def process_data():
    # Read the CSV files into pandas DataFrames
    filter_df = pd.read_csv('filter_data.csv')
    data_df = pd.read_csv('inputfromfmp.csv')

    # Convert date column in 412_421.csv to match the format in filter_data.csv
    data_df['Date'] = pd.to_datetime(data_df['Date']).dt.strftime('%Y-%m-%d')

    # Apply common filters
    data_df = apply_common_filters(data_df)

    # Process CN-specific data
    output_files_cn = process_cn_data(data_df)

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

    return output_files_cn, test_data_eu


# Call the function to process the data
output_files_cn, test_data_eu = process_data()

# Generate summary data
generate_summary(output_files_cn, test_data_eu)

# Generate EU summary data
generate_summary_eu(test_data_eu)
