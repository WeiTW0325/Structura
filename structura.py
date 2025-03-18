import os
import updater
if not(os.path.exists("lookups")):
    print("downloading lookup files")
    updater.update("https://update.structuralab.com/structuraUpdate","Structura1-6","")
import os
import argparse
import json
from structura_core import structura
from numpy import array, int32, minimum
import nbtlib

debug = False
models = {}

def update():
    with open("lookups/lookup_version.json") as file:
        version_data = json.load(file)
        print(version_data["version"])
    updated = updater.update(version_data["update_url"], "Structura1-6", version_data["version"])
    if updated:
        with open("lookups/lookup_version.json") as file:
            version_data = json.load(file)
        print("Updated!", version_data["notes"])
    else:
        print("Status", "You are currently up to date.")

def add_model(file, model_name, x, y, z, opacity):
    models[model_name] = {}
    models[model_name]["offsets"] = [x, y, z]
    models[model_name]["opacity"] = opacity
    models[model_name]["structure"] = file
    print(f"Model {model_name} added.")

def get_global_cords():
    mins = array([2147483647, 2147483647, 2147483647], dtype=int32)
    for name in models.keys():
        file = models[name]["structure"]
        struct = {}
        struct["nbt"] = nbtlib.load(file, byteorder='little')
        if "" in struct["nbt"].keys():
            struct["nbt"] = struct["nbt"][""]
        struct["mins"] = array(list(map(int, struct["nbt"]["structure_world_origin"])))
        mins = minimum(mins, struct["mins"])
    print(mins)

def delete_model(model_name):
    if model_name in models:
        del models[model_name]
        print(f"Model {model_name} deleted.")
    else:
        print(f"Model {model_name} not found.")

def run_from_cli(pack_name, icon_file, output_file, export_list, big_build, x, y, z, opacity):
    stop = False
    if os.path.isfile(f"{pack_name}.mcpack"):
        stop = True
        print("Error: pack already exists or pack name is empty")
    if not stop:
        structura_base = structura(pack_name)
        structura_base.set_opacity(opacity)
        if icon_file:
            structura_base.set_icon(icon_file)
        if debug:
            print(models)
        
        if not big_build:
            for name_tag in models.keys():
                structura_base.add_model(name_tag, models[name_tag]["structure"])
                structura_base.set_model_offset(name_tag, models[name_tag]["offsets"].copy())
            structura_base.generate_with_nametags()
            if export_list:
                structura_base.make_nametag_block_lists()
            structura_base.generate_nametag_file()
            structura_base.compile_pack()
        elif big_build:
            for name_tag in models.keys():
                structura_base.add_model(name_tag, models[name_tag]["structure"])
            structura_base.make_big_model([x, y, z])
            if export_list:
                structura_base.make_big_blocklist()
            structura_base.compile_pack()
        print(f"Pack {pack_name} generated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Structura CLI Tool")
    parser.add_argument("--update", action="store_true", help="Update lookup files")
    parser.add_argument("--add-model", nargs=6, metavar=('file', 'model_name', 'x', 'y', 'z', 'opacity'), help="Add a model with specified parameters")
    parser.add_argument("--delete-model", metavar='model_name', help="Delete a specified model")
    parser.add_argument("--get-global-cords", action="store_true", help="Get global coordinates")
    parser.add_argument("--run", nargs=7, metavar=('pack_name', 'icon_file', 'output_file', 'export_list', 'big_build', 'x', 'y', 'z', 'opacity'), help="Run the tool with specified parameters")

    args = parser.parse_args()

    if args.update:
        update()
    if args.add_model:
        add_model(*args.add_model)
    if args.delete_model:
        delete_model(args.delete_model)
    if args.get_global_cords:
        get_global_cords()
    if args.run:
        run_from_cli(*args.run)
