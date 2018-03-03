import bottle
import os
import random

my_x = -2
my_y = -2

curr_target_x = -1
curr_target_y = -1

#Input: game data, a possible move
#Output: boolean
def safeMove(data, move):
    myCoords = data['you']['body']['data']
    myLength = data['you']['length']

    if (move == 'up'):
        moveTo = [myCoords[0]['x'], myCoords[0]['y'] - 1]
    elif (move == 'down'):
        moveTo = [myCoords[0]['x'], myCoords[0]['y'] + 1]
    elif (move == 'left'):
        moveTo = [myCoords[0]['x'] - 1, myCoords[0]['y']]
    else:
        moveTo = [myCoords[0]['x'] + 1, myCoords[0]['y']]

    #make sure snake won't do anything stupid
    for i in range(1, myLength):
        #make sure snake won't run into itself
        if (moveTo[0] == myCoords[i]['x'] and moveTo[1] == myCoords[i]['y']):
            return False
        
    #make sure snake won't run into walls
    if ((moveTo[0] == data['width']) or (moveTo[0] == -1) or (moveTo[1] == data['height']) or (moveTo[1] == -1)):
        return False

    #TODO: this only accounts for where the other snakes are at that moment but doesn't anticipate where they will be next move
    #make sure snake won't run into other snakes
    for i in range(len(data['snakes']['data'])):
        for j in range(len(data['snakes']['data'][i]['body']['data'])):
            enemySnake_x = data['snakes']['data'][i]['body']['data'][j]['x']
            enemySnake_y = data['snakes']['data'][i]['body']['data'][j]['y']
            if (moveTo[0] == enemySnake_x and moveTo[1] == enemySnake_y):
                return False

    return True


# Input: snake coordinates, target coordinates
# Output: move
def goTo(my_x, my_y, target_x, target_y, data):
    
    move_x = my_x - target_x
    move_y = my_y - target_y

    #move to target
    if (move_y > 0 and safeMove(data, 'up')):
        return 'up'
    elif (move_y < 0 and safeMove(data, 'down')):
        return 'down'
    elif (move_x > 0 and safeMove(data, 'left')):
        return 'left'
    elif (move_x < 0 and safeMove(data, 'right')):
        return 'right'
    #if you cannot move towards the target, make any safe move
    elif (safeMove(data, 'up')):
        return 'up'
    elif (safeMove(data, 'down')):
        return 'down'
    elif (safeMove(data, 'left')):
        return 'left'
    elif (safeMove(data, 'right')):
        return 'right'

#Input: game data
#Output: coordinates of the closest food
def findClosestFood(data):
    closestDistance = 1000

    for i in range(len(data['food']['data'])):
        food_x = data['food']['data'][i]['x']
        food_y = data['food']['data'][i]['y']
        distance_x = abs(my_x - food_x)
        distance_y = abs(my_y - food_y)
        distance = distance_x + distance_y
        print('Food: ({0}, {1}) is {2} squares away'.format(food_x, food_y, distance))

        if (distance < closestDistance):
            closestDistance = distance
            target_x = food_x
            target_y = food_y
    
    print('Closest Food: ({0}, {1}) is {2} squares away'.format(target_x, target_y, closestDistance))

    return [target_x, target_y]

#Input: game data
#Output: the move to send to the battlesnake server
def nextMove(data):
    global curr_target_x, curr_target_y, my_x, my_y
    
    #location of snake's head
    my_x = data['you']['body']['data'][0]['x']
    my_y = data['you']['body']['data'][0]['y']
    print('My Snake: ({0}, {1})'.format(my_x, my_y))

    #find the closest food
    closestFood = findClosestFood(data)
    print('closest food: ({0}, {1})'.format(closestFood[0], closestFood[1]))
    curr_target_x = closestFood[0]
    curr_target_y = closestFood[1]
    print('3. curr_target: ({0}, {1})'.format(curr_target_x, curr_target_y))

    return goTo(my_x, my_y, curr_target_x, curr_target_y, data)


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    global curr_target_x, curr_target_y, my_x, my_y
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    my_x = -2
    my_y = -2

    curr_target_x = -1
    curr_target_y = -1

    print('START!!! my: ({0},{1})    ,     curr_target: ({2},{3})'.format(my_x, my_y, curr_target_x, curr_target_y))
   

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#FF9333',
        'taunt': 'What a fish!',
        'head_url': head_url,
        'name': 'Big Asp',
        'head_type': 'tongue',
        'tail_type': 'curled'
    }


@bottle.post('/move')
def move():
    print('Calculating Move')
    data = bottle.request.json
    print('Inside /move:    my: ({0},{1})    ,     curr_target: ({2},{3})'.format(my_x, my_y, curr_target_x, curr_target_y))
    move = nextMove(data)
    print(move)
    directions = ['up', 'down', 'left', 'right']

    return {
        'move': move,
        'taunt': 'You Fish!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))