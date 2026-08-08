import os
import re
import shutil


OFFSET = 5


folder = os.path.dirname(
    os.path.abspath(__file__)
)


backup = os.path.join(
    folder,
    "lowr_fix_backup"
)


if not os.path.exists(backup):
    os.makedirs(backup)



rename_list = []


# ==================================
# LOWR ORDNER FINDEN
# ==================================

for name in os.listdir(folder):

    path = os.path.join(
        folder,
        name
    )


    if not os.path.isdir(path):
        continue


    m = re.match(
        r"lowr_(\d+)_u",
        name,
        re.IGNORECASE
    )


    if not m:
        continue


    old_id = int(
        m.group(1)
    )


    rename_list.append(
        (
            old_id,
            name
        )
    )



# wichtig: rückwärts wegen Überschreiben
rename_list.sort(
    key=lambda x:x[0],
    reverse=True
)



print()
print("======================")
print("LOWR ORDNER FIX")
print("======================")
print()



for old_id,folder_name in rename_list:


    new_id = old_id + OFFSET


    new_folder_name = folder_name.replace(
        str(old_id),
        str(new_id),
        1
    )


    old_path = os.path.join(
        folder,
        folder_name
    )


    # Backup
    shutil.copytree(
        old_path,
        os.path.join(
            backup,
            folder_name
        ),
        dirs_exist_ok=True
    )



    temp_folder = os.path.join(
        folder,
        "__TEMP__" + folder_name
    )


    os.rename(
        old_path,
        temp_folder
    )



    # Dateien innen umbenennen

    for root, dirs, files in os.walk(
        temp_folder
    ):


        for file in files:


            old_file = os.path.join(
                root,
                file
            )


            new_file_name = file.replace(
                str(old_id),
                str(new_id)
            )


            new_file = os.path.join(
                root,
                new_file_name
            )


            if old_file != new_file:

                os.rename(
                    old_file,
                    new_file
                )



    # Ordner final umbenennen

    os.rename(
        temp_folder,
        os.path.join(
            folder,
            new_folder_name
        )
    )



    print(
        folder_name,
        "->",
        new_folder_name
    )



print()
print("======================")
print("FERTIG")
print("======================")
print()
print("Backup erstellt:")
print("lowr_fix_backup")


input(
    "ENTER drücken..."
)