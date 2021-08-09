# PharmaMeBiNet: The heterogeneouspharmacological medicalbiochemical network
Fist use Hetionet (http://het.io/) as start base and was updated to Neo4j database service 4.0.3.
First the different data source are parsed and then integrated into Neo4j database.
In the next step the different database are mapped and merged intho Hetionet and generate the database PharmaMeBiNet

The shell script do the integration into neo4j and the mapping and merging to Hetionet. 


./script_to_execute_all.sh /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-4.2.5/bin /home/cassandra/Documents/Project/ > output.txt 2>&1 &


