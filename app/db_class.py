import sqlite3
import os
from contextlib import closing
from app import app
import itertools


class Database:
    def __init__(self):
        try:
            self.database=os.environ.get("DATABASE")
            self.cursor = sqlite3.connect(self.database)
            self.cursor.row_factory = sqlite3.Row

        except Error as e:
            print(e)

    def connect_db(self): #TODO: This is redundant?
        try:
            conn = sqlite3.connect(self.database)
            conn.execute("pragma foreign_keys")
            return conn
        except Error as e:
            print(e)
            return None

    def init_db(self):
        with closing(self.connect_db()) as db:
            with app.open_resource('../Database/schema.sql', 'r') as f:
                db.cursor().executescript(f.read())
            db.commit()
        print('Initialized the database.')

    def populate_db(self):
        with closing(self.connect_db()) as db:
            with app.open_resource('../Database/populate_db.sql', 'r') as f:
                db.cursor().executescript(f.read())
            db.commit()
        print('Populated the database with some initial data')


    def __parse_data(self, row_data):
        rowarray_list = []
        for row in row_data:
            d = dict(zip(row.keys(), row))  # a dict with column names as keys
            rowarray_list.append(d)
        return rowarray_list


    def getAllAssembly(self):
        query = "SELECT * FROM Assemblies;"
        rows = self.cursor.execute(query).fetchall()
        return self.__parse_data(rows)


    def getAssembly(self, assem_id):
        query = "SELECT Parts.PartId, Parts.PartName, Parts.PartDescription, Parts.PartMaterialType, Parts.PartColor FROM Parts " \
                "INNER JOIN PartAssemblies " \
                "ON Parts.PartId = PartAssemblies.PartId " \
                "INNER JOIN Assemblies ON PartAssemblies.AssemblyId = Assemblies.AssemblyId " \
                "WHERE Assemblies.AssemblyId = ?;"
        res  = self.cursor.execute(query, (assem_id,))
        return self.__parse_data(res)


    def getAssemblyFirstLevelParts(self, assembly_id):
        query1 = "SELECT PartAssemblies.PartId, Parts.PartName FROM Parts " \
                 "INNER JOIN PartAssemblies ON PartAssemblies.PartId = Parts.PartId WHERE `AssemblyId` = ?;"
        query2 = "SELECT AssemblyParents.AssemblyId, Assemblies.AssemblyName FROM Assemblies " \
                 "INNER JOIN AssemblyParents ON Assemblies.AssemblyId = AssemblyParents.AssemblyId WHERE `ParentAssemblyId` = ?;"
        res1 = self.cursor.execute(query1, (assembly_id,))
        res2 = self.cursor.execute(query2, (assembly_id,))

        return (self.__parse_data(res1) + self.__parse_data(res2))


    def getAllAssemblyParts(self, assembly_id):
        # Get direct part descendants
        query1 = "SELECT PartAssemblies.PartId, Parts.PartName FROM Parts " \
                 "INNER JOIN PartAssemblies ON PartAssemblies.PartId = Parts.PartId WHERE `AssemblyId` = ?;"
        res1 = self.cursor.execute(query1, (assembly_id,))
        comp_res = self.__parse_data(res1)

        # Get first sub-assembly
        query2 = "SELECT AssemblyParents.AssemblyId, Assemblies.AssemblyName FROM Assemblies " \
                 "INNER JOIN AssemblyParents ON Assemblies.AssemblyId = AssemblyParents.AssemblyId WHERE `ParentAssemblyId` = ?;"
        res2 = self.cursor.execute(query2, (assembly_id,))
        res2_mod = self.__parse_data(res2)

        # Add sub-assembly parts to result
        comp_res += res2_mod

        # Step down tree to get ID of next child assembly and add to composite result
        #TODO: Handle more then 1 child assembly
        while res2_mod:
            next_id = res2_mod[0]['AssemblyId']
            res2 = self.cursor.execute(query2, (next_id,))
            res2_mod = self.__parse_data(res2)
            comp_res += res2_mod

        return comp_res


    def getTopLevelAssemblies(self):
        query = ("SELECT * FROM Assemblies "
                 "INNER JOIN AssemblyParents ON AssemblyParents.AssemblyId=Assemblies.AssemblyId "
                 "WHERE AssemblyParents.ParentAssemblyId IS NULL;")
        res = self.cursor.execute(query).fetchall()
        return self.__parse_data(res)


    def getSubAssemblies(self):
        query = ("SELECT * FROM Assemblies "
                 "INNER JOIN AssemblyParents ON AssemblyParents.AssemblyId=Assemblies.AssemblyId "
                 "WHERE AssemblyParents.ParentAssemblyId IS NOT NULL;")
        res = self.cursor.execute(query).fetchall()
        return self.__parse_data(res)


    def getAssembliesWithPart(self, part_id):
        query = "SELECT * FROM Assemblies " \
                "INNER JOIN PartAssemblies ON Assemblies.AssemblyId = PartAssemblies.AssemblyId " \
                "INNER JOIN Parts ON PartAssemblies.PartId = Parts.PartId " \
                "WHERE Parts.PartId = ?;"
        res = self.cursor.execute(query, (part_id,)).fetchall()
        return self.__parse_data(res)


    def combinePartsToAssembly(self, name, components):
        query = "INSERT INTO Assemblies (`AssemblyName`) VALUES(?);"
        new_id = self.cursor.execute(query, (name, )).lastrowid
        self.cursor.commit()
        query = "INSERT INTO PartAssemblies (`PartId`, `AssemblyId`) VALUES (?, ?);"

        # Zip each PartId with the newly created assemblyId for proper format for 'executemany' fn
        rc = self.cursor.executemany(query, list(zip(components, itertools.repeat(new_id)))).rowcount
        self.cursor.commit()
        return rc


    def addAssemblyToAssembly(self, assem):
        query = "INSERT INTO AssemblyParents (`AssemblyId`, `ParentAssemblyId`) VALUES (?, ?);"
        id = self.cursor.execute(query, (assem[0], assem[1])).lastrowid
        self.cursor.commit()
        return id


    def removePartFromAssembly(self, part_id, assembly_id):
        query = "DELETE FROM PartAssemblies WHERE `PartId` = ? AND `AssemblyId` = ?;"
        id = self.cursor.execute(query, (part_id, assembly_id)).rowcount
        self.cursor.commit()
        return id


    def getAllParts(self):
        query = "SELECT * from Parts;"
        rows = self.cursor.execute(query).fetchall()
        return self.__parse_data(rows)


    def getPart(self, part_id):
        query = "SELECT * from Parts WHERE PartId = {};".format(part_id)
        res = self.cursor.execute(query)
        return self.__parse_data(res)


    def addPart(self, data):
        query = "INSERT INTO Parts (`PartName`, `PartDescription`, `PartMaterialType`, `PartColor`) VALUES (?, ?, ?, ?);"
        id = self.cursor.execute(query, (data['PartName'], data['PartDescription'], data['PartMaterialType'], data['PartColor']) ).lastrowid
        self.cursor.commit()
        return id


    def getOrphanParts(self):
        query = "SELECT * FROM Parts WHERE PartId NOT IN (SELECT `PartId` FROM PartAssemblies);"
        res = self.cursor.execute(query)
        return self.__parse_data(res)


    def getComponentParts(self):
        query = "SELECT * FROM Parts " \
                "INNER JOIN PartAssemblies ON Parts.PartId = PartAssemblies.PartId " \
                "INNER JOIN AssemblyParents ON PartAssemblies.AssemblyId = AssemblyParents.AssemblyId " \
                "WHERE AssemblyParents.ParentAssemblyId IS NULL;"
        res = self.cursor.execute(query)
        return self.__parse_data(res)


    def deletePart(self, part_id):
        query = "DELETE FROM Parts WHERE (`PartId`) = ?;"
        id = self.cursor.execute(query, (part_id,)).rowcount
        self.cursor.commit()
        print(id)
        return id


    def close_connection(self):
        self.cursor.close()
