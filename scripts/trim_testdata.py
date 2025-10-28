import os
import pandas as pd

# Load the data
input_file = '/Users/mdik/CoachAgent-1/testData.csv'

# Check if the file exists and is not empty
if os.path.exists(input_file) and os.path.getsize(input_file) > 0:
    data = pd.read_csv(input_file)

    # Trim the data to the first 25 rows
    trimmed_data = data.head(25)

    # Remove columns with all empty values
    trimmed_data = trimmed_data.dropna(axis=1, how='all')

    # Save the trimmed data
    output_file = 'testData_trimmed.csv'
    trimmed_data.to_csv(output_file, index=False)
else:
    print(f"Error: '{input_file}' does not exist or is empty.")