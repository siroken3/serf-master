#!/usr/bin/env python

import os
import logging

class SerfHandler(object):
    def __init__(self):
        self.name = os.environ['SERF_SELF_NAME']
        _role = os.environ.get('SERF_SELF_ROLE')
        self.tag_key_value = [{'SERF_TAG_ROLE': _role}] if _role else []
        self.tag_key_value = self.tag_key_value.extend(
            [k[len('SERF_TAG_'):] + '_' + v for k, v
             in os.environ.items() if k.startswith('SERF_TAG_')]
        )
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
                self.handlers[k + '_' + v] = handler
        else:
            # for backward compatibility
            self.handlers['ROLE_' + tag] = handler

    def get_klass(self):
        klass = False
        for k_v in self.tag_key_value:
            if k_v in self.handlers:
                klass = self.handlers[k_v]
            elif 'default' in self.handlers:
                klass = self.handlers['default']
        return klass

    def run(self):
        klass = self.get_klass()
        if not klass:
            self.log("no handler for role")
        else:
            try:
                getattr(klass, self.event)()
            except AttributeError:
                self.log("event not implemented by class")
