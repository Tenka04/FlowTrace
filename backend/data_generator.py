import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_data():
    np.random.seed(42)
    random.seed(42)

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)

    # 1. Generate Customers & Accounts
    print("Generating 200 customers and 500 accounts...")
    customer_ids = [f"C{str(i).zfill(4)}" for i in range(1, 201)]
    
    customers = []
    for cid in customer_ids:
        declared_income = np.random.lognormal(mean=np.log(800000), sigma=1.0)
        risk_tier = np.random.choice(['LOW', 'MEDIUM', 'HIGH'], p=[0.7, 0.2, 0.1])
        customers.append({'customer_id': cid, 'declared_annual_income': round(declared_income), 'risk_tier': risk_tier})

    account_ids = [f"A{str(i).zfill(5)}" for i in range(1, 501)]
    accounts = []
    for aid in account_ids:
        cid = random.choice(customer_ids)
        atype = np.random.choice(['SAVINGS', 'CURRENT', 'SALARY'], p=[0.5, 0.3, 0.2])
        balance = np.random.lognormal(mean=np.log(200000), sigma=1.5)
        kyc = np.random.choice(['TIER_1', 'TIER_2', 'TIER_3'], p=[0.6, 0.3, 0.1])
        c_date = datetime.now() - timedelta(days=random.randint(30, 1800))
        days_since = random.randint(1, 45) # Most normal accounts active recently
        accounts.append({
            'account_id': aid,
            'customer_id': cid,
            'account_type': atype,
            'balance': round(balance, 2),
            'kyc_tier': kyc,
            'created_date': c_date.strftime("%Y-%m-%d"),
            'days_since_last_txn': days_since,
            'status': 'ACTIVE'
        })
    
    df_acc = pd.DataFrame(accounts)
    # Merge declared income for ease of processing later
    df_cust = pd.DataFrame(customers)
    df_acc = df_acc.merge(df_cust[['customer_id', 'declared_annual_income']], on='customer_id')

    # 2. General Normal Transactions
    print("Generating 50,000 normal transactions...")
    txns = []
    start_date = datetime.now() - timedelta(days=90)
    
    for i in range(50000):
        src = random.choice(account_ids)
        dst = random.choice(account_ids)
        while src == dst:
            dst = random.choice(account_ids)
        
        # log-normal mean 25k (log(25000) ~ 10.12)
        amount = round(np.random.lognormal(mean=np.log(25000), sigma=1.2), 2)
        
        # timestamp bias 9am-6pm
        days_back = random.randint(0, 90)
        hr = int(np.random.normal(13, 3))
        hr = max(0, min(23, hr))
        mn = random.randint(0, 59)
        ts = start_date + timedelta(days=days_back, hours=hr, minutes=mn)
        
        txns.append({
            'txn_id': f"T{str(len(txns)+1).zfill(7)}",
            'timestamp': ts.isoformat(),
            'from_account': src,
            'to_account': dst,
            'amount': amount,
            'channel': np.random.choice(['NEFT', 'IMPS', 'UPI', 'RTGS'], p=[0.3, 0.2, 0.4, 0.1]),
            'branch': f"BR{random.randint(1,50):03d}",
            'txn_type': 'TRANSFER'
        })

    # Fraud Scenarios Injection
    # 1. Circular (3 cases): A->B->C->D->A within 2 hours, 4-8 Lakhs
    print("Injecting 3 circular chains...")
    for c_idx in range(3):
        path = random.sample(account_ids, 4)
        path.append(path[0]) # Loop back
        base_time = datetime.now() - timedelta(days=random.randint(1, 30))
        for hop in range(4):
            amt = random.randint(400000, 800000)
            base_time += timedelta(minutes=random.randint(5, 25))
            txns.append({
                'txn_id': f"T_CIRC_{c_idx}_{hop}",
                'timestamp': base_time.isoformat(),
                'from_account': path[hop],
                'to_account': path[hop+1],
                'amount': amt,
                'channel': 'RTGS',
                'branch': 'ONLINE',
                'txn_type': 'TRANSFER'
            })
            
    # 2. Layering (4 cases): 6-8 hops, 90 mins, 20-50 Lakhs
    print("Injecting 4 layering chains...")
    for l_idx in range(4):
        hops = random.randint(6, 8)
        path = random.sample(account_ids, hops + 1)
        base_time = datetime.now() - timedelta(days=random.randint(1, 30))
        amt = random.randint(2000000, 5000000)
        for hop in range(hops):
            base_time += timedelta(minutes=random.randint(2, 10))
            amt = amt - random.randint(1000, 5000) # Slight drop for fees/retention
            txns.append({
                'txn_id': f"T_LAY_{l_idx}_{hop}",
                'timestamp': base_time.isoformat(),
                'from_account': path[hop],
                'to_account': path[hop+1],
                'amount': amt,
                'channel': 'IMPS',
                'branch': 'ONLINE',
                'txn_type': 'TRANSFER'
            })

    # 3. Structuring (5 cases): 4-6 txns of 8.5L-9.95L in 7 days
    print("Injecting 5 structuring clusters...")
    struct_accs = random.sample(account_ids, 5)
    for s_idx, sacc in enumerate(struct_accs):
        base_time = datetime.now() - timedelta(days=random.randint(10, 80))
        tx_count = random.randint(4, 6)
        for i in range(tx_count):
            ts = base_time + timedelta(days=random.randint(0, 6), hours=random.randint(1, 12))
            amt = random.randint(850000, 995000)
            txns.append({
                'txn_id': f"T_STR_{s_idx}_{i}",
                'timestamp': ts.isoformat(),
                'from_account': sacc,  # Sending out
                'to_account': random.choice(account_ids),
                'amount': amt,
                'channel': 'NEFT',
                'branch': 'BR001',
                'txn_type': 'TRANSFER'
            })

    # 4. Dormant (3 cases): 180+ days silence, then 30L+ out within 48h
    print("Injecting 3 dormant activations...")
    # modify account days_since_last_txn
    dormant_accs = random.sample(account_ids, 3)
    for d_idx, dacc in enumerate(dormant_accs):
        idx = df_acc.index[df_acc['account_id'] == dacc].tolist()[0]
        df_acc.at[idx, 'days_since_last_txn'] = random.randint(190, 300)
        df_acc.at[idx, 'balance'] = 5000000 # Give them balance
        
        ts = datetime.now() - timedelta(hours=random.randint(1, 40))
        txns.append({
            'txn_id': f"T_DORM_{d_idx}",
            'timestamp': ts.isoformat(),
            'from_account': dacc,
            'to_account': random.choice(account_ids),
            'amount': random.randint(3000000, 4500000),
            'channel': 'RTGS',
            'branch': 'ONLINE',
            'txn_type': 'TRANSFER'
        })

    # 5. Profile mismatch (2 cases): monthly flow 15x+ declared monthly income
    print("Injecting 2 profile mismatches...")
    pm_accs = random.sample(account_ids, 2)
    for p_idx, pacc in enumerate(pm_accs):
        idx = df_acc.index[df_acc['account_id'] == pacc].tolist()[0]
        inc = df_acc.at[idx, 'declared_annual_income']
        monthly_inc = inc / 12.0
        target_flow = monthly_inc * 18 # > 15x
        
        # generate 5-10 huge txns in last 30 days
        base_time = datetime.now() - timedelta(days=15)
        for i in range(8):
            ts = base_time + timedelta(days=i)
            txns.append({
                'txn_id': f"T_PM_{p_idx}_{i}",
                'timestamp': ts.isoformat(),
                'from_account': pacc,
                'to_account': random.choice(account_ids),
                'amount': target_flow / 8.0,
                'channel': 'NEFT',
                'branch': 'ONLINE',
                'txn_type': 'TRANSFER'
            })

    # Sort txns by timestamp
    df_txns = pd.DataFrame(txns)
    df_txns = df_txns.sort_values(by='timestamp').reset_index(drop=True)

    df_acc.to_csv(os.path.join(data_dir, 'accounts.csv'), index=False)
    df_txns.to_csv(os.path.join(data_dir, 'transactions.csv'), index=False)
    
    print("Data generation complete. Saved to backend/data/")

if __name__ == "__main__":
    generate_data()
