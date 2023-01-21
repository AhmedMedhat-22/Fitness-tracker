import pandas as pd
from glob import glob
"""
# --------------------------------------------------------------
# Read single CSV file
# --------------------------------------------------------------
single_file_acc=pd.read_csv('../../data/raw/MetaMotion/A-bench-heavy2-rpe8_MetaWear_2019-01-11T16.10.08.270_C42732BE255C_Accelerometer_12.500Hz_1.4.4.csv')
single_file_gyro=pd.read_csv('../../data/raw/MetaMotion/A-bench-heavy2-rpe8_MetaWear_2019-01-11T16.10.08.270_C42732BE255C_Gyroscope_25.000Hz_1.4.4.csv')
# --------------------------------------------------------------
# List all data in data/raw/MetaMotion
#glob->list all the file in the given directory path if you want to select specisic files extension to be list you can use '/*.extension' in the directory path 
# --------------------------------------------------------------
files=glob("../../data/raw/MetaMotion/*.csv")
len(files)
# --------------------------------------------------------------
# Extract features from filename
# --------------------------------------------------------------
#data_path="../../data/raw/MetaMotion/*.csv"
#extract the participant of the workout, type of training and weight lefted  and save them in the dataframe
#rstrip remove any char from the rigth from string 
data_path="../../data/raw/MetaMotion\\"

f=files[0]
participant=f.split('-')[0].replace(data_path,"")
label=f.split('-')[1]
category=f.split('-')[2].rstrip("123")

df=pd.read_csv(f)
df["participant"]=participant
df["label"]=label
df["category"]=category

# --------------------------------------------------------------
# Read all files
# --------------------------------------------------------------
acc_df=pd.DataFrame()
gyro_df=pd.DataFrame()
 
#create id for acc and gyro seys
acc_set=1
gyro_set=1

#loop on all files 
for f in files:
    f_temp=f.split("-")
    participant=f_temp[0].replace(data_path,"")
    label=f_temp[1]
    category=f_temp[2].rstrip("123").rstrip("MetaWear_2019")
    df=pd.read_csv(f)
    df["participant"]=participant
    df["label"]=label
    df["category"]=category  
    
    if "Accelerometer" in f:
        df['set']=acc_set
        acc_set+=1
        acc_df=pd.concat([acc_df,df])
    if "Gyroscope" in f:
        df['set']=gyro_set
        gyro_set+=1
        gyro_df=pd.concat([gyro_df,df])    
    
# --------------------------------------------------------------
# Working with datetimes
# --------------------------------------------------------------
acc_df.info()
#pd.to_datetime(df['epoch (ms)'],unit="ms")
#pd.to_datetime(df['time (01:00)']).dt.month
acc_df.index=pd.to_datetime(acc_df['epoch (ms)'],unit="ms")
gyro_df.index=pd.to_datetime(gyro_df["epoch (ms)"],unit='ms')

del(acc_df["epoch (ms)"])
del(acc_df["time (01:00)"])
del(acc_df["elapsed (s)"])

del(gyro_df["epoch (ms)"])
del(gyro_df["time (01:00)"])
del(gyro_df["elapsed (s)"])

"""
# --------------------------------------------------------------
# Turn into function
# --------------------------------------------------------------
data_path="../../data/raw/MetaMotion\\"
files=glob("../../data/raw/MetaMotion/*.csv")

def read_data_from_files(files):
    
    acc_df=pd.DataFrame()
    gyro_df=pd.DataFrame()
    

    acc_set=1
    gyro_set=1


    for f in files:
        f_temp=f.split("-")
        participant=f_temp[0].replace(data_path,"")
        label=f_temp[1]
        category=f_temp[2].rstrip("123").rstrip("MetaWear_2019")
        df=pd.read_csv(f)
        df["participant"]=participant
        df["label"]=label
        df["category"]=category  
        
        if "Accelerometer" in f:
            df['set']=acc_set
            acc_set+=1
            acc_df=pd.concat([acc_df,df])
        if "Gyroscope" in f:
            df['set']=gyro_set
            gyro_set+=1
            gyro_df=pd.concat([gyro_df,df])    
        


    acc_df.index=pd.to_datetime(acc_df['epoch (ms)'],unit="ms")
    gyro_df.index=pd.to_datetime(gyro_df["epoch (ms)"],unit='ms')

    del(acc_df["epoch (ms)"])
    del(acc_df["time (01:00)"])
    del(acc_df["elapsed (s)"])

    del(gyro_df["epoch (ms)"])
    del(gyro_df["time (01:00)"])
    del(gyro_df["elapsed (s)"])
    
    return acc_df,gyro_df

acc_data,gyro_data=read_data_from_files(files)
# --------------------------------------------------------------
# Merging datasets
# --------------------------------------------------------------
data_merged=pd.concat([acc_data.iloc[:,:3],gyro_data],axis=1)
data_merged.head(50)
data_merged.columns=[
     'acc_x',
    'acc_y',
    'acc_z',
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "participant",
    'label',
    "category",
    'set'
    
]
# --------------------------------------------------------------
# Resample data (frequency conversion)
# --------------------------------------------------------------

# Accelerometer:    12.500HZ
# Gyroscope:        25.000Hz
sampling={
    'acc_x':'mean',
    'acc_y':'mean',
    'acc_z':'mean',
    "gyro_x":'mean',
    "gyro_y":'mean',
    "gyro_z":'mean',
    "participant":'last',
    'label':'last',
    "category":'last',
    'set':'last'
}

#data_merged.resample(rule='200ms').apply(sampling)
days=[g for n,g in data_merged.groupby(pd.Grouper(freq="D"))]
data_resampled=pd.concat([df.resample(rule='200ms').apply(sampling).dropna()for df in days])
data_resampled.info()
data_resampled['set']=data_resampled['set'].astype('int')
        
# --------------------------------------------------------------
# Export dataset
# --------------------------------------------------------------
data_resampled.to_pickle("../../data/interim/0.1_dataprocessed.pkl")
