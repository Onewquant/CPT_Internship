import pandas as pd
import numpy as np

# 기본정보 설정 (prep.할 type, 약물 이름)

result_type = 'Phoenix'
result_type = 'R'

drug = 'Metformin'

input_file_dir_path = '.'
result_file_dir_path = '.'


# 경로 설정 및 데이터 불러오기

input_file_name = f"Summer_Internship_Metformin_Conc.xlsx"
input_file_path = f"{input_file_dir_path}/{input_file_name}"

result_file_name = f"CKD379_ConcPrep_{drug}({result_type}).csv"
result_file_path = f"{result_file_dir_path}/{result_file_name}"

df = pd.read_excel(input_file_path)

# Data Prep 수행

drug_prep_df = list()

for sn, fdf in df.groupby(by=['Subject No.']):

    fdf['ID'] = fdf['Subject No.'].copy()
    fdf['DOSE'] = 1500
    fdf['NTIME'] = fdf['Planned Time'].map(lambda x:float(x.split('h')[0]))
    fdf['ATIME'] = fdf['Actual Time'].map(lambda x: float(x))
    fdf['CONC'] = fdf['Concentration'].map(lambda x: float(x) if x not in ('BLQ', 'N.C.') else np.nan)

    if len(fdf[fdf['NTIME'] == 0])==2:
        period_change_inx = fdf[fdf['NTIME'] == 0].index[-1]
    elif len(fdf[fdf['NTIME'] == 0])==1:
        period_change_inx = len(df)+1
    else:
        print('NTIME = 0h 인 지점이 아예 없거나 3개 이상 입니다.')
        raise ValueError

    fdf['PERIOD'] = fdf.apply(lambda row: 1 if float(row.name) < period_change_inx else 2, axis=1)
    fdf['FEEDING'] = fdf.apply(lambda row: f"{row['ID'][0]}{row['PERIOD']}", axis=1).map({'A1':'FED','A2':'FASTED','B1':'FASTED','B2':'FED'})
    fdf['DRUG'] = drug

    for period, pfdf in fdf.groupby(by=['PERIOD']):

        pfdf = pfdf.sort_values(by=['NTIME'])
        pfdf.index = list(range(min(pfdf.index),min(pfdf.index)+len(pfdf)))

        if not np.isnan(np.nanmax(pfdf['CONC'])):
            tmax_inx = pfdf[pfdf['CONC'] == np.nanmax(pfdf['CONC'])].iloc[0].name
        else:
            print('All Conc Values are NAN !')
            tmax_inx = np.nan

        blq_before_tmax_inx_list = list(pfdf[(pfdf['CONC'].isna()) & (pfdf.index < tmax_inx)].index)
        blq_after_tmax_inx_list = list(pfdf[(pfdf['CONC'].isna()) & (pfdf.index > tmax_inx)].index)

        for blqinx in blq_before_tmax_inx_list:
            pfdf.at[blqinx,'CONC'] = 0.0

        for blqinx in blq_after_tmax_inx_list:
            pfdf.at[blqinx,'CONC'] = np.nan

        if result_type == 'Phoenix':
            pfdf['CONC'] = pfdf['CONC'].map(lambda x: str(x) if not np.isnan(x) else '.')
            drug_prep_df.append(pfdf[['ID', 'DOSE', 'NTIME', 'ATIME', 'CONC', 'PERIOD', 'FEEDING', 'DRUG']])
        elif result_type == 'R':
            drug_prep_df.append(pfdf[['ID', 'DOSE', 'NTIME', 'ATIME', 'CONC', 'PERIOD', 'FEEDING', 'DRUG']].dropna())

drug_prep_df = pd.concat(drug_prep_df, ignore_index=True)

# Phoenix Winolin의 경우 Column 다음에 단위를 나타내는 행 추가

if result_type == 'Phoenix':
    unit_row_dict = {'DOSE':'mg', 'NTIME': 'h', 'ATIME': 'h', 'CONC':'ng/mL'}
    additional_row = dict()
    for c in list(drug_prep_df.columns):
        try: additional_row[c] = unit_row_dict[c]
        except: additional_row[c] = ''

    drug_prep_df = pd.concat([pd.DataFrame([additional_row], index=['',]), drug_prep_df])

# Prep Data 저장

drug_prep_df.to_csv(result_file_path, header=True, index=False)


