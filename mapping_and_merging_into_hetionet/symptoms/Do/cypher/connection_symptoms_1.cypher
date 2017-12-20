begin 
MATCH (n:Disease{identifier:"DOID:0050046"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050046', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050046"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050046',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050046"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050046',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1442"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1442', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0080044"}),(s:Symptom{identifier:"C0392025"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0080044',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10921"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10921', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10921"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10921',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10921"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10921',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10881"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10881', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10881"}),(s:Symptom{identifier:"C0232462"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10881"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10881"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10883"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10883', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10883"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10883',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2929"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2929',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2929"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2929', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2929"}),(s:Symptom{identifier:"C0425449"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2929',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2929"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2929', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2929"}),(s:Symptom{identifier:"C0231706"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2929',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2929"}),(s:Symptom{identifier:"C0239182"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2929',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050491"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050491', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050491"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050491',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050491"}),(s:Symptom{identifier:"D004244"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050491', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050491"}),(s:Symptom{identifier:"C0233514"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050491',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050491"}),(s:Symptom{identifier:"C0233417"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050491',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050491"}),(s:Symptom{identifier:"D008569"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050491', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050491"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050491', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050491"}),(s:Symptom{identifier:"D007319"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050491', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050491"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050491',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050145"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050145', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050145"}),(s:Symptom{identifier:"C0332575"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050145',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050145"}),(s:Symptom{identifier:"C0038999"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050145',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050145"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050145',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10242"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10242', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10242"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10242', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10242"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10242', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10242"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10242',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9801"}),(s:Symptom{identifier:"C0232487"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9801',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9801"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9801', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9801"}),(s:Symptom{identifier:"D004614"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9801', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050383"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050383', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050383"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050383', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050383"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050383', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050383"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050383',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050383"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050383', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3240"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3240',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3240"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3240', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3240"}),(s:Symptom{identifier:"C0006266"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3240',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3240"}),(s:Symptom{identifier:"D006469"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3240', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3240"}),(s:Symptom{identifier:"C0577979"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3240',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3240"}),(s:Symptom{identifier:"C0476273"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3240',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13521"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13521', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13521"}),(s:Symptom{identifier:"C0392674"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13521',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4969"}),(s:Symptom{identifier:"D000381"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4969', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4969"}),(s:Symptom{identifier:"D060705"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4969', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4969"}),(s:Symptom{identifier:"D000377"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4969', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9415"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9415', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9415"}),(s:Symptom{identifier:"D012135"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9415', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9415"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9415', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9415"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9415', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9415"}),(s:Symptom{identifier:"C0232292"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9415',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:7427"}),(s:Symptom{identifier:"C0037299"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7427',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:7427"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7427', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:7427"}),(s:Symptom{identifier:"C0232462"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7427',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:7427"}),(s:Symptom{identifier:"C0151594"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7427',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:7427"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7427', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:7427"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7427', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1759"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1759',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1759"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1759', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1759"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1759',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1759"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1759', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13450"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13450',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13450"}),(s:Symptom{identifier:"C0003864"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13450',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1731"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1731',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1731"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1731', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1731"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1731',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1731"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1731', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050308"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050308', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050308"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050308', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050308"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050308', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050308"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050308', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050308"}),(s:Symptom{identifier:"C0040034"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050308',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050308"}),(s:Symptom{identifier:"C0019104"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050308',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3481"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3481"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3481"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3481',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3481"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3481"}),(s:Symptom{identifier:"C0036974"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3481',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10882"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10882', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10882"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10882',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10882"}),(s:Symptom{identifier:"C0032231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10882',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10882"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10882', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13258"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13258', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13258"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13258', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13258"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13258',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13258"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13258', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13258"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13258',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13258"}),(s:Symptom{identifier:"C0019209"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13258',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13258"}),(s:Symptom{identifier:"C0023530"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13258',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13282"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13282"}),(s:Symptom{identifier:"C0017181"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13282',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13282"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13282"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050456"}),(s:Symptom{identifier:"C0028259"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050456',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050710"}),(s:Symptom{identifier:"D009133"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050710', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050710"}),(s:Symptom{identifier:"C0699815"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050710',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050710"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050710', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050152"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050152', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050152"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050152', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12386"}),(s:Symptom{identifier:"D009120"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12386', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12386"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12386', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12386"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12386', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12386"}),(s:Symptom{identifier:"D006209"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12386', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10608"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D015746"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='DOID:10608'; 
MATCH (n:Disease{identifier:"DOID:10608"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D003248"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='DOID:10608'; 
MATCH (n:Disease{identifier:"DOID:10608"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D003967"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='DOID:10608'; 
 MATCH (n:Disease{identifier:"DOID:10608"}),(s:Symptom{identifier:"C0027498"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10608',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10608"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10608',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050490"}),(s:Symptom{identifier:"C0022107"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050490',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050490"}),(s:Symptom{identifier:"C0947509"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050490',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050490"}),(s:Symptom{identifier:"C0233818"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050490',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050490"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050490', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050490"}),(s:Symptom{identifier:"D007319"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050490', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050490"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050490', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050490"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050490', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050012"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050012', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050012"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050012', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050012"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050012',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050515"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050515', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050515"}),(s:Symptom{identifier:"C3697716"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050515',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3133"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3133', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3133"}),(s:Symptom{identifier:"C0442874"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3133',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3133"}),(s:Symptom{identifier:"C0262385"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3133',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3133"}),(s:Symptom{identifier:"C0033975"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3133',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"C2675627"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"C0426396"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"C0233514"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"C2830004"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2047"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2047', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:7147"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D010146"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='DOID:7147'; 
MATCH (n:Disease{identifier:"DOID:2043"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D005334"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='DOID:2043'; 
MATCH (n:Disease{identifier:"DOID:2043"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2043', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2043"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2043',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2043"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2043', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2043"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2043', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2043"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2043', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2043"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2043', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2043"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D007565"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='DOID:2043'; 
MATCH (n:Disease{identifier:"DOID:14115"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14115', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14115"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14115',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14115"}),(s:Symptom{identifier:"C0020649"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14115',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14115"}),(s:Symptom{identifier:"C0026766"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14115',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14115"}),(s:Symptom{identifier:"C0237849"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14115',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14115"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14115', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14115"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14115', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14115"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14115', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2122"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2122', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2122"}),(s:Symptom{identifier:"C0817096"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2122',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2122"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2122', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2122"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2122', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11573"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11573', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11573"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11573', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11573"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11573', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11573"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11573', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11573"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11573',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11573"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11573', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11573"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11573', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12549"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12549', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12549"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12549', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12549"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12549',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12549"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12549', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12549"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12549', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12549"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12549', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12549"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12549', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12549"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12549', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11339"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11339',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11339"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11339', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11339"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11339', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060216"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060216', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060216"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060216', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4998"}),(s:Symptom{identifier:"C1857042"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4998',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4998"}),(s:Symptom{identifier:"C1865017"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4998',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050514"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050514', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050514"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050514',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8729"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8729', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8729"}),(s:Symptom{identifier:"C0024225"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8729',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8729"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8729',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2841"}),(s:Symptom{identifier:"C0232292"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2841',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2841"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D004417"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='DOID:2841'; 
 MATCH (n:Disease{identifier:"DOID:2841"}),(s:Symptom{identifier:"C2610947"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2841',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2841"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D003371"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='DOID:2841'; 
MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"C1291077"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"C0232462"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"D003248"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050254"}),(s:Symptom{identifier:"C0018932"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050254',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050068"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050068', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050068"}),(s:Symptom{identifier:"C0024205"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050068',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050068"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050068', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050068"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050068',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13386"}),(s:Symptom{identifier:"C0221198"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13386',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13386"}),(s:Symptom{identifier:"D006396"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13386', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13386"}),(s:Symptom{identifier:"C1443924"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13386',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13386"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13386',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2297"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2297', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2297"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2297', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2297"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2297', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2297"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2297', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2297"}),(s:Symptom{identifier:"C0019209"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2297',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9063"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9063', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9063"}),(s:Symptom{identifier:"C0022107"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9063',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:6132"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:6132', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:6132"}),(s:Symptom{identifier:"C0239574"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:6132',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:6132"}),(s:Symptom{identifier:"C0232292"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:6132',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1787"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1787', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050061"}),(s:Symptom{identifier:"C0041834"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050061',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14456"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14456', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14456"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14456',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14456"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14456', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14456"}),(s:Symptom{identifier:"C0030196"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14456',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14456"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14456', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:5052"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:5052', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:5052"}),(s:Symptom{identifier:"C0476273"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:5052',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:5052"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:5052', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:5052"}),(s:Symptom{identifier:"C0221512"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:5052',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14239"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14239', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14239"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14239', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14239"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14239',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14239"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14239', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14239"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14239', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11055"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11055', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11055"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11055', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11055"}),(s:Symptom{identifier:"C0424790"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11055',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11055"}),(s:Symptom{identifier:"C0032285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11055',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11055"}),(s:Symptom{identifier:"D008580"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11055', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11055"}),(s:Symptom{identifier:"C0039231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11055',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:526"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:526', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:526"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:526', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:526"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:526', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:526"}),(s:Symptom{identifier:"C0860029"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:526',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:526"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:526', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:526"}),(s:Symptom{identifier:"C0149745"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:526',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:526"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:526', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:526"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:526',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:526"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:526',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11360"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11360', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11360"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11360', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11360"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11360', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11360"}),(s:Symptom{identifier:"C0039231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11360',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10773"}),(s:Symptom{identifier:"C0442800"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10773',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10773"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10773', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10773"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10773', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10773"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10773',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050125"}),(s:Symptom{identifier:"C0423798"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050125',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050125"}),(s:Symptom{identifier:"D005884"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050125', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050125"}),(s:Symptom{identifier:"C0014591"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050125',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050485"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050485', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050484"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050484', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050484"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050484', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050484"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050484', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4986"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4986', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4986"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4986',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4986"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4986', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4986"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4986', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4986"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4986', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4986"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4986',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4986"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4986', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:96"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:96', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:96"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:96', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:96"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:96', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:96"}),(s:Symptom{identifier:"D009120"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:96', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:96"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:96',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050481"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050481"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050481"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050481"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050481"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050481"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050481"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050481', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050481"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050481',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050480"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050480',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050480"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050480', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050480"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050480',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050480"}),(s:Symptom{identifier:"C3862404"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050480',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050480"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050480', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050480"}),(s:Symptom{identifier:"D053608"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050480', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050480"}),(s:Symptom{identifier:"D020795"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050480', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050480"}),(s:Symptom{identifier:"D003693"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050480', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:407"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:407', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:407"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:407', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:407"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:407', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:407"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:407', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:407"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:407', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:404"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:404', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:404"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:404', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:404"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:404', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:404"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:404', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:404"}),(s:Symptom{identifier:"C0278008"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:404',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:404"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:404', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:404"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:404', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:6088"}),(s:Symptom{identifier:"C0236720"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:6088',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:6088"}),(s:Symptom{identifier:"C0857051"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:6088',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:6088"}),(s:Symptom{identifier:"C0870186"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:6088',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"D005183"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"C0025289"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"C0008526"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"C0020255"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"D008607"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"C0029420"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050488"}),(s:Symptom{identifier:"C0240822"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050488',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12155"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12155', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12155"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12155',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12155"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12155', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12155"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12155', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12155"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12155',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12155"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12155', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12155"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12155', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050197"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050197', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050197"}),(s:Symptom{identifier:"C3887500"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050197',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050197"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050197', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050197"}),(s:Symptom{identifier:"D004244"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050197', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050197"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050197', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050197"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050197',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4448"}),(s:Symptom{identifier:"D001766"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4448', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1328"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1328', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1328"}),(s:Symptom{identifier:"D006396"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1328', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1328"}),(s:Symptom{identifier:"C0025323"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1328',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3905"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3905', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3905"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3905', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3905"}),(s:Symptom{identifier:"D006469"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3905', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8781"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8781', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8781"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8781',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8781"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8781', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8781"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8781', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8781"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8781',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060192"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060192', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0060192"}),(s:Symptom{identifier:"C0267596"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060192',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0060192"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060192',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060190"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060190"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060191"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060191', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060191"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060191', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060191"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060191', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0060191"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060191',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10264"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10264', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10264"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10264', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10264"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10264', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10264"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10264', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10264"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10264',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13369"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13369', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13369"}),(s:Symptom{identifier:"C0085624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13369',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13369"}),(s:Symptom{identifier:"C0392757"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13369',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1251"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1251', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1251"}),(s:Symptom{identifier:"C0282005"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1251',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1024"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1024',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1024"}),(s:Symptom{identifier:"C0278134"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1024',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1252"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1252', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1252"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1252', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1252"}),(s:Symptom{identifier:"C0034888"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1252',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1252"}),(s:Symptom{identifier:"C0151686"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1252',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3055"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3055', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3055"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3055', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3055"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3055', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3055"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3055',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3055"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3055', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3055"}),(s:Symptom{identifier:"D003248"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3055', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3055"}),(s:Symptom{identifier:"C0428977"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3055',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3055"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3055',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10784"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10784"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10784"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10784"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10784',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10784"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10784',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050035"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050035', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050035"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050035',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050035"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050035',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12403"}),(s:Symptom{identifier:"C0332469"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12403',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12403"}),(s:Symptom{identifier:"C0392757"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12403',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12403"}),(s:Symptom{identifier:"C0333525"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12403',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3292"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3292', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3292"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3292', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3292"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3292', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3292"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3292',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11103"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11103', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11103"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11103', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11103"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11103', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11103"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11103', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11103"}),(s:Symptom{identifier:"C0234920"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11103',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11101"}),(s:Symptom{identifier:"C0035021"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11101',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11101"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11101', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11101"}),(s:Symptom{identifier:"C0241032"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11101',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11100"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11100', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11100"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11100', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11100"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11100', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11100"}),(s:Symptom{identifier:"C0008033"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11100',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11100"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11100', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11100"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11100', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11104"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11104', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11104"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11104', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11104"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11104', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11104"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11104', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11262"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11262', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11262"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11262', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11262"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11262',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11262"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11262', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11262"}),(s:Symptom{identifier:"C0032285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11262',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11260"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11260', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11260"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11260', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11260"}),(s:Symptom{identifier:"C0003467"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11260',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11260"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11260', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11260"}),(s:Symptom{identifier:"C0085631"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11260',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11260"}),(s:Symptom{identifier:"D003693"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11260', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11260"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11260',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11260"}),(s:Symptom{identifier:"C1609481"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11260',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11260"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11260', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11266"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11266', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11266"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11266', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11266"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11266', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11266"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11266', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11266"}),(s:Symptom{identifier:"D011693"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11266', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11266"}),(s:Symptom{identifier:"D011507"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11266', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11266"}),(s:Symptom{identifier:"C0035078"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11266',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9584"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9584', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9584"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9584', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9584"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9584',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9584"}),(s:Symptom{identifier:"C2957106"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9584',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9584"}),(s:Symptom{identifier:"D020795"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9584', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050521"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050521', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050521"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050521', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050521"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050521', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050521"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050521', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050521"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050521', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050521"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050521', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050521"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050521', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050522"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050522', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050522"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050522', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050522"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050522', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050522"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050522', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050522"}),(s:Symptom{identifier:"D011693"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050522', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050522"}),(s:Symptom{identifier:"D011507"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050522', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050522"}),(s:Symptom{identifier:"C0035078"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050522',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13371"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13371', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13371"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13371', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13371"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13371', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13371"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13371', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13371"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13371',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13371"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13371',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13371"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13371',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13371"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13371',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8704"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8704', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8704"}),(s:Symptom{identifier:"C4282165"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8704',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11750"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11750', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11750"}),(s:Symptom{identifier:"D012912"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11750', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11750"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11750',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13622"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13622', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13622"}),(s:Symptom{identifier:"C0013369"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13622',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13622"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13622', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050198"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050198', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050198"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050198', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050198"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050198', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050198"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050198', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050198"}),(s:Symptom{identifier:"C0036974"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050198',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050198"}),(s:Symptom{identifier:"C0019080"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050198',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060189"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060189', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060189"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060189', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060189"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060189', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060188"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060188', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060188"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060188', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060188"}),(s:Symptom{identifier:"D009120"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060188', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8469"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8469', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8469"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8469', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8469"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8469',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8469"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8469',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8469"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8469', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8469"}),(s:Symptom{identifier:"C2957106"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8469',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8469"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8469', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8469"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8469',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:7551"}),(s:Symptom{identifier:"C2127347"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7551',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:7551"}),(s:Symptom{identifier:"C0232861"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7551',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13801"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13801', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13801"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13801', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12721"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12721', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12721"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12721', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12841"}),(s:Symptom{identifier:"C0267373"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12841',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12841"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12841', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12841"}),(s:Symptom{identifier:"C0002871"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12841',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12841"}),(s:Symptom{identifier:"C1443924"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12841',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12841"}),(s:Symptom{identifier:"C0162429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12841',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13036"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13036', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13036"}),(s:Symptom{identifier:"C0039231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13036',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13036"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13036',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13036"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13036',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9123"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9123', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9123"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9123',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13166"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13166', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13166"}),(s:Symptom{identifier:"D012135"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13166', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13166"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13166', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11077"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11077', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11077"}),(s:Symptom{identifier:"C0038984"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11077',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11077"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11077', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11077"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11077', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11077"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11077', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11077"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11077', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11076"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11076', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11076"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11076', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11076"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11076',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11076"}),(s:Symptom{identifier:"C0700590"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11076',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11076"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11076', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11076"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11076', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11076"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11076', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11076"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11076', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11076"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11076', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:636"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:636',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:636"}),(s:Symptom{identifier:"D004401"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:636', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050025"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050025', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050025"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050025', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050025"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050025', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050025"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050025', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050025"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050025',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8607"}),(s:Symptom{identifier:"C0221198"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8607',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8607"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8607', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8607"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8607',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050026"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050026', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050026"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050026', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050026"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050026', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050026"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050026', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050026"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050026',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14457"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14457', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14457"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14457', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14457"}),(s:Symptom{identifier:"C0038990"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14457',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14457"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14457', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14457"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14457',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14457"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14457', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14457"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14457', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14457"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14457', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13891"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13891', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13891"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13891',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13891"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13891', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9682"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9682', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9682"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9682', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9682"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9682', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9682"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9682', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9682"}),(s:Symptom{identifier:"C0036973"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9682',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9682"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9682',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9682"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9682', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9682"}),(s:Symptom{identifier:"D006472"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9682', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4337"}),(s:Symptom{identifier:"C0240941"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4337',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:7033"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7033', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:7033"}),(s:Symptom{identifier:"C0027498"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7033',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8568"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8568', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8568"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8568', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8568"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8568',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8568"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8568',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12179"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12179', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11782"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11782',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11302"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11302', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11302"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11302', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11302"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11302', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9210"}),(s:Symptom{identifier:"D014012"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9210', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9210"}),(s:Symptom{identifier:"D014717"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9210', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9210"}),(s:Symptom{identifier:"D004433"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9210', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9210"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9210', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13819"}),(s:Symptom{identifier:"C1735976"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13819',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13819"}),(s:Symptom{identifier:"C0024225"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13819',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:3298"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3298',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:3298"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:3298', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:7332"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7332',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:7332"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:7332"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:7332"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:7332"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:7332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050194"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050194', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050194"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050194', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050194"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050194',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050194"}),(s:Symptom{identifier:"C0023530"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050194',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050194"}),(s:Symptom{identifier:"C0040034"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050194',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4411"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4411', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4411"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4411', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4411"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4411',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4411"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4411', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4411"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4411', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4411"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4411', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4411"}),(s:Symptom{identifier:"C0426396"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4411',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4411"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4411', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4411"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4411', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2366"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2366', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2366"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2366',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2366"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2366', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2366"}),(s:Symptom{identifier:"C0741585"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2366',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2366"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2366', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2366"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2366',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2366"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2366', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14095"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14095', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13378"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D005334"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='DOID:13378'; 
 MATCH (n:Disease{identifier:"DOID:13378"}),(s:Symptom{identifier:"C0085649"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13378',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050118"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050118"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050118"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050118"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050118"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10371"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10371',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10027"}),(s:Symptom{identifier:"C0522510"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10027',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10027"}),(s:Symptom{identifier:"D020234"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10027', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10027"}),(s:Symptom{identifier:"D006941"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10027', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10027"}),(s:Symptom{identifier:"D010292"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10027', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10027"}),(s:Symptom{identifier:"C0242350"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10027',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4327"}),(s:Symptom{identifier:"C0019080"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4327',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"C0221512"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"C0235267"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4325"}),(s:Symptom{identifier:"D006606"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4325', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050050"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050050', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050050"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050050',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050051"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050051', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050051"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050051', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050051"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050051',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050051"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050051',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050052"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050052', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050052"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050052', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050052"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050052', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10845"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10845', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10845"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10845',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10845"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10845',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10845"}),(s:Symptom{identifier:"D053608"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10845', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10845"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10845', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10845"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10845', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10845"}),(s:Symptom{identifier:"D014202"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10845', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10845"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10845', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10845"}),(s:Symptom{identifier:"C0085621"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10845',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10844"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10844', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10844"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10844',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10844"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10844',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10844"}),(s:Symptom{identifier:"D053608"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10844', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10844"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10844', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10844"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10844', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10844"}),(s:Symptom{identifier:"D014202"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10844', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10844"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10844', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10844"}),(s:Symptom{identifier:"C0085621"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10844',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10841"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10841',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10841"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10841', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10841"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10841', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10841"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10841', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10841"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10841', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10841"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10841', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050059"}),(s:Symptom{identifier:"C0221198"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050059',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050059"}),(s:Symptom{identifier:"D006396"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050059', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050059"}),(s:Symptom{identifier:"C1443924"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050059',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050059"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050059',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10843"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10843', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10843"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10843', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10843"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10843', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10843"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10843', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10843"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10843', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10843"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10843',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10843"}),(s:Symptom{identifier:"C0278061"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10843',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10843"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10843',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14019"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14019', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14019"}),(s:Symptom{identifier:"C0038990"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14019',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14019"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14019',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14019"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14019', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14019"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14019', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14019"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14019',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:14019"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14019',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050195"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050195"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050195"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050195"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050195"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060311"}),(s:Symptom{identifier:"D012913"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060311', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0060311"}),(s:Symptom{identifier:"C0264618"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060311',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0060311"}),(s:Symptom{identifier:"C0029883"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060311',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4889"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4889',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4889"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4889', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4889"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4889', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4889"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4889', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4889"}),(s:Symptom{identifier:"C0028081"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4889',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4889"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4889', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"C0014591"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"D005884"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"D006396"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"C0025222"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050196"}),(s:Symptom{identifier:"C0025323"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050196',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4953"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4953', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4953"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4953',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4953"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4953', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4953"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4953', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4953"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4953', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4953"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4953',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4953"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4953', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4953"}),(s:Symptom{identifier:"C3697716"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4953',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4952"}),(s:Symptom{identifier:"D018908"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4952', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4952"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4952', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4952"}),(s:Symptom{identifier:"D012891"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4952', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4952"}),(s:Symptom{identifier:"C1260922"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4952',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:321"}),(s:Symptom{identifier:"C0221170"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:321',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:321"}),(s:Symptom{identifier:"D012678"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:321"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050354"}),(s:Symptom{identifier:"D003248"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050354', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050354"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050354', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050354"}),(s:Symptom{identifier:"C2183415"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050354',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050354"}),(s:Symptom{identifier:"C0740170"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050354',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050354"}),(s:Symptom{identifier:"C0033377"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050354',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050354"}),(s:Symptom{identifier:"C3552712"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050354',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050354"}),(s:Symptom{identifier:"D018908"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050354', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050199"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050199', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050199"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050199', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050199"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050199', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050352"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050352',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050352"}),(s:Symptom{identifier:"D004172"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050352', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050352"}),(s:Symptom{identifier:"D004401"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050352', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050352"}),(s:Symptom{identifier:"D055154"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050352', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050352"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050352',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4885"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4885', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4885"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4885', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4885"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4885', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4033"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4033', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4033"}),(s:Symptom{identifier:"D004415"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4033', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4033"}),(s:Symptom{identifier:"C1291077"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4033',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4033"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4033', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4033"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4033', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:992"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:992', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:992"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:992', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:992"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:992', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:992"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:992',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:992"}),(s:Symptom{identifier:"C0235592"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:992',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:992"}),(s:Symptom{identifier:"C0221752"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:992',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10398"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10398', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10398"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10398', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10398"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10398', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10398"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10398', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"D053608"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"D014202"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"D018908"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"D001766"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"C0028643"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2365"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1883"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1883', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1883"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1883', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1883"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1883',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1883"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1883', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1883"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1883', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1883"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1883', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1883"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1883', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1883"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1883', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11729"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11729', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11729"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11729', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11729"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11729', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4257"}),(s:Symptom{identifier:"C0238792"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4257',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4257"}),(s:Symptom{identifier:"C0022107"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4257',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14472"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14472', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14472"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14472', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14472"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14472', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14472"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14472', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:14472"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:14472', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2312"}),(s:Symptom{identifier:"C0032285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2312',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2312"}),(s:Symptom{identifier:"C0007642"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2312',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050288"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050288', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050288"}),(s:Symptom{identifier:"C0002871"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050288',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050288"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050288', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050288"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050288',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050288"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050288',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050288"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050288',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050211"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050211', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050211"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050211', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050211"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050211',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050211"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050211', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050211"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050211',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050211"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050211',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050211"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050211', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050211"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050211', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050211"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050211', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050047"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050047',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050047"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050047',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9786"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9786', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9786"}),(s:Symptom{identifier:"C1527347"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9786',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9786"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9786',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9786"}),(s:Symptom{identifier:"C0239043"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9786',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050513"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050513', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"C0151826"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"C0151602"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9537"}),(s:Symptom{identifier:"C2748540"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9537',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050043"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050043', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050043"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050043',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10039"}),(s:Symptom{identifier:"D010291"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10039', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10039"}),(s:Symptom{identifier:"C1406778"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10039',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10039"}),(s:Symptom{identifier:"C0029124"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10039',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10039"}),(s:Symptom{identifier:"C0155088"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10039',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10039"}),(s:Symptom{identifier:"D006319"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10039', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050517"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050517', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050517"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050517', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050517"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050517',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050516"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050516', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050516"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050516', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050516"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050516',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050516"}),(s:Symptom{identifier:"C0024205"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050516',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050201"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050201', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050201"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050201', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050201"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050201', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050201"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050201', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050201"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050201', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050201"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050201', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050201"}),(s:Symptom{identifier:"C1390214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050201',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050201"}),(s:Symptom{identifier:"C0035078"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050201',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"C0235267"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"C0020649"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050200"}),(s:Symptom{identifier:"C0022660"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050200',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"C0542115"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"C0032285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:4492"}),(s:Symptom{identifier:"C0748355"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:4492',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050202"}),(s:Symptom{identifier:"C0019080"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050202',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050204"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050204', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050204"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050204', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050204"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050204', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050204"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050204', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050204"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050204', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050204"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050204', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2957"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2957', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2957"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2957', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2957"}),(s:Symptom{identifier:"C0032227"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2957',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2957"}),(s:Symptom{identifier:"C0016059"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2957',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1273"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1273',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1273"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1273"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1273"}),(s:Symptom{identifier:"D012135"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1273"}),(s:Symptom{identifier:"C0476273"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1273',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060478"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060478', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0060478"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060478',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060478"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060478', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0060478"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0060478', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12663"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12663',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12663"}),(s:Symptom{identifier:"C0264545"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12663',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2934"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2934', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2934"}),(s:Symptom{identifier:"C0019209"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2934',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2934"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2934',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2934"}),(s:Symptom{identifier:"C0002871"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2934',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:5154"}),(s:Symptom{identifier:"C2939186"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:5154',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11258"}),(s:Symptom{identifier:"C0478664"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11258',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11258"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11258', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11258"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11258', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11258"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11258', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11258"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11258', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12096"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12096', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12096"}),(s:Symptom{identifier:"C0035021"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12096',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12096"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12096',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12096"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12096', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9159"}),(s:Symptom{identifier:"C0235957"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9159',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:9159"}),(s:Symptom{identifier:"C0243026"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:9159',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10250"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10250', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10250"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10250', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10250"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10250', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"C2830004"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"C4084858"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"D014202"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050179"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050179', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11320"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11320', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11320"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11320', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11320"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11320',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11320"}),(s:Symptom{identifier:"C3862404"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11320',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11320"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11320', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11320"}),(s:Symptom{identifier:"C0011175"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11320',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11320"}),(s:Symptom{identifier:"C2186261"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11320',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13035"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13035', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13035"}),(s:Symptom{identifier:"C0039231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13035',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13035"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13035',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13035"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13035',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050042"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050042', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050042"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050042',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13238"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13238', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13238"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13238', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13238"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13238',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13238"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13238', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11227"}),(s:Symptom{identifier:"C0595862"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11227',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11227"}),(s:Symptom{identifier:"C0162285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11227',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:11227"}),(s:Symptom{identifier:"D020795"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11227', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11227"}),(s:Symptom{identifier:"C0235267"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11227',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11227"}),(s:Symptom{identifier:"C0235263"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11227',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10842"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10842', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10842"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10842', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10842"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10842', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10842"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10842', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10842"}),(s:Symptom{identifier:"C0013144"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10842',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:10842"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10842', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10842"}),(s:Symptom{identifier:"C0441548"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10842',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:10842"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:10842',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050175"}),(s:Symptom{identifier:"C0013144"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050175',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050175"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050175', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050175"}),(s:Symptom{identifier:"D012678"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050175', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050175"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050175', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050174"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050174', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050174"}),(s:Symptom{identifier:"C0424790"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050174',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050174"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050174', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050174"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050174', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050174"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050174', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13444"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13444', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13444"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13444', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13444"}),(s:Symptom{identifier:"C0038990"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13444',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13444"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13444', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13444"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13444', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13444"}),(s:Symptom{identifier:"C0877322"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13444',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:13444"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13444', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:13444"}),(s:Symptom{identifier:"C3672042"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:13444',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12205"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12205', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12205"}),(s:Symptom{identifier:"C2957106"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12205',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12205"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12205', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12205"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12205',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050041"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050041', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12206"}),(s:Symptom{identifier:"C0040034"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12206',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12206"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12206',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1584"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1584', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:1584"}),(s:Symptom{identifier:"C0008033"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1584',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1584"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1584', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1584"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1584', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:1584"}),(s:Symptom{identifier:"D000860"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:1584', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8659"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8659', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8659"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8659', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8659"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8659', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8659"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8659', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8659"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8659', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8659"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8659',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8659"}),(s:Symptom{identifier:"C0005758"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8659',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2945"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2945', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2945"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2945', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:2945"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2945',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2945"}),(s:Symptom{identifier:"D000860"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2945', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8337"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8337', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8337"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8337', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8337"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8337', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8337"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8337', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8622"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8622', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8622"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8622', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8622"}),(s:Symptom{identifier:"C0086066"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8622',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8622"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8622',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8622"}),(s:Symptom{identifier:"C0443253"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8622',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2942"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2942', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2942"}),(s:Symptom{identifier:"D012135"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2942', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2942"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2942', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:2942"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:2942', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050518"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050518', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:0050518"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050518', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:0050518"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:0050518',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8536"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8536', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8536"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8536', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:8536"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8536',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8536"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8536', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8536"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8536', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:8536"}),(s:Symptom{identifier:"D010292"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:8536', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"C0221512"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"C0235267"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"C0455899"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"DOID:12287"}),(s:Symptom{identifier:"C0014591"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:12287',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"DOID:11168"}),(s:Symptom{identifier:"C0009663"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'DOID:11168',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 commit 
 begin 
 MATCH ()-[l:PRESENTS_DpS]->(s:Symptom) Where not exists(l.do) Set l.do='no', l.hetionet='yes'; 
 commit