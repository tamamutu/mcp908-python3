# Created on Jun 30, 2013
# @author: kickban

import os
import shutil
import sys
import zipfile

import MinecraftDiscovery
from commands import Commands


def copy_assets(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)

    try:
        shutil.copytree(src, dst)
    except:
        print("Error copying assets.")
        sys.exit()


def copy_library(src, dst, library):
    try:
        dst_path = os.path.split(os.path.join(dst, library['filename']))[0]

        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)
        os.makedirs(dst_path)

        shutil.copy2(os.path.join(src, library['filename']), dst_path)
    except:
        print("Error copying library %s" % library['name'])
        sys.exit()


# def extractLibrary(src, dst, library, version):
#    try:
#        srcPath = os.path.join(src, library['filename'])
#        dstPath = os.path.join(dst, "versions", version, "%s-natives"%version)
#    
#        if not os.path.exists(dstPath):
#            os.makedirs(dstPath)
#        
#        jarFile = zipfile.ZipFile(srcPath)
#        fileList = jarFile.namelist()
#    
#        for _file in fileList:
#            if not os.path.exists(os.path.join(dstPath, _file)):
#                exclude = False;
#                for entry in library['exclude']:
#                    if entry in _file:
#                        exclude = True
#                if not exclude:
#                    print("Extracting file %s from library %s"%(_file, library['name'].split(":")[1]))
#                    jarFile.extract(_file, dstPath)
#
#    except:
#        print ("Error extracting library %s"%library['name'])
#        sys.exit()

def extractNative(root, name, jarname, version):
    try:
        src_path = os.path.join(root, jarname)
        dst_path = os.path.join(root, "versions", version, "%s-natives" % version)

        if not os.path.exists(dst_path):
            os.makedirs(dst_path)

        jar_file = zipfile.ZipFile(src_path)
        jar_file.extract(name, dst_path)
    except:
        print("Error extracting native %s from %s" % (name, jarname))
        sys.exit()


def copy_minecraft(src, dst, version):
    try:
        jar_src_path = os.path.join(src, "versions", version, "%s.jar" % version)
        json_src_path = os.path.join(src, "versions", version, "%s.json" % version)
        dst_path = os.path.join(dst, "versions", version)

        if os.path.exists(dst_path):
            shutil.rmtree(dst_path)
        os.makedirs(dst_path)

        shutil.copy2(jar_src_path, dst_path)
        shutil.copy2(json_src_path, dst_path)
    except Exception as e:
        print("\nError while copying Minecraft : %s" % e)
        sys.exit()

    #########################################################################################################


def copy_client_assets(commands, work_dir=None):
    current_version = commands.versionClient

    os_keyword = MinecraftDiscovery.getNativesKeyword()
    if work_dir == None:
        if MinecraftDiscovery.checkCacheIntegrity(commands.dirjars, commands.jsonFile, os_keyword, current_version):
            return
        else:
            mcDir = MinecraftDiscovery.getMinecraftPath()
    else:
        mcDir = work_dir

    # if not workDir:
    #    mcDir = MinecraftDiscovery.getMinecraftPath()
    # else:
    #    mcDir = workDir

    dstDir = commands.dirjars

    # versionDir   = os.path.join(mcDir, "versions")
    # librariesDir = os.path.join(mcDir, "libraries")

    print("Looking in %s for mc installs..." % os.path.join(mcDir, "versions")),
    MinecraftDiscovery.checkMCDir(mcDir, current_version)
    print("OK")

    print("Copying assets..."),
    copy_assets(os.path.join(mcDir, "assets"), os.path.join(dstDir, "assets"))
    print("OK")

    print("Parsing JSON file..."),
    mcLibraries = MinecraftDiscovery.getLibraries(mcDir, MinecraftDiscovery.getJSONFilename(mcDir, current_version),
                                                  os_keyword)
    print("OK")

    print("Looking for minecraft main jar..."),
    if (MinecraftDiscovery.checkMinecraftExists(dstDir, current_version)):
        print("OK")
    else:
        print("Not found")
        print("Copying minecraft main jar..."),
        copy_minecraft(mcDir, dstDir, current_version)
        print("OK")

    print("> Checking libraries...")
    for library in mcLibraries.values():
        if not MinecraftDiscovery.checkLibraryExists(dstDir, library):
            print("\tCopying library %s..." % library['name'].split(':')[1]),
            copy_library(mcDir, dstDir, library)
            print("OK")

    print("> Checking Natives...")
    for native, jarname in MinecraftDiscovery.getNatives(dstDir, mcLibraries).items():
        if not MinecraftDiscovery.checkNativeExists(dstDir, native, current_version):
            print("\tExtracting native %s..." % native),
            extractNative(dstDir, native, jarname, current_version)
            print("OK")


if __name__ == '__main__':
    commands = Commands()
    copy_client_assets(commands)
