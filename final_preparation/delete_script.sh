#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# MATCH (n) WHERE ANY ( x IN labels(n) WHERE x in['drugSider', 'CTDpathway', 'NDF_RT_DISEASE_KIND', 'AeolusOutcome', 'Compound_DrugBank', 'NDF_RT_DRUG_KIND','Gene_Ncbi', 'NDF_RT_PHYSIOLOGIC_EFFECT_KIND', 'NDF_RT_THERAPEUTIC_CATEGORY_KIND', 'Pathway_DrugBank','PharmacologicClass_DrugBank', 'Product_DrugBank', 'Protein_DrugBank', 'Target_DrugBank','Transporter_DrugBank', 'efo', 'seSider', 'CTDchemical', 'AeolusDrug', 'HPOdisease', 'HPOsymptom','Protein_Uniprot', 'Salt_DrugBank', 'CTDgene', 'pathway_multi', 'go', 'diseaseontology', 'disease','Carrier_DrugBank', 'Enzyme_DrugBank', 'Metabolite_DrugBank', 'Mutated_protein_gene_DrugBank', 'CTDdisease','CTDGO', 'NDF_RT_DOSE_FORM_KIND', 'NDF_RT_INGREDIENT_KIND', 'NDF_RT_MECHANISM_OF_ACTION_KIND','NDF_RT_PHARMACOKINETICS_KIND', 'Variant_ClinVar', 'gene_omim', 'phenotype_omim','predominantly_phenotypes_omim', 'trait_BloodGroup_ClinVar', 'trait_Disease_ClinVar','trait_DrugResponse_ClinVar', 'trait_Finding_ClinVar', 'trait_NamedProteinVariant_ClinVar','trait_PhenotypeInstruction_ClinVar', 'trait_set_Disease_ClinVar', 'trait_set_DrugResponse_ClinVar','trait_set_Finding_ClinVar', 'trait_set_PhenotypeInstruction_ClinVar', 'trait_set_TraitChoice_ClinVar','Reaction_DrugBank','Additional_Pharmacologic_Classes_MED_RT','BlackBoxEvent_reactome', 'Affiliation_reactome','CandidateSet_reactome','CatalystActivityReference_reactome','CatalystActivity_reactome','ChemicalDrug_reactome','Chemical_Ingredient_MED_RT','Compartment_reactome','ControlReference_reactome','CrosslinkedResidue_reactome','DBInfo_reactome','DatabaseIdentifier_reactome','DefinedSet_reactome','Depolymerisation_reactome','Disease_Finding_MED_RT','Disease_reactome','Dose_Form_MED_RT','Drug_reactome','EntityFunctionalStatus_reactome','EntitySet_reactome','EntityWithAccessionedSequence_reactome', 'Event_reactome','FailedReaction_reactome','GO_Term_reactome','InstanceEdit_reactome', 'Mechanisms_of_Action_MED_RT', 'Pathway_reactome', 'Pharmacokinetics_MED_RT','Physiologic_Effects_MED_RT','Reaction_reactome','ReferenceDatabase_reactome','Taxon_reactome','Terminology_Extensions_for_Classification_MED_RT','Therapeutic_Categories_MED_RT', 'VA_Product_MED_RT','local_hierarchical_concept_MED_RT', 'other_MED_RT', 'DatabaseObject_reactome','drug_ADReCS_Target','variant_ADReCS_Target','CTDanatomy','ditop2_ADReCS_Target','FDA_Established_Pharmacologic_Classes_MED_RT', 'adr_ADReCS_Target','protein_IID','gene_ADReCS_Target','protein_ADReCS_Target'] ) RETURN count(n)
number_of_deleted_nodes=4500000
#number_of_deleted_nodes=50000
# number form program
STOP_AFTER=50000


# the add of STOP_AFTER-1 make sure that it is round up, because the division is only int and round down
number_of_runs=$((($number_of_deleted_nodes+$STOP_AFTER-1)/$STOP_AFTER))
echo $number_of_runs

for ((i=1; i<=$number_of_runs;i++));do
    now=$(date +"%F %T")
    echo "Current time: $now"
    echo $i
    python3 deleteNodes.py
    sleep 60

    $path_neo4j/neo4j restart


    sleep 120

    if (($i % 50 == 0))
    then 
        echo long sleep
        sleep 600
    fi

done

# other preprocess step
# write into each node how many edges go out
# python3 DBaddDegreeProperty.py