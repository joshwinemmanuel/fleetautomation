import pandas as pd
from datetime import datetime

def process_and_calculate(file_path, columns_values, output_directory, columns_to_average):
    df = pd.read_csv(file_path, low_memory=False)

    # Initialize selected_data with the entire DataFrame
    selected_data = df.copy()

    # Initialize separate DataFrames for each category
    category_dfs = {}

    for column, column_values in columns_values:
        # Check if the column exists in the DataFrame
        if column not in df.columns:
            print(f"Error: Column '{column}' not found in the DataFrame.")
            return

        # Apply filtering to selected_data
        selected_data = selected_data[selected_data[column].isin(column_values)]

        # Store filtered DataFrames in a dictionary for each category
        for value in column_values:
            category_dfs[value] = selected_data[selected_data[column] == value].copy()

    # Exclude rows with zeros in specified columns for each category
    for col in columns_to_average:
        for category, category_df in category_dfs.items():
            category_dfs[category] = category_df[category_df[col] != 0]

    # Apply additional filters for rows where the value in 'Total mileage (km)' is greater than 20
    # and 'Autonomous driving mileage (km)' is greater than 10
    for category, category_df in category_dfs.items():
        category_dfs[category] = category_df[(category_df['Total mileage (km)'] > 20) &
                                             (category_df['Autonomous driving mileage (km)'] > 10)]

    # Define a specific order for columns
    specific_order = ['Total driving time (min)', 'Average Total driving time (hour)',
                      'D gear time (min)', 'Average D gear time (hour)', 'D/total time',
                      'Total mileage (km)', 'Autonomous driving mileage (km)', 'Auto/total km',
                      'Takeover']

    # Generate a unique output file name with current date and time
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Calculate averages and additional values for specified columns for 'CP' and 'HNP' excluding specified cities
    results_dict = {}
    for category, category_df in category_dfs.items():
        if category in ['CP', 'HNP']:
            # Additional filtering based on specified cities
            excluded_cities = ['斯图加特', '法兰克福', '密西根州']
            category_df_excluded_cities = category_df[~category_df['Car City'].isin(excluded_cities)]

            # Calculate averages for specified columns
            averages = category_df_excluded_cities[columns_to_average].mean()

            # Additional calculations
            averages['Average Total driving time (hour)'] = averages['Total driving time (min)'] / 60
            averages['Average D gear time (hour)'] = averages['D gear time (min)'] / 60
            averages['D/total time'] = averages['D gear time (min)'] / averages['Total driving time (min)'] * 100
            averages['Auto/total km'] = (averages['Autonomous driving mileage (km)'] / averages['Total mileage (km)']) * 100

            results_dict[category] = averages

            # Save the filtered DataFrame to the new CSV file for each category
            output_file_data = f"{output_directory}/output_data_{category}_{current_datetime}.csv"
            category_df_excluded_cities.to_csv(output_file_data, index=False)

    # Create DataFrames with averages and additional values and save them to new CSV files for each category
    for category, results in results_dict.items():
        output_file_results = f"{output_directory}/output_results_{category}_{current_datetime}.csv"
        results_df = pd.DataFrame(results, columns=['Values'])
        results_df = results_df.reindex(specific_order, axis=0)
        results_df.to_csv(output_file_results, index=True, header=True)

        # Print results in the specified order
        print(f"\nResults for '{category}' (excluding specified cities):")
        for col in specific_order:
            if col in results:
                if "Average" in col:
                    print(f"{col}: {results[col]}")
                else:
                    print(f"Average {col}: {results[col]}")

# Example usage
file_path = '20240325_221423.csv'
columns_values = [('Primary Category', ['CP', 'HNP']), ('Car City', [])]  # Empty list to include all cities
output_directory = '.'  # Use the current directory, change as needed
columns_to_average = ['Autonomous driving mileage (km)', 'Manual driving mileage (km)', 'Total mileage (km)',
                      'Automatic driving time (min)', 'Manual driving time (min)', 'Total driving time (min)',
                      'Takeover', 'D gear time (min)']
process_and_calculate(file_path, columns_values, output_directory, columns_to_average)
