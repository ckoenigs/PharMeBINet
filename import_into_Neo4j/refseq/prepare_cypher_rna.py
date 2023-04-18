list_of_labels = ["refSeq_PrimaryTranscript",
                  "refSeq_lncRNA",
                  "refSeq_mRNA",
                  # "refSeq_Exon", can be a lot of different thins also RNA but I will exclude it!
                  "refSeq_miRNA",
                  "refSeq_Transcript",
                  "refSeq_snoRNA",
                  "refSeq_rRNA",
                  "refSeq_RNasePRNA",
                  "refSeq_RNaseMRPRNA",
                  "refSeq_scRNA",
                  "refSeq_snRNA",
                  "refSeq_YRNA",
                  "refSeq_antisenseRNA",
                  "refSeq_tRNA",
                  "refSeq_vaultRNA",
                  "refSeq_telomeraseRNA",
                  "refSeq_ncRNA"
                  ]
file = open('cypher_add_label.cypher', 'w', encoding='utf-8')

for label in list_of_labels:
    query = f'Match (n:{label}) Set n:refseq_RNA ;\n'
    file.write(query)

file.close()
