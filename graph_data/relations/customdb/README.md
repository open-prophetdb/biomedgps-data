### CustomDB

Download from the prophet-studio.3steps.cn and upload to the customdb folder.

You can connect to the database and fetch the related records by using the following sql query:

```sql
SELECT relation_type,source_name,source_type,source_id,target_name,target_type,target_id,key_sentence,pmid FROM biomedgps_knowledge_curation WHERE curator = '1635231996@qq.com' AND source_id != 'Unknown:Unknown' AND target_id != 'Unknown:Unknown';
```
