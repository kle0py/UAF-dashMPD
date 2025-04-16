# hello :)
print("Welcome to the UbiArt Framework \033[34m.mpd.ckd\033[0m file \033[1muncooker\033[0m!")
print("This is a tool made by \033[4mKleopy\033[0m")
print("Code version: 1\n")

import os, subprocess, struct, xml.etree.ElementTree as ET, xml.dom.minidom

def unpackUInt8():
    value = struct.unpack(">B", byte.read(1))[0]
    return value

def unpackUInt32():
    value = struct.unpack(">I", byte.read(4))[0]
    return value

def unpackFloat32():
    value = struct.unpack(">f", byte.read(4))[0]
    return value

def unpackStr8():
    length = struct.unpack(">I", byte.read(4))[0]
    text = byte.read(length).decode("utf8")
    return text

def beautifyFloat(val):
    if isinstance(val, list):
        return [beautifyFloat(v) for v in val]
    if val % 1 == 0:
        return int(val)
    return round(val, 6)

unpackDashType = {
    0: "static"
}

try:
    inputMPD = input("dashMPD file (\033[34m.mpd.ckd\033[0m)\nInput: ").strip('"')
    with open(inputMPD, "rb") as byte:
        print("\nLog:")
        flag = unpackUInt32()
        type = unpackUInt8(); dashType = unpackDashType.get(type, None)
        mediaPresentationDuration = unpackFloat32()
        minBufferTime = unpackFloat32()
        periodNumber = unpackUInt32()
        
        mpd = ET.Element("MPD", {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xmlns": "urn:mpeg:DASH:schema:MPD:2011",
            "xsi:schemaLocation": "urn:mpeg:DASH:schema:MPD:2011",
            "type": dashType,
            "mediaPresentationDuration": f"PT{beautifyFloat(mediaPresentationDuration)}S",
            "minBufferTime": f"PT{beautifyFloat(minBufferTime)}S",
            "profiles": "urn:webm:dash:profile:webm-on-demand:2012"
        })
        
        for a in range(periodNumber):
            id = unpackUInt32()
            start = unpackFloat32()
            duration = unpackFloat32()
            adaptationSetNumber = unpackUInt32()
            
            period = ET.SubElement(mpd, "Period", {
                "id": str(id),
                "start": f"PT{beautifyFloat(start)}S",
                "duration": f"PT{beautifyFloat(duration)}S"
            })
            
            for b in range(adaptationSetNumber):
                id = unpackUInt32()
                mimeType = unpackStr8()
                codecs = unpackStr8()
                maxWidth = unpackUInt32()
                maxHeight = unpackUInt32()
                byte.read(4) # Unknown
                subsegmentAlignment = unpackUInt32()
                subsegmentStartsWithSAP = unpackUInt8()
                bitstreamSwitching = unpackUInt8()
                representationNumber = unpackUInt32()
                
                if subsegmentAlignment == 0:
                    subsegmentAlignment = "false"                
                elif subsegmentAlignment == 1:
                    subsegmentAlignment = "true"
                else:
                    print("\033[31mThere is something wrong with 'subsegmentAlignment'.\033[0m")
                
                if bitstreamSwitching == 0:
                    bitstreamSwitching = "false"                
                elif bitstreamSwitching == 1:
                    bitstreamSwitching = "true"
                else:
                    print("\033[31mThere is something wrong with 'bitstreamSwitching'.\033[0m")
                
                adaptationSet = ET.SubElement(period, "AdaptationSet", {
                    "id": str(id),
                    "mimeType": mimeType,
                    "codecs": codecs,
                    "lang": "eng",
                    "maxWidth": str(maxWidth),
                    "maxHeight": str(maxHeight),
                    "subsegmentAlignment": subsegmentAlignment.lower(),
                    "subsegmentStartsWithSAP": str(subsegmentStartsWithSAP),
                    "bitstreamSwitching": bitstreamSwitching.lower()
                })
                
                representationList = []
                for c in range(representationNumber):
                    id = unpackUInt32()
                    bandwidth = unpackUInt32()
                    baseURL = unpackStr8()
                    rangeA = unpackUInt32()
                    rangeB = unpackUInt32()
                    indexRangeA = unpackUInt32()
                    indexRangeB = unpackUInt32()
                    
                    representation = ET.SubElement(adaptationSet, "Representation", {
                        "id": str(id),
                        "bandwidth": str(bandwidth)
                    })
                    
                    ET.SubElement(representation, "BaseURL").text = baseURL
                    
                    segmentBase = ET.SubElement(representation, "SegmentBase", {
                        "indexRange": f"{indexRangeA}-{indexRangeB}"
                    })
                    
                    ET.SubElement(segmentBase, "Initialization", {
                        "range": f"{rangeA}-{rangeB}"
                    })
                    
                    representationList.append(representation)
                    
    outputDir = os.path.join(os.getcwd(), "output")
    os.makedirs(outputDir, exist_ok=True)
    outputMPD = os.path.join(outputDir, os.path.splitext(os.path.basename(inputMPD))[0])
    strXML = xml.dom.minidom.parseString(ET.tostring(mpd, encoding="utf-8")).toprettyxml(indent="\t")
    strXML = strXML.replace('<?xml version="1.0" ?>', '<?xml version="1.0"?>')
    
    with open(outputMPD, "w", encoding="utf-8") as xml:
        xml.write(strXML)
        
    print(f"'{outputMPD}' \033[32mhas been successfully uncooked!\033[0m")
    
except Exception as e:
    print(f"\033[31mERROR:\033[0m {e}")
    