#!/usr/bin/env python

import os
import logging


class SerfHandler(object):
    def __init__(self):
        self.name = os.environ['SERF_SELF_NAME']
        self.role = os.environ.get('SERF_TAG_ROLE') or os.environ.get('SERF_SELF_ROLE')
        if self.role and len(self.role) > 0:
            self.tag_key_value = set(['ROLE_' + self.role])
        else:
            self.tag_key_value = set([])
        _prefix = 'SERF_TAG_'
        for k, v in os.environ.items():
            if k.startswith(_prefix):
                self.tag_key_value.add(k[len(_prefix):] + '_' + v)
        self.logger = logging.getLogger(type(self).__name__)
        if os.environ['SERF_EVENT'] == 'user':
            self.event = os.environ['SERF_USER_EVENT']
        else:
            self.event = os.environ['SERF_EVENT'].replace('-', '_')

    def log(self, message):
        self.logger.info(message)


class SerfHandlerProxy(SerfHandler):

    def __init__(self):
        super(SerfHandlerProxy, self).__init__()
        self.handlers = {}

    def register(self, tag, handler):
        if type(tag) == dict:
            for k, v in tag.items():
                self.handlers[k.upper() + '_' + v] = handler
        elif tag == 'default':
            # for backward compatibility
            self.handlers[tag] = handler
        else:
            # for backward compatibility
            self.handlers['ROLE_' + tag] = handler

    def get_klasses(self):
        klasses = [self.handlers['default']] if 'default' in self.handlers else []
        for k_v in self.handlers:
            if k_v in self.tag_key_value:
                klasses.append(self.handlers[k_v])
        return klasses

    def run(self):
        klasses = self.get_klasses()
        if not klasses:
            self.log("no handler for role")
        else:
            try:
                for klass in klasses:
                    getattr(klass, self.event)()
            except AttributeError:
                self.log("event not implemented by class")
