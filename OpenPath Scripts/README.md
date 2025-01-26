# OpenPath/Alta-Scripts
 A sample set of scripts that will sync user data between our environment and the Alta Open environment (formerly OpenPath).
 id-num-to-op.py is a script that grabs the ID number and other user data from the local environment and adds it to matching user accouts in OpenPath. This script calls Alta's API to get users who don't have their External ID, then only calls the API again if there's matching user data to add to each user. This runs on a schedule every hour with windows Task Scheduler.

prox-to-ad.py is a script that gets card numbers from OpenPath and adds them to the Pager field in Active Directory, and also to a user table in our ERP's database. This runs on a schedule every hour with windows Task Scheduler.

delete_cards.py and update_cards.py do similar things to the previous two scripts, but were made as single-use solutions for fixing some issues during Alta implementation.