
#!/usr/bin/env python

"""
Example to cycle a bulb between colors in a list, with a smooth fade
between.  Assumes the bulb is already on.
The python file with the Flux LED wrapper classes should live in
the same folder as this script
"""

import os
import sys
import time
from itertools import cycle

this_folder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(this_folder)
from flux_led import WifiLedBulb, BulbScanner, LedTimer


def crossFade(bulb, color1, color2):

	r1,g1,b1 = color1
	r2,g2,b2 = color2
	
	steps = 100
	for i in range(1,steps+1):
		r = r1 - int(i * float(r1 - r2)/steps)
		g = g1 - int(i * float(g1 - g2)/steps)
		b = b1 - int(i * float(b1 - b2)/steps)
		# (use non-persistent mode to help preserve flash)
		bulb.setRgb(r,g,b, persist=False)

def main():

	# Find the bulb on the LAN
	scanner = BulbScanner()
	scanner.scan(timeout=4)

	# Specific ID/MAC of the bulb to set 
	bulb_info = scanner.getBulbInfoByID('ACCF235FFFFF')
	
	if bulb_info:	

		bulb = WifiLedBulb(bulb_info['ipaddr'])

		bulb.turnOn()
		bulb.setRgb(0,0,0, persist=False)
		old_color = (0,0,0)

		previous_post = 0

		while (1):
			print "what color do you want (r, g, b,) ?",
			new_color = tuple(map(int,raw_input().split(',')))
			print "Your new color is: ", new_color
			type(new_color)
			crossFade(bulb, old_color, new_color)
			old_color = new_color

		# BASIC CLIENT INFO PULLS
			#client = TwitchClient(client_id='7mcwm6b6a5x4iafdt8eqceoxi8voqg')
			#users = client.users.translate_usernames_to_ids('jeglikerwhitegirls')
			#for user in users:
				#channel = client.channels.get_by_id(user.id)
			#posts = client.channel_feed.get_posts(channel.id, 10)
			#temp_post = posts[0]
			#print temp_post.body
			#newest_post = temp_post.body.split(',')
		

	else:
		print "Can't find bulb"                   

if __name__ == '__main__':
	main()
