# incremental-gaming

A Website built in Python using the Django Web Framework. Provides a server side ran Clicker Game which stays persistent for logged in users. Clicker games are managed through the use of JSON and lazy evaluation on the server side.

## Vist Game Site Flow
### Get Game Instance
Once a user signs in or registers the view used for the home page gets a Game Instance model currently owned by the user or creates a new one if it is a new user.
### Front-End-Handling
The front end then makes a AJAX get call on load. The server view then loads the user's game state from the database.
### Update The Instance
That Instance is then 'fast-forwarded' based off the time the request was made at and the last time the game state was last updated on the database. This updates the amount of resources in the game instance based on the read game state and the amount time that passed since the state was last stored.
### Back to the front end
The view then returns back a JSON blob containing all relevant, visible info about the game and the current values, such as costs of purchasing upgrades and buildings and the amount and rate of income for resources. The front end generates UI elements and content using Handlebars templates, and a javascript function fires on an interval, increasing the resource numbers locally in real time to reflect the estimated effective amounts given the amount of time that has passed since a response was last seen from the server.

## Click a Button Site Flow
### A Click is made
When a user clicks on a building or upgrade a AJAX post request is sent to the server containing info about the item in the page that was clicked. This data is then passed on the server side to the game instance that was loaded from the database with a request to purchase the building or upgrade.
### Can we do it?
The game instance object then checks the values of the up-to-date, fast-forwarded game state and sees if the user is actually allowed to make the purchase (such as ensuring that it is unlocked and affordable). If so, the game state changes to reflect the purchase and the changed state is reflected in both the JSON sent to the user and the state that is stored back in the database. If making the purchase is not possible, attempting the purchase does not change the game state and a simple fastforwarded state is reflected as if the page had simply been refreshed.
### Refresh the front-end
Using the handlebar templates the data on the page can be automatically updated without having to refresh the page, making the entire process of clicking a button near-seamless.

## Advantages of This Approach
### Server authority
Since the game state is only stored on the server, players of the game cannot cheat as the data on the client side is simply requests to perform actions in the game state; the server has full authority over the state of the game at all times.
### Performance
The model is also highly performant, as calculations on a user's game state need not ever be done when the game is not actively being updated by the player.
### Persistence
The server and client can also both be shut down at any time, as the complete state of all games can always be derived from the database and game algorithms alone.
### Modularity
Game models can be added to on the fly without even restarting the server, simply by updating their entries in the database. This means that games that already have active players can be expanded, balanced, and tweaked without interrupting user experience, and perhaps without the user even noticing.

## Developed By:
**Kent Ross**

**Ben Garnaat**

**Kyle Richardson**
