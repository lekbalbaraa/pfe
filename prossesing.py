#!/home/salim/.venv/bin/python3
import pandas as pd

file_paths = [
        "../bro/CTU-IoT-Malware-Capture-17-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-7-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-21-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-43-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-60-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-1-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-3-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-42-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-9-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-49-1_conn.log.labeled",
        "../bro/CTU-Honeypot-Capture-5-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-52-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-35-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-39-1_conn.log.labeled",
        "../bro/CTU-Honeypot-Capture-4-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-33-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-36-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-34-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-20-1_conn.log.labeled",
        "../bro/CTU-Honeypot-Capture-7-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-8-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-44-1_conn.log.labeled",
        "../bro/CTU-IoT-Malware-Capture-48-1_conn.log.labeled",
        ] 

frames=[]

for file in file_paths:
    print(f"loading {file}")
    frames.append( pd.read_table(filepath_or_buffer=file, skiprows=10, nrows=100000))

print("making it real...")
for frame in frames:
    frame.columns=['ts', 'uid', 'id.orig_h', 'id.orig_p', 'id.resp_h', 'id.resp_p', 'proto', 'service',
              'duration', 'orig_bytes', 'resp_bytes', 'conn_state', 'local_orig', 'local_resp', 'missed_bytes',
              'history', 'orig_pkts', 'orig_ip_bytes', 'resp_pkts', 'resp_ip_bytes', 'label']
    frame.drop(frame.tail(1).index,inplace=True)


print("concatinate all of the frames into one ")
df_c=pd.concat(frames)

print(df_c.shape)

print(df_c['label'].value_counts())

df_c.loc[(df_c.label == '-   Malicious   PartOfAHorizontalPortScan'), 'label'] = 'PartOfAHorizontalPortScan'
df_c.loc[(df_c.label == '(empty)   Malicious   PartOfAHorizontalPortScan'), 'label'] = 'PartOfAHorizontalPortScan'
df_c.loc[(df_c.label == '-   Malicious   Okiru'), 'label'] = 'Okiru'
df_c.loc[(df_c.label == '(empty)   Malicious   Okiru'), 'label'] = 'Okiru'
df_c.loc[(df_c.label == '-   Benign   -'), 'label'] = 'Benign'
df_c.loc[(df_c.label == '(empty)   Benign   -'), 'label'] = 'Benign'
df_c.loc[(df_c.label == '-   Malicious   DDoS'), 'label'] = 'DDoS'
df_c.loc[(df_c.label == '-   Malicious   C&C'), 'label'] = 'C&C'
df_c.loc[(df_c.label == '(empty)   Malicious   C&C'), 'label'] = 'C&C'
df_c.loc[(df_c.label == '-   Malicious   Attack'), 'label'] = 'Attack'
df_c.loc[(df_c.label == '(empty)   Malicious   Attack'), 'label'] = 'Attack'
df_c.loc[(df_c.label == '-   Malicious   C&C-HeartBeat'), 'label'] = 'C&C-HeartBeat'
df_c.loc[(df_c.label == '(empty)   Malicious   C&C-HeartBeat'), 'label'] = 'C&C-HeartBeat'
df_c.loc[(df_c.label == '-   Malicious   C&C-FileDownload'), 'label'] = 'C&C-FileDownload'
df_c.loc[(df_c.label == '-   Malicious   C&C-Torii'), 'label'] = 'C&C-Torii'
df_c.loc[(df_c.label == '-   Malicious   C&C-HeartBeat-FileDownload'), 'label'] = 'C&C-HeartBeat-FileDownload'
df_c.loc[(df_c.label == '-   Malicious   FileDownload'), 'label'] = 'FileDownload'
df_c.loc[(df_c.label == '-   Malicious   C&C-Mirai'), 'label'] = 'C&C-Mirai'
df_c.loc[(df_c.label == '-   Malicious   Okiru-Attack'), 'label'] = 'Okiru-Attack'

df_c['label'].value_counts()

pd.options.display.max_rows = 300
pd.options.display.max_columns = 300

df_c = df_c.drop(columns=['ts','uid','id.orig_h','id.orig_p','id.resp_h','id.resp_p',
                               'service','local_orig','local_resp','history'])

df_c = pd.get_dummies(df_c, columns=['proto'])
df_c = pd.get_dummies(df_c, columns=['conn_state'])

df_c

df_c['duration'] = df_c['duration'].str.replace('-','0')
df_c['orig_bytes'] = df_c['orig_bytes'].str.replace('-','0')
df_c['resp_bytes'] = df_c['resp_bytes'].str.replace('-','0')

df_c.fillna(-1,inplace=True)

df_c.isna().sum()

print(df_c.columns.tolist())

df_c.to_csv('iot23_combined.csv')

































