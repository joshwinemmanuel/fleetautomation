import pandas as pd
from datetime import datetime

def process_data_EU(file_path, output_directory, EU_CP_Hostname, EU_HNP_Hostname):
    df = pd.read_csv(file_path, low_memory=False)

    # Exclude rows with zeros in specified columns for each category
    columns_to_exclude_zeros = ['Autononous driving mileage (km)', 'Manual driving mileage (km)',
                                'Autononous driving time (hr)', 'Manual driving time (hr)',
                                'Total driving time (hr)', 'D gear time (hr)']
    
    # Filter data for categories 'CP' and 'HNP' for EU
    filtered_eu_df = df[
                        ((df['Hostname'].isin(EU_CP_Hostname)) |
                         (df['Hostname'].isin(EU_HNP_Hostname)))]

    # Apply additional filters for EU where the value in 'Total mileage (km)' is greater than 20
    # and 'Autononous driving mileage (km)' is greater than 10
    filtered_eu_df = filtered_eu_df[(filtered_eu_df['Total mileage (km)'] > 20) &
                                    (filtered_eu_df['Autononous driving mileage (km)'] > 10)]

    # Exclude rows with zeros in specified columns
    for col in columns_to_exclude_zeros:
        filtered_eu_df = filtered_eu_df[filtered_eu_df[col] != 0]

    # Filter out specific Hostnames for EU CP
    category_eu_cp_df = filtered_eu_df[filtered_eu_df['Hostname'].isin(EU_CP_Hostname)]

    # Filter out specific Hostnames for EU HNP
    category_eu_hnp_df = filtered_eu_df[filtered_eu_df['Hostname'].isin(EU_HNP_Hostname)]

    # Generate a unique output file name with current date and time
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save the filtered EU CP data to a new CSV file
    output_file_data_eu_cp = f"{output_directory}/output_data_EU_CP_{current_datetime}.csv"
    category_eu_cp_df.to_csv(output_file_data_eu_cp, index=False)

    # Save the filtered EU HNP data to a new CSV file
    output_file_data_eu_hnp = f"{output_directory}/output_data_EU_HNP_{current_datetime}.csv"
    category_eu_hnp_df.to_csv(output_file_data_eu_hnp, index=False)
                
    return output_file_data_eu_cp, output_file_data_eu_hnp

def process_data_CN(file_path, output_directory):
    df = pd.read_csv(file_path, low_memory=False)

    # Exclude rows with zeros in specified columns for each category
    columns_to_exclude_zeros = ['Autononous driving mileage (km)', 'Manual driving mileage (km)',
                                'Autononous driving time (hr)', 'Manual driving time (hr)',
                                'Total driving time (hr)', 'D gear time (hr)']
    
    # Filter data for categories 'CP' and 'HNP' for CN
    filtered_cn_df = df[df['Primary Category'].isin(['CP', 'HNP'])]

    # Apply additional filters for CN where the value in 'Total mileage (km)' is greater than 20
    # and 'Autononous driving mileage (km)' is greater than 10
    filtered_cn_df = filtered_cn_df[(filtered_cn_df['Total mileage (km)'] > 20) &
                                    (filtered_cn_df['Autononous driving mileage (km)'] > 10)]

    # Exclude rows with zeros in specified columns
    for col in columns_to_exclude_zeros:
        filtered_cn_df = filtered_cn_df[filtered_cn_df[col] != 0]

    # Filter out specific cities for CN
    excluded_cn_cities = ['斯图加特', '法兰克福', '密西根州']
    filtered_cn_df = filtered_cn_df[~filtered_cn_df['Car City'].isin(excluded_cn_cities)]

    # Generate a unique output file name with current date and time
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save the filtered CN CP and CN HNP data to new CSV files
    output_files = {}
    for category in ['CP', 'HNP']:
        output_file_data_cn = f"{output_directory}/output_data_CN_{category}_{current_datetime}.csv"
        category_cn_df = filtered_cn_df[filtered_cn_df['Primary Category'] == category]
        category_cn_df.to_csv(output_file_data_cn, index=False)
        output_files[category] = output_file_data_cn

    return output_files

def calculate_summary_data(df):
    numeric_cols = df.select_dtypes(include='number')
    averages = numeric_cols.mean()

    if not averages.empty:
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

def generate_summary(output_files):
    try:
        summary_data = {
            'EU-HNP': [None]*9,
            'CN-HNP': [None]*9,
            'EU-CP': [None]*9,
            'CN-CP': [None]*9,
        }

        # Process EU-CP data
        if 'EU_CP' in output_files:
            df_cp_eu = pd.read_csv(output_files['EU_CP'])
            summary_data['EU-CP'] = calculate_summary_data(df_cp_eu)

        # Process EU-HNP data
        if 'EU_HNP' in output_files:
            df_hnp_eu = pd.read_csv(output_files['EU_HNP'])
            summary_data['EU-HNP'] = calculate_summary_data(df_hnp_eu)

        # Process CN-CP data
        if 'CP' in output_files:
            df_cp_cn = pd.read_csv(output_files['CP'])
            summary_data['CN-CP'] = calculate_summary_data(df_cp_cn)

        # Process CN-HNP data
        if 'HNP' in output_files:
            df_hnp_cn = pd.read_csv(output_files['HNP'])
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
        print(f"An error occurred: {e}")


def process_specific_hostnames(file_path):
    df = pd.read_csv(file_path, low_memory=False)
    # Define hostnames and their corresponding labels
    hostname_labels = {
        'S580-BBSQ3142': 'ATGB1',
        'BBSQ5098': 'ATGB2',
        'BBQS3816': 'ATGB4',
        'S580-BBQS3685': 'ATGB6',
        'S580-BBQS3686': 'ATGB7',
        'S580-BBQS4364': 'ATGB8',
        'S580-BBQS4597': 'ATGB9',
        'S580-BBQS3817': 'ATGB10',
        'BBQS7149': 'ATGB11',
        'BBQS3823': 'ATGB12',
        'S580-BBQS3696': 'ATGB13',
        'BBQS4702': 'ATGB14',
        'BBQS7150': 'ATGB15',
        'BBOR7404': '223-4',
        'BBOR7405': '223-5',
        'S450-BBQS5622': 'Tiger',
        'S450L-BBSQ3150': 'Koala',
        'S580-BBQS3499': 'Shark'
    }
    
    # Filter data for specified hostnames
    filtered_df = df[df['Hostname'].isin(hostname_labels.keys())]
    
    # Apply additional filters for EU
    filtered_df = filtered_df[(filtered_df['Total mileage (km)'] > 20) &
                              (filtered_df['Autononous driving mileage (km)'] > 10)]
    


    columns_to_keep = ['Total mileage (km)', 'Autononous driving mileage (km)', 'Activate time (hr)', 'Total driving time (hr)']

# Filter the DataFrame to keep only the specified columns
    filtered_df = filtered_df[['Hostname'] + columns_to_keep]

# Convert relevant columns to numeric (if necessary)
    filtered_df[columns_to_keep] = filtered_df[columns_to_keep].apply(pd.to_numeric, errors='coerce')

# Drop rows with missing values
    filtered_df = filtered_df.dropna()

# Apply groupby and mean
    # averages = filtered_df.groupby('Hostname').mean()

    
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
    
    # Save the result to a new CSV file
    result_df.to_csv('specific_hostnames_summary.csv')

# Example usage
file_path = '414_421.csv'
output_directory = '.'  # Use the current directory, change as needed
EU_CP_Hostname = input("Enter the list of Hostnames of EU CP cars for the needed date separated by commas: ").split(',')
EU_HNP_Hostname = input("Enter the list of Hostnames of EU HNP cars for the needed date separated by commas: ").split(',')

output_file_data_eu_cp, output_file_data_eu_hnp = process_data_EU(file_path, output_directory, EU_CP_Hostname, EU_HNP_Hostname)
output_files_CN = process_data_CN(file_path, output_directory)

generate_summary({'EU_CP': output_file_data_eu_cp, 'EU_HNP': output_file_data_eu_hnp, **output_files_CN})
process_specific_hostnames(file_path)