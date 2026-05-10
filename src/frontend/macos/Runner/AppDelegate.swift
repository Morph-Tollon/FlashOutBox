import Cocoa
import FlutterMacOS

@main
class AppDelegate: FlutterAppDelegate {
    override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
    
    override func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
        return true
    }
    
    @IBAction func OpenGithubIssues(_ sender: Any){
        if let url = URL(string: "https://github.com/Morph-Tollon/FlashOutBox/issues") {
            NSWorkspace.shared.open(url)
            
            
        }
        
    }
    
}
