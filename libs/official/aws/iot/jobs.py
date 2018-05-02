"""
.. module:: aws_iot_jobs

************************************
Amazon Web Services IoT Jobs Library
************************************

The Zerynth AWS IoT Jobs Library can be used to handle `IoT Jobs <https://docs.aws.amazon.com/iot/latest/developerguide/iot-jobs.html>`_ with ease.

    """

import threading
import json
from mqtt import mqtt

class Jobs():
    """
==========
Jobs class
==========

.. class:: Jobs(thing)

    This class allows the retrieval of the :samp:`thing` job list.
    
    It requires the connection to thw MQTT broker to be already established: It subscribes to various
    topic to receive jobs notifications.

    """
    def __init__(self,thing):
        self.thing = thing
        self.evt = threading.Event()
        self.job_data = None
        self.chprefix = "$aws/things/"+self.thing.thingname+"/jobs"
        self.topic = self.chprefix+"/get/accepted"
        #subscribe to notify
        self.thing.mqtt.subscribe([[self.chprefix+"/notify", 0]])
        self.thing.mqtt.on(mqtt.PUBLISH, self._handle_notify, self._is_notify)
        self._changed = False

    def _is_notify(self,data):
        if 'message' in data:
            return data['message'].topic.startswith(self.chprefix+"/notify")
        return False


    def _handle_notify(self,client,data):
        self._changed = True
        

    def changed(self):
        """
    .. method:: changed()
    
        Return True if there are new pending jobs. If called again, and in the meantime no new job notifications have been received, return False.

        """
        ret = self._changed
        self._changed = False
        return ret

    def _handle_job(self,client,data):
        self.job_data = json.loads(data["message"].payload)
        self.evt.set()

    def _is_job(self,data):
        if 'message' in data:
            return data['message'].topic.startswith(self.topic)
        return False

    def list(self):
        """
    .. method:: list()
    
        Retrieve the list of jobs for the current Thing. The result value is a tuple with two items. The first item is the list of IN_PROGRESS jobs, while the second item is the list of QUEUED jobs (as :class:`Job` instances). 

        This method is *blocking*. Control is not released until the list of jobs is retrieved. Moreover, it is not safe to call the method from different threads.

        """
        self.job_data = None
        self.thing.mqtt.subscribe([[self.topic, 0]])
        self.thing.mqtt.on(mqtt.PUBLISH, self._handle_job, self._is_job)

        msg = {'clientToken': self.thing._client_token}

        self.thing.mqtt.publish(self.chprefix+'/get', json.dumps(msg))
        self.evt.wait()
        self.evt.clear()
        self.thing.mqtt.unsubscribe([self.topic])
        inp = []
        inq = []
        if not self.job_data:
            return inp,inq
        if "inProgressJobs" in self.job_data:
            for item in self.job_data["inProgressJobs"]:
                job = Job(self.thing,item["jobId"])
                inp.append(job)
        if "queuedJobs" in self.job_data:
            for item in self.job_data["queuedJobs"]:
                job = Job(self.thing,item["jobId"])
                inq.append(job)

        self.job_data = None
        return inp,inq


class Job():
    """
=========
Job class
=========

.. class:: Job(thing,jobid)

    This class abstracts an IoT Job related to a particular :samp:`thing` and having jobId :samp:`jobid`.
    There is no need to manually create instances of this class, they are returned by methods of the :class:`Jobs` class.

    """
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    SUCCEEDED = "SUCCEEDED"
    REJECTED = "REJECTED"
    
    def __init__(self,thing,jobid):
        self.thing = thing
        self.jobid = jobid
        self.chprefix = "$aws/things/"+self.thing.thingname+"/jobs/"+self.jobid
        self.evt = threading.Event()

    def _handle_job(self,client,data):
        self.job_data = json.loads(data["message"].payload)
        self.evt.set()
        
    def _is_job(self,data):
        if 'message' in data:
            return data['message'].topic.startswith(self.chprefix)
        return False
    
    def _handle_upd_job(self,client,data):
        upd = json.loads(data["message"].payload)
        self.job_data = upd["status"]
        self.evt.set()
        
    def _is_upd_job(self,data):
        if 'message' in data:
            return data['message'].topic.startswith(self.chprefix+"/updated")
        return False

    def describe(self):
        """
    .. method:: describe()

        Retrieves data about the job. In particular the fields :samp:`version`, :samp:`status` and :samp:`document` are associated to the job instance after a successful :samp:`describe`.
        
        This method is *blocking*. Control is not released until the job description is retrieved. Moreover, it is not safe to call the method from different threads.

        Return True on success, False otherwise.

        """
        self.job_data = None
        self.thing.mqtt.subscribe([[self.chprefix+"/get/accepted", 0]])
        self.thing.mqtt.on(mqtt.PUBLISH, self._handle_job, self._is_job)

        msg = {'clientToken': self.thing._client_token}

        self.thing.mqtt.publish(self.chprefix+'/get', json.dumps(msg))
        self.evt.wait()
        self.evt.clear()
        self.thing.mqtt.unsubscribe([self.chprefix+"/get/accepted"])
        if self.job_data is None:
            return False
        try:
            self.status = self.job_data["execution"]["status"]
            self.version = self.job_data["execution"]["versionNumber"]
            self.document = self.job_data["execution"]["jobDocument"]
        except Exception as e:
            self.job_data = None
            return False
        self.job_data = None
        return True
       
    def update(self,status,status_details={}):
        """
    .. method:: update(status,status_details={})

        Updates the status of the job. The :samp:`status` can be one of the following class constant:

        * :samp:`Job.IN_PROGRESS`
        * :samp:`Job.FAILED`
        * :samp:`Job.SUCCEEDED`

        The optional field :samp:`status_details` can contain custom values that are associated to the job status.

        This method is *blocking*. Control is not released until the status change is signaled. Moreover, it is not safe to call the method from different threads.

        Return True on success, False otherwise.

        """
        self.job_data = ""
        self.thing.mqtt.subscribe([[self.chprefix+"/updated/#", 0]])
        self.thing.mqtt.on(mqtt.PUBLISH, self._handle_upd_job, self._is_upd_job)
        msg = {
            "status":status,
            "statusDetails":status_details,
            "expectedVersion":self.version,
        }
        self.thing.mqtt.publish(self.chprefix+'/update', json.dumps(msg))
        self.evt.wait()
        self.evt.clear()
        self.thing.mqtt.unsubscribe([self.chprefix+"/updated/#"])
        return self.job_data == status

    
    def __str__(self):
        return self.jobid+"@"+self.thing.thingname





