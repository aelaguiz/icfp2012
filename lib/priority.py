import os
import random

def enqueue(array, item, priority):
    """Adds an item to the queue."""
    #print "Enqueue", len(item), priority
    array.append([item, priority])

def dequeue(lock, array):
    if(len(array) == 0):
        return None

    #print os.getpid(), "Waiting for lock"
    lock.acquire()
    #print os.getpid(), "Acquired lock"

    if(len(array) == 0):
        lock.release()
        #print os.getpid(), "Released lock"
        return None

    idx = random.randint(0, len(array)-1)
    res = array.pop(idx)
    lock.release()
    #print os.getpid(), "Released lock"
    return res[0]


    """Removes the highest priority item (smallest priority number) from the queue."""
    max = -1
    dq = 0
    count = len(array)

    if(count > 0):
        count -= 1

        for i in range(len(array)):
            if array[i][1] != None and array[i][1] > max:
                max = array[i][1]

        if max == -1:
            res = array.pop(0)
            #print "Popped", res[1]

            lock.release()
            print os.getpid(), "Released lock"
            return res[0]

            #return array.pop(0)
        else:
            for i in range(len(array)):
                if array[i][1] != None and array[i][1] <= max:
                    max = array[i][1]
                    dq = i
            res = array.pop(dq)
            #print "Popped", len(res)
            #print "Popped", res[1]

            lock.release()
            print os.getpid(), "Released lock"
            return res[0]
            #return array.pop(dq)
    
    lock.release()
    print os.getpid(), "Released lock"
