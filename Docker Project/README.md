* Auther: Gaurav Dindyal
*Email: gauravd@uoregon.edu
*
# Project : Adding authentication and user interface to brevet time calculator service
## Instructions

Use port 5001
localhost:5001/
###Authenticating the services 

- POST **/api/register**
When entered this link, a page will load to ask for a unique username, id,username,and hashed password will be retained.
- GET **/api/token**
This link will load a page that asks login for registered users, then a token will be provided to access recourses.

- GET **/RESOURCES**
When providing a valid token with the link, the specified resource will be accessed
To access recourse provide token in the following format
localhost:5001/resource?token="token given"

to logout, simply use localhost5001/logout