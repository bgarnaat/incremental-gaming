# Todos
in no carefully ranked order


## Site features
- games should be listed on the front page and be playable individually
- leaderboards
- games should be resettable (soft and hard, if implemented)
- it should be possible to purchase more than one building at once
- users should be able to author and publish games
- it should be possible to start playing a game without signing in, then create
a permanent account to which to attach the game as played so far
- there should be some form of helpful gui editor for the game descriptor json
- or at the very least, validation failure messages could be marginally more
helpful
- explain inactivity time decay curve and consider alternate equations and
settings


## Game features
#### Effects extensions
- effects should be able to add to base amount, add to a common multiplier,
multiply compoundly, and add flat values
- buildings should have effects
- upgrade costs should be targetable by effects
- upgrades should be able to add effects to buildings
- there should be common multipliers for individual resources, all upgrade
costs, all building costs etc.

#### General features
- games should specify a composite value for high scores
- games should have reset prestige mechanics
- buildings should be sellable
- buildings should be able to be toggleable
- when a building is subtracting from a resource that is depleted, that
building's output should be reduced proportionally to the supply/demand of
that resource (this will require similar logic on the front end counters)
- it should be possible to have citizens, workers, and jobs a la kittens game
- random events, websockets to the front end and server scheduling for their
occurrence
- seasons?


## Development work
- urls, assets, and apps should be reorganized and better delineated
