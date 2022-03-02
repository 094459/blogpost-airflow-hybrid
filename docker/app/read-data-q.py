from copy import copy
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import sys
import csv
import boto3
import json
import socket
def query_with_fetchone(query2run,secret,region):
    try:
        #Using local config file
        #dbconfig = read_db_config()
        #conn = MySQLConnection(**dbconfig)
        # When using AWS Secrets Manager 
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
        
        print("Connecting to ",str(hs)," database ", str(db), " as user ", str(un))
        print("Database host IP is :", socket.gethostbyname(hs))

        conn = MySQLConnection(user=un, password=pw, host=hs, database=db)
        cursor = conn.cursor()
        #query="select * from customers WHERE location = '{country}' AND (date BETWEEN '{start}' AND '{end}')".format(country=country,start=start,end=end)
        query=query2run
        print("Query is", str(query))
        #cursor.execute("select * from customers WHERE location = '{country}' AND (date BETWEEN '{start}' AND '{end}')".format(country=country,start=start,end=end))
        cursor.execute(query)
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
        raise SystemExit(f"Usage: {sys.argv[0]} <s3 bucket><s3 file><query><secret><region>")
    s3bucket=sys.argv[1]
    s3folder=sys.argv[2]
    query2run=sys.argv[3]
    secret=sys.argv[4]
    region=sys.argv[5]
    query_with_fetchone(query2run,secret,region)
    upload_to_s3(s3bucket,s3folder,region)

    # demo command to test this from the cli
    # for Cloud based MySQL
    # python app/read-data-q.py ricsue-airflow-hybrid period1/temp.csv "select * from customers WHERE location = 'Poland' AND (date BETWEEN '2022-01-01 14:15:55' AND '2022-09-29 10:15:55')" rds-airflow-hybrid eu-west-2
    # for local/remote based MySQL
    # python app/read-data-q.py ricsue-airflow-hybrid period1/temp2.csv "select * from customers WHERE location = 'China' AND (date BETWEEN '2022-01-01 14:15:55' AND '2022-09-29 10:15:55')" localmysql-airflow-hybrid eu-west-2
    
