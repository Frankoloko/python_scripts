from maya import cmds  # pylint: disable=import-error


def run():
    # Get the current file path
    thisFilePath = cmds.file(q=True, sn=True)
    # Load the old file back in
    cmds.file(thisFilePath, force=True, open=True)
