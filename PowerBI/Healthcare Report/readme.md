# Sample Healthcare Data Report

This report uses sample data from kaggle. You can find a [copy of this data here](https://www.kaggle.com/datasets/prasad22/healthcare-dataset/data).

## Process
- Started by cleaning the data. This involed fixing the *case* on all of the patient names, making sure all the fields used the correct formatting and correcting typos.
    - Since this is sample data, I also added a column for Paid Amount to use for comparison.
	- I also limited the results to a smaller number for manipulation.
- Think through a few data points that may be of interest to the parent medical company, list those out and explore the data.
- Add a few measured/calculated columns to help find important insights.
- Begin to chart out data.


## Areas for Improvement and Other Methods of Displaying Data
- This example report shows generic data about patient data and billing amounts owed by insurance provider. This could be more refined by narrowing the report down by date. If this was an interactive report, I could also add a date selector.
- With additional data more insights could be made. For example:
	- Amounts pending from insurance providers.
	- What was paid by the patient vs insurance.
	- Due dates.
