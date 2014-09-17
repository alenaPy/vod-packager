#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Local
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import logging
import os
import sys
import time
import shutil
import getopt

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Stand alone script
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from django.core.management import setup_environ
from Packager import settings
setup_environ(settings)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Modelo de la aplicacion
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Packager_app import models

import Settings


def usage():
    print "Usage: queue_dump [OPTION] [FILE]..."
    print "Dump information about Nepe Queue"
    print ""
    print "Options:"
    print "-z, --zabbix=\t"
    print "-w, --waiting=\tWaiting Queue"
    print "-a, --all=\tDump all information"
    print "-w, --queue=\tQueue"
    print "-u, --unasigned\tUnasigned Queue"
    print "-U, --unasigned_waiting\tUnasigned Waiting Queue"
    print "-p, --pulling\tPulling Queue"
    print "-e, --error\tError Queue"
    print "-E, --eta\tTime to finish all queues"
    print "\n"
    print "Report bugs to <ebilli@claxson.com>"


def get_seconds(duration=None):
    if duration is not None:
	hh,mm,ss = duration.split(':')
	return ( int(hh) * 3600 + int(mm) * 60 + int(ss) )
    return -1


def get_speed_average(vprofile=None):

    if vprofile is not None:
	acum = 0.0
	i = 0
	vr_list = models.VideoRendition.objects.filter(status='F', video_profile=vprofile)        
	for vr in vr_list:
	    if vr.speed != '':
		acum = acum + float(vr.speed)
	    else:
		i = i + 1	
	if acum != 0.0:	
	    return acum / (len(vr_list) - i)
	else:
	    return 0
    else:
	return -1





def get_unasigned_eta(vr_queue_unasigned=None, dict_vp_speed = {}):
    if vr_queue_unasigned is not None:
	acum = 0
	for vrq_unasigned in vr_queue_unasigned:
	    duration = get_seconds(vrq_unasigned.item.run_time)
	    if duration != -1:
		speed_vp = dict_vp_speed[str(vrq_unasigned.video_profile.id)]
		if speed_vp == 0:
		    continue
		if speed_vp != -1:
		    acum = acum + (duration / float(speed_vp))
		else:
		    return -1
	    else:
		return -1
	return acum
    else:
	return -1

def get_queue_eta(vr_queue_queue=None, dict_vp_speed = {}):
    if vr_queue_queue is not None:
	acum = 0
	progress = 0
	for vrq_queue in vr_queue_queue:
	    duration = get_seconds(vrq_queue.item.run_time)
	    if duration != -1:
		if vrq_queue.speed == '':
		    speed_vp = dict_vp_speed[str(vrq_queue.video_profile.id)]
		else:
		    speed_vp = vrq_queue.speed

		if speed_vp != -1:
		    if progress != 0:
			acum = acum + (duration /((100-int(progress))/100) /float(speed_vp) )
		    else:
			acum = acum + (duration / float(speed_vp))
		else:
		    return -1
	    else:
		return -1
	return acum
    else:
	return -1

def get_renditionqueue_eta(rq_waiting=None, dict_vp_speed = {}):
    if rq_waiting is not None:
	i = 0
	acum = 0
	for rq in rq_waiting:
	    vp_list = get_video_profile(rq.item)
	    i = i + len(vp_list)
	    for vp in vp_list:
		duration = get_seconds(rq.item.run_time)
		if duration != -1:
		    speed_vp = dict_vp_speed[str(vp.id)]
		    if speed_vp == 0:
			continue
		    if speed_vp != -1:
			acum = acum + (duration / float(speed_vp))
		    else:
			return -1,-1
		else:
		    return -1,-1
	return acum, i
    else:
	return -1,-1
    
    
def get_video_profile (Item=None):
    if Item is not None:
	VProfileList_pre = models.GetVideoProfilesBrand(Item.internal_brand)
	if Item.internal_brand.format == 'HD' and Item.format == 'SD':
	    #
	    # Hay que eliminar los HD
	    #
	    VProfileList = []
	    for VProfile in VProfileList_pre:
		if VProfile.format == 'SD':
		    VProfileList.append(VProfile)
	else:
	    VProfileList = VProfileList_pre	     
    
	return VProfileList
    else:
	return []
    

def main():
    try:
	opts, args = getopt.getopt(sys.argv[1:], "hzwquUepEa", [ "help", "zabbix", "waiting","queue","unasigned", "unasigned_waiting", "error", "pulling", "eta", "all"])
    except getopt.GetoptError as err:
	# print help information and exit:
        print str(err)
	usage()
        sys.exit(2)     

    zabbix  = False        
    option  = ''    
    
    for o,a in opts:
	if o == '-h':
	    usage()
	    sys.exit()
	elif o in ('-z', '--zabbix'):
	    zabbix = True
	elif o in ('-w', '--waiting'):
	    option = 'w'
	elif o in ('-q', '--queue'):
	    option = 'q'
	elif o in ('-u', '--unasigned'):
	    option = 'u'
	elif o in ('-U', '--unasigned_waiting'):
	    option = 'U'
	elif o in ('-e', '--error'):
	    option = 'e'
	elif o in ('-p', '--pulling'):
	    option = 'p'
	elif o in ('-E', '--eta'):
	    option = 'E'
	elif o in ('-a', '--all'):
	    zabbix = False
	    option = 'a'
    
    vr_queue_unasigned = models.VideoRendition.objects.filter(status='U')
    vr_queue_error     = models.VideoRendition.objects.filter(status='E')
    vr_queue_queue     = models.VideoRendition.objects.filter(status='Q')

    rq_queue_waiting   = models.RenditionQueue.objects.filter(queue_status='W')
    rq_queue_pulling   = models.RenditionQueue.objects.filter(queue_status='P')




    vp_list = models.VideoProfile.objects.filter(status='E')

    dict_vp_speed = {}

    for vp in vp_list:
	dict_vp_speed[str(vp.id)] = get_speed_average(vp)


    if zabbix == False:
	if option == 'a':
	    eta, unvr = get_renditionqueue_eta(rq_queue_waiting, dict_vp_speed)
	    eta =  (get_unasigned_eta(vr_queue_unasigned, dict_vp_speed) + eta + get_queue_eta(vr_queue_queue, dict_vp_speed)) / 60 / 60 / 9
	    print '%s\t%s\t%s\t%s\t%s\t%s' % ('UNASIGNED','QUEUE','ERROR','WAITING','PULLING', 'ETA (hr)')
	    print '%d +(%d)\t%d\t%d\t%d\t%d\t%f' % (len(vr_queue_unasigned),unvr, len(vr_queue_queue), len(vr_queue_error), len(rq_queue_waiting), len(rq_queue_pulling), eta)
	else:
	    print 'Bad Option\n'
	    usage()
	    sys.exit()
    else:
	if option == 'E':
	    eta, unvr = get_renditionqueue_eta(rq_queue_waiting, dict_vp_speed)
	    eta =  (get_unasigned_eta(vr_queue_unasigned, dict_vp_speed) + eta + get_queue_eta(vr_queue_queue, dict_vp_speed)) / 60 / 60 / 9		    
	    print eta
	if option == 'w':
	    print len(rq_queue_waiting)
	if option == 'q':
	    print len(vr_queue_queue)
	if option == 'u':
	    print len(vr_queue_unasigned)
	if option == 'U':
	    eta, unvr = get_renditionqueue_eta(rq_queue_waiting, dict_vp_speed)
	    print unvr
	if option == 'e':
	    print len(vr_queue_error)
	if option == 'p':
	    print len(rq_queue_pulling)
    
main()	    