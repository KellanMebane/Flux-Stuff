# TO DO
# MULTI COMMANDS WORK. ARGUMENTS PASSED, BUT NOT SETUP.
# ADD PRESETS
# ADD CUSTOMS
# ADD BRIGHTNESS
# ADD FADING STROBING ETC. (PROBABLY SAME FLOW AS CUSTOMS)
# TRY TO MAKE IT A VOTE (DEMOCRACY)
# IF THAT WORKS OUT, LOOK TO MAKE FASTER (AKA KEEP BULB CONNECTION)

import sys
import os
import irc.bot
import requests
import time
import struct
from itertools import cycle
try:
	import webcolors
	webcolors_available = True
except:
	webcolors_available = False

this_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(this_folder)
from flux_led import WifiLedBulb, BulbScanner, LedTimer


class TwitchBot(irc.bot.SingleServerIRCBot): # heavily inspired by twitch example https://github.com/twitchdev/chat-samples/blob/master/python/chatbot.py
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id,
                   'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print 'Connecting to ' + server + ' on port ' + str(port) + '...'
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port, 'oauth:'+token)], username, username)

        
    def on_welcome(self, c, e):
        print 'Joining ' + self.channel

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):

        # Previous, single command mode.
        #if e.arguments[0][:1] == '!':
        #    cmd = e.arguments[0].split(' ')[0][1:] # can modify this to get the entire comment, then parse it down. maybe just pass the left overs into do_command and only use them when needed
        #    test_str = e.arguments[0] # gets the full line after the command
        #    print 'Test Line: ' + test_str
        #    print 'Received command: ' + cmd
        #    self.do_command(e, cmd, test_str)

        ### WAX OFF EVERYTHING BEFORE FIRST COMMAND (SIMPLIFIES LOOP)
        test_str = e.arguments[0][0:]
        print "TEST STRING: " + test_str
        temp = test_str.split('!', 1)[0][0:] 
        test_str = test_str.replace(temp, "", 1)
        try:
            print "TEMP: " + temp
            print "REPLACE:" + test_str
        except IOError:
            print "initial karate training failed"
        ### END WAX

        i = 0 # iterator
        input_list = test_str.split('!')[1:] # break down into command blocks
        print input_list # just logging
        i_max = len(input_list) # constraint: end after last block command executes
        while (i < i_max): # run through blocks
            cmd = input_list[i].split(' ')[0][0:] # ex: {fun no more} --> {fun}
            argi = input_list[i].replace(cmd + " ", "", 1) # ex: {fun no more} --> {no more}
            self.do_command(e, cmd, argi) # execute the command
            i = i + 1 # move to next command block
            
        return

    def do_command(self, e, cmd, test_str):
        c = self.connection

        # Poll the API to get current game.
        if cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id,
                       'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] +
                      ' is currently playing ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id,
                       'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] +
                      ' channel title is currently ' + r['status'])

        # Provide basic information to viewers for specific commands

        # OLD WAY TO DO HEX CODE
        # Hex input as command
        # elif cmd[0] == '#':
        #     if len(cmd) == 7:
        #         newcmd = cmd.replace("#", "")
        #         try: 
        #             int(newcmd, 16)    
        #             bulb_info = autoScan()
        #             message = "Bulb color changed to " + cmd
        #             c.privmsg(self.channel, message)
        #             if bulb_info:
        #                 bulb = WifiLedBulb(bulb_info['ipaddr'])
        #                 bulb.turnOn()
        #                 rgb = struct.unpack('BBB', newcmd.decode('hex')) #convert hex to tuple
        #                 bulb.setRgb(rgb[0], rgb[1], rgb[2], persist=False)
        #         except ValueError:
        #             c.privmsg(self.channel, cmd + " is not a valid color code!")
        #     else:
        #         message = "Invalid command: color format example: #12D4F6"
        #         c.privmsg(self.channel, message)

        # Test Color Change
        elif cmd == "off":
            message = "Bulb has been turned off"
            bulb_info = autoScan()
            if bulb_info:
                bulb = WifiLedBulb(bulb_info['ipaddr'])
                bulb.turnOff()
                c.privmsg(self.channel, message)

        elif cmd == "warm": # Warm white big-command
            bulb_info = autoScan()
            if bulb_info:
                bulb = WifiLedBulb(bulb_info['ipaddr'])
                bulb.turnOn()
                

        # Will Be Direct Color Command or Fail
        else:
            try:
                rgb = generateRGB(cmd) # try to turn it into RGB
                bulb_info = autoScan() # at this point it worked
                if bulb_info: # change the bulb colors
                    bulb = WifiLedBulb(bulb_info['ipaddr'])
                    bulb.turnOn()
                    bulb.setRgb(rgb[0], rgb[1], rgb[2], persist=False)
                    message = "Bulb color changed to " + cmd
                    c.privmsg(self.channel, message)
            except ValueError: # If value doesn't exist, it's neither a color or a command
                c.privmsg(self.channel, cmd + " is not a color!")
                c.privmsg(self.channel, "Did not understand command: " + cmd)

def autoScan():
	scanner = BulbScanner()
	scanner.scan(timeout=4)
	bulb_info = scanner.getBulbInfoByID('ACCF235FFFFF')
	return bulb_info

def generateRGB(cmd): # given string, convert it to based on type of input: hex, name, rgb triplet.
    if (cmd[0] == '#'):
        rgb = webcolors.hex_to_rgb(cmd)
    elif (cmd[0] == '(') and (cmd[len(cmd) - 1] == ')'):
        newcmd_a = cmd.replace("(", "")
        newcmd_b = newcmd_a.replace(")", "") 
        rgb = tuple(newcmd_b.split(","))
    else:    
        rgb = webcolors.name_to_rgb(cmd)
    return rgb

def main(): # basic main function, get's twitch info and creates the bot
    if len(sys.argv) != 5:
        print("Usage: twitchbot <username> <client id> <token> <channel>")
        sys.exit(1)

    username = sys.argv[1]
    client_id = sys.argv[2]
    token = sys.argv[3]
    channel = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()


if __name__ == "__main__":
    main()
