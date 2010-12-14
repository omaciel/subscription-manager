#!/usr/bin/python
#
# Async wrapper module for managerlib methods, with glib integration
#
# Copyright (c) 2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

import threading
import Queue

import glib


class AsyncPool(object):

    def __init__(self, pool):
        self.pool = pool
        self.queue = Queue.Queue()

    def _run_refresh(self, active_on, callback):
        """
        method run in the worker thread.
        """
        try:
            self.pool.refresh(active_on)
            self.queue.put((callback, None))
        except Exception, e:
            self.queue.put((callback, e))

    def _watch_thread(self):
        """
        glib idle method to watch for thread completion.
        runs the provided callback method in the main thread.
        """
        try:
            (callback, error) = self.queue.get(block=False)
            if error:
                callback(error=error)
            else:
                callback()
            return False
        except Queue.Empty, e:
            return True

    def refresh(self, active_on, callback):
        """
        Run pool stash refresh asynchronously.
        """
        glib.idle_add(self._watch_thread)
        threading.Thread(target=self._run_refresh,
                args=(active_on, callback)).start()
