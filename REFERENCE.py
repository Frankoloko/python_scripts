# Get length of array/string
len(myArray)

# Throw error and stop code
raise ValueError("No object selected")

# Get selected items (returns an array)
selectedItems = cmds.ls(sl=True, long=True)

# Get all the keyable attributes of an object
attributes = cmds.listAttr(selectedObject, keyable=True)

# Get all the keyframes of the attribute
cmds.keyframe(name + 'X', query=True)

# Get the value of the attribute at the time(keyframe)
cmds.getAttr(name + 'X', time=10.0)

# Set the attribute value of an object
cmds.setAttr('{}.inputComponents', len(
    faceNames), *faceNames, type="componentList")

# Cut keyframes from frame 10 to 20 of cube1's "Translate X" attribute #
cmds.cutKey('cube1', time=(10, 20), attribute='translateX', option="keys")

# Cut from all active objects all keys in the range 0 to 60 #
cmds.cutKey(time=(0, 60))

# Using a global variable
SELECTEDOBJECT = 'something'
..in function:
global SELECTEDOBJECT
SELECTEDOBJECT = selectedItems[0]
