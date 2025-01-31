from django.db import migrations

def create_triggers(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_demo_on_superorg_change() 
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.flag = TRUE THEN
                    UPDATE my_demo 
                    SET name_formats = jsonb_build_object(
                        'first_name', my_demo.first_name,
                        'middle_name', my_demo.middle_name,
                        'last_name', my_demo.last_name,
                        'suffix', my_demo.suffix,
                        'full_name', my_demo.first_name || ' ' || my_demo.last_name
                    )
                    WHERE my_demo.super_org_id = NEW.id;
                ELSE
                    UPDATE my_demo 
                    SET name_formats = jsonb_build_object(
                        'first_name', my_demo.first_name,
                        'middle_name', my_demo.middle_name,
                        'last_name', my_demo.last_name,
                        'suffix', my_demo.suffix
                    )
                    WHERE my_demo.super_org_id = NEW.id;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER superorg_change_trigger
            AFTER INSERT OR UPDATE OF flag ON super_org
            FOR EACH ROW
            EXECUTE FUNCTION update_demo_on_superorg_change();
        """)

        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_name_formats_on_demo_change()
            RETURNS TRIGGER AS $$
            BEGIN
                IF (SELECT flag FROM super_org WHERE id = NEW.super_org_id) = TRUE THEN
                    UPDATE my_demo 
                    SET name_formats = jsonb_build_object(
                        'first_name', NEW.first_name,
                        'middle_name', NEW.middle_name,
                        'last_name', NEW.last_name,
                        'suffix', NEW.suffix,
                        'full_name', NEW.first_name || ' ' || NEW.last_name
                    )
                    WHERE id = NEW.id;
                ELSE
                    UPDATE my_demo 
                    SET name_formats = jsonb_build_object(
                        'first_name', NEW.first_name,
                        'middle_name', NEW.middle_name,
                        'last_name', NEW.last_name,
                        'suffix', NEW.suffix
                    )
                    WHERE id = NEW.id;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER demo_change_trigger
            AFTER INSERT OR UPDATE OF first_name, last_name, middle_name, suffix ON my_demo
            FOR EACH ROW
            EXECUTE FUNCTION update_name_formats_on_demo_change();
        """)

class Migration(migrations.Migration):

    dependencies = [
        ("demo", "0004_alter_demo_table_alter_superorg_table"),
    ]

    operations = [
        migrations.RunPython(create_triggers),
    ]
