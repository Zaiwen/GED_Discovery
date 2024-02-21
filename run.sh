#!/bin/bash
echo "==============================================Step 1=============================================="
java -jar GraMi_ExactSubgraphMatching-1.0-SNAPSHOT.jar filename=graph.lg datasetFolder=resource/ freq=100
echo "==============================================Step 2=============================================="
java -jar graphflow-0.1.0.jar
echo "==============================================Step 3=============================================="
java -jar GEDdependencyMining-1.0-SNAPSHOT.jar /user_data/hujw/yes/envs/Meta_FALCO/bin/python /user_data/hujw/GEDmining2/dependency_mining.py /user_data/hujw/GEDmining2 -1 -1
