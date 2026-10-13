# Alta Access-Scripts
 A sample set of scripts that will sync user data between our environment and the Alta Access environment (formerly OpenPath).

## Overview
Leadership knew that the legacy Door Access Control system had to go. It was deprecated, out of support, and expensive to maintain. Once they decided to work with Alta Access, we had to work fast to make sure that access could flow out of the SIS and into the system quickly. The PowerShell scripts get users added to their proper access groups, and the Python scripts update and get data once users have been granted access cards. This allows the campus safety team to have all the user info they need to manage access and print ID cards, while also allowing capabilities for other system integrations across campus with the user card number. These automations help the Campus Safety team not have to worry about the technical aspects of security so they can focus on keeping everyone safe.

**id-num-to-op.py** is a script that grabs the ID number and other user data from the local environment and adds it to matching user accounts in Alta Access. This script calls Alta's API to get users who don't have their External ID set, then only calls the API again if there's matching user data in our SIS. This runs on a schedule every hour with Windows Task Scheduler.

**prox-to-ad.py** is a script that gets user card numbers from Alta Access and adds them to the Pager field in Active Directory, and also to a user table in our SIS' database. This runs on a schedule every hour with Windows Task Scheduler.

**delete_cards.py** and **update_cards.py** do similar things to the previous two scripts, but were made as single-use solutions for fixing some issues during Alta implementation.
