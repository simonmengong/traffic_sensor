
HERE=`pwd`
cd ..
HAGIHOME=`pwd`
cd $HERE

sudo docker network create haginet

#####################
CONTNAME=master
CONTCPU=1
sudo docker run --cpuset-cpus="$CONTCPU" --net haginet --name $CONTNAME --hostname $CONTNAME -p 50070:50070 -p 8080:8080 -d -v $HAGIHOME/jdk1.8.0_221:/root/java -v $HAGIHOME/hadoop-2.7.1:/root/hadoop -v $HAGIHOME/spark-3.3.4-bin-hadoop2:/root/spark -v $HAGIHOME/kafka_2.13-3.3.1:/root/kafka -v $HAGIHOME/appli:/root/appli server
#####################
CONTNAME=slave1
CONTCPU=2
sudo docker run --cpuset-cpus="$CONTCPU" --net haginet --name $CONTNAME --hostname $CONTNAME -d -v $HAGIHOME/jdk1.8.0_221:/root/java -v $HAGIHOME/hadoop-2.7.1:/root/hadoop -v $HAGIHOME/spark-3.3.4-bin-hadoop2:/root/spark -v $HAGIHOME/kafka_2.13-3.3.1:/root/kafka server 
#####################
CONTNAME=slave2
CONTCPU=3
sudo docker run --cpuset-cpus="$CONTCPU" --net haginet --name $CONTNAME --hostname $CONTNAME -d -v $HAGIHOME/jdk1.8.0_221:/root/java -v $HAGIHOME/hadoop-2.7.1:/root/hadoop -v $HAGIHOME/spark-3.3.4-bin-hadoop2:/root/spark -v $HAGIHOME/kafka_2.13-3.3.1:/root/kafka server 
#####################
sudo docker run -d \
    --name=influxdb \
    --net haginet \
    -p 8086:8086 \
    -v $HAGIHOME/influxdb/data:/var/lib/influxdb2 \
    -v $HAGIHOME/influxdb/config:/etc/influxdb2 \
    --restart=unless-stopped \
    influxdb:2.7.4

#####################
sudo docker run -d -p 3000:3000 --name=grafana \
    --net haginet \
    --user "$(id -u)" \
    --volume "$HAGIHOME/grafana:/var/lib/grafana" \
    grafana/grafana-enterprise



