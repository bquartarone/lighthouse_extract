import requests
from datetime import datetime
import uuid
import boto3
from io import StringIO
import csv
import os

# s3 keys
ACCESS = os.environ['ACCESS']
SECRET = os.environ['SECRET']

# s3 information
BUCKET = os.environ['BUCKET']
FOLDER = os.environ['FOLDER']

# general information
urls = ["https://www.viagem.ciclic.com.br", "https://www.ciclic.com.br"]
timeNow = datetime.now()
strtimeNow = timeNow.strftime("%d-%m-%y-%HH-%MM")
randomUuid = uuid.uuid1()
struuid = str(randomUuid)

new_file = f'{strtimeNow}-{struuid}'
HEADERS = ["Created_time", "URL", "Performance Score", "FCP Score", "FCP Value",
           "FMP Score", "FMP Value", "Speed Index Score", "Speed Index Value",
           "TI Score", "TI Value", "File Name"]


def s3_connector():
    connector = boto3.client(
        "s3", aws_access_key_id=ACCESS, aws_secret_access_key=SECRET
    )
    return connector


def load(file):
    print("LOAD_COMEÇOU")
    s3 = s3_connector()
    key = f"{FOLDER}{new_file}.csv"
    s3.put_object(Bucket=BUCKET, Key=key, Body=file.getvalue().encode("utf-8"))
    print("ARQUIVO UPADO")


def generate_report(urls):
    global file
    file = StringIO()
    writer = csv.DictWriter(file, HEADERS, delimiter=",", lineterminator="\n")
    writer.writeheader()

    for website in urls:
        print(urls[1])
        chamada = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={website}&strategy=mobile'
        print(f'Requesting {website}...')
        r = requests.get(chamada)
        final = r.json()

        performanceScore = final['lighthouseResult']['categories']['performance']['score']

        fcpScore = final['lighthouseResult']['audits']['first-contentful-paint']['score']

        fcpValue = final['lighthouseResult']['audits']['first-contentful-paint']['displayValue']
        fcpValue = fcpValue.split()
        fcpValue = fcpValue[0]

        fmpScore = final['lighthouseResult']['audits']['first-meaningful-paint']['score']

        fmpValue = final['lighthouseResult']['audits']['first-meaningful-paint']['displayValue']
        fmpValue = fmpValue.split()
        fmpValue = fmpValue[0]

        speedIndexScore = final['lighthouseResult']['audits']['speed-index']['score']

        speedIndexValue = final['lighthouseResult']['audits']['speed-index']['displayValue']
        speedIndexValue = speedIndexValue.split()
        speedIndexValue = speedIndexValue[0]

        timeToInteractiveScore = final['lighthouseResult']['audits']['interactive']['score']

        timeToInteractiveValue = final['lighthouseResult']['audits']['interactive']['displayValue']
        timeToInteractiveValue = timeToInteractiveValue.split()
        timeToInteractiveValue = timeToInteractiveValue[0]
        row = {HEADERS[0]: strtimeNow, HEADERS[1]: website, HEADERS[2]: performanceScore,
               HEADERS[3]: fcpScore, HEADERS[4]: fcpValue,
               HEADERS[5]: fmpScore, HEADERS[6]: fmpValue, HEADERS[7]: speedIndexScore,
               HEADERS[8]: speedIndexValue,
               HEADERS[9]: timeToInteractiveScore, HEADERS[10]: timeToInteractiveValue, HEADERS[11]: new_file}

        try:
            writer.writerow(row)
            print("CSV GERADO")
        except KeyError:
            print(f'<KeyError> One or more keys not found.')
    return file



def handler(event, context):
    load(generate_report(urls))
    return f'File {new_file} uploaded!'


