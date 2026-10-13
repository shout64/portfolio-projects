# Finance ETL Scripts
*Some details (company, procedure and table names, and file locations) changed for anonymity.

## Overview
Greenville University had decided to move to a new finance system, which meant getting data over from the SIS, and the payroll system, to the new finance system. Building a query to pull data that fit their import template was challenge enough on it's own. What was just as crucial was building a reliable system to get the data transferred repeatedly and securely. I built a set of scripts that could pull what was needed, log what had been sent, and give us a way to go back and re-run if needed. This gave the finance team peace of mind to know that this data would not have to be pulled and imported manually, and to be confident that they are reporting on accurate data at all times.

## Payroll Transfer
**payroll_transfer.py** is a Python script that gets data from a payroll system to the finance system. First it connects to an SFTP for the payroll system to pull in multiple reports, then uses the Pandas library to concatenate all of the files to a single CSV with today's date. Then transfers that single file to the finance SFTP folder. The script then adds the date to each filename if needed and moves it to the history folder. Lastly, it checks the dates of each filename and removes it after the specified number of days.

## SIS Transfer
A Python script and SQL procedure I wrote to pull data from an SIS (student information system), and load it into a finance/budgeting ERP system. 
 
**SP_FINANCIAL_STUDENT_CHARGES_REPORT.sql** is a stored procedure that is ran from the production database of the SIS. It first creates a temp table that will be used to load transactions with the query. Then it looks at all the transaction IDs we want to load, and checks the custom log table to see if they have already been imported. If not, those "net-new" transactions are inserted into the temp table, and logged so they won't get pulled the next time.

Then a query is ran that gets the transaction data needed in the format the finance system has requested. The transactions are only "net-new" transactions, since the query has a join with the temp table. Then it's returned to whatever called the procedure, in this case, the Python script.

**main.py** is a script that connects to the production database and calls two stored procedures for getting transaction data, commits the procedure transactions and gets the results of the query. Then, if there are any transactions to send, it generates a CSV file with today's date for each query, uses the Paramiko library to connect to the finance system's SFTP folder and transfer the files. If there is no transaction data to send, then it exits the script. Lastly, the script looks at the dates in the file names and deletes any files older than the specified number of days.
