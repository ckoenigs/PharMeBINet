########################################################################################################
# Programmname:		ConvertXML_ClinVar.R                                                                 #
# Studie: 			                                                                                       #
# Beschreibung:		                                            			                                   #
# Autor:            MK                                                                                 #
# Letzte Änderung:  27-03-2017                                                                         #
# Hinweis:                                                                                             #                                                    
########################################################################################################

library(XML)
library(methods)
library(Hmisc)
library(reshape2)
#getwd()
setwd("/home/maren/Rfiles")
xml_file<-"ClinVarFullRelease_00-latest.xml"


# Give the input file name to the function.
result <- xmlParse(file = xml_file)


rootnode<-xmlRoot(result)

#res<-(result, 
#function for extraction
xml_ex<-function(set){
	#ClinVarAssertion - Gene
	gene<-xmlApply(rootnode, function(x){
		pre<-'unknown'
		onset<-'unknown'
		attributes<-'unknown'
	
		idAss<-xmlAttrs(x)['ID']
		#print(idAss)
		nameAss<-xmlValue(x[['ReferenceClinVarAssertion']][['MeasureSet']])
		#print(nameAss)
		type<-lapply(x[['ReferenceClinVarAssertion']]["MeasureSet"], xmlAttrs)
		refGene<-lapply(x[['ReferenceClinVarAssertion']][["MeasureSet"]][["Measure"]][["MeasureRelationship"]]["XRef"], xmlAttrs)
		#print(refGene)
		symbol<-xmlValue(x[['ReferenceClinVarAssertion']][["MeasureSet"]][["Measure"]][["MeasureRelationship"]][["Symbol"]])
		#print(symbol)
		#variants<-xpathSApply(x, "//MeasureSet/Measure", xmlAttrs)
		refGeneID<-lapply(refGene, function(x){
			if(x['DB']=="Gene") {
				return(x['ID'])
			}
			else{
				return(NULL)
			}
		})
		refGeneID<-unlist(refGeneID)
		refGeneID<-refGeneID[!is.null(refGeneID)]
		#print(refGeneID)

		#ModeofInheritance
		attributes_ns<-try(xmlChildren(x[['ReferenceClinVarAssertion']][['TraitSet']][['Trait']][['AttributeSet']]), silent=T)
		#print(attributes_ns)
		if(!inherits(attributes_ns, "try-error")){
		attributes<-lapply(attributes_ns, function(g){
			exists<-length(xmlGetAttr(g, "Type"))
			if(exists!=0 && xmlGetAttr(g, "Type")=="ModeOfInheritance"){
				return(xmlValue(g))			
			}
			else{
			return("unknown")
			}
		}
		)

		
		pre<-lapply(attributes_ns, function(h){
			exists<-length(xmlGetAttr(h, "Type"))
			if(exists!=0 && xmlGetAttr(h, "Type")=="prevalence"){
				return(xmlValue(h))			
			}
			else{
			return("unknown")
			}
		}
		)
		
		
		#print(pre['Attribute'])		
		onset<-lapply(attributes_ns, function(i){
			exists<-length(xmlGetAttr(i, "Type"))
			if(exists!=0 && xmlGetAttr(i, "Type")=="age of onset"){
				return(xmlValue(i))			
			}
			else{
			return("unknown")
			}
		}
		)
		
		#print(onset['Attribute'])	
	}
		#DiseaseMechanism
		#attributes2<-xpathApply(x, "MeasureSet/Measure/AttributeSet/Attribute[@Type='disease mechanism']", xmlValue)
		#print(attributes2)
		#prevalance
		#attributes3<-xpathApply(x, "//Attribute[@Type='prevalence']", xmlValue)
		clin_sig<-xmlValue(x[['ReferenceClinVarAssertion']][['ClinicalSignificance']][['Description']])
		#print(idAss)
		#print((c(idAss, nameAss, type[[1]][1], type[[1]][2], refGeneID, symbol[[1]], clin_sig,attributes[[1]], pre[[1]],onset[[1]] )))
	
	return((c(idAss, nameAss, type[[1]][1], type[[1]][2], refGeneID, symbol[[1]], clin_sig,attributes[[1]], pre[[1]],onset[[1]] )))
	})
	
	return(gene)
}
res<-xml_ex(result)
save(res, file="Res.Rdata")
dat<-lapply(res, length)

dat2<-lapply(dat, function (x)return(x==10))
dat2<-unlist(dat2)
data10<-res[dat2]
########
#Problem manche Einträge haben 9 statt 10 Zeilen- keine Gene type reference- discarded!

########
data9<-res[!dat2]

res_neu<-t(as.data.frame(data10))

colnames(res_neu)<-c("Ref_ID","NameVariant","Type","Variant_ID","Gene_ID","GeneSymbol","Clin_Sign","ModeOfInheritance","Prevalence","AgeOfOnset")
rownames(res_neu)<-NULL
#TABLE
PRESENTS_GpV<-data.frame(source="ClinVar", IDGene=res_neu[,5], IDVariant=res_neu[,4])
write.csv(PRESENTS_GpV, row.names=FALSE, file="PRESENTS_GpV.csv")

VARIANT<-data.frame(IDVariant=res_neu[,4],IDGene=res_neu[,5], lisence="ClinVar?", name=res_neu[,2], symbol=res_neu[,6],clin_sig=res_neu[,7], inheritance=res_neu[,8], prevalence=res_neu[,9], ageOfonset=res_neu[,10])
write.csv(VARIANT,row.names=FALSE,  file="VARIANT.csv")



