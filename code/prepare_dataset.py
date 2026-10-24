"""Rebuild the frozen ADS dataset from official source extracts.
Requires pandas and numpy. Run from any directory: python code/prepare_dataset.py
The source observations are retained; no records or values are simulated.
"""
from pathlib import Path
import pandas as pd, numpy as np, json
ROOT=Path(__file__).resolve().parents[1]
raw=ROOT/'raw'
p=pd.read_csv(raw/'official_permits_2019_2024.csv.gz',dtype=str,keep_default_na=False,na_values=[''])
assert len(p)==154689 and p.permit_number.is_unique and p.record_id.is_unique
assert p.primary_address_flag.eq('Y').all()
# Keep the identity fields as strings. Only documented whitespace/case normalization is used.
def norm(s): return s.astype('string').str.strip().str.upper()
filed=pd.to_datetime(p.filed_date,errors='coerce')
p['filed_year']=filed.dt.year.astype('Int64')
p['filed_month']=filed.dt.strftime('%Y-%m')
p['parcel_block_key']=norm(p.block)
p['parcel_lot_key']=norm(p.lot)
p['assessor_roll_year_key']=p.filed_year-2
# A roll labeled y-2 ends June 30 of y-1, before every filing in year y.
a=pd.read_csv(raw/'official_assessor_matching_rows_2017_2022.csv.gz',dtype=str,keep_default_na=False,na_values=[''])
a['parcel_block_key']=norm(a.block)
a['parcel_lot_key']=norm(a.lot)
a['assessor_roll_year_key']=pd.to_numeric(a.closed_roll_year).astype('Int64')
assert not a.duplicated(['parcel_block_key','parcel_lot_key','assessor_roll_year_key']).any()
a=a.rename(columns={c:'assessor_'+c for c in a.columns if c not in ['parcel_block_key','parcel_lot_key','assessor_roll_year_key']})
d=p.merge(a,on=['parcel_block_key','parcel_lot_key','assessor_roll_year_key'],how='left',validate='many_to_one',indicator=True)
d['assessor_matched']=d.pop('_merge').eq('both')
assert len(d)==len(p) and d.permit_number.is_unique
cpi_raw=json.load(open(raw/'official_bls_response.json'))
cpi=pd.DataFrame(cpi_raw['Results']['series'][0]['data'])
cpi=cpi[cpi.period.str.match(r'M(0[1-9]|1[0-2])$')].copy()
cpi['filed_month']=cpi.year+'-'+cpi.period.str[1:]
cpi['cpi_u_us_all_items_nsa']=pd.to_numeric(cpi.value)
cpi['cpi_series_id']='CUUR0000SA0'
cpi=cpi[['filed_month','cpi_u_us_all_items_nsa','cpi_series_id']]
assert len(cpi)==72 and cpi.filed_month.is_unique

d=d.merge(cpi,on='filed_month',how='left',validate='many_to_one')
assert len(d)==154689 and d.cpi_u_us_all_items_nsa.notna().all()
# Preserve original recorded strings. Parsed values are used only in transparently derived fields.
issued=pd.to_datetime(d.issued_date,errors='coerce')
approved=pd.to_datetime(d.approved_date,errors='coerce')
completed=pd.to_datetime(d.completed_date,errors='coerce')
cutoff=pd.Timestamp('2026-10-22')
def days_after(end,start):
 x=(end-start).dt.days
 return x.where(x.ge(0)&end.le(cutoff)).astype('Int64')
d['filing_to_issuance_days']=days_after(issued,filed)
d['filing_to_approval_days']=days_after(approved,filed)
d['approval_to_issuance_days']=days_after(issued,approved)
d['issuance_to_completion_days']=days_after(completed,issued)
d['invalid_issuance_chronology']=(issued.notna() & (issued.lt(filed)|issued.gt(cutoff)))
d['has_recorded_issuance']=issued.notna()
d['observed_at_least_365_days']=(cutoff-filed).dt.days.ge(365)
d['issued_within_365_days']=pd.Series(pd.NA,index=d.index,dtype='boolean')
elig=d.observed_at_least_365_days & ~d.invalid_issuance_chronology
d.loc[elig,'issued_within_365_days']=d.loc[elig,'filing_to_issuance_days'].le(365).fillna(False)
yearbuilt=pd.to_numeric(d.assessor_year_property_built,errors='coerce')
d['building_age_at_filing']=d.filed_year.sub(yearbuilt).where(yearbuilt.ge(1700)&yearbuilt.le(d.filed_year)).astype('Int64')
d['building_age_group']=pd.cut(d.building_age_at_filing,bins=[-1,29,59,99,np.inf],labels=['0-29 years','30-59 years','60-99 years','100+ years']).astype('string')
num_est=pd.to_numeric(d.estimated_cost,errors='coerce')
num_rev=pd.to_numeric(d.revised_cost,errors='coerce')
cpi2024=float(cpi.loc[cpi.filed_month.str.startswith('2024'),'cpi_u_us_all_items_nsa'].mean())
d['estimated_cost_2024_usd_cpi']=num_est.where(num_est.ge(0))*cpi2024/d.cpi_u_us_all_items_nsa
d['estimate_revision_usd']=num_rev.sub(num_est).where(num_est.ge(0)&num_rev.ge(0))
d['estimate_revision_pct']=num_rev.sub(num_est).div(num_est).mul(100).where(num_est.gt(0)&num_rev.ge(0))
d['snapshot_date_utc']='2026-10-22'
assert len(d)>=100000 and d.shape[1]>=40
out=ROOT/'data/construction_permits_ssot_rebuilt.csv.gz';d.to_csv(out,index=False,compression='gzip')
print(f"Saved {len(d):,} rows and {d.shape[1]} columns to {out}")
print(f"Assessor match: {d.assessor_matched.mean():.2%}; CPI match: {d.cpi_u_us_all_items_nsa.notna().mean():.2%}")
