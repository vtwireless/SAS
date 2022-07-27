import socketio
import time

client = socketio.Client()
client.connect("http://localhost:8000")

# Create User
testuser = {
    'secondaryUserName': 'pepsi',
    'secondaryUserEmail': 'pepsi@123',
    'secondaryUserPassword': 'password',
    'deviceID': '1.1.1.2',
    'location': '38.2296,-81.4139'
}

@client.on('createSUResponse')
def createSUResponse(data):
    print(data)

print("Emit event")
client.emit('createSU', testuser)
print("Emitted event")

time.sleep(4)
client.disconnect()
