# SQL Reports and Queries
 A sample set of queries used in reports and other integrations.
 
**housing_report.sql** is a query that was written after updating Jenzabar's housing product to a new version, and we needed a report to show who was housed in a given session. This query joins new housing sessions to the registration module's session tables to only provide data for a given term, where a student is an Undergraduate and has not withdrawn that term. The *:SessionCode* in the WHERE clause is a unique flag for Jenzabar's reporting application, Infomaker. This allows the user who's running the report to add their own session code to look at the data from the term they need.

**open_path_export.sql** is a query that was used as a baseline export while integrating local systems with OpenPath. Some details have been changed for anonymity. This joins in student course and term tables to only return current students for the export.
