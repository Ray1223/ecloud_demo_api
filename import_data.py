import os
from config import db_config
import pymysql
import pandas as pd
from sqlalchemy import create_engine
import zipfile

source_path = os.getcwd()+'/source/cur.zip'
select_col = [ "idx"
                ,"bill/PayerAccountId"
                ,"lineItem/UnblendedCost"
                ,"lineItem/UnblendedRate"
                ,"lineItem/UsageAccountId"
                ,"lineItem/UsageAmount"
                ,"lineItem/UsageStartDate"
                ,"lineItem/UsageEndDate"
                ,"product/ProductName"
]



def get_db_conn(db_config):
    conn = pymysql.connect(host=db_config['host']
                           , port=db_config['port']
                           , database=db_config['database']
                           , user=db_config['user']
                           , password=db_config['password']
                           )
    return conn

def read_from_csv(source_path = source_path):
    df = pd.read_csv(source_path)
    df = df.rename(mapper={'Unnamed: 0':'idx'},axis = 1)
    part_df = df[select_col]
    return part_df


def create_temp_table(table_name):

    sql = """

    CREATE TABLE `{}` (
    `idx` TEXT DEFAULT NULL
    ,`bill/PayerAccountId` TEXT DEFAULT NULL
    ,`lineItem/UnblendedCost` TEXT DEFAULT NULL
    ,`lineItem/UnblendedRate` TEXT DEFAULT NULL
    ,`lineItem/UsageAccountId` TEXT DEFAULT NULL
    ,`lineItem/UsageAmount` TEXT DEFAULT NULL
    ,`lineItem/UsageStartDate` TEXT DEFAULT NULL
    ,`lineItem/UsageEndDate` TEXT DEFAULT NULL
    ,`product/ProductName` TEXT DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=UTF8MB4;
    
    """.format(table_name)

    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()

    return print("create temp table finished!")

def create_target_table(table_name):

    sql = """
        create table `{}` (
        `idx` varchar(10) DEFAULT NULL
        ,`bill/PayerAccountId` varchar(20) DEFAULT NULL
        ,`lineItem/UnblendedCost` double DEFAULT NULL
        ,`lineItem/UnblendedRate` double DEFAULT NULL
        ,`lineItem/UsageAccountId` varchar(20) DEFAULT NULL
        ,`lineItem/UsageAmount` double DEFAULT NULL
        ,`lineItem/UsageStartDate` timestamp DEFAULT NULL
        ,`lineItem/UsageEndDate` timestamp DEFAULT NULL
        ,`product/ProductName` varchar(100) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=UTF8MB4;
    """.format(table_name)
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)

    return print("create target table finished!")



def import_data_to_db(df,target_table):

    engine = create_engine('mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(db_config['user']
                                                                            ,db_config['password']
                                                                            ,db_config['host']
                                                                            ,db_config['port']
                                                                            ,db_config['database'])
                           , echo=False)

    try:
        for idx in range(0,len(df)):
            if idx % 1000 ==0:
                print('There is {} count record to db'.format(idx))
                seg_df = df.iloc[idx:idx+1000,:]
                seg_df.to_sql(name=target_table, con=engine, if_exists = 'append', index=False)
    except Exception as e:
        print(e)
    finally:
        seg_df = df.iloc[idx:,:]
        seg_df.to_sql(name=target_table, con=engine, if_exists = 'append', index=False)

    return print('import to db finished')



def import_to_target_table(target_table,source_table):

    sql = """
        insert into {}
        select distinct *
        from {}
    
    """.format(target_table,source_table)

    try:
        cursor.execute(sql)
        conn.commit()
    except Exception:
        conn.rollback()

    return print("import data to target table finished!")


def create_index(table_name):

    sql = """
            CREATE INDEX usageaccountid_idx ON {} (`lineitem/usageaccountid`,`product/ProductName`);
    """.format(table_name)

    try:
        cursor.execute(sql)
        conn.commit()
    except Exception:
        conn.rollback()

    return print("create index finished!")



zf = zipfile.ZipFile(source_path)
df = read_from_csv(zf.open('output.csv'))
conn = get_db_conn(db_config)
cursor = conn.cursor()
try:
    create_temp_table('billing')
    create_target_table('temp_billing')
    import_data_to_db(df,'temp_billing')
    import_to_target_table('bdata.billing','bdata.temp_billing')
    create_index('billing')

except Exception as e:
    print(e)
finally:
    cursor.close()
    conn.close()