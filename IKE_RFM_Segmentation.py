#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd

df=pd.read_csv("RetaileCleaned.csv", header=None)
df.columns =["Invoice", "StockCode",  "Description",  "Quantity",  "InvoiceDate",  "Price",  "Customer_ID",  "Country",  "SourceSheet"]

df["InvoiceDate"]=pd.to_datetime(df["InvoiceDate"])
print(df.shape)
df.info()


# In[15]:


# filter and calculate recency frequency monetary

rfm_data=df[(df["Customer_ID" ].notna()) & (df["Quantity"] > 0)].copy()
snapshot_data=pd.to_datetime("2011-12-10")


rfm=rfm_data.groupby('Customer_ID').agg(
    Recency=("InvoiceDate", lambda x: (snapshot_data - x.max()).days),
    frequency=("Invoice", "nunique"),
    monetary=("Quantity", lambda x: (x * rfm_data.loc[x.index, "Price"]).sum())
).reset_index()


# In[17]:


# Score Customer and assign business segement 

rfm['R_Score'] = pd .qcut(rfm['Recency'], 5, labels=[5,4,3,2,1]).astype(int)
rfm['F_Score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
rfm['M_Score'] =pd.qcut(rfm['monetary'],5, labels=[1,2,3,4,5]).astype(int)

def segment_customer(row):
    if row['R_Score'] >= 4 and row['F_Score'] >= 4 and row['M_Score'] >=4:
        return 'Champions'
    elif row['R_Score'] >= 3 and row['F_Score'] >= 3:
        return 'Loyal'
    elif row['R_Score'] >= 2 and row['F_Score'] >= 3:
        return 'At Risk'
    elif row['R_Score'] >= 4 and row['F_Score'] >= 2:
        return 'New'
    elif row['R_Score'] >= 3 and row['F_Score'] >= 2:
        return 'Need Attention'
    else:
        return 'Lost'


rfm['segment'] = rfm .apply(segment_customer, axis=1)
rfm['IsChurned'] = rfm['Recency'] > 90




# In[18]:


# merge rfm result back onto transaction and export

df=df[(df['Customer_ID'].notna()) & (df["Quantity"] > 0 )].copy()
df['InoviceMonth'] =df['InvoiceDate'].dt.to_period('M').dt.to_timestamp()
df['Revenue'] =df['Quantity'] * df['Price']


df_final=df.merge(
    rfm[['Customer_ID', 'Recency', 'frequency', 'monetary', 'R_Score', 'F_Score', 'M_Score', 'segment', 'IsChurned']],
    on='Customer_ID', how='left'
)

df_final.to_excel("EcommerceDashboardData.xlsx" , index=False)


# In[ ]:




