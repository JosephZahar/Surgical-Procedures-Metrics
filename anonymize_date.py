import pandas as pd

endoscopic_duration_df = pd.read_csv('/Users/macbookpro/Surgical-Procedure-Metrics/Data_Definitions/endoscopic_dur_df.csv')
procedures = set(endoscopic_duration_df["snomed_code"])
hospitals = set(endoscopic_duration_df["account_name"])

procedure_dict = dict()
hospital_dict = dict()

for i, procedure in enumerate(procedures):
    procedure_dict[procedure] = str(i+1)

for i, hospital in enumerate(hospitals):
    hospital_dict[hospital] = str(i+1)

endoscopic_duration_df["snomed_code"] = endoscopic_duration_df["snomed_code"].apply(lambda row: "Procedure " + procedure_dict[row])
endoscopic_duration_df["account_name"] = endoscopic_duration_df["account_name"].apply(lambda row: "Hospital " + hospital_dict[row])

endoscopic_duration_df.to_csv('endoscopic_dur_df_2.csv')


