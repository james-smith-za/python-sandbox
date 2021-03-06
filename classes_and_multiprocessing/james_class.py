import os
import multiprocessing
import time


class james_class:
    """Test class written by James to figure out whether using classes and multiprocessing together works at all.
    """

    def __init__(self):
        print "now in __init__"
        self.interprocess_queue = multiprocessing.Queue()
        self.proc1 = multiprocessing.Process(name="stage1", target=self.pipeline_stage_1)
        self.proc2 = multiprocessing.Process(name="stage2", target=self.pipeline_stage_2)

        self.status = multiprocessing.Value('H', 0)

        time.sleep(1)

        self.proc1.start()
        self.proc2.start()

        # If these are uncommented, it waits for the processes to join before __init__ even finishes, and it holds on to the session.
        #self.proc1.join()
        #self.proc2.join()

    def pipeline_stage_1(self):
        print "Pipeline stage 1 starting."
        for i in range(0, 20):
            print "Pipeline stage 1 putting %d on the queue."%(i)
            self.interprocess_queue.put(i)
            print "ps1 writing %d to status value"%(i)
            self.status.value = i
            time.sleep(2)
        print "Pipeline stage 1 putting poison pill on the queue."
        self.interprocess_queue.put(None)

    def pipeline_stage_2(self):
        print "Pipeline stage 2 starting."
        for queue_output in iter(self.interprocess_queue.get, None):
            print "Pipeline stage 2 got %s from the queue."%(str(queue_output))
            print "self.status: %d"%self.status.value
        print "Pipeline stage 2 received poison pill."

    def do_something_else_in_the_meantime(self):
        print "Can something else be done while you're waiting?"
        print "Apparently it can!" + " ... I hope..."

if __name__ == "__main__":
    my_test_object = james_class()
    time.sleep(7)
    my_test_object.do_something_else_in_the_meantime()
    time.sleep(2)
    my_test_object.do_something_else_in_the_meantime()


