# %% [markdown]
# ## Hurricane Tracking Workflow
# This notebook selects trackpoints from a features class of trackpoints for a selected storm (season & name), creates a track line, and extracts US counties that intersect that trackline. 
# 
# Fall 2025
# sh808@duke.edu

# %%
#Import package
import arcpy
from pathlib import Path

#Set paths
raw_folder_path = Path.cwd().parent / 'data' / 'raw'
processed_folder_path = Path.cwd().parent / 'data' / 'processed'

#Arcpy environment settings
arcpy.env.workspace = str(raw_folder_path)
arcpy.env.overwriteOutput = True

# %%
#Set output csv file
output_csv = Path.cwd().parent / "data" / "processed" / "AffectedCounty.csv"

#Set model layers
ibtracs_NA_points = str(raw_folder_path /'IBTrACS_NA.shp')
usa_counties = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Counties_Generalized_Boundaries/FeatureServer/0'
storm_track_points =  "memory\\track_points"
storm_track_line = "memory\\Tracklines"

#%%
#Create dictionary of storm names for each season
storm_dict = {}

#Loop through each season
for storm_season in range(2000,2004):

    #Create a list to hold storm names for the season
    storm_names = []

    #Create a list of storm names for a given year
    cursor = arcpy.da.SearchCursor(
        in_table=ibtracs_NA_points,
        where_clause=f'SEASON = {storm_season}',
        field_names=['NAME']
    )

    #Iterate through rows in cursor
    for row in cursor:
        #Get the storm name
        storm_name = row[0]
        if not storm_name in storm_names and storm_name != 'UNAMED':
            storm_names.append(storm_name)


    del(cursor)
    
    storm_dict[storm_season] = storm_names

# %% [markdown]
# #### Select point features corresponding to a specific storm (season & name)

#Create the file object through the output csv
#out_file = open(output_csv, 'w')

#Write header line
#out_file.write("Storm_Season, Counties_Impacted\n")

#Iterate through each season
for storm_season in storm_dict.keys():

    #Get the list of storms in the season
    storm_names  = storm_dict[storm_season]

    #Iterate through storm names
    for storm_name in storm_names:

        #Select points for a given storm
        arcpy.analysis.Select(
            in_features=ibtracs_NA_points, 
            out_feature_class=storm_track_points, 
            where_clause=f"SEASON = {storm_season} And NAME = '{storm_name}'"
        )

        #Connect point to a track line
        arcpy.management.PointsToLine(
            Input_Features=storm_track_points,
            Output_Feature_Class=storm_track_line,
            Sort_Field='ISO_TIME'
        )

        #Select intersecting counties
        select_output = arcpy.management.SelectLayerByLocation(
            in_layer=usa_counties, 
            overlap_type="INTERSECT", 
            select_features=storm_track_line, 
            )
        select_result = select_output.getOutput(0)

        #Count the selected counties
        county_count = int(arcpy.management.GetCount(select_result).getOutput(0))
        print(storm_season, storm_name, county_count)


  

# %%
