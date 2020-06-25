import maya.OpenMaya as OpenMaya  # pylint: disable=import-error
import maya.OpenMayaAnim as OpenMayaAnim  # pylint: disable=import-error
from maya import cmds  # pylint: disable=import-error
import pprint
PPrint = pprint.PrettyPrinter(width=10).pprint

# Get all selected items
selectedItems = cmds.ls(sl=True, long=True)

# Check if no items are selected
if len(selectedItems) < 1:
    error = "ERROR: No object selected"
    print(error)
    raise ValueError(error)

# Get the first selected item
# TODO: check if the selected item is a camera
selectedObject = selectedItems[0]

# Object to hold all collected data
FINAL = {'X': {}, 'Y': {}, 'Z': {}}


def setupRotations():
    # Collect the rotation averages. Delete all the current keyframes. Set the camera's rotations to the rotation averages.

    # Setup the attribute name for later use
    attrNameBase = selectedObject + '.rotate'

    # Loop through each axis
    for axis in ['X', 'Y', 'Z']:
        # Setup the attribute name
        attrName = attrNameBase + axis

        # Get the max and min keyframes of the attribute
        keyframes = cmds.keyframe(attrName, query=True)
        minKeyframe = int(min(keyframes))
        maxKeyframe = int(max(keyframes))

        # Reset the min and max variables to a value that will be replaced immediately (we will use it below to hold the min and max values)
        maxValue = -9999999999
        minValue = 9999999999

        # Loop through every frame between the min and max keyframes
        for frame in range(minKeyframe, maxKeyframe):

            # Get the min and max values of the attribute
            value = cmds.getAttr(attrName, time=frame)
            if value > maxValue:
                maxValue = value
            if value < minValue:
                minValue = value

        # Get the rotation average
        rotationAverage = (maxValue + minValue) / 2

        # Delete all the camera's rotation keys
        cmds.cutKey(
            selectedObject,
            time=(minKeyframe, maxKeyframe),
            attribute='rotate' + axis,
            option="keys"
        )

        # Set the new rotation average
        cmds.setAttr(attrName, rotationAverage)

        # Save everything to the FINAL object in case of later use
        FINAL[axis]['attrName'] = attrName
        FINAL[axis]['maxValue'] = maxValue
        FINAL[axis]['minValue'] = minValue
        FINAL[axis]['maxKeyframe'] = maxKeyframe
        FINAL[axis]['minKeyframe'] = minKeyframe
        FINAL[axis]['rotationAverage'] = rotationAverage

# ======================================================================
# Get and set focal length to the max focal length in the animation


def setupFocalLength():
    # Get the max and min keyframes of the attribute
    keyframes = cmds.keyframe('perspShape.focalLength', query=True)
    minKeyframe = int(min(keyframes))
    maxKeyframe = int(max(keyframes))

    # Reset the min and max variables to a value that will be replaced immediately (we will use it below to hold the min and max values)
    maxValue = -9999999999

    # Loop through every frame between the min and max keyframes
    for frame in range(minKeyframe, maxKeyframe):
        # Get the max value of the focal length
        value = cmds.getAttr(attrName, time=frame)
        if value > maxValue:
            maxValue = value

    # Delete all the camera's focal length keys
    cmds.cutKey(
        selectedObject(?shape?),
        time=(minKeyframe, maxKeyframe),
        attribute='focalLength',
        option="keys"
    )

    # Set the new max focal length
    cmds.setAttr('perspShape.focalLength', maxValue)

    # print(rotAvg)
    PPrint(FINAL)
