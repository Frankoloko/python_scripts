import math
import maya.OpenMaya as OpenMaya  # pylint: disable=import-error
import maya.OpenMayaAnim as OpenMayaAnim  # pylint: disable=import-error
from maya import cmds  # pylint: disable=import-error
import pprint
PPrint = pprint.PrettyPrinter(width=10).pprint


class CompMoveCamera:
    def __init__(self):
        self.aperature = {}
        self.focal_length = {}
        self.resolution = {}
        self.selected = {}
        self.X = {}
        self.Y = {}
        self.Z = {}

    def __getitem__(self, item):
        # This allows you to do stuff like: self[variable]
        return getattr(self, item)

    def get_all_values_we_need(self):
        # region Get the selected camera object

        # Get camera object
        selected_items = cmds.ls(sl=True, long=True)

        # Check if no items are selected
        if not selected_items:
            error = "ERROR: No camera selected"
            print(error)
            raise ValueError(error)

        # Get camera shapes
        shapes = cmds.listRelatives(selected_items[0], shapes=True)

        # Check if no shapes are attached
        if not shapes:
            error = "ERROR: No shapes on camera object"
            print(error)
            raise ValueError(error)

        # TODO: check if the selected item is a camera
        self.selected = {
            'camera': selected_items[0],
            'shape': shapes[0]
        }

        # endregion

        # region Get the focal lengths

        # Set shape name
        shape_name = self.selected['shape'] + '.focalLength'

        # Get the max and min keyframes of the attribute
        keyframes = cmds.keyframe(shape_name, query=True)
        if keyframes:
            min_keyframe = int(min(keyframes))
            max_keyframe = int(max(keyframes))

            # Reset the min and max variables to a value that will be replaced immediately (we will use it below to hold the min and max values)
            max_focal_length = -9999999999
            min_focal_length = 9999999999

            # Loop through every frame between the min and max keyframes
            for frame in range(min_keyframe, max_keyframe):
                # Get the max value of the focal length
                value = cmds.getAttr(shape_name, time=frame)
                if value > max_focal_length:
                    max_focal_length = value
                if value < min_focal_length:
                    min_focal_length = value

            # Save everything to self for later use
            self.focal_length = {
                'keyframes': {
                    'min': min_keyframe,
                    'max': max_keyframe,
                },
                'value_millimeters': {
                    'min': min_focal_length,
                    'max': max_focal_length,
                },
                'value_inches': {
                    'min': min_focal_length / 25.4,
                    'max': max_focal_length / 25.4,
                }
            }
        else:
            # Get the current focal length
            focal_length = cmds.getAttr(shape_name)

            # Save everything to self for later use
            self.focal_length = {
                'value_millimeters': {
                    'min': focal_length,
                    'max': focal_length,
                },
                'value_inches': {
                    'min': focal_length / 25.4,
                    'max': focal_length / 25.4,
                }
            }

            # endregion

        # region Get rotation averages

        attr_name_base = self.selected['camera'] + '.rotate'

        # Loop through each axis
        for axis in ['X', 'Y']:
            # Setup the attribute name
            attr_name = attr_name_base + axis

            # Get the max and min keyframes of the attribute
            keyframes = cmds.keyframe(attr_name, query=True)

            # If there are no keyframes, just return the average data
            if not keyframes:
                rotation_average = cmds.getAttr(attr_name)

                # Field of angle increase (it is the triangle shape in the Word Reference document)
                field_of_angle_in_radians = math.radians(rotation_average)

                # Save everything to self for later use
                self[axis]['rotation'] = {
                    'attr_name': attr_name,
                    'rotation_average': rotation_average,
                    'field_of_angle_in_degrees': rotation_average,
                    'field_of_angle_in_radians': field_of_angle_in_radians
                }
                continue

            min_keyframe = int(min(keyframes))
            max_keyframe = int(max(keyframes))

            # Reset the min and max variables to a value that will be replaced immediately (we will use it below to hold the min and max values)
            max_value = -9999999999
            min_value = 9999999999

            # Loop through every frame between the min and max keyframes
            for frame in range(min_keyframe, max_keyframe):

                # Get the min and max values of the attribute
                value = cmds.getAttr(attr_name, time=frame)
                if value > max_value:
                    max_value = value
                if value < min_value:
                    min_value = value

            # Get the rotation average
            rotation_average = (max_value + min_value) / 2

            # Field of angle increase (it is the triangle shape in the Word Reference document)
            field_of_angle_in_degrees = max_value - rotation_average
            field_of_angle_in_radians = math.radians(field_of_angle_in_degrees)

            # Save everything to self for later use
            self[axis]['rotation'] = {
                'attr_name': attr_name,
                'rotation_average': rotation_average,
                'field_of_angle_in_degrees': field_of_angle_in_degrees,
                'field_of_angle_in_radians': field_of_angle_in_radians,
                'value': {
                    'min': min_value,
                    'max': max_value
                },
                'keyframes': {
                    'min': min_keyframe,
                    'max': max_keyframe
                }
            }
        # endregion

        # region Get the camera aperatures

        # Save everything to self for later use
        aperature_height = cmds.getAttr(
            self.selected['shape'] + '.verticalFilmAperture'
        )
        aperature_width = cmds.getAttr(
            self.selected['shape'] + '.horizontalFilmAperture'
        )

        # Save everything to self for later use
        self.aperature = {
            'original': {
                'height': aperature_height,
                'width': aperature_width
            }
        }
        # endregion

        # region Get the current resolutions
        resolution_height = cmds.getAttr(
            'defaultResolution.height'
        )
        resolution_width = cmds.getAttr(
            'defaultResolution.width'
        )

        # Save everything to self for later use
        self.resolution = {
            'original': {
                'height': resolution_height,
                'width': resolution_width
            }
        }
        # endregion

    def do_the_math(self):
        focal_min = self.focal_length['value_inches']['min']
        focal_max = self.focal_length['value_inches']['min']

        xHeight = self.aperature['original']['height'] / (focal_min * 2)
        yWidth = self.aperature['original']['width'] / (focal_min * 2)

        self.X['original_field_of_view'] = math.atan(xHeight)
        self.Y['original_field_of_view'] = math.atan(yWidth)

        xTan = self.X['original_field_of_view'] + \
            self.X['rotation']['field_of_angle_in_radians']
        yTan = self.Y['original_field_of_view'] + \
            self.Y['rotation']['field_of_angle_in_radians']

        self.aperature['new'] = {}
        self.aperature['new']['height'] = (2 * focal_max) * math.tan(xTan)
        self.aperature['new']['width'] = (2 * focal_max) * math.tan(yTan)

        temp_height = self.aperature['new']['height'] / \
            self.aperature['original']['height']
        temp_width = self.aperature['new']['width'] / \
            self.aperature['original']['width']

        self.resolution['new'] = {}
        self.resolution['new']['height'] = self.resolution['original']['height'] * temp_height
        self.resolution['new']['width'] = self.resolution['original']['width'] * temp_width

    def set_all_the_new_values(self):
        # region Set the focal length to the max focal length

        # If there are keyframes on the focalLength, then delete all keyframes. Otherwise just leave the current keyframe alone
        if 'keyframes' in self.focal_length:
            # Delete all the camera's focal length keys
            cmds.cutKey(
                self.selected['shape'],
                time=(self.focal_length['keyframes']['min'],
                      self.focal_length['keyframes']['max']),
                attribute='focalLength',
                option="keys"
            )

            # Round the value up
            max_value_rounded_up = math.ceil(
                self.focal_length['value_inches']['max'])

            # Set the new focal length to the max focal length
            cmds.setAttr(
                self.selected['shape'] +
                '.focalLength', max_value_rounded_up
            )
        # endregion

        # region Set the camera's rotation to the rotation averages

        for axis in ['X', 'Y']:
            # If there are keyframes on the rotation, then delete all keyframes. Otherwise just leave the current keyframe alone
            if 'keyframes' in self[axis]['rotation']:
                cmds.cutKey(
                    self.selected['camera'],
                    time=(self[axis]['rotation']['keyframes']['min'],
                          self[axis]['rotation']['keyframes']['max']),
                    attribute='rotate' + axis,
                    option="keys"
                )

            # Set the new rotation average
            cmds.setAttr(self[axis]['rotation']['attr_name'],
                         self[axis]['rotation']['rotation_average'])

        # endregion

        # region Set the camera's new apetures
        cmds.setAttr(
            self.selected['shape'] + '.verticalFilmAperture',
            round(self.aperature['new']['height'], 2)
        )
        cmds.setAttr(
            self.selected['shape'] + '.horizontalFilmAperture',
            round(self.aperature['new']['width'], 2)
        )
        # endregion

        # region Set the new render resolutions
        cmds.setAttr(
            'defaultResolution.height',
            round(self.resolution['new']['height'])
        )
        cmds.setAttr(
            'defaultResolution.width',
            round(self.resolution['new']['width'])
        )
        # endregion

        # Make sure pixel aspect ratio is 1
        cmds.setAttr('defaultResolution.pixelAspect', 1.000)

    def run(self):
        # This gets all the values we need and stores it in the class's self
        self.get_all_values_we_need()

        # Does all the complicated math using the variables from the class's self
        self.do_the_math()

        # Set all the new values in Maya
        self.set_all_the_new_values()

        # Print all values
        PPrint(vars(self))
