# README

## Setup Instructions

### Step 1: Clone or Pull Repository

Clone this repository to your local machine or pull the latest changes if you already have it cloned.

### Step 2: Open Script

Open the file named "CN_EU_CP_HNP_v4.5.py" in your preferred code editor.

### Step 3: Configure Weeks Details

Open the file named "filter_data.csv" and enter the details for the weeks using any spreadsheet application. You can use the "Fleet Report" sheet in Feishu or any other spreadsheet application.

### Step 4: Replace Input Data

Replace the placeholder "inputfromfmp.csv" with the actual CSV file downloaded from FMP (Fleet Management Platform) or any other data source. Update the following line in the script accordingly:

```python
data_df = pd.read_csv('inputfromfmp.csv')
```

### Step 5: Execute the Script

Execute the script to perform the fleet data analysis.

### Step 6: Copy Results to Feishu Sheet

Copy the results generated in "summary.csv" and "eu_summary.csv" to the "Fleet Operations KANBAN Board" sheet in Feishu or any other desired location.

## Docker Instructions (Optional)

If you encounter dependency version issues, you can use Docker to ensure consistent execution environment.

### Step 1: Run Docker Container

Navigate to the repository folder and run the following command:

```
docker run --rm -it -v .:/app joshiwn/fleetautomation:v1.0
```

This command will pull the Docker image and then you can execute the script within the container, providing isolation from host dependencies.
