import sys
import os
import os.path as osp
from datetime import datetime
import traceback
import xml.etree.ElementTree as xet
import hashlib

import pymongo
import utillib
import confreader
import scarf_to_json

file_mapping = dict()

def get_arun_date(arun_dirpath):
    '''Reads the 3rd line from run.out and
    converts it to datetime object
    '''

    run_dot_out = osp.join(arun_dirpath, 'run.out')

    if osp.isfile(run_dot_out):
        with open(run_dot_out) as fobj:
            fobj.readline(); fobj.readline();
            return datetime.strptime(fobj.readline().strip().strip('\n'),
                                     "%a %b %d %H:%M:%S %Z %Y")

def get_pkg_name_version(arun_dirpath):

    basename = osp.basename(arun_dirpath)
    pkg_name = osp.basename(osp.normpath(arun_dirpath)).split('---')[0]
    pkgs_base_dir = os.environ['PACKAGES_DIR']

    if osp.join(pkgs_base_dir, pkg_name):
        pkg_conf_file = osp.join(osp.join(pkgs_base_dir, pkg_name),
                                 'package.conf')
        pkg_conf = confreader.read_conf_into_dict(pkg_conf_file)
        
        return (pkg_conf['package-short-name'],
                pkg_conf['package-version'])

def get_platname(arun_dirpath):
    return osp.basename(osp.normpath(arun_dirpath)).split('---')[1]

def upload_source_files(db, arun_dirpath, source_files):
    file_collection = db['source_files']
    
    build_results_conf = confreader.read_conf_into_dict(osp.join(arun_dirpath,
                                                                  'build.conf'))

    build_results_archive = osp.join(arun_dirpath,
                                     build_results_conf['build-archive'])

    utillib.unpack_archive(build_results_archive, arun_dirpath)
    build_dir = osp.join(arun_dirpath,
                         osp.join(build_results_conf.get('build-root-dir', 'build'), 'pkg1'))
    
    for srcfile in source_files:
        if osp.isfile(osp.join(build_dir, srcfile)):
            try:
                with open(osp.join(build_dir, srcfile), 'rb') as fobj:
                    _bytes = fobj.read()
                    sha1 = hashlib.sha1()
                    sha1.update(_bytes)
                    sha1_digest = sha1.hexdigest();
                    file_collection.insert_one({'sha1_digest' : sha1_digest,
                                                'file_content' : _bytes.decode('utf-8')})
                    file_mapping[srcfile.replace(".", "_dot_")] = sha1_digest

            except UnicodeDecodeError as err:
                print(err)
                print(traceback.print_exc(limit=5))
                    
                
def get_scarf_json(arun_dirpath):
        
    if not osp.isdir(arun_dirpath):
        raise NotADirectoryError(arun_dirpath)

    if not osp.basename(osp.normpath(arun_dirpath)).split('---')[-1] == 'parse':
        raise NotImplementedError 
        
    date = get_arun_date(arun_dirpath)
    plat = get_platname(arun_dirpath)
    pkg_name, pkg_ver = get_pkg_name_version(arun_dirpath)

    parsed_results_conf = utillib.conf_file_to_dict(osp.join(arun_dirpath,
                                                             'parsed_results.conf'))

    parsed_results_archive = osp.join(arun_dirpath,
                                      parsed_results_conf['parsed-results-archive'])

    utillib.unpack_archive(parsed_results_archive, arun_dirpath)
    parsed_results_file = osp.join(osp.join(arun_dirpath,
                                            parsed_results_conf['parsed-results-dir']),
                                   parsed_results_conf['parsed-results-file'])

    cwe_mapping = scarf_to_json.get_cwe_mapping()
    scarf_json, source_files = scarf_to_json.scarf_to_json(parsed_results_file,
                                                           {'package-short-name' : pkg_name,
                                                            'package-version' : pkg_ver,
                                                            'platform' : plat,
                                                            'assessment-date' : date,
                                                        },
                                                           cwe_mapping)

    return (scarf_json, source_files)

client = pymongo.MongoClient()
db = client['scarf']

def get_uploader():

    results_collection = db['assessment_results']
    
    def upload(arun_dirpath):
        scarf_json, source_files = get_scarf_json(arun_dirpath)
        upload_source_files(db, arun_dirpath, source_files)
        return results_collection.insert_one(scarf_json)
        
    return upload
    
def main(args):
    uploader = get_uploader()
    for arun_dirpath in args:
        print('uploading: %s' % (osp.basename(arun_dirpath)))
        try:
            result = uploader(arun_dirpath)
        except Exception as err:
            print(traceback.print_exc(limit=5))
        else:
            print(result.inserted_id)

    db['source_mapping'].insert_one(file_mapping)

if __name__ == '__main__':
	main(sys.argv[1:])
