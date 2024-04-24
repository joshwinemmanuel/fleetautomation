import pandas as pd
from datetime import datetime

def process_and_calculate(file_path, columns_values, output_directory, columns_to_average, desired_hostnames):
    df = pd.read_csv(file_path, low_memory=False)

    # Initialize selected_data with the entire DataFrame
    selected_data = df.copy()

    # Apply filtering based on 'Hostname'
    selected_data = selected_data[selected_data['Hostname'].isin(desired_hostnames)]

    # Initialize separate DataFrame for the filtered data
    selected_data_filtered = selected_data.copy()

    # Exclude rows with zeros in specified columns
    for col in columns_to_average:
        selected_data_filtered = selected_data_filtered[selected_data_filtered[col] != 0]

    # Apply additional filters for rows where the value in 'Total mileage (km)' is greater than 20
    # and 'Autonomous driving mileage (km)' is greater than 10
    selected_data_filtered = selected_data_filtered[(selected_data_filtered['Total mileage (km)'] > 20) &
                                                     (selected_data_filtered['Autonomous driving mileage (km)'] > 10)]

    # Generate a unique output file name with the current date and time
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Calculate averages for specified columns
    averages = selected_data_filtered[columns_to_average].mean()

    # Define custom order and names for the columns
    custom_order_and_names = {
        'Total driving time (min)': 'Average Total driving time (min)',
        'D gear time (min)': 'Average D gear time (min)',
        'Total mileage (km)': 'Average Total mileage (km)',
        'Autonomous driving mileage (km)': 'Average Autonomous driving mileage (km)',
        'Takeover': 'Average Takeover'
    }

    # Redirect print statements to the existing CSV file
    output_file_averages = f"{output_directory}/output_averages.csv"
    with open(output_file_averages, 'a') as csv_file:
        # Calculate averages in the custom order with custom names
        csv_file.write("\nAverages of specified columns (excluding zeros):\n")
        for col in custom_order_and_names.keys():
            if col == 'Total driving time (min)':
                additional_calculation_3 = averages[col] / 60
                additional_calculation_3_percentage = additional_calculation_3 * 100
                csv_file.write(f"{custom_order_and_names[col]}:, {averages[col]}\n")
                csv_file.write(f"Average Total driving time (hour):, {additional_calculation_3}\n")

            elif col == 'D gear time (min)':
                additional_calculation_4 = averages[col] / 60
                csv_file.write(f"{custom_order_and_names[col]}:, {averages[col]}\n")
                csv_file.write(f"Average D gear time (hour):, {additional_calculation_4}\n")

                d_total_time_ratio = averages['D gear time (min)'] / averages['Total driving time (min)']
                d_total_time_percentage = d_total_time_ratio * 100
                csv_file.write(f"D/total time:, {d_total_time_percentage}\n")

            elif col == 'Autonomous driving mileage (km)':
                auto_total_km_ratio = averages['Autonomous driving mileage (km)'] / averages['Total mileage (km)'] * 100
                csv_file.write(f"{custom_order_and_names[col]}:, {averages[col]}\n")
                csv_file.write(f"auto/total km:, {auto_total_km_ratio}\n")

            else:
                csv_file.write(f"{custom_order_and_names[col]}:, {averages[col]}\n")

    # Save the filtered DataFrame to the new CSV file
    output_file_data = f"{output_directory}/output_data_{current_datetime}.csv"
    selected_data_filtered.to_csv(output_file_data, index=False)

# Example usage
file_path = '0131-0207.csv'
columns_values = []  # No specific columns to filter
output_directory = '.'  # Use the current directory, change as needed
columns_to_average = ['Autonomous driving mileage (km)', 'Manual driving mileage (km)', 'Total mileage (km)',
                      'Automatic driving time (min)', 'Manual driving time (min)', 'Total driving time (min)',
                      'Takeover', 'D gear time (min)']
desired_hostnames = ['S580-BBQS3685,S580-BBQS4364']  # Specify your desired hostnames here
process_and_calculate(file_path, columns_values, output_directory, columns_to_average, desired_hostnames)