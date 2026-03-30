import re
import os
import ast
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_sql_values(file_path):
    print(f"Reading file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Finding INSERT INTO statement...")
    # Matches the block until the semicolon
    # Made non-greedy to avoid matching all the way to the end of the file
    insert_match = re.search(r'INSERT\s+INTO\s+`.+?`.*?VALUES\s+(.*?);', content, re.DOTALL | re.IGNORECASE)
    if not insert_match:
        print("No INSERT INTO statement found!")
        return []
    
    values_str = insert_match.group(1)
    
    print("Extracting tuples...")
    # Find everything between ( )
    # This might fail if there are parentheses inside the strings, but looking at the SQL there aren't any.
    tuple_pattern = re.compile(r'\((.*?)\)', re.DOTALL)
    tuples_str_list = tuple_pattern.findall(values_str)
    
    parsed_data = []
    print(f"Parsing {len(tuples_str_list)} items...")
    for t_str in tuples_str_list:
        try:
            # We use ast.literal_eval to safely parse SQL values into Python types (int, str)
            # Example: 11, 'BOGOTÁ, D.C.'
            t_val = ast.literal_eval(f"({t_str})")
            if not isinstance(t_val, tuple):
                t_val = (t_val,) # In case of single element, which shouldn't happen here
            parsed_data.append(t_val)
        except Exception as e:
            print(f"Error parsing snippet '{t_str}': {e}")
            
    return parsed_data

def seed_database_from_sql():
    print("Creating tables if they don't exist...")
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(models.Department).count() > 0:
            print("La base de datos ya tiene datos, omitiendo seed.")
            return

        print("Procesando departamentos.sql...")
        dept_data = parse_sql_values(os.path.join(BASE_DIR, 'departamentos.sql'))
        for row in dept_data:
            id_dept = int(row[0])
            name = str(row[1])
            code = f"{id_dept:02d}"
            dept = models.Department(id=id_dept, name=name, code=code)
            db.add(dept)
        db.commit()
        print(f"Insertados {len(dept_data)} departamentos.")

        print("Procesando municipios.sql...")
        mun_data = parse_sql_values(os.path.join(BASE_DIR, 'municipios.sql'))
        for row in mun_data:
            id_mun = int(row[0])
            name = str(row[1])
            estado = int(row[2])
            dept_id = int(row[3])
            code = f"{dept_id:02d}{id_mun:03d}"
            
            city = models.City(id=id_mun, name=name, department_id=dept_id, code=code)
            db.add(city)
        db.commit()
        print(f"Insertados {len(mun_data)} municipios.")

        print("Base de datos poblada exitosamente con los archivos SQL!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database_from_sql()
