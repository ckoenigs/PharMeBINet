 # define import tool
import_tool=$1
# define path to pharmebinet
path_to_pharmebinet=$2

java -jar $import_tool.jar -i $path_to_pharmebinet"PharMeBiNet_finished.graphml"  -e bolt://localhost:7687 --username neo4j --password test  --modify-edge-labels false --indices "Reaction.identifier;Pathway.identifier;Interaction.identifier;SideEffect.identifier;CellularComponent.identifier;Anatomy.identifier;Symptom.identifier;Disease.identifier;ReactionLikeEvent.identifier;BiologicalProcess.identifier;Treatment.identifier;Chemical.identifier;Regulation.identifier;RNA.identifier;MolecularComplex.identifier;FailedReaction.identifier;Product.identifier;Depolymerisation.identifier;Gene.identifier;PharmacologicClass.identifier;MolecularFunction.identifier;Polymerisation.identifier;ClinicalAnnotation.identifier;VariantAnnotation.identifier;Metabolite.identifier;BlackBoxEvent.identifier;Variant.identifier;Protein.identifier;Compound.identifier;CellularComponent.name;BiologicalProcess.name;PharmacologicClass.name;Disease.name;Gene.name;SideEffect.name;Pathway.name;Compound.name;MolecularFunction.name;Symptom.name;Anatomy.name"
