import eventlet
eventlet.monkey_patch()

from flask import Flask , redirect , render_template , url_for , session , request
from flask_socketio import SocketIO , join_room , leave_room , close_room , emit

players = {}

game_app =Flask("TelebotGame",template_folder="",static_folder="")
game_app.secret_key = "ToolboxToolBotAppGame"

game_socket = SocketIO(game_app,async_mode="eventlet")

@game_app.route("/game&password:<password>&gametype:<game_type>",methods=["POST","GET"])
def game_register(password,game_type):
    game_name = game_type.split("_")
    game_name = f"{game_name[0]}  {game_name[1]}"

    if (request.method == "POST"):
        if (request.form):
            button_name = request.form.get("submit",False)
            username = request.form.get("username")

            if (button_name != False) and (username != ""):
                session["username"] = username
                session["password"] = password
                session["gamename"] = game_type

                if not (password in players):
                    players[password] = {"ids":[]}

                if (game_type == "space_shooter"):
                    return redirect(url_for(game_type))
                else:
                    return render_template("game.html",error="Game does not find !!",room_code=password,game_name=game_name)
            elif (button_name != False):
                return render_template("game.html",error="Please enter your username !!",room_code=password,game_name=game_name)
            else:
                return "404 Error !!"
        else:
            return "Bad request !!"
    else:
        return render_template("game.html",error="",room_code=password,game_name=game_name)

    
@game_app.route("/game/spaceshooter")
def space_shooter():
    if (session.get("username",False) != False):
        return render_template("space_shooter.html")
    else:
        return "Please click on join button to join this game !!"



@game_socket.on("connect")
def connection():
    room = session["password"]
    if (players.get(room , False) != False):
        if (len(players[room]["ids"]) != 2):
            players[room]["ids"].append(len(players[room]["ids"])+1)
            players_id = players[room]["ids"]

            join_room(room)
            emit("income",{"connection_update":True,"ids":players_id},to=room)
            print("A new client connected !!")
        else:
            emit("message","This room is full !!")
    else:
        emit("message","This room closed !! , make another room")



@game_socket.on("disconnect")
def disconnection():
    room = session["password"]
    if (players.get(room , False) != False):
        emit("income",{"closed_room":True},to=room)

        leave_room(room)
        players.pop(room)
        close_room(room)

        print(f"A client disconnected !! , room closed {room} !!")

        session.pop("username")
        session.pop("gamename")
        session.pop("password")



@game_socket.on("message")
def message(data):
    emit("message",data,to=session["password"])



if __name__ == "__main__":
    game_socket.run(game_app)

#https://cdnjs.com/libraries/socket.io