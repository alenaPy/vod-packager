#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Carbon Coder API
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from carbonapi.CarbonSocketLayer import *
from carbonapi.CarbonUtils import *
from carbonapi.CarbonJob import *
from carbonapi.CarbonSched import *


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Local Carbon Functions
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Retorna el Progreso y el Stado de un Job
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def GetJobState(transcoder_ip, job_guid):
    carbon = CarbonSocketLayer(transcoder_ip)
    Job = CarbonJob(carbon, job_guid)
    return Job.GetState(), str(Job.GetProgress())

def GetJobSpeed(transcoder_ip, job_guid):
    carbon = CarbonSocketLayer(transcoder_ip)
    Job = CarbonJob(carbon, job_guid)
    return Job.GetSpeed()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Remueve un Job
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def RemoveJob(transcoder_ip, job_guid):
    carbon = CarbonSocketLayer(transcoder_ip)
    Job = CarbonJob(carbon, job_guid)
    return Job.Remove()

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Stopea un Job
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def StopJob(transcoder_ip, job_guid):
    carbon = CarbonSocketLayer(transcoder_ip)
    Job = CarbonJob(carbon, job_guid)
    Job.Stop()