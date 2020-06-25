from maya import cmds  # pylint: disable=import-error


def createGear(pTeeth=10, pLength=0.3):
    """
    This function will create a gear with the given parameters
    Args:
        teeth: The number of teeth to create
        length: The length of the teeth

    Returns:
        A tuple of the transform, constructor and extrude
    """
    spans = pTeeth * 2
    transform, constructor = cmds.polyPipe(subdivisionsAxis=spans)

    sideFaces = range(spans * 2, spans * 3, 2)

    cmds.select(clear=True)

    for face in sideFaces:
        cmds.select('{}.f[{}]'.format(transform, face), add=True)

    extrude = cmds.polyExtrudeFacet(localTranslateZ=pLength)[0]

    cmds.select(clear=True)

    return transform, constructor, extrude


def changeTeeth(constructor, extrude, teeth=10, length=0.3):
    spans = teeth * 2

    cmds.polyPipe(constructor, edit=True, subdivisionsAxis=spans)

    sideFaces = range(spans * 2, spans * 3, 2)

    faceNames = []

    for face in sideFaces:
        faceName = 'f[{}]'.format(face)
        faceNames.append(faceName)

    cmds.setAttr('{}.inputComponents'.format(extrude), len(
        faceNames), *faceNames, type="componentList")

    cmds.polyExtrudeFacet(extrude, edit=True, ltz=length)
