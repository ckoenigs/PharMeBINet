#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

# define bioDWH2 tool
biodwh2=$3

#password
password=$4

#path other data source space
path_data_source=$5


# prepare directories
if [ ! -d output ]; then
  mkdir output
fi
if [ ! -d $path_data_source/refseq/ ]; then
  mkdir $path_data_source/refseq/
fi


echo load latest version of mirbase and generat GraphML file

dir=$path_data_source/refseq/sources/

# prepare workspace and add TTD to bioDWB2 tool
if [ ! -d "$dir" ]; 
then
    echo generate workspace in directory
    java -jar ../$biodwh2.jar -c $path_data_source/refseq

    java -jar ../$biodwh2.jar --add-data-source $path_data_source/refseq RefSeq

fi

java -jar ../$biodwh2.jar -u $path_data_source/refseq

echo $import_tool


echo integrate refseq into neo4j

java -jar ../$import_tool.jar -i $path_data_source/refseq/sources/RefSeq/intermediate.graphml.gz  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix refSeq_ --indices "refSeq_Assembly.id;refSeq_BiologicalRegion.id;refSeq_CAATSignal.id;refSeq_CAGECluster.id;refSeq_CDS.id;refSeq_CGeneSegment.id;refSeq_Centromere.id;refSeq_Chromosome.id;refSeq_ChromosomeBreakpoint.id;refSeq_ConservedRegion.id;refSeq_DGeneSegment.id;refSeq_DLoop.id;refSeq_DNaseIHypersensitiveSite.id;refSeq_DirectRepeat.id;refSeq_DispersedRepeat.id;refSeq_Enhancer.id;refSeq_EnhancerBlockingElement.id;refSeq_EpigeneticallyModifiedRegion.id;refSeq_Exon.id;refSeq_GCRichPromoterRegion.id;refSeq_Gene.id;refSeq_ImprintingControlRegion.id;refSeq_Insulator.id;refSeq_JGeneSegment.id;refSeq_LocusControlRegion.id;refSeq_Match.id;refSeq_MatrixAttachmentSite.id;refSeq_MeioticRecombinationRegion.id;refSeq_MicroSatellite.id;refSeq_MiniSatellite.id;refSeq_MitoticRecombinationRegion.id;refSeq_MobileGeneticElement.id;refSeq_NonAllelicHomologousRecombinationRegion.id;refSeq_NucleotideCleavageSite.id;refSeq_NucleotideMotif.id;refSeq_OriginOfReplication.id;refSeq_PrimaryTranscript.id;refSeq_Promoter.id;refSeq_ProteinBindingSite.id;refSeq_PseudoGene.id;refSeq_RNaseMRPRNA.id;refSeq_RNasePRNA.id;refSeq_RecombinationFeature.id;refSeq_Region.id;refSeq_RegulatoryRegion.id;refSeq_RepeatInstabilityRegion.id;refSeq_RepeatRegion.id;refSeq_ReplicationRegulatoryRegion.id;refSeq_ReplicationStartSite.id;refSeq_ResponseElement.id;refSeq_SequenceAlteration.id;refSeq_SequenceAlterationArtifact.id;refSeq_SequenceComparison.id;refSeq_SequenceFeature.id;refSeq_SequenceSecondaryStructure.id;refSeq_Silencer.id;refSeq_TATABox.id;refSeq_TandemRepeat.id;refSeq_Transcript.id;refSeq_TranscriptionalCisRegulatoryRegion.id;refSeq_VGeneSegment.id;refSeq_YRNA.id;refSeq_antisenseRNA.id;refSeq_cDNAMatch.id;refSeq_lncRNA.id;refSeq_mRNA.id;refSeq_miRNA.id;refSeq_ncRNA.id;refSeq_rRNA.id;refSeq_scRNA.id;refSeq_snRNA.id;refSeq_snoRNA.id;refSeq_tRNA.id;refSeq_telomeraseRNA.id;refSeq_vaultRNA.id" > output/import_tool_output.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30


python ../../execute_cypher_shell.py $path_neo4j $password cypher_add_label.cypher > output/cypher.txt




