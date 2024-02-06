from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, LongType, TimestampType
from pyspark.sql.functions import *
from pyspark.sql.types import *
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

KAFKA_BOOTSTRAP_SERVERS = "master:9092"
KAFKA_TOPIC = "traffic_sensor"
INFLUXDB_TOKEN = "BDcVwn_3NJbnoWqqWcx62pyDSB3mhvpQih1mkYqt59jsJUEKEZa2MY8zlDNNJk7wCbgZSYtuMNqxz0T-Na35qQ=="
INFLUXDB_ORG = "my-org"
INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_BUCKET="my-bucket"
SCHEMA = StructType([
    StructField("count", LongType(), True),
    StructField("time", TimestampType(), True)
])

class InfluxDBWriter:
    def __init__(self, bucket, measurement):
        self.bucket = bucket
        self.measurement = measurement
        self.client = InfluxDBClient(url=INFLUXDB_URL, 
                    token=INFLUXDB_TOKEN,
                    org=INFLUXDB_ORG
                    )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.is_connected()

    def open(self, partition_id, epoch_id):
        print("Opened %d, %d" % (partition_id, epoch_id))
        return True

    # def process(self, row):
    def process(self, timestamp, tags, fields):
        point = Point(self.measurement)

        for key, value in tags.items():
            point.tag(key, value)

        # Add fields to the Point
        for key, value in fields.items():
            point.field(key, value)

        point.time(timestamp, WritePrecision.S)
        self.write_api.write(bucket=self.bucket, record=point)

    def close(self, error):
        self.write_api.__del__()
        self.client.__del__()
        print("Closed with error: %s" % str(error))

    def row_to_line_protocol(measurement, tags, fields, timestamp):
        """
        Convert a row into InfluxDB Line Protocol format.

        Args:
        - measurement (str): The measurement name.
        - tags (dict): A dictionary of tag key-value pairs.
        - fields (dict): A dictionary of field key-value pairs.
        - timestamp (int): The timestamp in Unix epoch format (milliseconds).

        Returns:
        - str: The InfluxDB Line Protocol string.
        """
        # Convert tags to a comma-separated string
        tag_str = ",".join([f"{k}={v}" for k, v in tags.items()])

        # Convert fields to a comma-separated string
        field_str = ",".join([f"{k}={v}" for k, v in fields.items()])

        # Combine measurement, tags, fields, and timestamp
        line_protocol = f"{measurement}{',' + tag_str if tag_str else ''} {field_str} {timestamp}"

        return line_protocol
    
    def is_connected(self):
        try:
            # Attempt a simple query to test the connection
            query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1m)'
            self.client.query_api().query_data_frame(query)
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

if __name__ == '__main__':

    spark = SparkSession.builder.appName("read_traffic_sensor").getOrCreate()

    # Reduce logging
    spark.sparkContext.setLogLevel("WARN")
    influxdb_writer = InfluxDBWriter(INFLUXDB_BUCKET, "traffic_final")


    df = spark \
        .readStream.format("kafka")\
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)\
        .option("subscribe", KAFKA_TOPIC)\
        .option("startingOffsets", "earliest")\
        .load()
    
    trafficDataframe = df.select(col("value").cast("string").alias("data"))

    inputStream = trafficDataframe.selectExpr("CAST(data as STRING)")

    trafficDataframe = inputStream.select(from_json(col("data"), SCHEMA).alias("traffic"))

    def process_batch(batch_df, batch_id):
        realtimeTraffic = batch_df.select("traffic.*")
        for row in realtimeTraffic.collect():
            timestamp = row["time"]
            tags = {}
            fields = {
                "count": row['count'],
            }
            influxdb_writer.process(timestamp, tags, fields)

    query = trafficDataframe \
        .writeStream \
        .foreachBatch(process_batch) \
        .option("truncate", "false")\
        .outputMode("update") \
        .start()

    query.awaitTermination()

