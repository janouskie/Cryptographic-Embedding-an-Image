#!/usr/bin/env python3

import enum
import importlib
from typing import Dict, Optional, Union

DEPENDENCIES = {
    'Cairo': {
        'module': 'cairo',
        'required': True,
    },
    'PyGobject': {
        'module': 'gi',
        'required': True,
    },
    'GdkPixbuf from PyGobject': {
        'module': 'gi.repository.GdkPixbuf',
        'required': True,
    },
    'Poppler from PyGobject': {
        'module': 'gi.repository.Poppler',
        'required': True,
    },
    'GLib from PyGobject': {
        'module': 'gi.repository.GLib',
        'required': True,
    },
    'Mutagen': {
        'module': 'mutagen',
        'required': True,
    },
}

def check_dependencies() -> Dict[str, Dict[str, bool]]:
    ret = dict()  # type: Dict[str, dict]

    for key, value in DEPENDENCIES.items():
        ret[key] = {
            'found': True,
            'required': value['required'],
        }
        try:
            importlib.import_module(value['module'])  # type: ignore
        except ImportError:  # pragma: no cover
            ret[key]['found'] = False

    # Import here to avoid circular import
    from . import exiftool, video
    CMD_DEPENDENCIES = {
        'Exiftool': {
            'cmd': exiftool._get_exiftool_path,
            'required': False,
        },
        'Ffmpeg': {
            'cmd': video._get_ffmpeg_path,
            'required': False,
        },
    }

    for k, v in CMD_DEPENDENCIES.items():
        ret[k] = {
            'found': True,
            'required': v['required'],
        }
        try:
            v['cmd']()  # type: ignore
        except RuntimeError:  # pragma: no cover
            ret[k]['found'] = False

    return ret


@enum.unique
class UnknownMemberPolicy(enum.Enum):
    ABORT = 'abort'
    OMIT = 'omit'
    KEEP = 'keep'
