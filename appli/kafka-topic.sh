cd /root/kafka

bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic traffic_sensor

bin/kafka-topics.sh --create --replication-factor 1 --bootstrap-server localhost:9092 --topic traffic_sensor