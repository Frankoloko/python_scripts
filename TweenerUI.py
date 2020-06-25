from maya import cmds  # pylint: disable=import-error


def tween(pPercentage, pObj=None, pAttrs=None, selection=True):
    # If no obj is available to use, throw an error
    if not pObj and not selection:
        raise ValueError("No object given to tween")

    # If not obj is given, get it from the first selected item
    if not pObj:
        pObj = cmds.ls(selection=True)[0]

    if not pAttrs:
        pAttrs = cmds.listAttr(pObj, keyable=True)

    currentTime = cmds.currentTime(query=True)

    for attr in pAttrs:
        attrFull = '{}.{}'.format(pObj, attr)
        keyframes = cmds.keyframe(attrFull, query=True)

        if not keyframes:
            continue

        previousKeyframes = []
        for frame in keyframes:
            if frame < currentTime:
                previousKeyframes.append(frame)

        laterKeyframes = [frame for frame in keyframes if frame > currentTime]

        if not previousKeyframes and not laterKeyframes:
            continue

        if previousKeyframes:
            previousFrame = max(previousKeyframes)
        else:
            previousFrame = None

        nextFrame = min(laterKeyframes) if laterKeyframes else None

        if not previousFrame or not nextFrame:
            continue

        previousValue = cmds.getAttr(attrFull, time=previousFrame)
        nextValue = cmds.getAttr(attrFull, time=nextFrame)

        difference = nextValue - previousValue
        weightedDifference = (difference * pPercentage) / 100.0
        currentValue = previousValue + weightedDifference

        cmds.setKeyframe(attrFull, time=currentTime, value=currentValue)


class TweenWindow(object):
    windowName = "TweenerWindow"

    def show(self):
        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName)
        self.buildUI()
        cmds.showWindow()

    def buildUI(self):
        column = cmds.columnLayout()
        cmds.text(label="Use this slider to set the tween amount")

        row = cmds.rowLayout(numberOfColumns=2)

        self.slider = cmds.floatSlider(
            min=0, max=100, value=50, step=1, changeCommand=tween)

        cmds.button(label="Reset", command=self.reset)

        cmds.setParent(column)
        cmds.button(label="Close", command=self.close)

    def reset(self, *args):
        cmds.floatSlider(self.slider, edit=True, value=50)

    def close(self, *args):
        cmds.deleteUI(self.windowName)
