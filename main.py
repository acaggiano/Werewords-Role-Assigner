from flask import Flask, request, render_template, url_for
from flask_socketio import SocketIO, join_room, leave_room

import random

app = Flask(__name__)

socketio = SocketIO(app)

users = {}
ROLES = ['seer', 'werewolf', 'villager', 'villager', 'villager', 'villager', 'werewolf', 'villager', 'villager', 'villager']


@app.route('/')
def sessions():
    return render_template('session.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!')

@socketio.on('connect')
def connect():
    print(request.sid)
    socketio.emit('update users', { 'user_list': list(users.values()) })

@socketio.on('disconnect')
def user_disconnected():
    user_key = request.sid
    if user_key in users.keys():
        del users[user_key]
    socketio.emit('update users', { 'user_list': list(users.values()) })

@socketio.on('leave')
def on_leave(data, room):
   leave_room(room)
   socketio.emit('update users', { 'message': username + ' has left', 'user_list': list(users.values()) }, room=room)

@socketio.on('join')
def on_join(data, room):
    username = data['username'] + "#" + request.sid[0:4]
    join_room(room)
    users[str(request.sid)] = username
    socketio.emit('set username', { 'username': username }, room=request.sid, broadcast=False)
    socketio.emit('update users', { 'user_list': list(users.values()) }, broadcast=True)

@socketio.on('assign')
def assign_roles():
    number_of_users = len(users)
    random_index = random.randint(1, number_of_users - 1)
    roles_for_players = ROLES[0:number_of_users]
    roles_for_players[random_index] = 'mayor & ' + roles_for_players[random_index]
    random.shuffle(roles_for_players)
    role_dict = dict(zip(list(users.values()), roles_for_players))
    socketio.emit('role response', role_dict, room='werewords')

if __name__ == '__main__':
    socketio.run(app, debug = True)