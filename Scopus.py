import requests
import csv
import json

apiKey = 'a181fe4fe173334fd2e7d4be48b2752f'
query = 'machine learning'  # Example search query

params = {
    'apiKey': apiKey,
    'query': "med",
    'count': 10,  # Return 3 results
    'httpAccess': 'application/json',
    'start' : 0,
}
column_names = ["universityName" , "cityName" , "countryName"]

Allresult = []
for startIndex in range(0,5000,10):
  params['start'] = startIndex
  response = requests.get('https://api.elsevier.com/content/search/scopus', params=params)
  
  if (response.status_code == 200 ):
      data = response.json()
      print(startIndex)
      search_results = data['search-results']
      nextLink = search_results["link"][2]['@href']
      entry = search_results['entry']
      for e in entry:
        Allresult.append(e)
  else:
      print('already reach 5000')
      break
print("Done!")

# File path to save the JSON file
json_file_path = "array_data.json"

# Save the array data to a JSON file
with open(json_file_path, 'w') as json_file:
    json.dump(Allresult, json_file, indent=4)

print("JSON data has been saved to:", json_file_path)

csvData = [] #data to tranform to csv

# Open the JSON file
with open('array_data.json', 'r') as array_data:
    # Load JSON data from the file
    data = json.load(array_data)
    for e in data:
        try:
            sample = e.get('affiliation', [{}])[0]  # Get the first affiliation or an empty dictionary
            universityName = sample.get('affilname', '')  # extract university's name
            cityName = sample.get('affiliation-city', '')  # extract city's name
            countryName = sample.get('affiliation-country', '')  # extract country's name
            result = [universityName, cityName, countryName]
            print(result)
            csvData.append(result)  # append result to csvData
        except Exception as e:
            print(f"Error processing entry: {e}")

with open('result_csv.csv', 'w', newline='') as csvfile:
    # Create a CSV writer object
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(column_names)
    # Write multiple rows of string data
    csv_writer.writerows(csvData)

print("String data written to result_csv.csv")