// Mask of the photo's subject(s), using macOS's own "lift subject from background" (Vision framework).
// Usage: swift lift_subject.swift <input image> <output mask.png>
import Foundation
import Vision
import CoreImage
import ImageIO

let args = CommandLine.arguments
guard args.count == 3,
      let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: args[1]) as CFURL, nil),
      let image = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
    FileHandle.standardError.write("usage: lift_subject.swift <input image> <output mask.png>\n".data(using: .utf8)!)
    exit(1)
}
let handler = VNImageRequestHandler(cgImage: image, options: [:])
let request = VNGenerateForegroundInstanceMaskRequest()
do {
    try handler.perform([request])
    guard let result = request.results?.first else {
        FileHandle.standardError.write("no subject found\n".data(using: .utf8)!)
        exit(2)
    }
    let mask = try result.generateScaledMaskForImage(forInstances: result.allInstances, from: handler)
    let ci = CIImage(cvPixelBuffer: mask)
    try CIContext().writePNGRepresentation(of: ci, to: URL(fileURLWithPath: args[2]), format: .L8,
                                           colorSpace: CGColorSpaceCreateDeviceGray())
    print("subjects: \(result.allInstances.count)")
} catch {
    FileHandle.standardError.write("failed: \(error)\n".data(using: .utf8)!)
    exit(3)
}
