# hello :)
print("A tool made by Kleopy!")
print("Build: 1\n")

import os, struct, xml.etree.ElementTree as ET

def packUInt8(value):
    return struct.pack(">B", value)

def packUInt32(value):
    return struct.pack(">I", value)

def packFloat32(value):
    return struct.pack(">f", float(value))

def packStr8(text):
    encoded = text.encode("utf-8")
    return struct.pack(">I", len(encoded)) + encoded

packDashType = {
    "static": 0
}

def parseDuration(dashTime):
    if dashTime.startswith("PT") and dashTime.endswith("S"):
        return float(dashTime[2:-1])
    raise ValueError("Unsupported time format!")

try:
    inputMPD = input("dashMPD file (not serialized)\nInput: ").strip('"')
    print("\nLog:")
    tree = ET.parse(inputMPD)
    mpd = tree.getroot()
    binData = b''
    binData += packUInt32(0x1) # flag
    dashType = mpd.get("type")
    binData += packUInt8(packDashType.get(dashType, 0)) # type
    binData += packFloat32(parseDuration(mpd.get("mediaPresentationDuration", "PT0S"))) # mediaPresentationDuration
    binData += packFloat32(parseDuration(mpd.get("minBufferTime", "PT0S"))) # minBufferTime
    periods = mpd.findall("{urn:mpeg:DASH:schema:MPD:2011}Period")
    binData += packUInt32(len(periods)) # periodNumber
    
    for a in periods:
        binData += packUInt32(int(a.get("id"))) # id
        binData += packFloat32(parseDuration(a.get("start", "PT0S"))) # start
        binData += packFloat32(parseDuration(a.get("duration", "PT0S"))) # duration
        adaptationSets = a.findall("{urn:mpeg:DASH:schema:MPD:2011}AdaptationSet")
        binData += packUInt32(len(adaptationSets)) # btationSetNumber
        
        for b in adaptationSets:
            binData += packUInt32(int(b.get("id"))) # id
            binData += packStr8(b.get("mimeType", "")) # mimeType
            binData += packStr8(b.get("codecs", "")) # codecs
            binData += packUInt32(int(b.get("maxWidth", 0))) # maxWidth
            binData += packUInt32(int(b.get("maxHeight", 0))) # maxHeight
            binData += packUInt32(0x0) # Unknown
            binData += packUInt32(1 if b.get("subsegmentAlignment") == "true" else 0) # subsegmentAlignment
            binData += packUInt8(int(b.get("subsegmentStartsWithSAP", 0))) # subsegmentStartsWithSAP
            binData += packUInt8(1 if b.get("bitstreamSwitching") == "true" else 0) # bitstreamSwitching
            representations = b.findall("{urn:mpeg:DASH:schema:MPD:2011}Representation")
            binData += packUInt32(len(representations)) # cresentationNumber
            
            for c in representations:
                binData += packUInt32(int(c.get("id", 0))) # id
                binData += packUInt32(int(c.get("bandwidth", 0))) # bandwidth
                baseURL = c.find("{urn:mpeg:DASH:schema:MPD:2011}BaseURL")
                binData += packStr8(baseURL.text if baseURL is not None else "") # baseURL
                segmentBase = c.find("{urn:mpeg:DASH:schema:MPD:2011}SegmentBase")
                
                if segmentBase is not None:
                    indexRange = segmentBase.get("indexRange", "0-0").split("-") # indexRange
                    indexRangeA = int(indexRange[0])
                    indexRangeB = int(indexRange[1])
                else:
                    indexRangeA = indexRangeB = 0
                    
                init = segmentBase.find("{urn:mpeg:DASH:schema:MPD:2011}Initialization") if segmentBase is not None else None
                
                if init is not None:
                    initRange = init.get("range", "0-0").split("-") # range
                    rangeA = int(initRange[0])
                    rangeB = int(initRange[1])
                else:
                    rangeA = rangeB = 0
                    
                binData += packUInt32(rangeA) # rangeA
                binData += packUInt32(rangeB) # rangeB
                binData += packUInt32(indexRangeA) # indexRangeA
                binData += packUInt32(indexRangeB) # indexRangeB
                
    outputDir = os.path.join(os.getcwd(), "output")
    os.makedirs(outputDir, exist_ok=True)
    outputMPD = os.path.join(outputDir, os.path.splitext(os.path.basename(inputMPD))[0] + ".mpd.ckd")
    
    with open(outputMPD, "wb") as bin:
        bin.write(binData)
        
    print(f"'{outputMPD}' has been serialized!")

except Exception as e:
    print(f"{e}")
