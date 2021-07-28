#!/bin/bash
#define path to neo4j bin
path_neo4j=$1

python ../add_info_from_removed_node_to_other_node.py DOID:60003 MONDO:0002829 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:8256 MONDO:0002722 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:7602 MONDO:0002631 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:955 MONDO:0002546 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:2747 MONDO:0002412 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:2775 MONDO:0002422 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:5517 MONDO:0004950 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:1037 MONDO:0004967 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0050686 MONDO:0004992 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0050687 MONDO:0004992 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:2348 MONDO:0002277 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:2751 MONDO:0010598 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0040087 MONDO:0000774 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0060773 MONDO:0009151 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0070141 MONDO:0009054 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0050743 MONDO:0000430 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:7235 MONDO:0018523 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0040098 MONDO:0006558 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:3284 MONDO:0006451 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:5766 MONDO:0006280 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:13949 MONDO:0018301 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:5411 MONDO:0008433 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:12118 MONDO:0008346 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0080335 MONDO:0014175 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:3774 MONDO:0016706 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0070022 MONDO:0014076 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:1468 MONDO:0002008 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:9562 MONDO:0016575 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:7922 MONDO:0004398 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0050671 MONDO:0004379 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:2702 MONDO:0006906 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:4839 MONDO:0006962 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:12895 MONDO:0006733 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:3948 MONDO:0006639 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:660 MONDO:0006639 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0050667 MONDO:0016011 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:13725 MONDO:0006676 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:12639 MONDO:0001561 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:656 MONDO:0003924 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0060054 MONDO:0001300 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:11701 MONDO:0001341 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:5709 MONDO:0013280 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:5917 MONDO:0003704 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:12965 MONDO:0003730 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0080304 MONDO:0027772 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0110087 MONDO:0013127 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:5859 MONDO:0003680 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0080276 MONDO:0033044 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0060084 MONDO:0005165 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0060085 MONDO:0005165 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:3498 MONDO:0005184 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0050933 MONDO:0005211 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:9893 MONDO:0005076 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0050861 MONDO:0005008 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:7891 MONDO:0020513 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:686 MONDO:0007256 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0111701 MONDO:0010958 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:8500 MONDO:0019118 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:10579 MONDO:0019046 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0050987 MONDO:0019046 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0070227 MONDO:0019072 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:6620 MONDO:0010626 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:5176 MONDO:0019004 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:13137 MONDO:0009669 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:1849 MONDO:0005689 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:2691 MONDO:0003061 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:5672 MONDO:0005575 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0080008 MONDO:0005380 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0050860 MONDO:0005484 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
python ../add_info_from_removed_node_to_other_node.py DOID:0060104 MONDO:0007959 Disease
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
                    echo "Current time: $now"
