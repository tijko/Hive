#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time


class ShMemMonitorProcess(object):

    def __init__(self, ppid: str):
        self.ppid = ppid
        # Create a Sub-Class for Thread module
        self.memory = {'kB':1024, 'mB':1024*1024, 'gB':1024*1024*1024}
        self.scrape_procfs
        
    def calculate_memory(self, vmrss: str) -> int:
        memory, size = vmrss.split()
        return int(memory) * self.memory[size]

    @property
    def scrape_procfs(self):
        rss = 0
        child_ps = dict()
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
                            with open('/proc/{}/status'.format(pid)) as fh:
                                vmrss = fh.readlines()
                                vmrss = [i for i in vmrss if i.startswith('VmRSS')]
                            if not vmrss:
                                continue
                            vmrss = vmrss[0].split('\t')[1].strip('\n')
                            ps_rss = self.calculate_memory(vmrss)
                            if not child_ps.get(pid):
                                with open('/proc/{}/comm'.format(pid)) as fh:
                                    comm = fh.readlines()
                                    print('Found Child Process {}!'.format(pid))
                                    print(comm)
                                print('Adding Process to Hash...')
                                child_ps[pid] = ps_rss
                                rss += ps_rss
                                time.sleep(1)
                            else:
                                # re-calculate process memory
                                print('Process was already found running...')
                                print('Re-calculating memory usage...')
                                previous_rss_used = child_ps[pid]
                                if previous_rss_used > ps_rss:
                                    memory_adj = previous_rss_used - ps_rss
                                    rss -= memory_adj
                                elif previous_rss_used <= ps_rss:
                                    memory_adj = ps_rss - previous_rss_used
                                    rss += memory_adj
                                child_ps[pid] = ps_rss
                            print('Bytes....{}'.format(rss))
                except FileNotFoundError:
                    continue


if __name__ == '__main__':
    pid = sys.argv[1]
    shmem = ShMemMonitorProcess(pid)