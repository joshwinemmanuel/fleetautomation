import pandas as pd
from datetime import datetime

def process_data(file_path, output_directory, EU_Plate_Number):
    df = pd.read_csv(file_path, low_memory=False)

    # Exclude rows with zeros in specified columns for each category
    columns_to_exclude_zeros = ['Autonomous driving mileage (km)', 'Manual driving mileage (km)',
                                'Automatic driving time (min)', 'Manual driving time (min)',
                                'Total driving time (min)', 'Takeover', 'D gear time (min)']
    
    # Filter data for categories 'CP' and 'HNP' for CN
    filtered_cn_df = df[df['Primary Category'].isin(['CP', 'HNP'])]


    # Apply additional filters for CN where the value in 'Total mileage (km)' is greater than 20
    # and 'Autonomous driving mileage (km)' is greater than 10
    filtered_cn_df = filtered_cn_df[(filtered_cn_df['Total mileage (km)'] > 20) &
                                    (filtered_cn_df['Autonomous driving mileage (km)'] > 10)]

    # Exclude rows with zeros in specified columns
    for col in columns_to_exclude_zeros:
        filtered_cn_df = filtered_cn_df[filtered_cn_df[col] != 0]

    # Filter out specific cities for CN
    excluded_cn_cities = ['斯图加特', '法兰克福', '密西根州']
    filtered_cn_df = filtered_cn_df[~filtered_cn_df['Car City'].isin(excluded_cn_cities)]

    # Filter data for categories 'CP' and 'HNP' for EU
    filtered_eu_df = df[df['Primary Category'].isin(['CP', 'HNP', 'Others'])]

    # Apply additional filters for EU where the value in 'Total mileage (km)' is greater than 20
    # and 'Autonomous driving mileage (km)' is greater than 10
    filtered_eu_df = filtered_eu_df[(filtered_eu_df['Total mileage (km)'] > 20) &
                                    (filtered_eu_df['Autonomous driving mileage (km)'] > 10)]

    # Exclude rows with zeros in specified columns
    for col in columns_to_exclude_zeros:
        filtered_eu_df = filtered_eu_df[filtered_eu_df[col] != 0]

    # Filter out specific plate numbers for EU
    filtered_eu_df = filtered_eu_df[filtered_eu_df['Plate number'].isin(EU_Plate_Number)]

    # Generate a unique output file name with current date and time
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save the filtered CN CP and CN HNP data to new CSV files
    output_files = {}
    for category in ['CP', 'HNP']:
        output_file_data_cn = f"{output_directory}/output_data_CN_{category}_{current_datetime}.csv"
        category_cn_df = filtered_cn_df[filtered_cn_df['Primary Category'] == category]
        category_cn_df.to_csv(output_file_data_cn, index=False)
        output_files[category] = output_file_data_cn

    # Save the filtered EU CP data to a new CSV file
    output_file_data_eu_cp = f"{output_directory}/output_data_EU_CP_{current_datetime}.csv"
    category_eu_cp_df = filtered_eu_df[filtered_eu_df['Primary Category'] == 'CP']
    category_eu_cp_df.to_csv(output_file_data_eu_cp, index=False)
    output_files['EU_CP'] = output_file_data_eu_cp

    # Combine EU HNP with Others data and save to a new CSV file
    combined_eu_hnp_others_df = filtered_eu_df[(filtered_eu_df['Primary Category'] == 'HNP') |
                                                (filtered_eu_df['Primary Category'] == 'Others')]
    output_file_data_eu_hnp_others = f"{output_directory}/output_data_EU_HNP_Others_{current_datetime}.csv"
    combined_eu_hnp_others_df.to_csv(output_file_data_eu_hnp_others, index=False)
    output_files['HNP_Others'] = output_file_data_eu_hnp_others
                
    return output_files

def generate_summary(output_files):
    try:
        # Initialize summary data with None for each category
        summary_data = {
            'EU-HNP': [None]*9,
            'CN-HNP': [None]*9,
            'EU-CP': [None]*9,
            'CN-CP': [None]*9,
        }

        # Read the CSV files if they exist and update summary data
        if 'EU_CP' in output_files:
            df_cp_eu = pd.read_csv(output_files['EU_CP'])
            numeric_cols_cp_eu = df_cp_eu.select_dtypes(include='number')
            averages_cp_eu = numeric_cols_cp_eu.mean()

            # Calculate additional values only if DataFrame is not empty
            if not averages_cp_eu.empty:
                averages_cp_eu['Average Total driving time (hour)'] = averages_cp_eu['Total driving time (min)'] / 60
                averages_cp_eu['Average D gear time (hour)'] = averages_cp_eu['D gear time (min)'] / 60
                averages_cp_eu['D/total time'] = averages_cp_eu['D gear time (min)'] / averages_cp_eu['Total driving time (min)'] * 100
                averages_cp_eu['Auto/total km'] = (averages_cp_eu['Autonomous driving mileage (km)'] / averages_cp_eu['Total mileage (km)']) * 100

                summary_data['EU-CP'] = [
                    averages_cp_eu['Total driving time (min)'],
                    averages_cp_eu['Average Total driving time (hour)'],
                    averages_cp_eu['D gear time (min)'],
                    averages_cp_eu['Average D gear time (hour)'],
                    averages_cp_eu['D/total time'],
                    averages_cp_eu['Total mileage (km)'],
                    averages_cp_eu['Autonomous driving mileage (km)'],
                    averages_cp_eu['Auto/total km'],
                    averages_cp_eu['Takeover']
                ]

        if 'HNP_Others' in output_files:
            df_hnp_others_eu = pd.read_csv(output_files['HNP_Others'])
            numeric_cols_hnp_others_eu = df_hnp_others_eu.select_dtypes(include='number')
            averages_hnp_others_eu = numeric_cols_hnp_others_eu.mean()

            if not averages_hnp_others_eu.empty:
                averages_hnp_others_eu['Average Total driving time (hour)'] = averages_hnp_others_eu['Total driving time (min)'] / 60
                averages_hnp_others_eu['Average D gear time (hour)'] = averages_hnp_others_eu['D gear time (min)'] / 60
                averages_hnp_others_eu['D/total time'] = averages_hnp_others_eu['D gear time (min)'] / averages_hnp_others_eu['Total driving time (min)'] * 100
                averages_hnp_others_eu['Auto/total km'] = (averages_hnp_others_eu['Autonomous driving mileage (km)'] / averages_hnp_others_eu['Total mileage (km)']) * 100

                summary_data['EU-HNP'] = [
                    averages_hnp_others_eu['Total driving time (min)'],
                    averages_hnp_others_eu['Average Total driving time (hour)'],
                    averages_hnp_others_eu['D gear time (min)'],
                    averages_hnp_others_eu['Average D gear time (hour)'],
                    averages_hnp_others_eu['D/total time'],
                    averages_hnp_others_eu['Total mileage (km)'],
                    averages_hnp_others_eu['Autonomous driving mileage (km)'],
                    averages_hnp_others_eu['Auto/total km'],
                    averages_hnp_others_eu['Takeover']
                ]

        if 'CP' in output_files:
            df_cp_cn = pd.read_csv(output_files['CP'])
            numeric_cols_cp_cn = df_cp_cn.select_dtypes(include='number')
            averages_cp_cn = numeric_cols_cp_cn.mean()

            if not averages_cp_cn.empty:
                averages_cp_cn['Average Total driving time (hour)'] = averages_cp_cn['Total driving time (min)'] / 60
                averages_cp_cn['Average D gear time (hour)'] = averages_cp_cn['D gear time (min)'] / 60
                averages_cp_cn['D/total time'] = averages_cp_cn['D gear time (min)'] / averages_cp_cn['Total driving time (min)'] * 100
                averages_cp_cn['Auto/total km'] = (averages_cp_cn['Autonomous driving mileage (km)'] / averages_cp_cn['Total mileage (km)']) * 100

                summary_data['CN-CP'] = [
                    averages_cp_cn['Total driving time (min)'],
                    averages_cp_cn['Average Total driving time (hour)'],
                    averages_cp_cn['D gear time (min)'],
                    averages_cp_cn['Average D gear time (hour)'],
                    averages_cp_cn['D/total time'],
                    averages_cp_cn['Total mileage (km)'],
                    averages_cp_cn['Autonomous driving mileage (km)'],
                    averages_cp_cn['Auto/total km'],
                    averages_cp_cn['Takeover']
                ]

        if 'HNP' in output_files:
            df_hnp_cn = pd.read_csv(output_files['HNP'])
            numeric_cols_hnp_cn = df_hnp_cn.select_dtypes(include='number')
            averages_hnp_cn = numeric_cols_hnp_cn.mean()

            if not averages_hnp_cn.empty:
                averages_hnp_cn['Average Total driving time (hour)'] = averages_hnp_cn['Total driving time (min)'] / 60
                averages_hnp_cn['Average D gear time (hour)'] = averages_hnp_cn['D gear time (min)'] / 60
                averages_hnp_cn['D/total time'] = averages_hnp_cn['D gear time (min)'] / averages_hnp_cn['Total driving time (min)'] * 100
                averages_hnp_cn['Auto/total km'] = (averages_hnp_cn['Autonomous driving mileage (km)'] / averages_hnp_cn['Total mileage (km)']) * 100

                summary_data['CN-HNP'] = [
                    averages_hnp_cn['Total driving time (min)'],
                    averages_hnp_cn['Average Total driving time (hour)'],
                    averages_hnp_cn['D gear time (min)'],
                    averages_hnp_cn['Average D gear time (hour)'],
                    averages_hnp_cn['D/total time'],
                    averages_hnp_cn['Total mileage (km)'],
                    averages_hnp_cn['Autonomous driving mileage (km)'],
                    averages_hnp_cn['Auto/total km'],
                    averages_hnp_cn['Takeover']
                ]

        # Create a DataFrame from the summary data
        summary_df = pd.DataFrame(summary_data, index=[
            'average total online time (min)',
            'average total online time (hr)',
            'average total D drive time (min)',
            'average total D drive time (hr)',
            'D/total time (%)',
            'average total km/day',
            'average automatic km/day',
            'auto/total km (%)',
            'average takeover No.'
        ])

        # Write the summary DataFrame to a CSV file
        summary_df.to_csv('summary.csv', index=True)

    except Exception as e:
        print(f"An error occurred: {e}")



# Example usage
file_path = '0107-0114.csv'
columns_values = [('Primary Category', ['CP', 'HNP', 'Others']), ('Car City', [])]  # Empty list to include all cities
output_directory = '.'  # Use the current directory, change as needed
columns_to_average = ['Autonomous driving mileage (km)', 'Manual driving mileage (km)', 'Total mileage (km)',
                      'Automatic driving time (min)', 'Manual driving time (min)', 'Total driving time (min)',
                      'Takeover', 'D gear time (min)']
EU_Plate_Number = input("Enter the list of plate numbers of cars for the needed date separated by commas: ").split(',')
output_files = process_data(file_path, output_directory, EU_Plate_Number)
generate_summary(output_files)
