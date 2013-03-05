# Muni LED display
import argparse
import time
import os
import urllib
import urllib2
from xml.dom import minidom
import LPD8806

# Can be used for testing without the LED strip connected
class ConsoleStrip(LPD8806.LEDStrip):
	def __init__(self, leds, dev=None):
		LPD8806.LEDStrip.__init__(self, leds, '/dev/null')

	def update(self):
		line = []
		for x in range(self.leds):
			r = self.buffer[x][self.c_order[0]]
			g = self.buffer[x][self.c_order[1]]
			b = self.buffer[x][self.c_order[2]]
			if r == 255:
				line.append('S')
			elif r == 134:
				line.append('T')
			else:
				line.append('_')
		os.system('clear')
		print ''.join(line)

def main(args):
	if (args.display == 'led'):
		led_strip = LPD8806.LEDStrip(160)
	elif args.display == 'console':
		led_strip = ConsoleStrip(160)	
	led_strip.all_off()
	try:
		while True:
			update(led_strip)	
			time.sleep(5.0)
	except:
		led_strip.all_off()
		raise


def get_predictions(route, stop_id, led_strip):
	base_url = 'http://webservices.nextbus.com/service/publicXMLFeed'
	params = {
		'command': 'predictions',
		'a': 'sf-muni',
		'r': route,
		's': stop_id,
		'useShortTitles': 'true'
	}

	# attempt to fetch and retry on error after a pause
	while True:
		try:
			response = urllib2.urlopen('{url}?{params}'.format(
				url=base_url,
				params=urllib.urlencode(params)))
			break
		except urllib2.URLError, e:	
			print e.reason
			dim(led_strip)
			time.sleep(5.0)
			pass

	dom = minidom.parse(response)
	predictions = dom.getElementsByTagName('prediction')
	return [int(p.attributes['minutes'].value) for p in predictions]


def update(led_strip=None):
	line = [False for i in range(led_strip.leds)]

	# inbound
	for prediction in get_predictions('N', 3915, led_strip):
		line[80 - prediction - 1] = True

	# outbound
	for prediction in get_predictions('N', 3914, led_strip):
		line[80 + prediction] = True

	# set train leds
	for i in range(led_strip.leds):
		if line[i]:
			led_strip.setHSV(i, 225, .7, 1)
		else:
			led_strip.setHSV(i, 0, 0, 0)

	# set station leds
	led_strip.setHSV(79, 320, .7, 1)
	led_strip.setHSV(80, 320, .7, 1)

	# Update the strip
	led_strip.update()

def dim(led_strip):
	# dim all the leds a little
	# TODO
	pass


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Muni trains on a LED strip.')
	parser.add_argument('-d', '--display', choices=['led', 'console'],
						default='led', dest='display',
                   		help='Where to display muni stops.')
	args = parser.parse_args()
	main(args)
