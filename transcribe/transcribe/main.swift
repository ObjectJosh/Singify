/* This code should be compiled using swiftc
the compiled code should be in the same directory as this file.
*/
import Foundation
import Speech
import AppKit
let app = NSApplication.shared

class AppDelegate: NSObject, NSApplicationDelegate {

    private let audioEngine = AVAudioEngine()
    private let speechRecognizer = SFSpeechRecognizer()
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    
    func writeToTxt(_ str: String) {

        let filename = getDocumentsDirectory().appendingPathComponent("output.txt")
        do {
            try str.write(to: filename, atomically: true, encoding: String.Encoding.utf8)
        } catch {
            // failed to write file – bad permissions, bad filename, missing permissions, or more likely it can't be converted to the encoding
        }
    }
    
    func getDocumentsDirectory() -> URL {
        let paths = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)
        return paths[0]
    }
    
    
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { (buffer: AVAudioPCMBuffer, when: AVAudioTime) in
            self.recognitionRequest?.append(buffer)
        }

        SFSpeechRecognizer.requestAuthorization({ (authStatus: SFSpeechRecognizerAuthorizationStatus) in
            self.recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
            guard let speechRecognizer = self.speechRecognizer else { fatalError("Unable to create a SpeechRecognizer object") }
            guard let recognitionRequest = self.recognitionRequest else { fatalError("Unable to create a SFSpeechAudioBufferRecognitionRequest object") }
            recognitionRequest.shouldReportPartialResults = true
            self.recognitionTask = speechRecognizer.recognitionTask(with: recognitionRequest) { result, error in

                var isFinal = false
                if let result = result {
                    isFinal = result.isFinal
                    let notification: [String: Any] = [
                        "text": result.bestTranscription.formattedString,
                        "isFinal": result.isFinal,
                    ]
                    let jsonData = try! JSONSerialization.data(withJSONObject: notification)
                    if let jsonString = String(data: jsonData, encoding: String.Encoding.utf8) {
//                       print(jsonString)
                        // print("\u{001B}[2J") // to clear terminal, might be removed

                         print("\(result.bestTranscription.formattedString)")
                        // NSLog("\(result.bestTranscription.formattedString)")
//                        self.writeToTxt(jsonString)
                    }
                }
                if error != nil || isFinal {
                    self.audioEngine.stop()
                    inputNode.removeTap(onBus: 0)
                    self.recognitionRequest = nil
                    self.recognitionTask = nil
                    app.terminate(self)
                }
            }
        })
        audioEngine.prepare()

        try! audioEngine.start()
    }
}

let delegate = AppDelegate()
app.delegate = delegate
app.run()
