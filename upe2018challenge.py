import json, requests, time

urlBase = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/"
link = {'content-type': 'application/x-www-form-urlencoded'}

#Access the Token before the session starts
urlSession = urlBase + "session"
infoSession =  { 'uid': '404979154' }
req = requests.post(urlSession, infoSession, link)
ACCESS_TOKEN = json.loads(req.text)["token"]

#returns the position of the proposed move (even if it brings it out of bounds or to a wall)
def edit_position(x, y, dir):
    if dir == "RIGHT":
        return (x+1, y)
    if dir == "LEFT":
        return (x-1, y)
    if dir == "UP":
        return (x, y-1)
    if dir == "DOWN":
        return (x, y+1)

#returns the initial position of the player
def start_position():
    req = requests.get(urlGame, link)
    return json.loads(req.text)["current_location"]

#Executes the action and returns the validity of the move
def move_player(dir):
    info = {'action': dir}
    req = requests.post(urlGame, info, link)
    return json.loads(req.text)["result"]

#Returns game status
def game_status():
    req = requests.get(urlGame, link)
    return json.loads(req.text)["status"]
#Returns game size
def game_size():
    req = requests.get(urlGame, link)
    return json.loads(req.text)["maze_size"]

#Recursively plays the maze for the individual level
def play_level(xi, yi):
    if beenThere[xi][yi] == 0:
        beenThere[xi][yi] = 1
        for dir in dirs:
            (x2, y2) = edit_position(xi, yi, dir)
            if x2 < size[0] and x2 > -1 and y2 > -1 and y2 < size[1] and beenThere[x2][y2] == 0:
                new_position = move_player(dir)
                if new_position == "WALL" or new_position == "OUT_OF_BOUNDS":
                    beenThere[x2][y2] = 1 #adds 1 for every position already checked
                if new_position == "END":
                    return True
                if new_position == "SUCCESS":
                    if play_level(x2, y2):
                        return True
                    else:
                        move_player(rev[dir])
        return False
    return False



urlGame = urlBase + "game?token=" + ACCESS_TOKEN
stat = game_status()
size = game_size()
level = 1

dirs = ["DOWN","RIGHT","UP", "LEFT"]
rev = {
"UP": "DOWN",
"DOWN": "UP",
"LEFT": "RIGHT",
"RIGHT": "LEFT"
}
print "Time of completion:"
#Plays the game for the given number of levels
while stat != "FINISHED":
    initTime = time.time()
    beenThere = [[0 for i in range(size[1])] for j in range(size[0])]
    p = start_position()[0]
    q = start_position()[1]
    play_level(p, q)
    stat = game_status()
    size = game_size()
    if stat == "GAME_OVER" or stat == "NONE":
        print "Level failed. Try again"
        break
    print "Level %d: %s seconds" %(level, (time.time() - initTime))
    level = level + 1

if stat == "FINISHED":
        print "SUCCESS"
