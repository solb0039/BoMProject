# RESTful Bills of Materials

### Description:
JSON-based REST API to create, update, delete and query bills of materials.

### Installation

Download directory named SilaProject.

Enter directory from a Mac terminal window:
```sh
$ cd BoMProject
```

Create Python3 virtual environment and install required packages:
```sh
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

The Flask server can be run with various settings.
To run locally on the default port 5000:
```sh
$ flask run
```

In this configuration, the API is accessible as http://localhost:5000.

Or, to run on the local network with the page accessible to other computers:

```
$ flask run --host='0.0.0.0'
```

In order to access the API from other computers, the local IP address of the computer running Flask would need to be determined using shell commands such as ifconfig.

To stop the server, type 'ctrl-c' from the terminal window.

### Usage

The accompanying PDF documents in the /Database directory provides details of the schema and prepopulated data, including the pen varieties:

AssemblyId 6: Red, plastic pen.
AssemblyId 7: Red, metal pen.
AssemblyId 10: Blue, plastic pen.
AssemblyId 11: Blue, metal pen.


Refer to the root page (e.g. http:localhost:5000/) for basic description of the API methods implemented in this project.