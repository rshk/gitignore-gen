"""
:author: samu
:created: 2/25/13 3:39 PM
"""

from collections import defaultdict

import os
import optparse

from flask import Flask, request, render_template, make_response

app = Flask(__name__)
GITIGNORE_DIR = None


def _find_gitignores(base_dir):
    for root, dirs, files in os.walk(base_dir):
        for el in dirs:
            if el.startswith('.'):
                dirs.remove(el)
        for file_name in files:
            if file_name.startswith('.'):
                continue
            if file_name.endswith('.gitignore'):
                yield os.path.join(root, file_name)


def _find_structured_gitignores(base_dir):
    groups = defaultdict(lambda: [])
    for g in _find_gitignores(base_dir):
        relpath = os.path.relpath(g, base_dir)
        dirname = os.path.dirname(relpath)
        filename = os.path.splitext(os.path.basename(relpath))[0]
        groups[dirname].append((filename, relpath))
    for k in groups:
        groups[k] = sorted(groups[k])
    return groups


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        ## Process the POST -> return .gitignore file

        gitignore_file = []

        for file_name in request.form.getlist('enabled_gitignores'):
            with open(os.path.join(GITIGNORE_DIR, file_name)) as f:
                gitignore_file.append('## {}'.format(file_name))
                gitignore_file.append(f.read())

        response = make_response("\n\n".join(gitignore_file))
        response.mimetype = 'text/plain'
        response.headers['Content-disposition'] = 'attachment; filename=gitignore'
        return response

    return render_template(
        'form.html',
        gitignores=_find_structured_gitignores(GITIGNORE_DIR))


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--gitignore-dir', action='store', dest='gitignore_dir',
                      metavar='DIR',
                      help="Directory containing the gitignore files. Usually"
                           "a git clone of https://github.com/github/gitignore")
    parser.add_option('--host', action='store', dest='listen_host',
                      default='127.0.0.1', metavar='ADDRESS',
                      help="Address on which to listen")
    parser.add_option('--port', action='store', dest='listen_port',
                      type='int', default=5000, metavar='ADDRESS',
                      help="TCP port on which to listen")
    parser.add_option('--debug', action='store_true', dest='debug',
                      default=False,
                      help="Whether to enable debugging mode")

    options, args = parser.parse_args()

    GITIGNORE_DIR = options.gitignore_dir

    assert GITIGNORE_DIR is not None

    app.run(
        host=options.listen_host,
        port=options.listen_port,
        debug=options.debug)
