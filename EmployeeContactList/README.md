# Employee-Contact-List
 Set of scripts that will pull employee information into a CSV, then convert to an Excel sheet that is more easily readable by Faculty and Staff
 GenerateContactList.ps1 looks at every user in the AD group "PhoneDirectory-Employees" and pulls the info we are looking for and dumps it in a CSV.
 main.py takes the CSV and updates the column headers to be more readable, creates an Excel file, then resizes the columns to fit the contents. You could change this to be done dynamically, but this simple static size change works fine for now.

 In my environment we have a batch file that runs nightly on our server with Windows Task Scheduler. I added the Powershell and Python scripts to this nightly batch so that this file is updated every night as we update contact information for our users.

 If you want to use this in your environment, you will want to change the output locations to make sense for your environment so users can easily access this directory.