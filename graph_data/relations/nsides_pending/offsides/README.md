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

drug_rxnorn_id,drug_concept_name,condition_meddra_id,condition_concept_name,A,B,C,D,PRR,PRR_error,mean_reporting_frequency
4024,"ergoloid mesylates, USP",10002034,Anaemia,6,126,21,1299,2.85714,0.45382,0.0454545
4024,"ergoloid mesylates, USP",10002965,Aplasia pure red cell,1,131,1,1319,10.0,1.41126,0.00757576
4024,"ergoloid mesylates, USP",10013442,Disseminated intravascular coagulation,1,131,6,1314,1.66667,1.07626,0.00757576

# 我有一个很大的表，以上是其中的一部分。请帮我从数据中抽取以下信息，并输出出一个新的表格，包包含以下十列：

drug_rxnorn_id  
source_id 就是 RxNorm:drug_rxnorn_id 的值
source_name 就是 drug_concept_name
source_type 就是 Compound

condition_meddra_id 
target_id 就是 Meddra:condition_meddra_id 的值
target_name 就是 condition_concept_name
target_type 就是 Symptom
relation_type 就是 DRUGBANK::target::Compound:Symptom
resource 就是 nSides

请你一步一步的思考，说出你的计划。

我本地有一个非常大的数据表。请给我可以在本地操作的python代码，使我可以在本地生成包含以上十列的csv文件。

