# Web Scraping Project
 
**scrape.py** is a Python script I wrote as part of an online programming challenge. The task was to build a script/function that can take the input of a link for a published Google Doc, parse it's contents (a table containing x/y coordinates and a unicode character) and output the corrent image based on the contents of the table. This script uses the Beautiful Soup library to get the contents of the link, find the table, and parse through it to get the data in the table.

The script then finds the maximum x and y values and makes a grid using a list of lists. Then the items in the lists are joined together and printed to the console, revealing the hidden code in the document.
