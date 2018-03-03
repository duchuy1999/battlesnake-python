import bottle
import os
import random


#codes adapted from https://github.com/terahn/battlesnake-bigasp
def move(data, move):
    myCoor = data['you']['body']['data']
    myLen = data['you']['length']

    if (move == 'up'):
        nextMove = [myCoor[0]['x'], myCoor[0]['y'] - 1]
    elif (move == 'down'):
        nextMove = [myCoor[0]['x'], myCoor[0]['y'] + 1]
    elif (move == 'left'):
        nextMove = [myCoor[0]['x'] - 1, myCoor[0]['y']]
    else:
        nextMove = [myCoor[0]['x'] + 1, myCoor[0]['y']]

	#snake won't run into itself
    for i in range(1, myLen):
        if (nextMove[0] == myCoor[i]['x'] and nextMove[1] == myCoor[i]['y']):
            return False
        
    #snake won't run into walls
    if ((nextMove[0] == data['width']) or (nextMove[0] == -1) or (nextMove[1] == data['height']) or (nextMove[1] == -1)):
        return False

    #snake won't run into other snakes
    for i in range(len(data['snakes']['data'])):
        for j in range(len(data['snakes']['data'][i]['body']['data'])):
            enemyX = data['snakes']['data'][i]['body']['data'][j]['x']
            enemyY = data['snakes']['data'][i]['body']['data'][j]['y']
            if (nextMove[0] == enemyX and nextMove[1] == enemyY):
                return False

    return True



@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data['game_id']
    board_width = data['width']
    board_height = data['height']

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': '#00FF00',
        'taunt': '{} ({}x{})'.format(game_id, board_width, board_height),
        'head_url': head_url,
        'name': 'battlesnake-python'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    directions = ['up', 'down', 'left', 'right']

	global goX, goY, myX, myY
    
    #x and y coordinates of snake's head
    myX = data['you']['body']['data'][0]['x']
    myY = data['you']['body']['data'][0]['y']

    #set go to location to closest food
	closestDist = 1000

    for i in range(len(data['food']['data'])):
        foodX = data['food']['data'][i]['x']
        foodY = data['food']['data'][i]['y']
        distX = abs(myX - foodX)
        distY = abs(myY - foodY)
        dist = distX + distY

        if (dist < closestDist):
            closestDist = dist
            goX = foodX
            goY = foodY
	
	moveX = myX - goX
	moveY = myY - goY

	#call def move to check if it is safe to move
    if (moveY > 0 and move(data, 'up')):
        return 'up'
    elif (moveY < 0 and move(data, 'down')):
        return 'down'
    elif (moveX > 0 and move(data, 'left')):
        return 'left'
    elif (moveX < 0 and move(data, 'right')):
        return 'right'
	
    return {
        'move': random.choice(directions),
        'taunt': 'Yichun and Huy have won the game!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '8080'))
