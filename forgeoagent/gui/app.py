import wx

class LauncherApp(wx.App):
    """The main application class for the fast, compact launcher."""
    def OnInit(self):
        # We will instantiate LauncherFrame here
        return True

def run_launcher():
    app = LauncherApp()
    app.MainLoop()
