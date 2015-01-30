# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

MB = 1 * 1024 * 1024

FORMAT = '%(asctime)-15s - %(levelname)-10s - %(name)s - %(message)s'
DATEFMT = '%Y-%m-%d %H:%M:%S'
LOGLEVEL = logging.WARNING
CONTEXT_LOGLEVEL_ATTR = 'click_utils_loglevel'
MAXBYTES = 15 * MB
BACKUPCOUNT = 14
