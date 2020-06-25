from maya import cmds  # pylint: disable=import-error
import os
import json
import pprint

userAppDir = cmds.internalVar(userAppDir=True)
DIRECTORY = os.path.join(userAppDir, 'controllerLibrary')


def createDirectory(pDirectory=DIRECTORY):
    """
    Creates the given directory if it doesn't exist already
    Args:
        directory (str): The directory to create
    """
    if not os.path.exists(pDirectory):
        os.mkdir(pDirectory)


class ControllerLibrary(dict):
    def save(self, pName, pDirectory=DIRECTORY):
        createDirectory(pDirectory)
        path = os.path.join(pDirectory, '{}.ma'.format(pName))

        cmds.file(rename=path)

        if cmds.ls(selection=True):
            cmds.file(force=True, type='mayaAscci', exportSelected=True)
        else:
            cmds.file(save=True, type='mayaAscii', force=True)

    def find(self, pDirectory=DIRECTORY):
        if not os.path.exists(pDirectory):
            return

        files = os.listdir(pDirectory)
