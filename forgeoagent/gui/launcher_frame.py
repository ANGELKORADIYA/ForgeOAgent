import wx

class LauncherFrame(wx.Frame):
    """A compact, spotlight-like launcher window."""
    def __init__(self, parent=None):
        super().__init__(parent, title="ForgeOAgent Launcher", size=(600, 100))
        self.Center()
        # To be implemented: single prompt input, provider dropdown, run button
