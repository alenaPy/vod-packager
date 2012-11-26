import sys






if __name__ == "__main__":
	if len(sys.argv) == 2:
		if 'start'     == sys.argv[1]:
		    pass
		elif 'stop'    == sys.argv[1]:
		    pass
		elif 'restart' == sys.argv[1]:
		    pass
		elif 'test'    == sys.argv[1]:
		    pass
		
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|test|install" % sys.argv[0]
		sys.exit(2)