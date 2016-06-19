import os
import os.path as osp
import shutil
import uuid
import datetime

from flask import redirect, url_for, render_template, request, abort
from flask import current_app, session, jsonify, make_response
from flask.ext.wtf import Form
from flask.ext.wtf.file import FileAllowed, FileRequired,  FileField
from wtforms import SubmitField, TextField
from wtforms.validators import Required
from werkzeug import secure_filename

from bson.objectid import ObjectId

from . import main
from .. import mongo
from manage import app
import db_util


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/assessments', methods=['POST'])
def get_aruns():
    '''This route is called by the datatable using ajax from the browser.
    This method, returns a json object with information about the
    assessment results in the database
    '''
    
    form_data = dict(request.form)
    coll = mongo.db['assessment_results']
    cursur = coll.find({}, {'tool-version': 1, 'platform': 1,
                            'package-version': 1, 'tool-type': 1,
                            'package-short-name': 1,
                            'assessment-date':1 })

    start = int(form_data['start'][0])
    length = int(form_data['length'][0])
    total = cursur.count()
    end =  total if start+length > total else start+length    

    data = list()

    count = start+1
    for arun in cursur[start:end]:
        data.append([count,
                     arun['package-short-name'],
                     arun['package-version'],
                    '%s-%s' % (arun['package-short-name'], arun['package-version']), 
                     arun['platform'],
                     arun['tool-type'],
                     arun['tool-version'],
                    '%s-%s' % (arun['tool-type'], arun['tool-version']),
                     arun['assessment-date']])
        count += 1

    return jsonify({ 'draw' : int(form_data['draw'][0]) ,
                     'recordsTotal' : total,
                     'recordsFiltered' : total,
                     'data' : data })


@main.route('/results', methods=['POST'])
def view_results():
    '''From the request object gets the assessment info .
    Gets the scarf results uuid for that particular assessment, and renders
    only the template for the results page, which contains
    the assessment report uuid.
    The actual results are obtained by get_report route
    '''

    form_data = dict(request.form)
    
    coll = mongo.db['assessment_results']
    cursur = coll.find_one({'tool-type' : form_data['tool_type'][0],
                            'tool-version' : form_data['tool_version'][0],
                            'platform' : form_data['platform'][0],
                            'package-short-name' : form_data['package_short_name'][0],
                            'package-version' : form_data['package_version'][0]},
                           {'_id' : 1})

    return render_template('results.html', report_id=str(cursur['_id']))


@main.route('/report', methods=['POST'])
def get_report():
    '''The datatable in the UI calls this route with required results
    bug ids start and end numbers'''
    
    form_data = dict(request.form)
    start = int(form_data['start'][0])
    length = int(form_data['length'][0])
    
    coll = mongo.db['assessment_results']
    cursur = coll.find_one({'_id' : ObjectId(form_data['report_id'][0])})

    data = list()

    total = len(cursur['BugInstances'])
    end =  total if start+length > total else start+length
    
    for bug in cursur['BugInstances'][start:end]:
        data.append([ bug['id'],
                      bug.get('BugCode', '-'),
                      bug.get('CWEID', '-'),
                      bug.get('BugMessage', '-'),
                      bug.get('BugGroup', '-'),
                      bug.get('BugSeverity', '-'),
                      bug.get('BugRank', '-'),
                      bug['Methods'][0]['name'] if len(bug['Methods']) > 0 else "-",
                      '%s-%s' % (bug['BugLocations'][0].get('StartLine', ''), \
                                 bug['BugLocations'][0].get('EndLine', ''),),
                      bug['BugLocations'][0].get('StartLine', ''),
                      bug['BugLocations'][0].get('EndLine', ''),
                      bug['BugLocations'][0].get('SourceFile', '')
                  ])

    return jsonify({ 'draw' : int(form_data['draw'][0]) ,
                     'recordsTotal' : total,
                     'recordsFiltered' : total,
                     'data' : data })


@main.route('/sourcefile')
def get_source_file():
    '''The UI uses this route to request the source code for a
    particular file in the bug'''

    filepath = request.args.get('filepath')

    #source_mapping = dict()
    #for cur in mongo.db['source_mapping'].find({}):
    #    source_mapping.update(cur)

    source_mapping = mongo.db['source_mapping'].find_one({'file_path' : filepath})
    if source_mapping:
        coll = mongo.db['source_files']
        cursur = coll.find_one({ 'sha1_digest' : source_mapping['sha1_digest']})
        return make_response(cursur['file_content'])


class UploadForm(Form):
    '''
    Form to upload SCARF results and package source
    '''
    parsed_results = FileField('Select parsed results XML file',
                               validators=[FileRequired(),
                                           FileAllowed(['xml'])])
    pkg_src_archive = FileField('Select package source archive',
                                validators=[FileRequired(),
                                            FileAllowed(['zip', 'tar.gz', 'tar'])])
    pkg_short_name = TextField('Package short name', validators=[Required()])
    pkg_version = TextField('Package version', validators=[Required()])
    platform = TextField('Platform', validators=[Required()])
    
    submit = SubmitField('Submit')


@main.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        _uuid = str(uuid.uuid4())
        dirpath = osp.abspath(osp.join(app.config['TEMP_FOLDER'], _uuid))
        app.logger.debug(dirpath)
        os.makedirs(dirpath, exist_ok=True)

        parsed_results = request.files['parsed_results']
        parsed_results_file = osp.join(dirpath,
                                       secure_filename(parsed_results.filename))
        parsed_results.save(parsed_results_file)

        pkg_src_archive = request.files['pkg_src_archive']
        pkg_src_archive_file = osp.join(dirpath,
                                        secure_filename(pkg_src_archive.filename))
        pkg_src_archive.save(pkg_src_archive_file)

        
        try:
            _id = db_util.store_in_db(parsed_results_file,
                                      pkg_src_archive_file,
                                      {'package-short-name' : form.pkg_short_name.data,
                                       'package-version' : form.pkg_version.data,
                                       'platform' : form.platform.data,
                                       'assessment-date' : datetime.datetime.today()})
            return render_template('results.html', report_id=_id)

        except Exception as err:
            app.logger.debug(err)
            return abort(400)
        else:
            return render_template('view.html')
    else:
        return render_template('upload.html', form=form)
