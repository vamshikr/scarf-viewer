import os
import os.path as osp
import subprocess
import sys
import re
import shlex


class UnpackArchiveError(Exception):
    def __init__(self, filename):
        Exception.__init__(self)
        self.filename = filename
        self.exit_code = 5

    def __str__(self):
        return "Unpacking archive '{0}' failed".format(self.filename)


def _unpack_archive_xz(archive, dirpath):

    xz_proc = subprocess.Popen(['xz', '--decompress', '--stdout', archive],
                               stdout=subprocess.PIPE,
                               stderr=sys.stderr)

    tar_proc = subprocess.Popen(['tar', '-x'],
                                stdin=xz_proc.stdout,
                                stdout=sys.stdout,
                                stderr=sys.stderr,
                                cwd=dirpath)

    xz_proc.stdout.close()
    tar_proc.communicate()

    return tar_proc.returncode

def unpack_archive(archive, dirpath, createdir=True):

    if not osp.isfile(archive):
        raise FileNotFoundError(archive)

    if not osp.isdir(dirpath):
        if createdir:
            os.makedirs(dirpath)
        else:
            raise NotADirectoryError(dirpath)

    archive = osp.abspath(archive)
    dirpath = osp.abspath(dirpath)

    if archive.endswith('.tar.gz'):
        return run_cmd(['tar', '-x', '-z', '-f', archive], cwd=dirpath)[0]
    elif archive.endswith('.tgz'):
        return run_cmd(['tar', '-x', '-z', '-f', archive], cwd=dirpath)[0]
    elif archive.endswith('.tar.Z'):
        return run_cmd(['tar', '-x', '-Z', '-f', archive], cwd=dirpath)[0]
    elif archive.endswith('.tar.bz2'):
        return run_cmd(['tar', '-x', '-j', '-f', archive], cwd=dirpath)[0]
    elif archive.endswith('.tar'):
        return run_cmd(['tar', '-x', '-f', archive], cwd=dirpath)[0]
    elif archive.endswith('.tar.xz'):
        return _unpack_archive_xz(archive, dirpath)
    elif osp.splitext(archive)[1].lower() in \
         ['.zip', '.jar', '.war', '.ear']:
        return run_cmd(['unzip', '-qq', '-o', archive], cwd=dirpath)[0]
    else:
        raise ValueError('Format not supported')

def run_cmd(cmd,
            outfile=sys.stdout,
            errfile=sys.stderr,
            infile=None,
            cwd='.',
            shell=False,
            env=None):
    '''argument cmd should be a list'''
    openfile = lambda filename, mode: \
               open(filename, mode) if(isinstance(filename, str)) else filename

    out = openfile(outfile, 'w')
    err = openfile(errfile, 'w')
    inn = openfile(infile, 'r')

    if isinstance(cmd, str):
        shell = True

    environ = dict(os.environ) if env is None else env

    try:
        popen = subprocess.Popen(cmd,
                                 stdout=out,
                                 stderr=err,
                                 stdin=inn,
                                 shell=shell,
                                 cwd=cwd,
                                 env=environ)
        popen.wait()
        return (popen.returncode, environ)
    except subprocess.CalledProcessError as err:
        return (err.returncode, environ)
    finally:
        closefile = lambda filename, fileobj: \
                    fileobj.close() if(isinstance(filename, str)) else None
        closefile(outfile, out)
        closefile(errfile, err)
        closefile(infile, inn)


def conf_file_to_dict(filename):

    regex = re.compile(r'((?P<comment>^\s*#.*)|(?P<keyval>^\s*[^\s]+\s*=\s*.+)|(?P<blankline>^\s*))')

    conf_dict = {}

    with open(filename) as fobj:
        try:
            line = next(fobj)
            while True:
                match = regex.match(line)

                if match and match.groupdict()['keyval']:

                    re1 = re.compile(r'^\s*(?P<key>[^\s]+?)\s*=(?P<value>\s*.+)')
                    m1 = re1.match(line)
                    key = m1.groupdict()['key']
                    value = m1.groupdict()['value']
                    value = value.strip('\n').strip()

                    if value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    conf_dict[key] = value

                line = next(fobj)

        except StopIteration:
            pass
    return conf_dict


def main(filepath):
    print(conf_file_to_dict(filepath))


if __name__ == '__main__':
	main(sys.argv[1])
