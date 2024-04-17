# 第一步：提取出这个adverse_reactions_active_labels中对应的副作用、疾病和药物的信息。需要生成以下几列：
source_id     
source_type
target_id
target_type
source_name
target_name
relation_type  
resource
ttd_target_id (disease) 
ttd_source_id (drug)

# Relation type:  DRUGBANK::target::Compound:Symptom

# 向ChatGPT问题：
s
set_id,spl_version,pt_meddra_id,pt_meddra_term,num_ingredients,ingredients_rxcuis,ingredients_names
dffb4544-0e47-40cd-9baa-d622075838cc,1,10000059,Abdominal discomfort,1,6916,metolazone
dffb4544-0e47-40cd-9baa-d622075838cc,1,10000060,Abdominal distension,1,6916,metolazone
dffb4544-0e47-40cd-9baa-d622075838cc,1,10000081,Abdominal pain,1,6916,metolazone

# 我有一个很大的表，以上是其中的一部分。请帮我从数据中抽取以下信息，并输出出一个新的表格，包包含以下十列：

onsides_drug_id  就是 ingredients_rxcuis的值
source_id 就是 RxNorm:ingredients_rxcuis的值
source_name 就是 ingredients_names
source_type 就是 Compound

onsides_adverse_reaction_id 就是 pt_meddra_id
target_id 就是 Meddra:pt_meddra_id的值
target_name 就是 ingredients_names
target_type 就是 Symptom
relation_type 就是 DRUGBANK::target::Compound:Symptom
resource 就是 nSides

请你一步一步的思考，说出你的计划。

我本地有一个非常大的数据表。请给我可以在本地操作的python代码，使我可以在本地生成包含以上十列的csv文件。

