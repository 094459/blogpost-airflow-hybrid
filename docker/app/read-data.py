from copy import copy
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import sys
import csv
import boto3
import json

def query_with_fetchone(country,secret,region,start,end):
    try:
        #Using local config file
        #dbconfig = read_db_config()
        #conn = MySQLConnection(**dbconfig)
        # When using AWS Secrets Manager 
        print(country)
        print(start)
        print(end)
        print(secret)
        print(region)
        secret_name = secret
        region_name = region
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        info=json.loads(get_secret_value_response['SecretString'])
        pw=info['password']
        un=info['username']
        hs=info['host']
        db=info['database']
        
        conn = MySQLConnection(user=un, password=pw, host=hs, database=db)
        cursor = conn.cursor()
        query="select * from customers WHERE location = '{country}' AND (date BETWEEN '{start}' AND '{end}')".format(country=country,start=start,end=end)
        print("Query is", str(query))
        cursor.execute("select * from customers WHERE location = '{country}' AND (date BETWEEN '{start}' AND '{end}')".format(country=country,start=start,end=end))

        records = cursor.fetchall()
        c = csv.writer(open("temp.csv","w"))
        c.writerows(records)
        print("Records exported:")
        for row in records:
            print(row[0],",",row[1],",",row[2],",",row[3],",",row[4],",",row[5], ",",row[6],",",row[7] )

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()
def upload_to_s3(s3bucket,s3folder,region):
    try:
        s3 = boto3.client('s3', region_name=region)
        s3.upload_file('temp.csv',s3bucket,s3folder)
    except FileNotFoundError:
        print("The file was not found")
        return False
    except Error as e:
        print(e)

if __name__ == '__main__':
    try:
        arg = sys.argv[2]
    except IndexError:
        raise SystemExit(f"Usage: {sys.argv[0]} <s3 bucket><s3 file><country><db><region><start time><end time><secret>")
    #s3bucket='ricsue-airflow-hybrid'
    #s3folder='period2/temp.csv' 
    s3bucket=sys.argv[1]
    s3folder=sys.argv[2]
    country=sys.argv[3]
    start=sys.argv[6]
    end=sys.argv[7]
    secret=sys.argv[4]
    region=sys.argv[5]
    query_with_fetchone(country,secret,region,start,end)
    upload_to_s3(s3bucket,s3folder,region)


    # demo command is
    # python app/read-data.py ricsue-airflow-hybrid period2/temp.csv China rds-airflow-hybrid eu-west-2 '2022-01-01 14:15:55' '2022-09-29 10:15:55' 