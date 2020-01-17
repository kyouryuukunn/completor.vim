# -*- coding: utf-8 -*-

import uuid
import json
import logging
import vim
from completor import Completor
from completor.compat import to_unicode
logger = logging.getLogger('completor')

JSONRPC_VERSION = '2.0'

# Workflow: initilize -> initialized -> didchangeconfiguration -> open
# -> completion


class Base(object):
    method = ''
    # Is this request a notification?
    notify = False

    def to_dict(self):
        return

    def gen_request(self, params=None):
        req = {
            'jsonrpc': JSONRPC_VERSION,
            'method': self.method,
        }
        if params is not None:
            req['params'] = params
        if not self.notify:
            req['id'] = uuid.uuid4().hex[:16]
        return req

    def to_request(self):
        req = self.gen_request(params=self.to_dict())
        req_id = req.get('id')
        data = json.dumps(req)
        items = ['Content-Length: {}'.format(len(data)), '', data]
        return req_id, '\r\n'.join(items)


class Initialize(Base):
    method = 'initialize'

    def __init__(self, ppid, workspace):
        self.ppid = ppid
        self.workspace = workspace

    def to_dict(self):
        return {
            'processId': self.ppid,
            'capabilities': {
                'workspace': {'configuration': True},
                'textDocument': {}
            },
            'rootUri': self.workspace[0]['uri'],
            # 'workspaceFolders': self.workspace,
        }


class Initialized(Base):
    method = 'initialized'
    notify = True

    def to_dict(self):
        return {}


class DidChangeConfiguration(Base):
    method = 'workspace/didChangeConfiguration'
    notify = True

    def __init__(self, filetype):
        m = Completor.get_option('filetype_map') or {}
        m = m.get(filetype, {})

        # convert vim.Dictionary to python dic
        def to_python_type(vim_type):
            if isinstance(vim_type, vim.Dictionary):
                python_type = {}
                keys = vim_type.keys()
                for k in keys:
                    v = vim_type.get(k)
                    python_type[to_unicode(k, 'utf-8')] = to_python_type(v)
            elif isinstance(vim_type, vim.List):
                python_type = []
                for i in vim_type:
                    python_type.append(to_python_type(i))
            elif isinstance(vim_type, bytes):
                python_type = to_unicode(vim_type, 'utf-8')
            else:
                python_type = vim_type
            return python_type

        self.config = {}
        if m.has_key('workspace_config'):
            vimm = m.get('workspace_config')
            self.config = to_python_type(vimm)
        else:
            self.config = {}
        logger.info('config: %r', self.config)

    def to_dict(self):
        return {
            'settings': self.config
        }


class DidOpen(Base):
    method = 'textDocument/didOpen'
    notify = True

    def __init__(self, uri, language_id, version, text):
        self.uri = uri
        self.language_id = language_id
        self.version = version
        self.text = text

    def to_dict(self):
        return {
            'textDocument': {
                'uri': self.uri,
                'languageId': self.language_id,
                'version': self.version,
                'text': self.text
            }
        }


class DidSave(Base):
    method = 'textDocument/didSave'
    notify = True

    def __init__(self, uri, version, text):
        self.uri = uri
        self.version = version
        self.text = text

    def to_dict(self):
        return {
            'textDocument': {
                'uri': self.uri,
                'version': self.version
            },
            'text': self.text
        }


class DidChange(Base):
    method = 'textDocument/didChange'
    notify = True

    def __init__(self, uri, version, text):
        self.uri = uri
        self.version = version
        self.text = text

    def to_dict(self):
        return {
            'textDocument': {
                'uri': self.uri,
                'version': self.version
            },
            'contentChanges': [
                {
                    'text': self.text
                }
            ]
        }


class Completion(Base):
    method = 'textDocument/completion'

    def __init__(self, uri, line, offset):
        self.uri = uri
        self.line = line
        self.offset = offset

    def to_dict(self):
        return {
            'textDocument': {
                'uri': self.uri,
            },
            'position': {
                'line': self.line,
                'character': self.offset
            }
        }


class Definition(Completion):
    method = 'textDocument/definition'


class Format(Base):
    method = 'textDocument/formatting'

    def __init__(self, uri):
        self.uri = uri

    def to_dict(self):
        return {
            'textDocument': {
                'uri': self.uri
            }
        }


class Rename(Completion):
    method = 'textDocument/rename'

    def __init__(self, *args, **kwargs):
        Completion.__init__(self, *args, **kwargs)
        self.name = ''

    def set_name(self, name):
        self.name = name

    def to_dict(self):
        ret = Completion.to_dict(self)
        ret['newName'] = self.name
        return ret


class Signature(Completion):
    method = "textDocument/signatureHelp"


class Hover(Completion):
    method = "textDocument/hover"
