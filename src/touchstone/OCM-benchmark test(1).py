#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().system('pip3 install git+git://github.com/Ayesha279/benchmark-comparison.git')
from touchstone import __version__
from touchstone.benchmarks.generic import Benchmark
from touchstone import decision_maker
from touchstone import databases
from touchstone.utils.lib import mergedicts, flatten_and_discard
from touchstone.utils.lib import mergedicts, flatten_and_discard
from tabulate import tabulate
import pandas as pd

compute_header = []

uuid="aeed6306-b7e1-11eb-b313-e86a640406b2"
database="elasticsearch"
es_url="https://search-perfscale-dev-chmf5l4sh66lvxbnadi4bznl3a.us-west-2.es.amazonaws.com"
benchmark=Benchmark(open("config.json"), database)
main = {}

for compute in benchmark.compute_map['ocm-requests'] :
    conn=databases.grab(database,es_url)
    result=conn.emit_compute_dict(uuid,
                                  compute,
                                  "ocm-requests",
                                  "uuid")
    mergedicts(result,main)
    
for key in compute.get("filter", []):
        compute_header.append(key.split(".keyword")[0])
for bucket in compute.get("buckets", []):
        compute_header.append(bucket.split(".keyword")[0])
for extra_h in ["key", 'uuid', "value"]:
        compute_header.append(extra_h)


        row_list = []
        
        
flatten_and_discard(main, compute_header, row_list)
print(
    tabulate(row_list, headers=compute_header, tablefmt="pretty")
)

test5 = tabulate(row_list, headers=compute_header, tablefmt="pretty")


# In[61]:


print(test5)


# In[64]:


test5 =pd.DataFrame.from_records(
    [
        (level1, level2, level3, level4, level5, level6, level7, level8, leaf)
        for level1, level2_dict in result.items()
        for level2, level3_dict in level2_dict.items()
        for level3, level4_dict in level3_dict.items()
        for level4, level5_dict in level4_dict.items()
        for level5, level6_dict in level5_dict.items()
        for level6, level7_dict in level6_dict.items()
        for level7, level8_dict in level7_dict.items()
        for level8, leaf in level8_dict.items()
    ],
    columns=['type1', 'code', 'type2', 'Bytes_in', 'type3','Bytes_out', 'KEY', 'UUID', 'VALUE']
)


# In[65]:


print(test5)


# # 

# In[3]:


df1 =pd.DataFrame.from_records(
   [
       (level1, level2, level3, level4, level5, level6, level7, level8, leaf)
       for level1, level2_dict in result.items()
       for level2, level3_dict in level2_dict.items()
       for level3, level4_dict in level3_dict.items()
       for level4, level5_dict in level4_dict.items()
       for level5, level6_dict in level5_dict.items()
       for level6, level7_dict in level6_dict.items()
       for level7, level8_dict in level7_dict.items()
       for level8, leaf in level8_dict.items()
   ],
   columns=['type1', 'code', 'type2', 'Bytes_in', 'type3','Bytes_out', 'KEY', 'UUID', 'VALUE']
)


# In[5]:


df1 =df1.drop(columns=['type1', 'type2', 'type3'])


# In[6]:


df1.insert(0, 'New_ID', range(1, 1 + len(df1)))


# In[7]:


print(df1)


# In[59]:



import pandas as pd
import matplotlib.pyplot as plt


fig, ax = plt.subplots(2, figsize=(10, 6))
ax[0].scatter(x = df1['VALUE'], y = df1['Bytes_in'], c = df1['code'], cmap='Spectral')
ax[0].set_xlabel("avrage latency")
ax[0].set_ylabel("Bytes_in")

ax[1].scatter(x = df1['VALUE'], y = df1['Bytes_out'], c = df1['code'], cmap='Spectral')
ax[1].set_xlabel("avrage latency")
ax[1].set_ylabel("Bytes_out")


plt.show()


# In[ ]:




