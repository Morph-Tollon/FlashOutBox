import Cocoa
import FlutterMacOS

@main
class AppDelegate: FlutterAppDelegate {
    var navigationChannel: FlutterMethodChannel?

    override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
    
    override func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
        return true
    }
    override func applicationDidFinishLaunching(_ notification: Notification) {
        // Grab the controller from the main window
        if let window = NSApplication.shared.windows.first,
           let controller = window.contentViewController as? FlutterViewController {
            
            navigationChannel = FlutterMethodChannel(
                name: "uk.co.morphtollon.flashoutbox/channel",
                binaryMessenger: controller.engine.binaryMessenger
            )
        }
    }
    
    @IBAction func OpenGithubIssues(_ sender: Any){
        if let url = URL(string: "https://github.com/Morph-Tollon/FlashOutBox/issues") {
            NSWorkspace.shared.open(url)
            
            
        }
    }
        
    @IBAction func settingsPage(_ sender: Any){
        navigationChannel?.invokeMethod("page", arguments:"/settings")


    }
        
    
    
}

