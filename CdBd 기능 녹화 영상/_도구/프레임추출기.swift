import Foundation
import AVFoundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

let a = CommandLine.arguments
guard a.count >= 6 else { print("usage: in out interval duration maxW"); exit(1) }
let inURL = URL(fileURLWithPath: a[1])
let outDir = a[2]
let interval = Double(a[3])!
let duration = Double(a[4])!
let maxW = Int(a[5])!

try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)

let asset = AVURLAsset(url: inURL)
let gen = AVAssetImageGenerator(asset: asset)
gen.appliesPreferredTrackTransform = true
gen.requestedTimeToleranceBefore = CMTime(seconds: 0.15, preferredTimescale: 600)
gen.requestedTimeToleranceAfter  = CMTime(seconds: 0.15, preferredTimescale: 600)

func resize(_ img: CGImage, _ maxW: Int) -> CGImage {
    if img.width <= maxW { return img }
    let scale = Double(maxW) / Double(img.width)
    let w = maxW, h = Int(Double(img.height) * scale)
    let cs = CGColorSpaceCreateDeviceRGB()
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
                              bytesPerRow: 0, space: cs,
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { return img }
    ctx.interpolationQuality = .high
    ctx.draw(img, in: CGRect(x: 0, y: 0, width: w, height: h))
    return ctx.makeImage() ?? img
}

var t = 0.0
var n = 0
while t < duration {
    let time = CMTime(seconds: t, preferredTimescale: 600)
    do {
        var actual = CMTime.zero
        let cg = try gen.copyCGImage(at: time, actualTime: &actual)
        let out = resize(cg, maxW)
        let name = String(format: "t%06.1f.jpg", t)
        let url = URL(fileURLWithPath: outDir).appendingPathComponent(name)
        if let dest = CGImageDestinationCreateWithURL(url as CFURL, UTType.jpeg.identifier as CFString, 1, nil) {
            CGImageDestinationAddImage(dest, out, [kCGImageDestinationLossyCompressionQuality: 0.72] as CFDictionary)
            CGImageDestinationFinalize(dest)
            n += 1
        }
    } catch {
        FileHandle.standardError.write("skip \(t): \(error)\n".data(using: .utf8)!)
    }
    t += interval
}
print("\(n) frames -> \(outDir)")
