# TripadvisorScrapping

## Description 

This project is used to scrap restaurants and user infos from tripadvisor.

## How to use

In order to use this srcipt, you'll need to setup some things : 
- A database with a 
- The geckodriver in the same folder as the main.py (in both userToRestau and restauToUser)

We also made it so it could work on a linux server with close to no intervention.

### Technology used

We used Python 3.8.0 to create this program

### Dependencies

We use some libraries in order to make this work : 
- *Selenium* is used to scrap data
- *Psutil* is used to detect when the script is down (when the network is not used)

### RestauToUser

This first part is used to get all the users from the restaurants with their url in database. 

To begin scrapping : you need to launch the `runme.sh`. This programme is going to kill every process used by program.  

### UserToRestau

This second part is used to get at max 10 reviews from the users and the restaurants linked to these reviews.

To begin scrapping, you need to lauch the `launch.py` script in the folder. This script is going to reload the `main.py` every hour and detect if the script is down. 

