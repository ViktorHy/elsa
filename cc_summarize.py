import glob
import os
import re
SEPARATOR = ","

def read_results_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

        # Initialize storage for current file
        metadata = {}
        assay_results = {}

        # Control flags
        metadata_section = True
        assay_section = False

        for line in lines:
            line = line.strip()

            # Stop processing if "Report Interpretation" is found
            if "Report Interpretation" in line:
                break  

            # Detect section change
            if re.match(r"^-+$", line):  # Matches lines of dashes
                metadata_section = False
                assay_section = True
                continue

            # Parse metadata section
            if metadata_section and ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                metadata[key] = value if value else None  # Store empty values as None

            # Parse assay results section
            elif assay_section and "," in line:
                parts = line.split(",")
                assay_name = parts[0].strip()
                result = parts[1].strip()
                flag = parts[2].strip() if len(parts) > 2 else ""
                ref_range = parts[3].strip() if len(parts) > 3 else ""
                unit = parts[4].strip() if len(parts) > 4 else ""

                assay_results[assay_name] = {
                    "Result": result,
                    "Flag": flag if flag else None,
                    "Reference Range": ref_range if ref_range else None,
                    "Unit": unit if unit else None
                }
    return assay_results,metadata

def check_categories(all_results):
    """
    Check that all files in directory has been run on the same assay
    """
    _categories = []
    for file in all_results:
        categories = list(all_results[file]["Assay Results"].keys())
        categories.pop(0)
        if len(_categories) == 0:
            _categories = categories
        else:
            if _categories != categories:
                exit("Seems to samples with different panels in the mix of files")
    return _categories

def print_results(all_results):
    """
    Print results. Get categories dynamically from headers
    """
    print(f"ANIMAL_NAME,Medical_ID,SAMPLE_ID",end=SEPARATOR)
    categories = check_categories(all_results)
    print(SEPARATOR.join(categories))
    for file in all_results:
        print(all_results[file]["Metadata"]["ANIMAL NAME"].replace(",",""),end=SEPARATOR)
        print(all_results[file]["Metadata"]["Medical ID"].replace(",",""),end=SEPARATOR)
        print(all_results[file]["Metadata"]["SAMPLE ID"].replace(",",""),end=SEPARATOR)
        results = []
        for cat in categories:
            results.append(all_results[file]["Assay Results"][cat]["Result"].replace(",",""))
        print(SEPARATOR.join(results))  
        

# Define the file pattern (modify as needed)
file_pattern = "UserReport*.csv"
all_results = {}
# Get list of all matching files
file_list = glob.glob(file_pattern)
for file in file_list:
    # Store results using the filename as the key
    assay_results,metadata = read_results_file(file)
    file_name = os.path.basename(file)  # Get only the filename, not the full path
    all_results[file_name] = {
        "Metadata": metadata,
        "Assay Results": assay_results
    }

print_results(all_results)    

# Print formatted dictionary
import pprint
#pprint.pprint(all_results)