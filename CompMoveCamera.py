import math
import maya.OpenMaya as OpenMaya  # pylint: disable=import-error
import maya.OpenMayaAnim as OpenMayaAnim  # pylint: disable=import-error
from maya import cmds  # pylint: disable=import-error
import pprint
PPrint = pprint.PrettyPrinter(width=10).pprint

# Object to hold all collected data
FINAL = {}


def getAllValuesWeNeed():
    global FINAL

    # region Get the selected camera object

    # Get camera object
    selectedItems = cmds.ls(sl=True, long=True)

    # Check if no items are selected
    if len(selectedItems) < 1:
        error = "ERROR: No object selected"
        print(error)
        raise ValueError(error)

    # Get camera shapes
    shapes = cmds.listRelatives(selectedItems[0], shapes=True)

    # Check if no shapes are attached
    if len(shapes) < 1:
        error = "ERROR: No shapes on camera object"
        print(error)
        raise ValueError(error)

    # TODO: check if the selected item is a camera
    FINAL['selected'] = {
        'camera': selectedItems[0],
        'shape': shapes[0]
    }

    # endregion

    # region Get the focal lengths

    # Set shape name
    shapeName = FINAL['selected']['shape'] + '.focalLength'

    # Get the max and min keyframes of the attribute
    keyframes = cmds.keyframe(shapeName, query=True)
    minKeyframe = int(min(keyframes))
    maxKeyframe = int(max(keyframes))

    # Reset the min and max variables to a value that will be replaced immediately (we will use it below to hold the min and max values)
    maxFocalLength = -9999999999
    minFocalLength = 9999999999

    # Loop through every frame between the min and max keyframes
    for frame in range(minKeyframe, maxKeyframe):
        # Get the max value of the focal length
        value = cmds.getAttr(shapeName, time=frame)
        if value > maxFocalLength:
            maxFocalLength = value
        if value < minFocalLength:
            minFocalLength = value

    # Save everything to the FINAL object in case of later use
    FINAL['focalLength'] = {
        'keyframes': {
            'min': minKeyframe,
            'max': maxKeyframe,
        },
        'valueMillimeters': {
            'min': minFocalLength,
            'max': maxFocalLength,
        },
        'valueInches': {
            'min': minFocalLength / 25.4,
            'max': maxFocalLength / 25.4,
        }
    }
    # endregion

    # region Get rotation averages

    attrNameBase = FINAL['selected']['camera'] + '.rotate'

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

        # Field of angle increase (it is the triangle shape in the Word Reference document)
        fieldOfAngleInDegrees = maxValue - rotationAverage
        fieldOfAngleInRadians = math.radians(fieldOfAngleInDegrees)

        # Save everything to the FINAL object in case of later use
        FINAL[axis] = {
            'attrName': attrName,
            'rotationAverage': rotationAverage,
            'fieldOfAngleInDegrees': fieldOfAngleInDegrees,
            'fieldOfAngleInRadians': fieldOfAngleInRadians,
            'value': {
                'min': minValue,
                'max': maxValue
            },
            'keyframes': {
                'min': minKeyframe,
                'max': maxKeyframe
            },
        }
    # endregion

    # region Get the camera aperatures

    # Save everything to the FINAL object in case of later use
    aperatureHeight = cmds.getAttr(
        FINAL['selected']['shape'] + '.verticalFilmAperture'
    )
    aperatureWidth = cmds.getAttr(
        FINAL['selected']['shape'] + '.horizontalFilmAperture'
    )

    # Save everything to the FINAL object in case of later use
    FINAL['aperature'] = {
        'height': aperatureHeight,
        'width': aperatureWidth
    }
    # endregion

    # region Get the current resolutions
    resolutionHeight = cmds.getAttr(
        'defaultResolution.height'
    )
    resolutionWidth = cmds.getAttr(
        'defaultResolution.width'
    )

    # Save everything to the FINAL object in case of later use
    FINAL['resolution'] = {
        'height': resolutionHeight,
        'width': resolutionWidth
    }
    # endregion


def doTheMath():
    global FINAL

    focalMin = FINAL['focalLength']['valueInches']['min']
    focalMax = FINAL['focalLength']['valueInches']['min']

    xHeight = FINAL['aperature']['height'] / (focalMin * 2)
    yWidth = FINAL['aperature']['width'] / (focalMin * 2)

    xOriginalFieldOfView = math.atan(xHeight)
    yOriginalFieldOfView = math.atan(yWidth)

    xTan = xOriginalFieldOfView + FINAL['X']['fieldOfAngleInRadians']
    yTan = yOriginalFieldOfView + FINAL['Y']['fieldOfAngleInRadians']

    heightNewCameraAperture = (2 * focalMax) * math.tan(xTan)
    widthNewCameraAperture = (2 * focalMax) * math.tan(yTan)

    tempHeight = heightNewCameraAperture / FINAL['aperature']['height']
    tempWidth = widthNewCameraAperture / FINAL['aperature']['width']

    newCustomResolutionHeight = FINAL['resolution']['height'] * tempHeight
    newCustomResolutionWidth = FINAL['resolution']['width'] * tempWidth

    # Save everything to the FINAL object in case of later use
    FINAL['X']['originalFieldOfView'] = xOriginalFieldOfView
    FINAL['Y']['originalFieldOfView'] = yOriginalFieldOfView
    FINAL['heightNewCameraAperture'] = heightNewCameraAperture
    FINAL['widthNewCameraAperture'] = widthNewCameraAperture
    FINAL['newCustomResolutionHeight'] = newCustomResolutionHeight
    FINAL['newCustomResolutionWidth'] = newCustomResolutionWidth


def setAllTheNewValues():
    # region Set the focal length to the max focal length

    # Delete all the camera's focal length keys
    cmds.cutKey(
        FINAL['selected']['shape'],
        time=(FINAL['focalLength']['keyframes']['min'],
              FINAL['focalLength']['keyframes']['max']),
        attribute='focalLength',
        option="keys"
    )

    # Round the value up
    maxValueRoundedUp = math.ceil(FINAL['focalLength']['valueInches']['max'])

    # Set the new focal length to the max focal length
    cmds.setAttr(
        FINAL['selected']['shape'] +
        '.focalLength', maxValueRoundedUp
    )

    # endregion

    # region Set the camera's rotation to the rotation averages

    for axis in ['X', 'Y', 'Z']:
        cmds.cutKey(
            FINAL['selected']['camera'],
            time=(FINAL[axis]['keyframes']['min'],
                  FINAL[axis]['keyframes']['max']),
            attribute='rotate' + axis,
            option="keys"
        )

        # Set the new rotation average
        cmds.setAttr(FINAL[axis]['attrName'], FINAL[axis]['rotationAverage'])

    # endregion

    # region Set the camera's new apetures
    cmds.setAttr(
        FINAL['selected']['shape'] + '.verticalFilmAperture',
        round(FINAL['heightNewCameraAperture'], 2)
    )
    cmds.setAttr(
        FINAL['selected']['shape'] + '.horizontalFilmAperture',
        round(FINAL['widthNewCameraAperture'], 2)
    )
    # endregion

    # region Set the new render resolutions
    cmds.setAttr(
        'defaultResolution.height',
        round(FINAL['newCustomResolutionHeight'])
    )
    cmds.setAttr(
        'defaultResolution.width',
        round(FINAL['newCustomResolutionWidth'])
    )
    # endregion

    # Make sure pixel aspect ratio is 1
    cmds.setAttr('defaultResolution.pixelAspect', 1.000)


# This gets all the values we need and stores it in the global FINAL object
getAllValuesWeNeed()
PPrint(FINAL)

# Does all the complicated math using the variables from the global FINAL object
doTheMath()

# Set all the new values in Maya
setAllTheNewValues()
