from maya import cmds  # pylint: disable=import-error


def run():
    # Get the current file path
    thisFilePath = cmds.file(q=True, sn=True)
    # Create a copy of the file (to throw away unsaved changes)
    cmds.file(new=True, force=True)
    # Load the old file back in
    cmds.file(thisFilePath, open=True)
