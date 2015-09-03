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

        time.sleep(1)

        self.proc1.start()
        self.proc2.start()

        self.proc1.join()
        self.proc2.join()

    def pipeline_stage_1(self):
        print "Pipeline stage 1 starting."
        for i in range(0, 20):
            print "Pipeline stage 1 putting %d on the queue."%(i)
            self.interprocess_queue.put(i)
            time.sleep(2)
        print "Pipeline stage 1 putting poison pill on the queue."
        self.interprocess_queue.put(None)

    def pipeline_stage_2(self):
        print "Pipeline stage 2 starting."
        for queue_output in iter(self.interprocess_queue.get, None):
            print "Pipeline stage 2 got %s from the queue."%(str(queue_output))
        print "Pipeline stage 2 received poison pill."

if __name__ == "__main__":
    my_test_object = james_class()


