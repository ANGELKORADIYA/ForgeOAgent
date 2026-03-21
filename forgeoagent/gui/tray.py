import wx.adv
import wx

class LauncherTaskBarIcon(wx.adv.TaskBarIcon):
    """System tray component to keep the app warm and ready."""
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
