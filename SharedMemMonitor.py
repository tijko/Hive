#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time


class ShMemMonitorProcess(object):

    def __init__(self, ppid):
        self.ppid = ppid
        # Create a Sub-Class for Thread module
        self.memory = {'kB':1024, 'mB':1024*1024, 'gB':1024*1024*1024}
        self.scrape_procfs
        
    def calculate_memory(self, vmrss):
        memory, size = vmrss.split()
        return int(memory) * self.memory[size]

    @property
    def scrape_procfs(self):
        rss = 0
        child_ps = set() # XXX create a hash to look-up the previous memory used if already found....
        start = time.time()
        while (time.time() - start) < 100:
            for pid in filter(lambda p: p.isdigit(), os.listdir('/proc')):
                try:
                    # open /proc/PID/status but catch as some can be ephemeral
                    with open('/proc/{}/status'.format(pid)) as fh:
                        ppid = [i for i in fh.readlines() if i.startswith('PPid')]
                        if not ppid:
                            continue
                        ppid = ppid[0].split('\t')[1].strip('\n')
                        if ppid == self.ppid:
                            if pid not in child_ps:
                                print('Adding Process to Set...')
                                child_ps.add(pid)
                                with open('/proc/{}/comm'.format(pid)) as fh:
                                    comm = fh.readlines()
                                    print('Found Child Process {}!'.format(pid))
                                    print(comm)
                                    time.sleep(1)
                                with open('/proc/{}/status'.format(pid)) as fh:
                                    vmrss = fh.readlines()
                                    vmrss = [i for i in vmrss if i.startswith('VmRSS')]
                                    if not vmrss:
                                        continue
                                    vmrss = vmrss[0].split('\t')[1].strip('\n')
                                    rss += self.calculate_memory(vmrss)
                                print('Bytes....{}'.format(rss))
                            else:
                                print('Process was in set...')
                except FileNotFoundError:
                    continue


if __name__ == '__main__':
    shmem = ShMemMonitorProcess('327257')