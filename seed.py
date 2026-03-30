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
    # Parse char by char to correctly handle parentheses inside quoted strings
    # e.g. 'Albán (San José)' would break a naive regex approach
    parsed_data = []
    i = 0
    n = len(values_str)
    while i < n:
        if values_str[i] != '(':
            i += 1
            continue
        j = i + 1
        in_quote = False
        while j < n:
            c = values_str[j]
            if in_quote:
                if c == "'":
                    if j + 1 < n and values_str[j + 1] == "'":
                        j += 1  # escaped quote ''
                    else:
                        in_quote = False
            else:
                if c == "'":
                    in_quote = True
                elif c == ')':
                    break
            j += 1
        t_str = values_str[i + 1:j]
        try:
            t_val = ast.literal_eval(f"({t_str},)")
            parsed_data.append(t_val)
        except Exception as e:
            print(f"Error parsing snippet '{t_str[:60]}': {e}")
        i = j + 1

    print(f"Parsed {len(parsed_data)} items...")
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
