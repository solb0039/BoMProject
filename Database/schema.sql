-- -----------------------------------------------------
-- Table `Parts`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Parts` ;

CREATE TABLE IF NOT EXISTS `Parts` (
 `PartId` INTEGER PRIMARY KEY AUTOINCREMENT,
 `PartName` TEXT NOT NULL,
 `PartDescription` TEXT,
 `PartMaterialType` TEXT,
 `PartColor` TEXT
);


-- -----------------------------------------------------
-- Table `Assemblies`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `Assemblies` ;

CREATE TABLE IF NOT EXISTS `Assemblies` (
 `AssemblyId` INTEGER PRIMARY KEY AUTOINCREMENT,
 `AssemblyName` TEXT NOT NULL
);


-- -----------------------------------------------------
-- Table `PartAssemblies`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `PartAssemblies` ;

CREATE TABLE IF NOT EXISTS `PartAssemblies`(
 `Id` INTEGER PRIMARY KEY AUTOINCREMENT,
 `AssemblyId` INTEGER NOT NULL,
 `PartId` INTEGER NOT NULL,
 /*PRIMARY KEY (`AssemblyId`, `PartId`),*/
 FOREIGN KEY (`AssemblyId`) REFERENCES `Assemblies` (`AssemblyId`) ON DELETE CASCADE ON UPDATE CASCADE,
 FOREIGN KEY (`PartId`) REFERENCES `Parts` (`PartId`) ON DELETE CASCADE ON UPDATE CASCADE
 );


-- -----------------------------------------------------
-- Table `AssemblyParents`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `AssemblyParents` ;

CREATE TABLE IF NOT EXISTS `AssemblyParents` (
 `Id` INTEGER PRIMARY KEY AUTOINCREMENT,
 `AssemblyId` INT,
 `ParentAssemblyId` INT,
 UNIQUE (`AssemblyId`, `ParentAssemblyId`),
 FOREIGN KEY (`AssemblyId`) REFERENCES `Assemblies` (`AssemblyId`) ON DELETE CASCADE ON UPDATE CASCADE
 );