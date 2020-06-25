import math
import maya.OpenMaya as OpenMaya  # pylint: disable=import-error
import maya.OpenMayaAnim as OpenMayaAnim  # pylint: disable=import-error
from maya import cmds  # pylint: disable=import-error
import pprint
PPrint = pprint.PrettyPrinter(width=10).pprint

# Object to hold all collected data
FINAL = {'X': {}, 'Y': {}, 'Z': {}, 'maxFocalLength': None}
SELECTEDOBJECT = None
STARTINGFILMBACKHEIGHT = 20.25
STARTINGFILMBACKWIDTH = 36
DEFAULTRESOLUTIONWIDTH = 1920
DEFAULTRESOLUTIONHEIGHT = 1080


def getSelectedCamera():
    # Get all selected items
    selectedItems = cmds.ls(sl=True, long=True)

    # Check if no items are selected
    if len(selectedItems) < 1:
        error = "ERROR: No object selected"
        print(error)
        raise ValueError(error)

    # Get the first selected item
    # TODO: check if the selected item is a camera
    global SELECTEDOBJECT
    SELECTEDOBJECT = selectedItems[0]


def setupFocalLength():
    # Get and set focal length to the max focal length in the animation

    # Get shapes on object (to access focal length)
    shapes = cmds.listRelatives(SELECTEDOBJECT, shapes=True)

    # Set shape name
    shapeName = shapes[0] + '.focalLength'

    # Get the max and min keyframes of the attribute
    keyframes = cmds.keyframe(shapeName, query=True)
    minKeyframe = int(min(keyframes))
    maxKeyframe = int(max(keyframes))

    # Reset the min and max variables to a value that will be replaced immediately (we will use it below to hold the min and max values)
    maxValue = -9999999999
    minValue = 9999999999

    # Loop through every frame between the min and max keyframes
    for frame in range(minKeyframe, maxKeyframe):
        # Get the max value of the focal length
        value = cmds.getAttr(shapeName, time=frame)
        if value > maxValue:
            maxValue = value
        if value < minValue:
            minValue = value

    # Delete all the camera's focal length keys
    cmds.cutKey(
        shapeName,
        time=(minKeyframe, maxKeyframe),
        attribute='focalLength',
        option="keys"
    )

    # Round the value up
    maxValueRoundedUp = math.ceil(maxValue)

    # Set the new max focal length
    cmds.setAttr(shapeName, maxValueRoundedUp)

    # Save everything to the FINAL object in case of later use
    global FINAL
    FINAL['maxFocalLength'] = maxValue
    FINAL['minFocalLength'] = minValue


def setupRotations():
    # Collect the rotation averages. Delete all the current keyframes. Set the camera's rotations to the rotation averages.

    # Setup the attribute name for later use
    attrNameBase = SELECTEDOBJECT + '.rotate'

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
            SELECTEDOBJECT,
            time=(minKeyframe, maxKeyframe),
            attribute='rotate' + axis,
            option="keys"
        )

        # Set the new rotation average
        cmds.setAttr(attrName, rotationAverage)

        # Field of angle increase (it is the triangle shape in the Word Reference document)
        fieldOfAngleDegrees = maxValue - rotationAverage
        fieldOfAngleRadians = math.radians(fieldOfAngleDegrees)

        # Save everything to the FINAL object in case of later use
        global FINAL
        FINAL[axis]['attrName'] = attrName
        FINAL[axis]['maxValue'] = maxValue
        FINAL[axis]['minValue'] = minValue
        FINAL[axis]['maxKeyframe'] = maxKeyframe
        FINAL[axis]['minKeyframe'] = minKeyframe
        FINAL[axis]['rotationAverage'] = rotationAverage
        FINAL[axis]['fieldOfAngleDegrees'] = fieldOfAngleDegrees
        FINAL[axis]['fieldOfAngleRadians'] = fieldOfAngleRadians


def setupFieldOfView():
    # y = width
    # x = height
    global FINAL
    focalMinVariable = 2 * FINAL['minFocalLength']
    focalMaxVariable = 2 * FINAL['maxFocalLength']

    xHeight = STARTINGFILMBACKHEIGHT / focalMinVariable
    yWidth = STARTINGFILMBACKWIDTH / focalMinVariable

    xOriginalFieldOfView = math.atan(xHeight)
    yOriginalFieldOfView = math.atan(yWidth)

    xTan = xOriginalFieldOfView + FINAL['X']['fieldOfAngleRadians']
    yTan = yOriginalFieldOfView + FINAL['Y']['fieldOfAngleRadians']

    heightNewCameraAperture = focalMaxVariable * math.tan(xTan)
    widthNewCameraAperture = focalMaxVariable * math.tan(yTan)

    print('heightNewCameraAperture', heightNewCameraAperture)
    print('widthNewCameraAperture', widthNewCameraAperture)
    print('focalMaxVariable', focalMaxVariable)
    print('yTan', yTan)
    print(FINAL)

    # Get shapes on object (to access focal length)
    shapes = cmds.listRelatives(SELECTEDOBJECT, shapes=True)

    # Set the new camera apeture lengths
    cmds.setAttr(shapes[0] + '.verticalFilmAperture',
                 round(heightNewCameraAperture, 2))
    cmds.setAttr(shapes[0] + '.horizontalFilmAperture',
                 round(widthNewCameraAperture, 2))

    # Save everything to the FINAL object in case of later use
    FINAL['X']['originalFieldOfView'] = xOriginalFieldOfView
    FINAL['Y']['originalFieldOfView'] = yOriginalFieldOfView
    FINAL['heightNewCameraAperture'] = heightNewCameraAperture
    FINAL['widthNewCameraAperture'] = widthNewCameraAperture


def setupCustomResolutions():
    tempHeight = FINAL['heightNewCameraAperture'] / STARTINGFILMBACKHEIGHT
    tempWidth = FINAL['widthNewCameraAperture'] / STARTINGFILMBACKWIDTH

    newCustomResolutionHeight = DEFAULTRESOLUTIONHEIGHT * tempHeight
    newCustomResolutionWidth = DEFAULTRESOLUTIONWIDTH * tempWidth

    # Set the new resolutions
    cmds.setAttr('defaultResolution.height', round(newCustomResolutionHeight))
    cmds.setAttr('defaultResolution.width', round(newCustomResolutionWidth))

    # Save everything to the FINAL object in case of later use
    FINAL['newCustomResolutionHeight'] = newCustomResolutionHeight
    FINAL['newCustomResolutionWidth'] = newCustomResolutionWidth


def test():
    print('hi')


getSelectedCamera()
# Break all keys on the focal length and set it to the max focal length (rounded up)
setupFocalLength()
# Break all rotation value keys, and set the rotation values to the averages
setupRotations()
# Round up the height and width to 2 decimals and set in the camera aperture(mm)
setupFieldOfView()
# Set width and height resolution in render settings
setupCustomResolutions()
# Make sure pixel aspect ratio is 1
cmds.setAttr('defaultResolution.pixelAspect', 1.000)

# print(rotAvg)
PPrint(FINAL)
