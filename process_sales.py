from io import UnsupportedOperation
import pandas as pd
import numpy as np
import os

parcel = pd.read_csv('input/EXTR_Parcel.csv', encoding='latin-1', dtype={'Major': 'object', 'Minor': 'object'})
parcel_main = parcel[['Major', 'Minor', 'PropType']]

common_columns = ['Major', 'Minor', 'YrBuilt', 'PropType', 'Area']


#sales
sales = pd.read_csv('input/EXTR_RPSale.csv', encoding='latin-1', dtype={'Major': 'object', 'Minor': 'object'})
lookup = pd.read_csv('input/EXTR_LookUp.csv')

property_type_desc = lookup.loc[lookup.LUType == 1]
principal_use_desc = lookup.loc[lookup.LUType == 2]
sale_instrument_desc = lookup.loc[lookup.LUType == 6]
sale_reason_desc = lookup.loc[lookup.LUType == 5]
property_class_desc = lookup.loc[lookup.LUType == 4]

sales = sales \
    .merge(property_type_desc, how="left", left_on="PropertyType", right_on="LUItem") \
    .drop(['PropertyType', 'LUItem', 'LUType'], axis=1) \
    .rename(columns={'LUDescription': 'PropertyType'}) \
    .merge(property_type_desc, how="left", left_on="PrincipalUse", right_on="LUItem") \
    .drop(['PrincipalUse', 'LUItem', 'LUType'], axis=1) \
    .rename(columns={'LUDescription': 'PrincipalUse'}) \
    .merge(sale_instrument_desc, how="left", left_on="SaleInstrument", right_on="LUItem") \
    .drop(['SaleInstrument', 'LUItem', 'LUType'], axis=1) \
    .rename(columns={'LUDescription': 'SaleInstrument'}) \
    .merge(sale_reason_desc, how="left", left_on="SaleReason", right_on="LUItem") \
    .drop(['SaleReason', 'LUItem', 'LUType'], axis=1) \
    .rename(columns={'LUDescription': 'SaleReason'}) \
    .merge(property_class_desc, how="left", left_on="PropertyClass", right_on="LUItem") \
    .drop(['PropertyClass', 'LUItem', 'LUType'], axis=1) \
    .rename(columns={'LUDescription': 'PropertyClass'})

#residential buildings
resbldg = pd.read_csv('input/EXTR_ResBldg.csv', dtype={'ZipCode': 'object', 'Major': 'object', 'Minor': 'object'})
resbldg['Area'] = resbldg.SqFtTotLiving + resbldg.SqFtTotBasement - resbldg.SqFtFinBasement + resbldg.SqFtGarageAttached + resbldg.SqFtOpenPorch + resbldg.SqFtEnclosedPorch + resbldg.SqFtDeck
resbldg_common = resbldg.merge(parcel_main, how="inner", on=['Major', 'Minor'])[common_columns]

resbldg_common['PropType'] = np.where(resbldg_common['PropType'] == 'R', 'RESIDENTIAL',
                                      np.where(resbldg_common['PropType'] == 'C', 'COMMERICAL', 'RESIDENTIAL'))

#commercial buildings
commbldg = pd.read_csv('input/CommercialBuilding/EXTR_CommBldg.csv', dtype={'Major': 'object', 'Minor': 'object'}, encoding='latin-1')
commbldg['Area'] = commbldg['BldgGrossSqFt']
commbldg_common = commbldg.merge(parcel_main, how="inner", on=['Major', 'Minor'])[common_columns]

commbldg_common['PropType'] = np.where(commbldg_common['PropType'] == 'C', 'COMMERICAL',
                                      np.where(commbldg_common['PropType'] == 'K', 'CONDOMINIMUM', 'COMMERICAL'))

#condo
condo_complex = pd.read_csv('input/CondoComplex/EXTR_CondoComplex.csv',  dtype={'Major': 'object'})

condo_unit = pd.read_csv('input/CondoComplex/EXTR_CondoUnit2.csv', dtype={'Major': 'object', 'Minor': 'object'})

condo_complex_unit = condo_complex.merge(condo_unit, how="left", on="Major")
condo_complex_unit['YrBuilt'] = np.where(condo_complex_unit["YrBuilt_y"] > 0, condo_complex_unit['YrBuilt_y'], condo_complex_unit['YrBuilt_x'])
condo_complex_unit['Area'] = np.where(condo_complex_unit['UnitOfMeasure'] == 1, condo_complex_unit['Footage'], 0)

condo_complex_unit_common = condo_complex_unit.merge(parcel_main, how="left", on=['Major', 'Minor'])[common_columns]

condo_complex_unit_common['PropType'] = np.where(condo_complex_unit_common['PropType'] == 'K', 'CONDOMINIMUM', 'CONDOMINIMUM')

#final dataset
building_data = pd.concat([resbldg_common, commbldg_common, condo_complex_unit_common])

sales = sales.merge(building_data, how="left", on=['Major', 'Minor'])
sales['YrBuilt'] = sales['YrBuilt'].fillna(0)
sales['Area'] = sales['Area'].fillna(0)
sales = sales.astype({'YrBuilt': int, 'Area': int})

def get_sales(format='csv'):
    os.makedirs('output', exist_ok=True)

    if format == 'csv':
        sales.to_csv('output/sales.csv')
        return 'output/sales.csv'
    elif format == 'paraquet':
        sales.to_parquet('output/sales.parquet')
        return 'output/sales.parquet'
    else:
        raise UnsupportedOperation