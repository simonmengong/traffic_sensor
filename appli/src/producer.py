from kafka import KafkaProducer
import pyarrow.parquet as pq
from os import walk, path
import time
import pandas as pd
import json


producer = KafkaProducer(bootstrap_servers=['master:9092'])
TOPIC_NAME = "traffic_sensor"
FILE_PATH = "data/AGOSTO_2022_PARQUET_FINAL/"

def send_parquet_records(parquet_file=FILE_PATH):
        table = pq.read_table(parquet_file)
        records = table.to_pandas().set_index(pd.to_datetime(table["DATA HORA"]))
        records2 = records["DATA HORA"].groupby(pd.Grouper(freq='5Min')).count()
        for row, record in records2.items():
            message = json.dumps({"time": row.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z", "count": record})
            producer.send(TOPIC_NAME, value=message.encode(), key=None)
            time.sleep(0.5)




if __name__ == '__main__':
        filenames = next(walk(FILE_PATH), (None, None, []))[2]  # [] if no
        filenames = [f for f in filenames if f.split('.')[-1] == "parquet"]
        for f in filenames:
             send_parquet_records(FILE_PATH+f)
        producer.close()
