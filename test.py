import pandas as pd
import sqlite3

conn = sqlite3.connect('db-11.sqlite3')
df = pd.read_sql('select * from file_library_kgu', conn)
df.to_excel('result.xlsx', index=False)