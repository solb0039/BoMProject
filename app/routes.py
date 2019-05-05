from app import app
from flask import jsonify, request, render_template
from .db_class import Database
import re

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


'''Instantiate the database and populate'''
@app.before_first_request
def start_app():
    def init_tasks():
        db_inst = Database()
        db_inst.init_db()
        db_inst.populate_db()
    init_tasks()


'''Render basic web page with route references'''
@app.route('/')
def index():
    return render_template('index.html')


'''list all assemblies'''
@app.route('/list-all-assemblies', methods=['GET'])
def get_all_assemblies():
    db_inst = Database()
    res = jsonify(list(db_inst.getAllAssembly()))
    db_inst.close_connection()
    return res


'''list all parts in a specific assembly (which are not sub-assemblies)'''
@app.route('/assembly/<int:id>', methods=['GET'])
def get_assembly(id):
    db_inst = Database()
    res = jsonify(list(db_inst.getAssembly(id)))
    db_inst.close_connection()
    return res


'''add one or more parts as "children" to a "parent" part, which then becomes an assembly'''
'''POST Request with params PartId1, PartId2, PartId3... & required AssemblyName'''
@app.route('/combine-parts', methods=['POST'])
def combine_parts():
    data = request.form.to_dict()
    if 'AssemblyName' not in data.keys() or len([x for x in data.keys() if re.search('^.+[Part]', x)]) < 2:
        raise InvalidUsage('Error: Assembly Name is missing or not enough PartIds provided', status_code=400)
    db_inst = Database()

    # Get Name attr from dict and then pop it so that remaining items in list are just Parts
    name = data['AssemblyName']
    del data['AssemblyName']
    rc = jsonify( db_inst.combinePartsToAssembly(name, [int(v) for k,v in data.items()]) )
    db_inst.close_connection()
    if rc:
        return jsonify("Created new assembly part.")
    else:
        return jsonify("Error creating assembly")


'''- remove one or more parts from an assembly'''
@app.route('/remove-part-assembly', methods=['DELETE'])
def remove_part_assembly():
    data = request.form.to_dict()
    if 'AssemblyId' not in data.keys() or 'PartId' not in data.keys():
        raise InvalidUsage('Error: Assembly Name is missing or not enough PartIds provided', status_code=400)
    db_inst = Database()
    res = db_inst.removePartFromAssembly(data['PartId'], data['AssemblyId'])
    db_inst.close_connection()
    if res:
        return jsonify("Successfully removed part from assembly")
    else:
        return jsonify("Error removing part from assembly")


'''Method to combine existing assemblies'''
@app.route('/add-assembly-to-assembly', methods=['POST'])
def add_assembly_to_assembly():
    data = request.form.to_dict()
    # Minimal check that AssemblyId were provided in request
    if len([x for x in data.keys() if re.search('^.+[AssemblyId]', x)]) < 2:
        raise InvalidUsage('Error: Not enough AssemblyIds provided', status_code=400)
    assem = [x for x in data.values()]
    db_inst = Database()
    id = db_inst.addAssemblyToAssembly(assem)
    if id:
        return jsonify("Sucessfully added assembly to assembly with new id", id)
    else:
        return jsonify("Error adding assembly")


'''list all the first-level children of a specific assembly'''
@app.route('/assembly-parts/<int:assembly_id>', methods=['GET'])
def get_assembly_parts(assembly_id):
    db_inst = Database()
    res = jsonify(list(db_inst.getAssemblyFirstLevelParts(assembly_id)))
    db_inst.close_connection()
    return res


'''list all children of a specific assembly'''
@app.route('/get-all-assembly-parts/<int:assembly_id>', methods=['GET'])
def get_all_assembly_parts(assembly_id):
    db_inst = Database()
    res = jsonify(list(db_inst.getAllAssemblyParts(assembly_id)))
    db_inst.close_connection()
    return res


'''list all top level assemblies (assemblies that are not children of another assembly)'''
@app.route('/top-level-assemblies', methods=['GET'])
def get_top_level_assemblies():
    db_inst = Database()
    res = jsonify(list(db_inst.getTopLevelAssemblies()))
    db_inst.close_connection()
    return res


'''list all subassemblies (assemblies that are children of another assembly)'''
@app.route('/sub-assemblies', methods=['GET'])
def get_sub_assemblies():
    db_inst = Database()
    res = jsonify(list(db_inst.getSubAssemblies()))
    db_inst.close_connection()
    return res


'''list all component parts (parts that are not subassemblies, but are included in a parent assembly)'''
@app.route('/component-parts', methods=['GET'])
def get_comp_parts():
    db_inst = Database()
    res = jsonify(list(db_inst.getComponentParts()))
    db_inst.close_connection()
    return res


'''list all assemblies that contain a specific child part, either directly or indirectly (via a subassembly)'''
@app.route('/part-in-assemblies/<int:part_id>', methods=['GET'])
def get_assemblies_with_part(part_id):
    db_inst = Database()
    res = jsonify(list(db_inst.getAssembliesWithPart(part_id)))
    db_inst.close_connection()
    return res


''' list all parts '''
@app.route('/list-all-parts', methods=['GET'])
def get_all_parts():
    db_inst = Database()
    res = jsonify(list(db_inst.getAllParts()))
    db_inst.close_connection()
    return res


'''Part by id'''
@app.route('/part/<int:part_id>', methods=['GET'])
def get_part(part_id):
    db_inst = Database()
    res =  jsonify(list(db_inst.getPart(part_id)))
    db_inst.close_connection()
    return res


'''create a new part'''
@app.route('/add-part', methods=['POST'])
def add_part():
    data = request.form.to_dict()
    if 'PartName' not in data.keys():
        raise InvalidUsage('Error: Part Name is missing', status_code=400)

    # Set optional columns to None type for db integrity
    columns = ['PartDescription', 'PartMaterialType', 'PartColor']
    for key in list(set(columns) - set(data.keys())):
        data[key] = None

    db_inst = Database()
    id = db_inst.addPart(data)
    db_inst.close_connection()
    if id:
        return jsonify("Sucessfully added new part with id", id)
    else:
        return jsonify("Error adding part")


'''delete a part (thereby also deleting the part from its parent assemblies)'''
@app.route('/delete-part', methods=['DELETE'])
def delete_part():
    data = request.form.to_dict()
    if 'PartId' not in data.keys():
        raise InvalidUsage('Error: PartId is missing', status_code=400)
    db_inst = Database()
    row = db_inst.deletePart(data['PartId'])
    db_inst.close_connection()
    if row:
        return jsonify("Successfully deleted ", data['PartId'])
    else:
        return jsonify("Error deleting part.")


'''list all orphan parts (parts with neither parents nor children)'''
@app.route('/orphan-parts', methods=['GET'])
def get_orphan_parts():
    db_inst = Database()
    res =  jsonify(list(db_inst.getOrphanParts()))
    db_inst.close_connection()
    return res


@app.route('/<path:path>')
def catch_all(path):
    return 'Error: Page does not exist.'


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response