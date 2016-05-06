# incremental-gaming

A Website built in Python using the Django Web Framework. Provides a server side ran Clicker Game which stays persistent for logged in users. Clicker games are managed through the use of JSON and lazy evaluation on the server side.

## Vist Game Site Flow
### Get Game Instance
Once a user signs in or registers the view used for the home page gets a Game Instance model currently owned by the user or creates a new one if it is a new user.
### Update The Instance
That Instance is then 'fast-forwarded' based off the time the request was made at and the last time the game state was updated on the database. This updates the ammount of resources you have based off the time that has passed.
### Front-End-Handling
The front end then makes a AJAX get call. The view then returns back a JSON blob containing all info about the game and the current values. The front end generates content using Handlebars. A javascript interval function then fires automatically increasing the income numbers locally by the income value of the resource.

## Click a Button Site Flow
### A Click is made
When a user clicks on a building or upgrade a AJAX post request is sent to the server containing info about the item in the page that was clicked. This data is then passed to buy upgrade or buy building function. 
### Can we do it?
The view then checks the values on the database after updating them and sees if the user is actually allowed to make the purchase. If so the database makes the necessary changes to the game instance and returns back the updated JSON. If the user can't buy it a normal fastforward JSON response is given. This is the same as refreshing the page.
### Refresh the front-end
Using the handlebar templates the data on the page can be automaticaly updated without having to refresh the page making the entire process of clicking a button near-seamless.

## Developed By:
**Kent Ross**

**Ben Garnaat**

**Kyle Richardson**
