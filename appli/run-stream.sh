cd /root/appli

spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1 src/streaming/read_traffic.py