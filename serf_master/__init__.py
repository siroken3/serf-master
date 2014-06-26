#!/usr/bin/env python

import os
import logging


class SerfHandler(object):
    def __init__(self):
        self.name = os.environ['SERF_SELF_NAME']
        _role = os.environ.get('SERF_SELF_ROLE')
	#print "{0}:{2}: SERF_SELF_ROLE = '{1}'".format(self.name, _role, type(self).__name__)
        self.tag_key_value = ['ROLE_' + _role] if len(_role) > 0 else []
        _prefix = 'SERF_TAG_'
	for k, v in os.environ.items():
            if k.startswith(_prefix):
	        self.tag_key_value.append(k[len(_prefix):] + '_' + v)
        self.logger = logging.getLogger(type(self).__name__)
        if os.environ['SERF_EVENT'] == 'user':
            self.event = os.environ['SERF_USER_EVENT']
        else:
            self.event = os.environ['SERF_EVENT'].replace('-', '_')
	#print self.tag_key_value

    def log(self, message):
        self.logger.info(message)


class _NopHandler(SerfHandler):
    pass


class SerfHandlerProxy(SerfHandler):

    def __init__(self, default=_NopHandler()):
        super(SerfHandlerProxy, self).__init__()
        self.handlers = {}
        self.default_handler = default

    def register(self, tag, handler):
        if type(tag) == dict:
            for k, v in tag.items():
                self.handlers[k + '_' + v] = handler
        else:
            # for backward compatibility
            self.handlers['ROLE_' + tag] = handler

    def get_klasses(self):
        klasses = []
        for k_v in self.handlers:
            if k_v in self.tag_key_value:
                klasses.append(self.handlers[k_v])
        if not klasses:
            klasses.append(self.default_handler)
        #print "self.handlers = {0}".format(self.handlers)
        #print "self.tag_key_value = {0}".format(self.tag_key_value)
	#print "{0}:{1}".format(type(self).__name__, klasses)
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
