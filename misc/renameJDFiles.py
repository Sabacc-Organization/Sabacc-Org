import os

def replace_spaces_in_filenames(directory):
    # Loop through all files in the specified directory
    for filename in os.listdir(directory):
        # Check if the filename contains a space
        if ' ' in filename:
            # Create the new filename by replacing spaces with underscores
            new_filename = filename.replace(' ', '_')
            # Construct full file paths
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_filename)
            # Rename the file
            os.rename(old_file, new_file)
            print(f'Renamed: {old_file} -> {new_file}')

# Replace 'your_directory_path' with the path to your directory
replace_spaces_in_filenames('client/static/images/cards/corellian/jacob-densford')
