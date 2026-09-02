import pandas as pd 
data={
    "product":["Laptop","Phone","Keyboard"],
    "sales":[50000,30000,10000]
}
df=pd.DataFrame(data)
print(df)
print()
print("Total Sales:",df["sales"].sum())