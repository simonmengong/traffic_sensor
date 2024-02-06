# Traffic Sensor

Cluster de container pour une chaine de traitement de données de traffic routier intégrant les techs: kafka, spark, InfluxDB et Grafana.

## Setup

Commencer par faire un buil de l'image:

Dans le dossier containers: `./build-image.sh`

Démarrer les containers: `./start-containers.sh`

Lancer spark dans un premier terminal (1)
```
docker exec -it master bash
cd /root/appli
./start.sh
```
au besoin ajouter d'abord les permissions à chaque fois avec: `chmod +x filename.sh`

Lancer le service zookeeper de Kafka dans un second terminal (2)
```
docker exec -it master bash
cd /root/appli
./start-zookeeper.sh
```

Lancer le broker de Kafka dans un autre terminal (3)
```
docker exec -it master bash
cd /root/appli
./start-kafka-broker.sh
```

Créer le topic `traffic_sensor` dans lequel on va écrire les données que spark va récupérer. Dans un quatrième terminal (4):
```
docker exec -it master bash
cd /root/appli
./kafka-topic.sh
```

### InfluxDB Setup
Dans un navigateur aller à l'adresse `localhost:8086` créer une organisation, un bucket et récupérer le token
ouvrir le fichier `appli/src/streaming/read_traffic.py` dans un editeur et modifier les variables
```
INFLUXDB_TOKEN = "my-token"
INFLUXDB_ORG = "my-org"
INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_BUCKET="my-bucket"
```
avec les valeurs appropriées.
Une fois fait enregistrer le fichier et fermer l'éditeur. Dans un autre terminal (5) lancer le consumer du topic créé précédemment:
```
docker exec -it master bash
cd /root/appli
./run-stream.sh
```

### Grafana Setup (optional)
Aller à l'adresse 'localhost:3000' et configurer la source de données InfluxDB pour Grafana

Enfin dans le terminal 4 lancer le producer kafka:
`./run-producer.sh`


### Visualisation

se rendre à l'adresse 
```
http://localhost:3000/explore?schemaVersion=1&panes=%7B%22FAa%22:%7B%22datasource%22:%22aa29c13e-c6d8-4b46-a853-f96dcc5ab1f7%22,%22queries%22:%5B%7B%22datasource%22:%7B%22type%22:%22influxdb%22,%22uid%22:%22aa29c13e-c6d8-4b46-a853-f96dcc5ab1f7%22%7D,%22query%22:%22from%28bucket:%20%5C%22my-bucket%5C%22%29%5Cn%7C%3E%20range%28start:%202022-05-31%29%5Cn%7C%3E%20filter%28fn:%20%28r%29%20%3D%3E%20r._measurement%20%3D%3D%20%5C%22traffic_final%5C%22%29%22,%22refId%22:%22A%22%7D%5D,%22range%22:%7B%22from%22:%221659340800000%22,%22to%22:%221659425100000%22%7D%7D%7D&orgId=1
```
pour visualiser les graphes sans besoin de reconfigurer grafana.

Grafana affiche le graphe du nombre de véhicules circulant toutes les 5 minutes.

Fin.



