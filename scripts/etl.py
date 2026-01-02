import csv
import psycopg2

def main():
    conn = psycopg2.connect(
        host="localhost",        
        port=5432,
        database="postgres",
        user="postgres",
        password="12qwaszx"
    )
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        cursor.execute("SET search_path TO statement, public")

        with open("data.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)

        group_names = sorted(set(row["group_name"] for row in records))
        group_map = {}
        for name in group_names:
            cursor.execute("""
                INSERT INTO groups (group_name)
                VALUES (%s)
                ON CONFLICT (group_name) DO NOTHING
                RETURNING group_id
            """, (name,))
            row = cursor.fetchone()
            if row:
                group_map[name] = row[0]
            else:
                cursor.execute("SELECT group_id FROM groups WHERE group_name = %s", (name,))
                group_map[name] = cursor.fetchone()[0]

        student_map = {}
        seen = set()
        for row in records:
            sid = int(row["student_id"])
            if sid in seen:
                continue
            seen.add(sid)
            cursor.execute("""
                INSERT INTO students (first_name, second_name, surname, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING student_id
            """, (
                row["first_name"],
                row["second_name"],
                row["surname"],
                group_map[row["group_name"]]
            ))
            student_map[sid] = cursor.fetchone()[0]

        subject_names = sorted(set(row["subject_name"] for row in records))
        subject_map = {}
        for name in subject_names:
            cursor.execute("""
                INSERT INTO subjects (subject_name)
                VALUES (%s)
                ON CONFLICT (subject_name) DO NOTHING
                RETURNING subject_id
            """, (name,))
            row = cursor.fetchone()
            if row:
                subject_map[name] = row[0]
            else:
                cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = %s", (name,))
                subject_map[name] = cursor.fetchone()[0]

        for row in records:
            cursor.execute("""
                INSERT INTO grades (student_id, subject_id, grade_numeric, grade_ects)
                VALUES (%s, %s, %s, %s)
            """, (
                student_map[int(row["student_id"])],
                subject_map[row["subject_name"]],
                int(row["grade_numeric"]),
                row["grade_ects"]
            ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()