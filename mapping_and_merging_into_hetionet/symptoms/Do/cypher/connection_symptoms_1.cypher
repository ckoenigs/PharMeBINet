begin 
MATCH (n:Disease{identifier:"MONDO:0017882"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017882', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017882"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017882', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017882"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017882', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017882"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017882',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017882"}),(s:Symptom{identifier:"C0235592"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017882',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017882"}),(s:Symptom{identifier:"C0221752"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017882',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017880"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017880', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017880"}),(s:Symptom{identifier:"D006396"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017880', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017880"}),(s:Symptom{identifier:"C0025323"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017880',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017881"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017881', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017881"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017881', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017881"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017881"}),(s:Symptom{identifier:"C3862404"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017881"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017881', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017881"}),(s:Symptom{identifier:"C0011175"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017881"}),(s:Symptom{identifier:"C2186261"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0015804"}),(s:Symptom{identifier:"D003248"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015804', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0015804"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015804', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0015804"}),(s:Symptom{identifier:"C2183415"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015804',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0015804"}),(s:Symptom{identifier:"C0740170"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015804',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0015804"}),(s:Symptom{identifier:"C0033377"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015804',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0015804"}),(s:Symptom{identifier:"C3552712"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015804',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0015804"}),(s:Symptom{identifier:"D018908"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015804', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001678"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001678', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001678"}),(s:Symptom{identifier:"C0017181"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001678',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001678"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001678', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001678"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001678', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018626"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018626', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018626"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018626', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018626"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018626', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018626"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018626',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018626"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018626', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018626"}),(s:Symptom{identifier:"D003248"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018626', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018626"}),(s:Symptom{identifier:"C0428977"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018626',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018626"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018626',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019359"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019359', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019359"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019359', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019359"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019359', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"C1291077"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"C0232462"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D003248"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"C0018932"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"C1291077"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"C0232462"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"D003248"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000295"}),(s:Symptom{identifier:"C0018932"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000295',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001461"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001461', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001461"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001461', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005109"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005109', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005109"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005109', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005109"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005109', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005109"}),(s:Symptom{identifier:"C0860029"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005109',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005109"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005109', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005109"}),(s:Symptom{identifier:"C0149745"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005109',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005109"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005109', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005109"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005109',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005109"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005109',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001667"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001667', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001667"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001667', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001667"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001667',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001667"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001667', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001667"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001667', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001667"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001667', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001667"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001667',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001667"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001667', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"C0542115"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"C0032285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018695"}),(s:Symptom{identifier:"C0748355"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018695',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005672"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005672',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005672"}),(s:Symptom{identifier:"C0264545"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005672',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005676"}),(s:Symptom{identifier:"C2939186"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005676',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005609"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005609', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005609"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005609', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005609"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005609',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005609"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005609', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005609"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005609', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005609"}),(s:Symptom{identifier:"D010292"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005609', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000229"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000229', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000229"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000229',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000229"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000229', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000229"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000229',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005619"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005619', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005619"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005619', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005619"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005619',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005619"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005619', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005619"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005619',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005619"}),(s:Symptom{identifier:"C0019209"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005619',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005619"}),(s:Symptom{identifier:"C0023530"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005619',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000327"}),(s:Symptom{identifier:"C0028259"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000327',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005231"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005231"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005231"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005231',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005231"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005231"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005231"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005231"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005231"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017874"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017874', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017874"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017874', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017874"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017874',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017874"}),(s:Symptom{identifier:"C0023530"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017874',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017874"}),(s:Symptom{identifier:"C0040034"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017874',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019121"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019121',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019121"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019121', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019121"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019121', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004277"}),(s:Symptom{identifier:"C2127347"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004277',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004277"}),(s:Symptom{identifier:"C0232861"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004277',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005791"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005791', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005791"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005791',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005791"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005791', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005791"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005791',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005790"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005790', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005790"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005790', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005790"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005790',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005790"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005790', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005790"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005790', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005790"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005790', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005790"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005790', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005790"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005790', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017416"}),(s:Symptom{identifier:"D018908"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017416', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017416"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017416', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017416"}),(s:Symptom{identifier:"D012891"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017416', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017416"}),(s:Symptom{identifier:"C1260922"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017416',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000282"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000282"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000282"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000282"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000282"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000282"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0235267"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0020649"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0022660"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0235267"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0020649"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000283"}),(s:Symptom{identifier:"C0022660"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000283',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"C1390214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"C0035078"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"C1390214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000284"}),(s:Symptom{identifier:"C0035078"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000284',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017879"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017879', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017879"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017879', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017879"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017879', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017879"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017879', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017879"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017879', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000286"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000286', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003781"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003781', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0003781"}),(s:Symptom{identifier:"C0239574"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003781',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0003781"}),(s:Symptom{identifier:"C0232292"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003781',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005991"}),(s:Symptom{identifier:"C0035021"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005991',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005991"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005991', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005991"}),(s:Symptom{identifier:"C0241032"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005991',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005996"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005996', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005996"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005996', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005996"}),(s:Symptom{identifier:"C0034888"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005996',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005996"}),(s:Symptom{identifier:"C0151686"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005996',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001577"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001577',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001577"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001577', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001577"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001577', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001577"}),(s:Symptom{identifier:"D012135"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001577', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001577"}),(s:Symptom{identifier:"C0476273"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001577',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001881"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001881', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001881"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001881"}),(s:Symptom{identifier:"C0020649"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001881"}),(s:Symptom{identifier:"C0026766"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001881"}),(s:Symptom{identifier:"C0237849"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001881',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001881"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001881', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001881"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001881', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001881"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001881', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002099"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002099',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002099"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002099', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002099"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002099',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002099"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002099', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002099"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002099',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002099"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002099', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002099"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002099',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002099"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002099', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005647"}),(s:Symptom{identifier:"C0009663"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005647',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005850"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005850', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005850"}),(s:Symptom{identifier:"C0024225"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005850',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005850"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005850',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005688"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005688', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005688"}),(s:Symptom{identifier:"C0013369"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005688',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005688"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005688', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005768"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005768', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005768"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005768', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005768"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005768', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005768"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005768', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005768"}),(s:Symptom{identifier:"C0278008"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005768',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005768"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005768', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005768"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005768', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005769"}),(s:Symptom{identifier:"D014012"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005769', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005769"}),(s:Symptom{identifier:"D014717"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005769', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005769"}),(s:Symptom{identifier:"D004433"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005769', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005769"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005769', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005641"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005641', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005641"}),(s:Symptom{identifier:"C0019209"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005641',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005641"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005641',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005641"}),(s:Symptom{identifier:"C0002871"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005641',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005913"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005913', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005913"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005913', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005913"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005913', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005913"}),(s:Symptom{identifier:"C0039231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005913',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005911"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005911', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005911"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005911', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005767"}),(s:Symptom{identifier:"C0235957"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005767',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005767"}),(s:Symptom{identifier:"C0243026"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005767',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000989"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000989', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000989"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000989', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000989"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000989', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000989"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000989', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000989"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000989',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005649"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005649', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005649"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005649', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005649"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005649', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005649"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005649', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018950"}),(s:Symptom{identifier:"D009133"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018950', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018950"}),(s:Symptom{identifier:"C0699815"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018950',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018950"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018950', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"C0030196"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"C0030196"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001972"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001972', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0003763"}),(s:Symptom{identifier:"C0236720"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003763',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0003763"}),(s:Symptom{identifier:"C0857051"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003763',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0003763"}),(s:Symptom{identifier:"C0870186"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003763',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004712"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004712', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004712"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004712',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"C0013144"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"C0441548"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"C0013144"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"C0441548"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001137"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001137',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"C2830004"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"C4084858"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D014202"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"C2830004"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"C4084858"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D014202"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000276"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000276', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005787"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005787', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005787"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005787', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005787"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005787', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005787"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005787', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005787"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005787', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005784"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005784"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005784"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005784"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005784"}),(s:Symptom{identifier:"D011693"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005784"}),(s:Symptom{identifier:"D011507"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005784"}),(s:Symptom{identifier:"C0035078"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005784',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005306"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D010146"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='MONDO:0005306'; 
MATCH (n:Disease{identifier:"MONDO:0005788"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005788', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005788"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005788', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005788"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005788',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005788"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005788', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005788"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005788', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005788"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005788', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005788"}),(s:Symptom{identifier:"C0426396"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005788',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005788"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005788', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005788"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005788', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"C2675627"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"C0426396"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"C0240735"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"C0037317"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"C0233514"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"C2830004"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005789"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005789', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0006052"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006052', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0006052"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006052', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0006052"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006052', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0006052"}),(s:Symptom{identifier:"C0032227"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006052',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0006052"}),(s:Symptom{identifier:"C0016059"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006052',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"C0424790"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"C0424790"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000273"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000273', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001112"}),(s:Symptom{identifier:"C0442800"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001112',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001112"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001112', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001112"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001112', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001112"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001112',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001112"}),(s:Symptom{identifier:"C0442800"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001112',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001112"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001112', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001112"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001112', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001112"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001112',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0007874"}),(s:Symptom{identifier:"C1857042"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0007874',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0007874"}),(s:Symptom{identifier:"C1865017"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0007874',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005645"}),(s:Symptom{identifier:"C0267373"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005645',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005645"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005645', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005645"}),(s:Symptom{identifier:"C0002871"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005645',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005645"}),(s:Symptom{identifier:"C1443924"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005645',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005645"}),(s:Symptom{identifier:"C0162429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005645',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005091"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005091', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005091"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005091', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005091"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005091',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005091"}),(s:Symptom{identifier:"D000860"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005091', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005904"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005904', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005901"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005901', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005901"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005901', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005901"}),(s:Symptom{identifier:"C0424790"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005901',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005901"}),(s:Symptom{identifier:"C0032285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005901',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005901"}),(s:Symptom{identifier:"D008580"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005901', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005901"}),(s:Symptom{identifier:"C0039231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005901',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0012727"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D005334"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='MONDO:0012727'; 
 MATCH (n:Disease{identifier:"MONDO:0012727"}),(s:Symptom{identifier:"C0085649"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0012727',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005751"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005751', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005751"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005751',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005751"}),(s:Symptom{identifier:"C0032231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005751',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005751"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005751', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0006692"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006692',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0006692"}),(s:Symptom{identifier:"D004401"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006692', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"D012135"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"C0232292"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"D012135"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004784"}),(s:Symptom{identifier:"C0232292"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004784',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005634"}),(s:Symptom{identifier:"C0595862"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005634',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005634"}),(s:Symptom{identifier:"C0162285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005634',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005634"}),(s:Symptom{identifier:"D020795"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005634', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005634"}),(s:Symptom{identifier:"C0235267"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005634',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005634"}),(s:Symptom{identifier:"C0235263"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005634',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005632"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005632', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005632"}),(s:Symptom{identifier:"C0008033"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005632',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005632"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005632', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005632"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005632', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005632"}),(s:Symptom{identifier:"D000860"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005632', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001620"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001620', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001620"}),(s:Symptom{identifier:"C0039231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001620',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001620"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001620',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001620"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001620',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"C0002871"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"C0002871"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000304"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000304',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000265"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000265', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000265"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000265', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002967"}),(s:Symptom{identifier:"C0240941"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002967',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002842"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002842', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002842"}),(s:Symptom{identifier:"D004415"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002842', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002842"}),(s:Symptom{identifier:"C1291077"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002842',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002842"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002842', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002842"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002842', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001154"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001154', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001154"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001154',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001154"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001154',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001154"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001154', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001154"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001154',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001154"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001154',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001118"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001118',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018312"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018312',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018312"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018312', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018312"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018312',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018312"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018312', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000339"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000339', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000339"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000339', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000709"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000709', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000709"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000709', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000709"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000709', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000708"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000708', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000708"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000708', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000708"}),(s:Symptom{identifier:"D009120"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000708', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000344"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000344', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000344"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000344', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000344"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000344',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000344"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000344', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000344"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000344', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000344"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000344',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005812"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005812', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005812"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005812', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005812"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005812',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005812"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005812',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005812"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005812', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005812"}),(s:Symptom{identifier:"C2957106"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005812',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005812"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005812', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005812"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005812',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0015200"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015200', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0015200"}),(s:Symptom{identifier:"C0027498"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015200',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005875"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005875',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005875"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005875', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005875"}),(s:Symptom{identifier:"C0425449"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005875',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005875"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005875', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005875"}),(s:Symptom{identifier:"C0231706"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005875',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005875"}),(s:Symptom{identifier:"C0239182"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005875',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019380"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019380', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019380"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019380', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019380"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019380', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019380"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019380', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019380"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019380', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019380"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019380',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019380"}),(s:Symptom{identifier:"C0278061"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019380',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019380"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019380',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005971"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005971', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005971"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005971', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005971"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005971', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005971"}),(s:Symptom{identifier:"D009120"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005971', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005971"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005971',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005708"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005708', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005708"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005708', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005708"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005708', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005532"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005532', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005532"}),(s:Symptom{identifier:"C0267596"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005532',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005532"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005532',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0015453"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015453', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0015453"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015453', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018661"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018661', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0018661"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018661',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018661"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018661', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0018661"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0018661', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005977"}),(s:Symptom{identifier:"C0522510"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005977',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005977"}),(s:Symptom{identifier:"D020234"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005977', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005977"}),(s:Symptom{identifier:"D006941"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005977', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005977"}),(s:Symptom{identifier:"D010292"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005977', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005977"}),(s:Symptom{identifier:"C0242350"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005977',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005700"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005700', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005700"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005700', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005700"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005700', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005700"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005700', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005700"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005700', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005700"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005700',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005700"}),(s:Symptom{identifier:"C0005758"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005700',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020502"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020502', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020502"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020502', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020502"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020502', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020502"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020502', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0020502"}),(s:Symptom{identifier:"C0036973"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020502',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0020502"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020502',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020502"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020502', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020502"}),(s:Symptom{identifier:"D006472"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020502', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005706"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005706',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005706"}),(s:Symptom{identifier:"C0003864"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005706',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0011284"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0011284',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005534"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005534', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005534"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005534', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005534"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005534', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005534"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005534', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001024"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001024', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001024"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001024', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001024"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001024', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001024"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001024', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019669"}),(s:Symptom{identifier:"C0392025"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019669',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000238"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000238', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000238"}),(s:Symptom{identifier:"C0024205"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000238',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000238"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000238', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000238"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000238',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000238"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000238', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000238"}),(s:Symptom{identifier:"C0024205"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000238',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000238"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000238', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000238"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000238',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"C0040034"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"C0019104"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"C0040034"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000310"}),(s:Symptom{identifier:"C0019104"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000310',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000261"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000261', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000261"}),(s:Symptom{identifier:"C0332575"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000261',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000261"}),(s:Symptom{identifier:"C0038999"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000261',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000261"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000261',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017878"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017878', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017878"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017878', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017878"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017878', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017878"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017878', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017878"}),(s:Symptom{identifier:"C0036974"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017878',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017878"}),(s:Symptom{identifier:"C0019080"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017878',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0008039"}),(s:Symptom{identifier:"C0221170"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0008039',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0008039"}),(s:Symptom{identifier:"D012678"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0008039', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0008039"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0008039', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002520"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002520', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002520"}),(s:Symptom{identifier:"C0442874"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002520',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002520"}),(s:Symptom{identifier:"C0262385"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002520',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002520"}),(s:Symptom{identifier:"C0033975"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002520',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005130"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D015746"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='MONDO:0005130'; 
MATCH (n:Disease{identifier:"MONDO:0005130"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D003248"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='MONDO:0005130'; 
MATCH (n:Disease{identifier:"MONDO:0005130"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D003967"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='MONDO:0005130'; 
 MATCH (n:Disease{identifier:"MONDO:0005130"}),(s:Symptom{identifier:"C0027498"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005130',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005130"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005130',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001701"}),(s:Symptom{identifier:"C0221198"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001701',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001701"}),(s:Symptom{identifier:"D006396"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001701', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001701"}),(s:Symptom{identifier:"C1443924"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001701',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001701"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001701',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001701"}),(s:Symptom{identifier:"C0221198"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001701',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001701"}),(s:Symptom{identifier:"D006396"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001701', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001701"}),(s:Symptom{identifier:"C1443924"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001701',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001701"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001701',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005683"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005683', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005683"}),(s:Symptom{identifier:"C0038984"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005683',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005683"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005683', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005683"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005683', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005683"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005683', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005683"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005683', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005138"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005138', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005138"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005138', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005138"}),(s:Symptom{identifier:"D006469"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005138', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"C0022107"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"C0947509"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"C0233818"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"D007319"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"C0022107"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"C0947509"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"C0233818"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"D007319"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000335"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000335', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001621"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001621', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001621"}),(s:Symptom{identifier:"C0039231"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001621',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001621"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001621',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001621"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001621',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0016453"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016453',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0016453"}),(s:Symptom{identifier:"D004172"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016453', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0016453"}),(s:Symptom{identifier:"D004401"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016453', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0016453"}),(s:Symptom{identifier:"D055154"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016453', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0016453"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016453',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D004244"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"C0233514"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"C0233417"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D008569"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D007319"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D004244"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"C0233514"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"C0233417"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D008569"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"D007319"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000336"}),(s:Symptom{identifier:"C0344232"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000336',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005888"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005888', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005888"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005888', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005888"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005888',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005888"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005888', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005888"}),(s:Symptom{identifier:"C0032285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005888',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000710"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000710', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000710"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000710', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000710"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000710', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000710"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000710',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000710"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000710', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000710"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000710', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000710"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000710', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000710"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000710',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"C0221512"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"C0235267"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005737"}),(s:Symptom{identifier:"D006606"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005737', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005736"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005736',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005736"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005736', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005736"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005736', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005736"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005736', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005736"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005736', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005736"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005736', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002572"}),(s:Symptom{identifier:"C0850149"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002572',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002572"}),(s:Symptom{identifier:"D059246"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002572', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002572"}),(s:Symptom{identifier:"C0006266"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002572',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002572"}),(s:Symptom{identifier:"D006469"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002572', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002572"}),(s:Symptom{identifier:"C0577979"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002572',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002572"}),(s:Symptom{identifier:"C0476273"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002572',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003004"}),(s:Symptom{identifier:"D001766"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003004', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004979"}),(s:Symptom{identifier:"C0232292"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004979',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004979"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D004417"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='MONDO:0004979'; 
 MATCH (n:Disease{identifier:"MONDO:0004979"}),(s:Symptom{identifier:"C2610947"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004979',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004979"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D003371"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='MONDO:0004979'; 
MATCH (n:Disease{identifier:"MONDO:0005969"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005969', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005969"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005969',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005969"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005969',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005969"}),(s:Symptom{identifier:"D053608"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005969', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005969"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005969', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005969"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005969', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005969"}),(s:Symptom{identifier:"D014202"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005969', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005969"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005969', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005969"}),(s:Symptom{identifier:"C0085621"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005969',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005502"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005502', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005502"}),(s:Symptom{identifier:"C2957106"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005502',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005502"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005502', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005502"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005502',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005684"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005684', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005684"}),(s:Symptom{identifier:"C1527347"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005684',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005684"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005684',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005684"}),(s:Symptom{identifier:"C0239043"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005684',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000248"}),(s:Symptom{identifier:"C0423798"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000248',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000248"}),(s:Symptom{identifier:"D005884"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000248', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000248"}),(s:Symptom{identifier:"C0014591"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000248',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000248"}),(s:Symptom{identifier:"C0423798"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000248',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000248"}),(s:Symptom{identifier:"D005884"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000248', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000248"}),(s:Symptom{identifier:"C0014591"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000248',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000321"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000321', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004616"}),(s:Symptom{identifier:"C0221198"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004616',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004616"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004616', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004616"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004616',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"C0038990"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"C0038990"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001857"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001857',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005124"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005124',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005124"}),(s:Symptom{identifier:"C0278134"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005124',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0016648"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016648', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0016648"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016648', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001737"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001737', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001737"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001737', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001737"}),(s:Symptom{identifier:"C0392674"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001737',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005692"}),(s:Symptom{identifier:"C0478664"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005692',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005692"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005692', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005692"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005692', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005692"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005692', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005692"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005692', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005358"}),(s:Symptom{identifier:"C0040034"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005358',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005358"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005358',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002594"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002594', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002594"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002594', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002594"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002594', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002594"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002594',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002595"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002595',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002595"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002595', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019365"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019365"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019365"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019365"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019365', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019365"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019365',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019365"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019365',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019365"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019365',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019365"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019365',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019360"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019360', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019360"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019360', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019360"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019360', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019360"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019360', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019360"}),(s:Symptom{identifier:"C0234920"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019360',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004189"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004189',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004189"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004189', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004189"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004189', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004189"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004189', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004189"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004189', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019362"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019362',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019362"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019362', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019362"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019362',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019362"}),(s:Symptom{identifier:"C3862404"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019362',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019362"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019362', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019362"}),(s:Symptom{identifier:"D053608"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019362', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019362"}),(s:Symptom{identifier:"D020795"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019362', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019362"}),(s:Symptom{identifier:"D003693"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019362', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000343"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000343', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000343"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000343', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000343"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000343',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000343"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000343', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000343"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000343', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000343"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000343',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"C0036974"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"C0277794"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005956"}),(s:Symptom{identifier:"C0036974"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005956',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001537"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001537', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001537"}),(s:Symptom{identifier:"C0282005"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001537',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001537"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001537', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001537"}),(s:Symptom{identifier:"C0282005"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001537',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002212"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002212', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002212"}),(s:Symptom{identifier:"C0817096"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002212',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002212"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002212', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002212"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002212', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002212"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002212', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002212"}),(s:Symptom{identifier:"C0817096"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002212',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002212"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002212', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002212"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002212', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005677"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005677', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001432"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001432', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001432"}),(s:Symptom{identifier:"C0035021"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001432',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001432"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001432',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001432"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001432', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"C0221512"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"C0235267"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"C0455899"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0020501"}),(s:Symptom{identifier:"C0014591"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020501',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0020500"}),(s:Symptom{identifier:"C0019080"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0020500',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005810"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005810', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005810"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005810', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005810"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005810',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005810"}),(s:Symptom{identifier:"C0038002"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005810',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002465"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002465', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002465"}),(s:Symptom{identifier:"D012135"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002465', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002465"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002465', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002465"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002465', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000330"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000330',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000331"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000331', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000331"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000331', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000331"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000331', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000331"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000331', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000331"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000331', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000331"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000331', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000332"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000332', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"D005183"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0025289"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0008526"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0020255"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"D008607"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0029420"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0240822"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0019214"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"D005183"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0025289"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0008526"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0020255"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"D008607"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0029420"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000333"}),(s:Symptom{identifier:"C0240822"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000333',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005344"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D005334"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='MONDO:0005344'; 
MATCH (n:Disease{identifier:"MONDO:0005344"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005344', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005344"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005344',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005344"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005344', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005344"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005344', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005344"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005344', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005344"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005344', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005344"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"D007565"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='MONDO:0005344'; 
MATCH (n:Disease{identifier:"MONDO:0004619"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004619', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004619"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004619', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004619"}),(s:Symptom{identifier:"C0086066"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004619',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004619"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004619',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004619"}),(s:Symptom{identifier:"C0443253"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004619',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000231"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000231"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000231',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000231"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000231',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000231"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000231"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000231',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000231"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000231',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000230"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000230', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000230"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000230',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000230"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000230', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000230"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000230',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000233"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000233', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000233"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000233',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000233"}),(s:Symptom{identifier:"C1504535"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000233',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000233"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000233', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000233"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000233',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000233"}),(s:Symptom{identifier:"C1504535"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000233',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000232"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000232',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000232"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000232',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000232"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000232',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000232"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000232',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000234"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000234', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000234"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000234', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000234"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000234',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000234"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000234',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000234"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000234', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000234"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000234', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000234"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000234',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000234"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000234',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000237"}),(s:Symptom{identifier:"C0041834"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000237',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000237"}),(s:Symptom{identifier:"C0241164"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000237',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000236"}),(s:Symptom{identifier:"C0221198"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000236',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000236"}),(s:Symptom{identifier:"D006396"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000236', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000236"}),(s:Symptom{identifier:"C1443924"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000236',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000236"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000236',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005984"}),(s:Symptom{identifier:"C0332469"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005984',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005984"}),(s:Symptom{identifier:"C0392757"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005984',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005984"}),(s:Symptom{identifier:"C0333525"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005984',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019173"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019173', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019173"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019173', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019173"}),(s:Symptom{identifier:"C0003467"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019173',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019173"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019173', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019173"}),(s:Symptom{identifier:"C0085631"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019173',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019173"}),(s:Symptom{identifier:"D003693"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019173', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019173"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019173',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019173"}),(s:Symptom{identifier:"C1609481"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019173',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019173"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019173', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0007244"}),(s:Symptom{identifier:"C0238792"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0007244',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0007244"}),(s:Symptom{identifier:"C0022107"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0007244',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005119"}),(s:Symptom{identifier:"C0037299"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005119',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005119"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005119', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005119"}),(s:Symptom{identifier:"C0232462"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005119',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005119"}),(s:Symptom{identifier:"C0151594"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005119',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005119"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005119', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005119"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005119', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005460"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005460', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001353"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001353', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001353"}),(s:Symptom{identifier:"D012912"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001353', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001353"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001353',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001353"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001353', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001353"}),(s:Symptom{identifier:"D012912"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001353', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001353"}),(s:Symptom{identifier:"C1260880"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001353',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005948"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005948', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005948"}),(s:Symptom{identifier:"C0022107"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005948',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0006019"}),(s:Symptom{identifier:"C0037284"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006019',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005118"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005118',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000225"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000225',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019209"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019209', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019209"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019209',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019209"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019209',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019209"}),(s:Symptom{identifier:"D053608"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019209', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019209"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019209', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019209"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019209', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019209"}),(s:Symptom{identifier:"D014202"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019209', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019209"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019209', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019209"}),(s:Symptom{identifier:"C0085621"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019209',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001449"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001449', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001449"}),(s:Symptom{identifier:"C1971624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001449',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001449"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001449', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001449"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001449', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001449"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001449',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001449"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001449', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001449"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001449', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019378"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019378', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019378"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019378', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019378"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019378', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019378"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019378', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019378"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019378', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004656"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004656', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004656"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004656',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004656"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004656', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0004656"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004656', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0004656"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0004656',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017872"}),(s:Symptom{identifier:"C0019080"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017872',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005829"}),(s:Symptom{identifier:"D053609"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005829', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005829"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005829', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005829"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005829', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005828"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005828', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005828"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005828', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005828"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005828', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005828"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005828', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005828"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005828',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005828"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005828', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005828"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005828', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017877"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017877', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017877"}),(s:Symptom{identifier:"C3887500"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017877',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017877"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017877', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017877"}),(s:Symptom{identifier:"D004244"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017877', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017877"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017877', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017877"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017877',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"C3714552"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"C0014591"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"D005884"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"D006396"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"C0025222"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017876"}),(s:Symptom{identifier:"C0025323"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017876',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017875"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017875', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017875"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017875', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017875"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017875', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017875"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017875', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017875"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017875', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000740"}),(s:Symptom{identifier:"D012913"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000740', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000740"}),(s:Symptom{identifier:"C0264618"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000740',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000740"}),(s:Symptom{identifier:"C0029883"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000740',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000740"}),(s:Symptom{identifier:"D012913"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000740', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000740"}),(s:Symptom{identifier:"C0264618"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000740',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000740"}),(s:Symptom{identifier:"C0029883"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000740',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002282"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002282"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002282',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002282"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002282"}),(s:Symptom{identifier:"C0741585"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002282',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002282"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0002282"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002282',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0002282"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0002282', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001916"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001916', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"D010291"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"C1406778"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"C0029124"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"C0155088"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"D006319"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"D010291"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"C1406778"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"C0029124"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"C0155088"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005821"}),(s:Symptom{identifier:"D006319"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005821', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"C0151826"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"D001416"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"D003967"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"C0009763"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"C0151602"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005820"}),(s:Symptom{identifier:"C2748540"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005820',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005825"}),(s:Symptom{identifier:"D007565"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005825', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005825"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005825', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005825"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005825', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005825"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005825', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005825"}),(s:Symptom{identifier:"C0019209"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005825',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005831"}),(s:Symptom{identifier:"C0497156"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005831',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005831"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005831', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005831"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005831', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005831"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005831', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005831"}),(s:Symptom{identifier:"C0028081"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005831',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005831"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005831', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005773"}),(s:Symptom{identifier:"D000381"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005773', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005773"}),(s:Symptom{identifier:"D060705"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005773', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005773"}),(s:Symptom{identifier:"D000377"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005773', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"C2055125"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"D053608"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"D003128"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"D014202"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"D012640"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"D018908"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"D001766"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"C0028643"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019376"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019376', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000228"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000228', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000228"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000228', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005770"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005770', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005770"}),(s:Symptom{identifier:"C4282165"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005770',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019632"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019632', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019632"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019632', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019632"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019632', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005774"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005774', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005774"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005774', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005774"}),(s:Symptom{identifier:"C0038990"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005774',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005774"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005774', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005774"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005774', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005774"}),(s:Symptom{identifier:"C0877322"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005774',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005774"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005774', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005774"}),(s:Symptom{identifier:"C3672042"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005774',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001699"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001699', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001699"}),(s:Symptom{identifier:"C0085624"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001699',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001699"}),(s:Symptom{identifier:"C0392757"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001699',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005779"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005779', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005779"}),(s:Symptom{identifier:"C0232462"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005779',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005779"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005779',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005779"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005779',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000227"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000227', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000227"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000227',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000227"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000227',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000227"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000227', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000227"}),(s:Symptom{identifier:"C0521172"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000227',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000227"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000227',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001973"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001973', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001973"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001973', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001973"}),(s:Symptom{identifier:"C0038990"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001973',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001973"}),(s:Symptom{identifier:"D015431"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001973', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001973"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001973',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001973"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001973', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001973"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001973', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001973"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001973', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017373"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017373', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017373"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017373',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017373"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017373', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017373"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017373', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017373"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017373', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017373"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017373',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017373"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017373', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017373"}),(s:Symptom{identifier:"C3697716"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017373',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000345"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000345', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001260"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001260', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001260"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001260', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001260"}),(s:Symptom{identifier:"D011537"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001260', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D011693"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D011507"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"C0035078"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D005483"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D011693"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"D011507"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000346"}),(s:Symptom{identifier:"C0035078"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000346',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000341"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000341', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000341"}),(s:Symptom{identifier:"C3697716"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000341',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000341"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000341', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000341"}),(s:Symptom{identifier:"C3697716"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000341',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000340"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000340', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000340"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000340',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000340"}),(s:Symptom{identifier:"D004417"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000340', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000340"}),(s:Symptom{identifier:"C0011168"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000340',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000342"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000342', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000342"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000342', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000342"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000342',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000342"}),(s:Symptom{identifier:"C0024205"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000342',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000342"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000342', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0000342"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000342', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000342"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000342',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0000342"}),(s:Symptom{identifier:"C0024205"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0000342',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001195"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001195"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001195"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001195"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001195"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001195"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001195"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001195"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001195', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017775"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017775', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017775"}),(s:Symptom{identifier:"C0476273"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017775',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017775"}),(s:Symptom{identifier:"D002637"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017775', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017775"}),(s:Symptom{identifier:"C0221512"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017775',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017776"}),(s:Symptom{identifier:"C0032285"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017776',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017776"}),(s:Symptom{identifier:"C0007642"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017776',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"C0700590"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"C0700590"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D000855"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0001190"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0001190', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0006005"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006005', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0006005"}),(s:Symptom{identifier:"D023341"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006005', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0006005"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006005',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0006005"}),(s:Symptom{identifier:"C2957106"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006005',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0006005"}),(s:Symptom{identifier:"D020795"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006005', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019186"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019186', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019186"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019186', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019186"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019186', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0019186"}),(s:Symptom{identifier:"C0008033"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019186',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019186"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019186', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0019186"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0019186', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0006000"}),(s:Symptom{identifier:"C0232487"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006000',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0006000"}),(s:Symptom{identifier:"D010146"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006000', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0006000"}),(s:Symptom{identifier:"D004614"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0006000', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017941"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017941', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017941"}),(s:Symptom{identifier:"D018771"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017941', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017941"}),(s:Symptom{identifier:"C0423791"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017941',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0017572"}),(s:Symptom{identifier:"C0013144"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017572',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017572"}),(s:Symptom{identifier:"D003221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017572', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017572"}),(s:Symptom{identifier:"D012678"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017572', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0017572"}),(s:Symptom{identifier:"D010243"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0017572', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005834"}),(s:Symptom{identifier:"C1735976"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005834',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005834"}),(s:Symptom{identifier:"C0024225"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005834',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005668"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005668', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0005668"}),(s:Symptom{identifier:"C0231218"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005668',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005668"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005668', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0015243"}),(s:Symptom{identifier:"D003371"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015243', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0015243"}),(s:Symptom{identifier:"D012135"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015243', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0015243"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0015243', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005662"}),(s:Symptom{identifier:"D009120"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005662', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005662"}),(s:Symptom{identifier:"D015746"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005662', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005662"}),(s:Symptom{identifier:"D009325"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005662', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0005662"}),(s:Symptom{identifier:"D006209"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0005662', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0016003"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016003', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0016003"}),(s:Symptom{identifier:"D063806"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016003', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0016003"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016003', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0016003"}),(s:Symptom{identifier:"C0015230"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0016003',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D005334"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"C0242429"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D006261"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D014839"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D005221"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
  MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"C0151315"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); 
 MATCH (n:Disease{identifier:"MONDO:0003231"}),(s:Symptom{identifier:"D013035"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'MONDO:0003231', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); 
 commit 
 begin 
 MATCH ()-[l:PRESENTS_DpS]->(s:Symptom) Where not exists(l.do) Set l.do='no', l.hetionet='yes'; 
 commit