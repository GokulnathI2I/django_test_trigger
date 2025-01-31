from django.db import migrations

def update_triggers(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        # Drop the old triggers and functions
        cursor.execute("DROP TRIGGER IF EXISTS superorg_change_trigger ON super_org;")
        cursor.execute("DROP TRIGGER IF EXISTS demo_change_trigger ON my_demo;")
        cursor.execute("DROP FUNCTION IF EXISTS update_demo_on_superorg_change;")
        cursor.execute("DROP FUNCTION IF EXISTS update_display_names_on_demo_change;")

        # Create a new function for updating demo fields based on SuperOrg flag
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_demo_on_superorg_change() 
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.flag = TRUE THEN
                    UPDATE my_demo 
                    SET 
                        display_first_name = first_name,
                        display_last_name = TRIM(last_name || ' ' || COALESCE(suffix, '')),
                        display_full_name_first_name_first = first_name || ' ' || TRIM(last_name || ' ' || COALESCE(suffix, '')),
                        display_full_name_last_name_first = TRIM(last_name || ' ' || COALESCE(suffix, '')) || ' ' || first_name
                    WHERE my_demo.super_org_id = NEW.id;
                ELSE
                    UPDATE my_demo 
                    SET 
                        display_first_name = first_name,
                        display_last_name = TRIM(last_name || ' ' || COALESCE(suffix, '')),
                        display_full_name_first_name_first = NULL,
                        display_full_name_last_name_first = NULL
                    WHERE my_demo.super_org_id = NEW.id;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # Create the trigger for SuperOrg
        cursor.execute("""
            CREATE TRIGGER superorg_change_trigger
            AFTER INSERT OR UPDATE OF flag ON super_org
            FOR EACH ROW
            EXECUTE FUNCTION update_demo_on_superorg_change();
        """)

        # Create a function for updating demo display fields when demo record changes
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_display_names_on_demo_change()
            RETURNS TRIGGER AS $$
            BEGIN
                IF (SELECT flag FROM super_org WHERE id = NEW.super_org_id) = TRUE THEN
                    UPDATE my_demo 
                    SET 
                        display_first_name = NEW.first_name,
                        display_last_name = TRIM(NEW.last_name || ' ' || COALESCE(NEW.suffix, '')),
                        display_full_name_first_name_first = NEW.first_name || ' ' || TRIM(NEW.last_name || ' ' || COALESCE(NEW.suffix, '')),
                        display_full_name_last_name_first = TRIM(NEW.last_name || ' ' || COALESCE(NEW.suffix, '')) || ' ' || NEW.first_name
                    WHERE id = NEW.id;
                ELSE
                    UPDATE my_demo 
                    SET 
                        display_first_name = NEW.first_name,
                        display_last_name = TRIM(NEW.last_name || ' ' || COALESCE(NEW.suffix, '')),
                        display_full_name_first_name_first = NULL,
                        display_full_name_last_name_first = NULL
                    WHERE id = NEW.id;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # Create the trigger for Demo table
        cursor.execute("""
            CREATE TRIGGER demo_change_trigger
            AFTER INSERT OR UPDATE OF first_name, last_name, middle_name, suffix ON my_demo
            FOR EACH ROW
            EXECUTE FUNCTION update_display_names_on_demo_change();
        """)

class Migration(migrations.Migration):

    dependencies = [
        ("demo", "0005_add_trigger"),
    ]

    operations = [
        migrations.RunPython(update_triggers),
    ]
