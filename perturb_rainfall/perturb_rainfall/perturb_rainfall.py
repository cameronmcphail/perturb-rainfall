import os
import csv

def get_locations():
    locations = ["belair", "cgardens", "clarendon", "hahndorf", "hvalley", "mclaren", "myponga", "unley"]
    return locations

def get_years():
    years = ["2025", "2030", "2035", "2040", "2045", "2050", "2055", "2060", "2065", "2070", "2075", "2080", "2085", "2090"]
    return years

def get_time_periods():
    time_periods = ["annual", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    return time_periods

class rainData:
    def __init__(self, day, month, year, rain):
        self.day = day
        self.month = month  
        self.year = year
        self.rain = rain

class rainfallSeries:
    def __init__(self, location, name, rainfall):
        self.location = location
        self.name = name
        self.rainfall = rainfall

def read_historical_rainfall(root_dir):
    all_filepaths = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".rai"):
                 all_filepaths.append(os.path.join(root, file))
    locations = get_locations()
    historical_rainfall = []
    for location in locations:
        for filepath in all_filepaths:
            path, filename = os.path.split(filepath)
            if filename == location + ".rai":
                with open(filepath) as csvfile:
                    str_data = csv.reader(csvfile, delimiter='\t')
                    file_data = []
                    for row in str_data:
                        file_data.append(rainData(row[0], row[1], row[2], row[3]))
                    historical_rainfall.append(rainfallSeries(location, "historical", file_data))
    return historical_rainfall

def find_all_projections(root_dir, endWith=".csv"):
    all_projections = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(endWith):
                 all_projections.append(os.path.join(root, file))
    return all_projections

def filter_historical_data(historical_data, first_year, final_year):
    new_historical_data = []
    for location in historical_data:
        location_data = []
        for row in location.rainfall:
            if int(row.year) >= first_year and int(row.year) <= final_year:
                location_data.append(row)
        new_historical_data.append(rainfallSeries(location.location, location.name, location_data))
    return new_historical_data

class projection:
    def __init__(self, filepath, row, column, change):
        self.location = self.get_location(filepath)
        self.projection_name = self.get_projection_name(filepath)
        self.time_period = get_time_periods()[row]
        self.year = get_years()[column]
        self.change = change
        x=5
    def get_location(self, filepath):
        path, filename = os.path.split(filepath)
        underscore_position = filename.find('_')
        location = filename[:underscore_position]
        return location
    def get_projection_name(self, filepath):
        path, filename = os.path.split(filepath)
        projection_position = filename.find('_') + 1
        projection_name = filename[projection_position:-4]
        return projection_name

def read_projections(projections_filepaths):
    locations = get_locations()
    years = get_years()
    projections_data = []
    for filepath in projections_filepaths:
        with open(filepath) as csvfile:
            str_data = csv.reader(csvfile)
            counter = 0
            for row in str_data:
                if counter > 0:
                    for year_idx in range(len(years)):
                        projections_data.append(projection(filepath, counter - 1, year_idx, row[year_idx + 1]))
                counter = counter + 1
    return projections_data

def perturb_rainfall(historical_data, rainfall_projections_filepaths, rainfall_projections_data, output_dir):
    locations = get_locations()
    years = get_years()
    time_periods = get_time_periods()
    counter = 0
    reportingNum = 20
    reporting = [x / reportingNum for x in range(1, reportingNum + 1)]
    for fileIdx, projection_filepath in enumerate(rainfall_projections_filepaths):
        completion = fileIdx / len(rainfall_projections_filepaths)
        if completion > reporting[counter]:
            print('\t' + str(reporting[counter] * 100) + '% complete.')
            counter += 1
        path, filename = os.path.split(projection_filepath)
        underscore_position = filename.find('_')
        projection_location = filename[:underscore_position]
        projection_name = filename[underscore_position+1:-4]
        for data in historical_data:
            if data.location == projection_location:
                for year in years:
                    for rainfall_projection in rainfall_projections_data:
                        if (projection_location == rainfall_projection.location
                            and projection_name == rainfall_projection.projection_name
                            and year == rainfall_projection.year
                            and rainfall_projection.time_period == 'annual'):
                            rainfall = [
                                rainData(row.day, row.month, row.year, str(float(row.rain) * (1 + float(rainfall_projection.change)/100)))
                                for row in data.rainfall
                            ]
                            #for row in data.rainfall:
                            #    if rainfall_projection.projection_name == 'rcp_2.6_bcc-csm1-1-m' and row.year == '1986' and row.month == '1' and row.day == '14':
                            #        temp3 = (float(row.rain) * (1 + float(rainfall_projection.change)/100))
                            #        temp3
                            #    row.rain = str(float(row.rain) * (1 + float(rainfall_projection.change)/100)) # annual change
                            break
                    timeSeries = rainfallSeries(projection_location, projection_name + '_' + year, rainfall)
                    write_perturbed_data(output_dir, timeSeries)
                break

def ensure_directory_exists(directory):
    path = os.path.dirname(directory)
    if not os.path.exists(path):
        os.makedirs(path)

def write_perturbed_data(output_dir, data):
    #for data in perturbed_data:
    #    filepath = output_dir + data.location + '_' + data.name + '.rai'
    #    ensure_directory_exists(filepath)
    #    output_str = ""
    #    for row in data.rainfall:
    #        output_str = output_str + row.day + "\t" + row.month + "\t" + row.year + "\t" + row.rain + "\n"
    #    file = open(filepath, mode='w')
    #    file.write(output_str)
    #    file.close()
    filepath = output_dir + data.location + '_' + data.name + '.rai'
    ensure_directory_exists(filepath)
    output_str = ""
    for row in data.rainfall:
        output_str = output_str + row.day + "\t" + row.month + "\t" + row.year + "\t" + row.rain + "\n"
    output_str += "1\t1\t2006\t0.0\n2\t1\t2006\t0.0\n3\t1\t2006\t0.0\n"
    file = open(filepath, mode='w')
    file.write(output_str)
    file.close()

def addExtraDay(dir):
    filepaths = find_all_projections(dir, '.rai')
    extraDayStr = "1\t1\t2006\t0.0\n2\t1\t2006\t0.0\n3\t1\t2006\t0.0\n"
    for filepath in filepaths:
        with open(filepath, "a") as myfile:
            myfile.write(extraDayStr)

if __name__ == "__main__":
    historical_dir = "D:\\Dropbox\\_PhD\\Historical Data\\raindata\\"
    rainfall_projections_dir = "D:\\Dropbox\\_PhD\\Climate Change Projections\\Restructured Data\\rainfall\\Complete Data\\"
    evapotranspiration_projections_dir = "D:\\Dropbox\\_PhD\\Climate Change Projections\\Restructured Data\\evapotranspiration\\Complete Data\\"
    first_year = 1986
    final_year = 2005
    output_dir = "D:\\Dropbox\\_PhD\\Climate Change Projections\\Annual Perturbed Data\\"

    print('Reading historical data...')
    historical_rainfall = read_historical_rainfall(historical_dir)
    
    print('Filtering historical data to the years ' + str(first_year) + '-' + str(final_year))
    filtered_historical_rainfall = filter_historical_data(historical_rainfall, first_year, final_year)

    print('Finding Projections...')
    all_rainfall_projections = find_all_projections(rainfall_projections_dir)
    #all_evapotranspiration_projections = find_all_projections(evapotranspiration_projections_dir)
    #if len(all_rainfall_projections) != len(all_evapotranspiration_projections):
    #    print('Error: ' + str(len(all_rainfall_projections)) + ' rainfall projections found and ' + str(len(all_evapotranspiration_projections)) + ' evapotranspiration projections found.')
    #else:
    print(str(len(all_rainfall_projections)) + ' projections found.')

    print('Reading projections data...')
    rainfall_projections_data = read_projections(all_rainfall_projections) # [projection][time-period][year]

    print('Perturbing historical data...')
    perturbed_rainfall = perturb_rainfall(filtered_historical_rainfall, all_rainfall_projections, rainfall_projections_data, output_dir)
