import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

DB = 'patient_satisfaction.db'
CSV = 'data/cms_hospital_patient_satisfaction_2020.csv'
SCHEMA = 'schema/schema.sql'

conn=sqlite3.connect(DB)

def schema_read():
    with sqlite3.connect(DB) as conn:
        with open(SCHEMA, 'r') as f:
            conn.executescript(f.read())

def data_extract():
    df = pd.read_csv(CSV)
    return df

def trans_load(df):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        #Hospitals
        hos_df = df[['Facility ID', 'Facility Name', 'State']]
        hos_df = hos_df.drop_duplicates(subset=['Facility ID'])
        hos_df.columns = ['facility_id','facility_name','state']
        for row in hos_df.itertuples(index=False):
            cursor.execute("""
                INSERT OR IGNORE INTO hospitals (facility_id, facility_name, state)
                VALUES (?,?,?)
            """, row)

        #Measures
        meas_df = df[['HCAHPS Measure ID', 'HCAHPS Question', 'HCAHPS Answer Description']]
        meas_df = meas_df.drop_duplicates(subset=['HCAHPS Measure ID'])
        meas_df.columns = ['hcahps_measure_id','hcahps_question','hcahps_answer_description']
        for row in meas_df.itertuples(index=False):
            cursor.execute("""
                INSERT OR IGNORE INTO measures (hcahps_measure_id, hcahps_question, hcahps_answer_description)
                VALUES (?,?,?)
            """, row)

        #Ratings
        rat_df = df[['Facility ID', 'HCAHPS Measure ID', 'Patient Survey Star Rating', 'Patient experience national comparison']].drop_duplicates()
        rat_df = rat_df.dropna(subset=['Facility ID', 'HCAHPS Measure ID'])
        rat_df = rat_df.drop_duplicates()
        rat_df.columns = ['facility_id','hcahps_measure_id','patient_survey_star_rating','patient_experience_national_comparison']
        for row in rat_df.itertuples(index=False):
            cursor.execute("""
                INSERT OR IGNORE INTO ratings (facility_id, hcahps_measure_id, patient_survey_star_rating, patient_experience_national_comparison)
                VALUES (?,?,?,?)
            """, row)
    
def run_etl():
    schema_read()
    df = data_extract()
    trans_load(df)

#Analysis

#Find the strongest states when it comes to patient satisfaction
print('#1 What states have the highest average patient satisfaction rating?') 
q1="""
SELECT h.state, ROUND(AVG(r.patient_survey_star_rating),2) AS avg_rating
FROM ratings r
JOIN hospitals h ON r.facility_id = h.facility_id
WHERE r.patient_survey_star_rating IS NOT NULL
GROUP BY h.state
ORDER BY avg_rating DESC
"""
df_q1 = pd.read_sql_query(q1, conn)
print(df_q1.head(10))


#Find the areas of improvement in patient satisfaction 
print('#2 What HCAHPS measures have the lowest average score?') 
q2="""
SELECT m.hcahps_measure_id,m.hcahps_question, ROUND(AVG(r.patient_survey_star_rating),2) AS avg_rating
FROM ratings r
JOIN measures m ON r.hcahps_measure_id = m.hcahps_measure_id
WHERE r.patient_survey_star_rating IS NOT NULL
GROUP BY r.hcahps_measure_id
ORDER BY avg_rating ASC
LIMIT 5
"""
df_q2 = pd.read_sql_query(q2, conn)
print(df_q2)


#Find the strongest hospitals
print('#3 List the top 10 hospitals that have the highest average patient satisfication rank.') 
df= pd.read_csv('data/cms_hospital_patient_satisfaction_2020.csv')
df.columns =df.columns.str.strip()
df['Patient Survey Star Rating'] = pd.to_numeric(df['Patient Survey Star Rating'], errors='coerce')
t10=(df[['Facility ID', 'Facility Name', 'Patient Survey Star Rating']]
     .dropna(subset=['Patient Survey Star Rating'])
     .groupby(['Facility ID', 'Facility Name'])
     .mean(numeric_only=True)
     .sort_values(by='Patient Survey Star Rating', ascending=False)
     .head(10)
     .reset_index())

print(t10)


if __name__ == '__main__':
    run_etl()