import requests
import urllib3
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm
# from core.const import name as n

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

geeklist_ids = ['226924','236201','251339','267760','300101','325217','329286']

def get_geeklist(id):
	xml = b'Your request for this geeklist has been'
	while 'Your request for this geeklist has been' in xml.decode("utf-8"):
		# print(id,'waiting for access...')
		try:
			response = requests.get('https://www.boardgamegeek.com/xmlapi/'+"geeklist/"+id,verify=False) #TODO: replace with global variable
		except:
			# print(id,'connection error... retrying')
			continue
		xml = response.content
	# print(id, 'done!')
	return xml

def xml_to_df(xml):
	xmlTree = ET.fromstring(xml)
	# tags = {print(elem.tag) for elem in xmlTree.iter()}
	items = {elem for elem in xmlTree.iter() if elem.tag == 'item'}
# 	print(list(items))
	
	df = pd.DataFrame()
	for item in items:
		new_row = pd.DataFrame(item.attrib, index=[0])
		df = pd.concat([df,new_row])
	return df

if __name__ == "__main__":
	df_geeklists = pd.DataFrame()
	for id in geeklist_ids:
		xml = get_geeklist(id)
		df_new = xml_to_df(xml)
		df_geeklists = pd.concat([df_geeklists,df_new])
		print(id, 'done!')

	df_items = pd.DataFrame()
	for id, date, title in tqdm(zip(df_geeklists['objectid'],df_geeklists['postdate'],df_geeklists['objectname']),total=len(df_geeklists)):
		xml = get_geeklist(id)
		df_new = xml_to_df(xml)
		df_new['geeklist_id'] = id
		df_new['geeklist_date'] = date
		df_new['geeklist_title'] = title
		df_items = pd.concat([df_items,df_new])

	cols = [col for col in df_items.columns if 'date' in col]
	for col in cols:
		df_items[col] = pd.to_datetime(df_items[col], utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')

	df_final = df_items.sort_values(by='postdate')
	df_final.to_csv('items.csv', index_label='objectid')
