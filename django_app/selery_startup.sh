#!/bin/bash
celery -A blog_nextgen worker --beat --loglevel=debug
