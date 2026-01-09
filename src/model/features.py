import pandas as pd
import numpy as np
import gc

# ---------------------------------------------------------
# Fonction utilitaire pour l'encodage One-Hot
# ---------------------------------------------------------
def one_hot_encoder(df, nan_as_category=True):
    original_columns = list(df.columns)
    categorical_columns = [col for col in df.columns if df[col].dtype == 'object']
    df = pd.get_dummies(df, columns=categorical_columns, dummy_na=nan_as_category)
    new_columns = [c for c in df.columns if c not in original_columns]
    return df, new_columns

# ---------------------------------------------------------
# 1. Traitement de application_{train|test}.csv
# ---------------------------------------------------------
def preprocess_application_train_test(data_path, sample_size=None):
    print("Chargement des fichiers application_train/test...")
    
    df_train = pd.read_csv(f'{data_path}/application_train.csv', nrows=sample_size)
    df_test = pd.read_csv(f'{data_path}/application_test.csv', nrows=sample_size)
    
    print(f"Train samples: {len(df_train)}, Test samples: {len(df_test)}")
    
    # Fusion
    df = pd.concat([df_train, df_test]).reset_index(drop=True)
    
    # Nettoyage
    df = df[df['CODE_GENDER'] != 'XNA']

    # Encodage binaire
    for bin_feature in ['CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY']:
        df[bin_feature], _ = pd.factorize(df[bin_feature])
        
    # Encodage One-Hot
    df, _ = one_hot_encoder(df)
    
    # --- CORRECTION 1 : Suppression de inplace=True ---
    # Ancien code : df['DAYS_EMPLOYED'].replace(365243, np.nan, inplace=True)
    df['DAYS_EMPLOYED'] = df['DAYS_EMPLOYED'].replace(365243, np.nan)
    
    # Ratios
    df['DAYS_EMPLOYED_PERC'] = df['DAYS_EMPLOYED'] / df['DAYS_BIRTH']
    df['INCOME_CREDIT_PERC'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']
    df['INCOME_PER_PERSON'] = df['AMT_INCOME_TOTAL'] / df['CNT_FAM_MEMBERS']
    df['ANNUITY_INCOME_PERC'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL']
    df['PAYMENT_RATE'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']
    
    del df_test, df_train
    gc.collect()
    return df

# ---------------------------------------------------------
# 2. Traitement de bureau.csv et bureau_balance.csv
# ---------------------------------------------------------
def preprocess_bureau_and_balance(data_path, sample_size=None):
    print("Traitement de bureau et bureau_balance...")
    
    bureau = pd.read_csv(f'{data_path}/bureau.csv', nrows=sample_size)
    bb = pd.read_csv(f'{data_path}/bureau_balance.csv', nrows=sample_size)
    
    # Agrégation BB
    bb, bb_cat = one_hot_encoder(bb, nan_as_category=True)
    bb_aggregations = {'MONTHS_BALANCE': ['min', 'max', 'size']}
    for col in bb_cat:
        bb_aggregations[col] = ['mean']
    
    bb_agg = bb.groupby('SK_ID_BUREAU').agg(bb_aggregations)
    bb_agg.columns = pd.Index([e[0] + "_" + e[1].upper() for e in bb_agg.columns.tolist()])
    
    # Fusion Bureau
    bureau = bureau.join(bb_agg, how='left', on='SK_ID_BUREAU')
    bureau.drop(['SK_ID_BUREAU'], axis=1, inplace=True)
    del bb, bb_agg
    gc.collect()
    
    # Agrégation Bureau
    bureau, bureau_cat = one_hot_encoder(bureau, nan_as_category=True)
    
    num_aggregations = {
        'DAYS_CREDIT': ['min', 'max', 'mean', 'var'],
        'DAYS_CREDIT_ENDDATE': ['min', 'max', 'mean'],
        'DAYS_CREDIT_UPDATE': ['mean'],
        'CREDIT_DAY_OVERDUE': ['max', 'mean'],
        'AMT_CREDIT_MAX_OVERDUE': ['mean'],
        'AMT_CREDIT_SUM': ['max', 'mean', 'sum'],
        'AMT_CREDIT_SUM_DEBT': ['max', 'mean', 'sum'],
        'AMT_CREDIT_SUM_OVERDUE': ['mean'],
        'AMT_CREDIT_SUM_LIMIT': ['mean', 'sum'],
        'AMT_ANNUITY': ['max', 'mean'],
        'CNT_CREDIT_PROLONG': ['sum'],
        'MONTHS_BALANCE_MIN': ['min'],
        'MONTHS_BALANCE_MAX': ['max'],
        'MONTHS_BALANCE_SIZE': ['mean', 'sum']
    }
    
    cat_aggregations = {}
    for cat in bureau_cat: cat_aggregations[cat] = ['mean']
    for cat in bb_cat: cat_aggregations[cat + "_MEAN"] = ['mean']
    
    bureau_agg = bureau.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})
    bureau_agg.columns = pd.Index(['BURO_' + e[0] + "_" + e[1].upper() for e in bureau_agg.columns.tolist()])
    
    # Agrégations spécifiques (Active / Closed)
    active = bureau[bureau['CREDIT_ACTIVE_Active'] == 1]
    active_agg = active.groupby('SK_ID_CURR').agg(num_aggregations)
    active_agg.columns = pd.Index(['ACTIVE_' + e[0] + "_" + e[1].upper() for e in active_agg.columns.tolist()])
    
    closed = bureau[bureau['CREDIT_ACTIVE_Closed'] == 1]
    closed_agg = closed.groupby('SK_ID_CURR').agg(num_aggregations)
    closed_agg.columns = pd.Index(['CLOSED_' + e[0] + "_" + e[1].upper() for e in closed_agg.columns.tolist()])
    
    # Fusion finale
    bureau_agg = bureau_agg.join(active_agg, how='left', on='SK_ID_CURR')
    bureau_agg = bureau_agg.join(closed_agg, how='left', on='SK_ID_CURR')
    
    del active, closed, active_agg, closed_agg, bureau
    gc.collect()
    
    return bureau_agg

# ---------------------------------------------------------
# 3. Traitement de previous_application.csv
# ---------------------------------------------------------
def preprocess_previous_applications(data_path, sample_size=None):
    print("Traitement de previous_application...")
    prev = pd.read_csv(f'{data_path}/previous_application.csv', nrows=sample_size)
    prev, cat_cols = one_hot_encoder(prev, nan_as_category=True)
    
    # --- CORRECTION 2 : Suppression de inplace=True dans la boucle ---
    # Ancien code : prev[col].replace(365243, np.nan, inplace=True)
    for col in ['DAYS_FIRST_DRAWING', 'DAYS_FIRST_DUE', 'DAYS_LAST_DUE_1ST_VERSION', 'DAYS_LAST_DUE', 'DAYS_TERMINATION']:
        prev[col] = prev[col].replace(365243, np.nan)
        
    prev['APP_CREDIT_PERC'] = prev['AMT_APPLICATION'] / prev['AMT_CREDIT']
    
    num_aggregations = {
        'AMT_ANNUITY': ['min', 'max', 'mean'],
        'AMT_APPLICATION': ['min', 'max', 'mean'],
        'AMT_CREDIT': ['min', 'max', 'mean'],
        'APP_CREDIT_PERC': ['min', 'max', 'mean', 'var'],
        'AMT_DOWN_PAYMENT': ['min', 'max', 'mean'],
        'AMT_GOODS_PRICE': ['min', 'max', 'mean'],
        'HOUR_APPR_PROCESS_START': ['min', 'max', 'mean'],
        'RATE_DOWN_PAYMENT': ['min', 'max', 'mean'],
        'DAYS_DECISION': ['min', 'max', 'mean'],
        'CNT_PAYMENT': ['mean', 'sum'],
    }
    
    cat_aggregations = {}
    for cat in cat_cols: cat_aggregations[cat] = ['mean']
    
    prev_agg = prev.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})
    prev_agg.columns = pd.Index(['PREV_' + e[0] + "_" + e[1].upper() for e in prev_agg.columns.tolist()])
    
    # Agrégations Approved / Refused
    approved = prev[prev['NAME_CONTRACT_STATUS_Approved'] == 1]
    approved_agg = approved.groupby('SK_ID_CURR').agg(num_aggregations)
    approved_agg.columns = pd.Index(['APPROVED_' + e[0] + "_" + e[1].upper() for e in approved_agg.columns.tolist()])
    
    refused = prev[prev['NAME_CONTRACT_STATUS_Refused'] == 1]
    refused_agg = refused.groupby('SK_ID_CURR').agg(num_aggregations)
    refused_agg.columns = pd.Index(['REFUSED_' + e[0] + "_" + e[1].upper() for e in refused_agg.columns.tolist()])
    
    prev_agg = prev_agg.join(approved_agg, how='left', on='SK_ID_CURR')
    prev_agg = prev_agg.join(refused_agg, how='left', on='SK_ID_CURR')
    
    del prev, approved, refused, approved_agg, refused_agg
    gc.collect()
    return prev_agg

# ---------------------------------------------------------
# 4. Traitement de POS_CASH_balance.csv
# ---------------------------------------------------------
def preprocess_pos_cash_balance(data_path, sample_size=None):
    print("Traitement de POS_CASH_balance...")
    pos = pd.read_csv(f'{data_path}/POS_CASH_balance.csv', nrows=sample_size)
    pos, cat_cols = one_hot_encoder(pos, nan_as_category=True)
    
    aggregations = {
        'MONTHS_BALANCE': ['max', 'mean', 'size'],
        'SK_DPD': ['max', 'mean'],
        'SK_DPD_DEF': ['max', 'mean']
    }
    for cat in cat_cols: aggregations[cat] = ['mean']
    
    pos_agg = pos.groupby('SK_ID_CURR').agg(aggregations)
    pos_agg.columns = pd.Index(['POS_' + e[0] + "_" + e[1].upper() for e in pos_agg.columns.tolist()])
    pos_agg['POS_COUNT'] = pos.groupby('SK_ID_CURR').size()
    
    del pos
    gc.collect()
    return pos_agg

# ---------------------------------------------------------
# 5. Traitement de installments_payments.csv
# ---------------------------------------------------------
def preprocess_installments_payments(data_path, sample_size=None):
    print("Traitement de installments_payments...")
    ins = pd.read_csv(f'{data_path}/installments_payments.csv', nrows=sample_size)
    ins, cat_cols = one_hot_encoder(ins, nan_as_category=True)
    
    ins['PAYMENT_PERC'] = ins['AMT_PAYMENT'] / ins['AMT_INSTALMENT']
    ins['PAYMENT_DIFF'] = ins['AMT_INSTALMENT'] - ins['AMT_PAYMENT']
    ins['DPD'] = ins['DAYS_ENTRY_PAYMENT'] - ins['DAYS_INSTALMENT']
    ins['DBD'] = ins['DAYS_INSTALMENT'] - ins['DAYS_ENTRY_PAYMENT']
    ins['DPD'] = ins['DPD'].apply(lambda x: x if x > 0 else 0)
    ins['DBD'] = ins['DBD'].apply(lambda x: x if x > 0 else 0)
    
    aggregations = {
        'NUM_INSTALMENT_VERSION': ['nunique'],
        'DPD': ['max', 'mean', 'sum'],
        'DBD': ['max', 'mean', 'sum'],
        'PAYMENT_PERC': ['max', 'mean', 'sum', 'var'],
        'PAYMENT_DIFF': ['max', 'mean', 'sum', 'var'],
        'AMT_INSTALMENT': ['max', 'mean', 'sum'],
        'AMT_PAYMENT': ['min', 'max', 'mean', 'sum'],
        'DAYS_ENTRY_PAYMENT': ['max', 'mean', 'sum']
    }
    for cat in cat_cols: aggregations[cat] = ['mean']
    
    ins_agg = ins.groupby('SK_ID_CURR').agg(aggregations)
    ins_agg.columns = pd.Index(['INSTAL_' + e[0] + "_" + e[1].upper() for e in ins_agg.columns.tolist()])
    ins_agg['INSTAL_COUNT'] = ins.groupby('SK_ID_CURR').size()
    
    del ins
    gc.collect()
    return ins_agg

# ---------------------------------------------------------
# 6. Traitement de credit_card_balance.csv
# ---------------------------------------------------------
def preprocess_credit_card_balance(data_path, sample_size=None):
    print("Traitement de credit_card_balance...")
    cc = pd.read_csv(f'{data_path}/credit_card_balance.csv', nrows=sample_size)
    cc, _ = one_hot_encoder(cc, nan_as_category=True)
    
    cc.drop(['SK_ID_PREV'], axis=1, inplace=True)
    cc_agg = cc.groupby('SK_ID_CURR').agg(['min', 'max', 'mean', 'sum', 'var'])
    cc_agg.columns = pd.Index(['CC_' + e[0] + "_" + e[1].upper() for e in cc_agg.columns.tolist()])
    cc_agg['CC_COUNT'] = cc.groupby('SK_ID_CURR').size()
    
    del cc
    gc.collect()
    return cc_agg

