import pandas as pd
import openpyxl as ox
from openpyxl.worksheet.table import Table, TableStyleInfo

# Read CSV, update column names and sort by Name
df = pd.read_csv(r'C:\members.csv')
df = df.rename(columns={'displayName': 'Name', 'title': 'Title', 'department': 'Department', 'physicalDeliveryOfficeName': 'Office Location', 'mail': 'Email', 'telephoneNumber': 'Phone Number'})
df = df.sort_values('Name')

# Create Excel Doc
df.to_excel(r'C:\Contact List.xlsx', sheet_name='Contacts', index=False)

# Adjust column width
workbook = ox.load_workbook(r'C:\Contact List.xlsx')
worksheet = workbook['Contacts']
worksheet.column_dimensions['A'].width = 25
worksheet.column_dimensions['B'].width = 65
worksheet.column_dimensions['C'].width = 48
worksheet.column_dimensions['D'].width = 40
worksheet.column_dimensions['E'].width = 40
worksheet.column_dimensions['F'].width = 20

#Get Cell Range for new table for formatting
#Using F because there's 5 columns. If we decide to change the columns the F will need to be changed to reflect the proper column
row_count = worksheet.max_row
table_cells = "A1:F" + str(row_count)

#Put data in a table for formatting
tab = Table(displayName='Contacts', ref=table_cells)
style = TableStyleInfo(name='TableStyleLight1', showRowStripes=True, showColumnStripes=False)
tab.tableStyleInfo = style
workbook['Contacts'].add_table(tab)

workbook.save(r'C:\Contact List.xlsx')
