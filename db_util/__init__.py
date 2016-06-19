import os.path as osp
import sys
import hashlib

from app import mongo
from manage import app as app_obj

from . import utillib
from . import scarf_to_json


def store_in_db(parsed_results_file, source_archive, pkg_info):
    '''pkg_info is a dictionary'''
    scarf_json, source_files = scarf_to_json.scarf_to_json(parsed_results_file,
                                                           pkg_info)

    upload_source_files(source_archive, source_files)
    result = mongo.db['assessment_results'].insert_one(scarf_json)
    return result.inserted_id

def upload_source_files(source_archive, source_files):

    base_dir = osp.dirname(source_archive)
    
    if utillib.unpack_archive(source_archive, base_dir) == 0:
        if osp.isdir(osp.join(base_dir, 'build')) and \
           osp.isfile(osp.join(base_dir, 'build_summary.xml')):

            pkg_dir = osp.join(base_dir, 'build/pkg1')
        else:
            pkg_dir = base_dir

        file_mapping = dict()
        
        for srcfile in source_files:
            if osp.isfile(osp.join(pkg_dir, srcfile)):
                try:
                    with open(osp.join(pkg_dir, srcfile), 'rb') as fobj:
                        _bytes = fobj.read()
                        sha1 = hashlib.sha1()
                        sha1.update(_bytes)
                        sha1_digest = sha1.hexdigest();
                        mongo.db['source_files'].insert_one({'sha1_digest' : sha1_digest,
                                                             'file_content' : _bytes.decode('utf-8')})
                        mongo.db['source_mapping'].insert_one({'sha1_digest' : sha1_digest,
                                                               'file_path' : srcfile })

                except UnicodeDecodeError as err:
                    print(err)
                    print(traceback.print_exc(limit=5))

        if file_mapping:
            mongo.db['source_mapping'].insert_one(file_mapping)


if __name__ == '__main__':
    store_in_db(sys.argv[1], sys.argv[2])
