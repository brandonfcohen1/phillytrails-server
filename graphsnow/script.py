from datetime import datetime
import requests
import json
import boto3
import os
import math
from slack_sdk import WebClient

slack_token = os.environ["SLACK"]
client = WebClient(token=slack_token)

s3_client = boto3.client('s3', aws_access_key_id=os.environ["AWS_ACCESS_KEY"],
                         aws_secret_access_key=os.environ["AWS_SECRET_KEY"])


def leading_zero(input):
    input = str(input)
    if len(input) == 1:
        return "0" + input
    else:
        return input


# Determine datestrings
today = datetime.today()
monthstring = leading_zero(today.year) + leading_zero(today.month)
datestring = leading_zero(today.year) + \
    leading_zero(today.month) + leading_zero(today.day)
timestring = leading_zero(str(math.floor(datetime.utcnow().hour/6)*6))


data_types = ["snowfall", "snowdensity", "snowdepth"]

for data_type in data_types:

    try:

        # geojson template
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        # Create URL
        url = "https://www.nohrsc.noaa.gov/nsa/discussions_text/National/" + \
            data_type + "/" + datestring[0:6] + \
            "/" + data_type + "_" + datestring + timestring + "_e.txt"

        # Download file and remove first/last row
        downloadfile = requests.get(url)
        row_list = downloadfile.text.split("\n")
        row_list = row_list[1:-1]

        # Loop through rows and add to geojson
        for row in row_list:
            row_ = row.split("|")
            try:
                if data_type == "snowfall":
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(row_[3]), float(row_[2])]
                        },
                        "properties": {
                            "name": row_[1],
                            "elevation": row_[4],
                            "report_time_utc": row_[6],
                            "amount": row_[7],
                            "units": row_[8],
                            "duration": row_[9],
                            "durationunits": row_[10],
                        }
                    }
                else:
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(row_[3]), float(row_[2])]
                        },
                        "properties": {
                            "name": row_[1],
                            "elevation": row_[4],
                            "report_time_utc": row_[6],
                            "amount": row_[7],
                            "units": row_[8],
                        }
                    }
                geojson["features"].append(feature)

            except:
                print(row_)

        filename = data_type + ".json"

        # dump to json file
        with open("tmp/"+filename, "w") as f:
            json.dump(geojson, f)

        # post to s3
        response = s3_client.upload_file(
            "tmp/"+filename, "graphsnowgeojson", filename, ExtraArgs={'ACL': 'public-read'})

        response = client.chat_postMessage(
            channel="status",
            type="text",
            text="loaded data for " + data_type
        )

    except Exception as e:
        response = client.chat_postMessage(
            channel="status",
            type="text",
            text="failure for " + data_type + "\n\n" + str(e)
        )
