# Finance ETL Scripts
Some details (company, procedure and table names, and file locations) changed for anonymity.

## Payroll Transfer
**payroll_transfer.py** is a Python script that gets data from a payroll system to the finance system. First it connects to an SFTP for the payroll system to pull in multiple reports, then uses the Pandas library to concatenate all of the files to a single CSV with today's date. Then transfers that single file to the finance SFTP folder. The script then adds the date to each filename if needed and moves it to the history folder. Lastly, it checks the dates of each filename and removes it after the specified number of days.

## SIS Transfer
A Python script and SQL procedure I wrote to pull data from an SIS (student information system), and load it into a finance/budgeting ERP system. 
 
**SP_FINANCIAL_STUDENT_CHARGES_REPORT.sql** is a stored procedure that is ran from the production database of the SIS. It first creates a temp table that will be used to load transactions with the query. Then it looks at all the transaction IDs we want to load, and checks the custom log table to see if they have already been imported. If not, those "net-new" transactions are inserted into the temp table, and logged so they won't get pulled the next time.

Then a query is ran that gets the transaction data needed in the format the finance system has requested. The transactions are only "net-new" transactions, since the query has a join with the temp table. Then it's returned to who called the procedure, in this case the Python script.

**main.py** is a script that connects to the production database and calls the stored procedure, commits the transaction and gets the results of the query. Then it generates a CSV file with today's date, uses the Paramiko library to connect to the finance system's SFTP folder and transfer the file. Lastly, the script looks at the dates in the file names and deletes any files older than the specified number of days.
