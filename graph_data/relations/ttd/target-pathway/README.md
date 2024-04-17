# 先确认以下哪些列是在原文件中可以获取？我们需要先把能提取的出来都从原文件中提取出来，那些不能提取出来的，哪些是需要做匹配，可以下一步再进行匹配。
# 我们需要知道什么是source什么是target。对于relation_type DRUGBANK::target::Compound:Gene,前面的就是source，后面的就是target
# 
source_id
source_type
target_id
target_type
source_name
target_name
relation_type  
ttd_target_id (gene)
ttd_source_id (drug)
resource

# 测试ChatGPT能否从这一段中提取出我们想要的信息。
TTDID	KEGG pathway ID	KEGG pathway name
T00039	hsa04390	Hippo signaling pathway
T00140	hsa00590	Arachidonic acid metabolism
T00140	hsa01100	Metabolic pathways
T00140	hsa04726	Serotonergic synapse
T00140	hsa04913	Ovarian steroidogenesis
T00140	hsa05145	Toxoplasmosis

请帮我把刚发给你的这一段抽取成十列的表格，十列分别是：

source_id 是TTDID
source_type都是Gene
target_id 是kegg:KEGG pathway ID,例如kegg:hsa04390
target_type都是Pathway
source_name 请先空着
target_name是 KEGG pathway name
relation_type 都是Hetionet::GpPW::Gene:Pathway
ttd_gene_id 是TTDID	
ttd_pathway_id 是KEGG pathway ID
resource都是TTD

请一步一步思考，并说出你计划你如何抽取这些列。

请给我可以在本地操作的python代码，使我可以在本地生成包含以上十列的csv文件。

# 接下来，我们需要把source_id替换成NM可以识别的数据，通过数据metching实现。

我有两个表，第一个表的一部分如下：
source_id,source_type,target_id,target_type,source_name,target_name,relation_type,ttd_gene_id,ttd_pathway_id,resource
T00039,Gene,kegg:hsa04390,Pathway,,Hippo signaling pathway,Hetionet::GpPW::Gene:Pathway,T00039,hsa04390,TTD
T00140,Gene,kegg:hsa00590,Pathway,,Arachidonic acid metabolism,Hetionet::GpPW::Gene:Pathway,T00140,hsa00590,TTD

第二个表的一部分如下；
ttd_target_id,target_name,target_id,ttd_uniprot_id,source_id,source_name,source_type,target_type,relation_type,ttd_source_id,resource
T47101,FGFR1,SYMBOL:FGFR1,FGFR1_HUMAN,D0O6UY,Pemigatinib,Compound,Gene,DRUGBANK::target::Compound:Gene,D0O6UY,TTD
T47101,FGFR1,SYMBOL:FGFR1,FGFR1_HUMAN,D09HNV,Intedanib,Compound,Gene,DRUGBANK::target::Compound:Gene,D09HNV,TTD
T47101,FGFR1,SYMBOL:FGFR1,FGFR1_HUMAN,D01PZD,Romiplostim,Compound,Gene,DRUGBANK::target::Compound:Gene,D01PZD,TTD


第一个表中的source_id与第二个表中的ttd_target_id相同，请按照这个进行匹配，合并两表。
请为第一个表增加一列，ttd_uniprot_id，值为第二列中ttd_uniprot_id这一列的值。

现要求你，撰写python代码，使我能够在本地导入这两份数据，最后生成一个新的csv文件。


# 第三步

我有两个数据表，这是我的第一个表
source_id,source_type,target_id,target_type,source_name,target_name,relation_type,ttd_gene_id,ttd_pathway_id,resource,ttd_uniprot_id
T00039,Gene,kegg:hsa04390,Pathway,,Hippo signaling pathway,Hetionet::GpPW::Gene:Pathway,T00039,hsa04390,TTD,CTGF_HUMAN
T00140,Gene,kegg:hsa00590,Pathway,,Arachidonic acid metabolism,Hetionet::GpPW::Gene:Pathway,T00140,hsa00590,TTD,LOX5_HUMAN
T00140,Gene,kegg:hsa00590,Pathway,,Arachidonic acid metabolism,Hetionet::GpPW::Gene:Pathway,T00140,hsa00590,TTD,LOX5_HUMAN
T00140,Gene,kegg:hsa00590,Pathway,,Arachidonic acid metabolism,Hetionet::GpPW::Gene:Pathway,T00140,hsa00590,TTD,LOX5_HUMAN

第二个表的一部分如下；
ttd_target_id,target_name,target_id,ttd_uniprot_id,source_id,source_name,source_type,target_type,relation_type,ttd_source_id,resource
T47101,FGFR1,SYMBOL:FGFR1,FGFR1_HUMAN,D0O6UY,Pemigatinib,Compound,Gene,DRUGBANK::target::Compound:Gene,D0O6UY,TTD
T47101,FGFR1,SYMBOL:FGFR1,FGFR1_HUMAN,D09HNV,Intedanib,Compound,Gene,DRUGBANK::target::Compound:Gene,D09HNV,TTD
T47101,FGFR1,SYMBOL:FGFR1,FGFR1_HUMAN,D01PZD,Romiplostim,Compound,Gene,DRUGBANK::target::Compound:Gene,D01PZD,TTD


请给第一个表，增加一列，ttd_gene_id,为第一个表source_id的值

请一步一步思考，说出你的计划。

请给我一个可以在本地操作的python代码。


# 增加source_name

我有两个表，第一个表的ttd_gene_id与第二个表的ttd_target_id一样，请按照这两列进行匹配。

请将第一个表的source_name的值写为第二个表的target_name的值。

请再将第一个表的source_id 改是SYMBOL:target_name,target_name为第二个表中target_name的值，例如SYMBOL:FGFR1

并帮我输出一个新的表。

给我本地操作的python代码。

请一步一步思考。