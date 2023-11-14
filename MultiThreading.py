#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, threading, abc, os
from optparse import OptionParser

OUT = 'Generated'
VIDEO_DIR = OUT + '/Videos'
AUDIO_DIR = OUT + '/Audios'
DOWNLOADS = OUT + '/Downloads'

def parse_options(num_of_threads):
    parser = OptionParser()
    parser.add_option("-t", action="store", type="int", dest="threadNum", default=num_of_threads,
                      help="thread count [1]")
    (options, args) = parser.parse_args()
    return options

class thread_sample(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.kill_received = False
 
    def run(self):
        current = 0
        while not self.kill_received:
            res = self.func(self.args[current])
            print(res)
            current += 1
            if current >= len(self.args):
                break

def has_live_threads(threads):
    return True in [t.is_alive() for t in threads]

def multi_thread(func, args, num_of_threads=1):
    options = parse_options(num_of_threads)    
    threads = []
    
    def spliter(n, args):
        return [args[i::n] for i in range(n)]

    for i in range(options.threadNum):
        # split the args so that each thread has a part of the args
        thread = thread_sample(func, spliter(options.threadNum, args)[i])
        thread.start()
        threads.append(thread)

    while has_live_threads(threads):
        try:
            # synchronization timeout of threads kill
            [t.join(1) for t in threads
             if t is not None and t.is_alive()]
            
        except KeyboardInterrupt:
            for t in threads:
                t.kill_received = True
                
            return True
        
    return False

if __name__ == '__main__':
    def test(args):
        print(args)
    
    multi_thread(test, range(100), 2)