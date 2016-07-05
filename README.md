# SCARF Viewer

Folks who work for the SWAMP project have come up with a normalized results format to which reports from various static analysis tools are converted into. It is called SWAMP Common Assessment Results Format (SCARF).

This is a web based application to display SCARF results. The SCARF results are displayed in a tabular format along side with the source code.

### Technologies Used
The primary programming languages used in this application are **Python 3** and **Javascript**. The following frameworks, libraries and software are used.
* [Flask](http://flask.pocoo.org/) for backend web services.
* [MongoDB](https://www.mongodb.org/) for storing results and source files.
* [Prism](http://prismjs.com/) for formating and displaying the source code.
* [DataTables](https://datatables.net/) for tables on the user interface.
* [jQuery](http://jquery.com/) for client side scripting.


### Getting Started

#### Creating Database.
A sample set of results are provided as MongoDB dump [here](https://www.cs.wisc.edu/~vamshi/scarf_test_db.dump). If you have a MongoDB server running, run the following command to create the database with the sample set of results.

```sh
% mongorestore --archive=scarf_test_db.dump
```

If you need instructions on how to run an instance of MongoDB server, please see [Getting Started with MongoDB](https://docs.mongodb.org/getting-started/shell/)


#### Starting the Web Application

After uploading the sample results into MongoDB, run the following commands

```sh
% git clone git@bitbucket.org:vamshi_kr/viewer-v2.git
% cd viewer-v2
% pyvenv venv  # Create python virtual environment
% source venv/bin/activate  # Activate the virtual environment
% pip install --upgrade pip  # Upgrade PIP (Optional)
% pip install -r requirements.txt  # Install all the application dependencies
% ./manage.py runserver # Run the flask web server
```

The output you will see on the terminal will be similar to
```sh
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger pin code: 281-341-497
```

Open a web browser window and go to http://127.0.0.1:5000/


### Sample database set.
A sample set of [results] (https://www.cs.wisc.edu/~vamshi/scarf_test_db.dump) contain the following results:

| Package | Platform | Tool |
| --- | --- | --- |
| railsgoat-9052b4fcf0 | scientific-6.4-64 | brakeman-3.0.5 |
| railsgoat-9052b4fcf0 | scientific-6.4-64 | dawnscanner-1.3.5 |
| railsgoat-9052b4fcf0 | scientific-6.4-64 | reek-3.1 |
| railsgoat-9052b4fcf0 | scientific-6.4-64 | rubocop-0.33.0 |
| railsgoat-9052b4fcf0 | scientific-6.4-64 | ruby-lint-2.0.4 |
| luigi-1.0.20 | scientific-6.4-64 | pylint-py2-1.4.4 |
| luigi-1.0.20 | scientific-6.4-64 | flake8-py2-2.4.1 |
| luigi-1.0.20 | scientific-6.4-64 | bandit-py2-0.14.0 |
| webgoat-5.4_1 | rhel-6.4-64 | pmd-5.4.1 |
| webgoat-5.4_1 | rhel-6.4-64 | findbugs-3.0.1 |
| webgoat-5.4_1 | rhel-6.4-64 | error-prone-2.0.9 |
| rabbitmq-c-0.4.1 | fedora-19.0-64 | clang-sa-3.7.0 |
| rabbitmq-c-0.4.1 | fedora-19.0-64 | cppcheck-1.72 |
