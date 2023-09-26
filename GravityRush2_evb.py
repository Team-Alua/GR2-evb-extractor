# Noesis Gravity Rush 2 .evb Extractor

from inc_noesis import *
import noesis
import rapi
import os

debug = False
global_scale = 100

def registerNoesisTypes():

    handle = noesis.register('Gravity Rush 2 evb database', '.evb')
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    if debug:
        noesis.logPopup()  # please comment out when done.
    return 1


def noepyCheckType(data):
    file = NoeBitStream(data)
    if len(data) < 4:
        return 0
    header = file.readBytes(4).decode('ASCII').rstrip("\0")
    if header == 'FBKK':
        return 1
    return 0

# loading the bones!


def noepyLoadModel(data, mdlList):
    global bs
    bs = NoeBitStream(data)

    global bones
    bones = []

    bs.seek(0x38, NOESEEK_ABS)
    file_name = loadStringFromPointer(bs.readUInt())
    print("Filename: " + file_name)
    bs.seek(0x24, NOESEEK_REL)
    num_of_data_chunk = bs.readUInt()
    bs.seek(bs.readUInt() - 4, NOESEEK_REL)
    for dataChunkIndex in range(num_of_data_chunk):
        readDataChunk(bs.readUInt())

    mdl = NoeModel()
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1


def readDataChunk(offset):
    origonal_offset = bs.tell()
    bs.seek(offset - 4, NOESEEK_REL)
    print("Loading Data Chunk at " + hex(bs.tell()))
    # print("Upstream - " + hex(origonal_offset))
    # print("offset - " + hex(offset))
    bs.seek(0x08, NOESEEK_REL)
    name = loadStringFromPointer(bs.readUInt())
    print("Data Chunk name: " + name)
    bs.seek(0x24, NOESEEK_REL)
    subdata_chunk_count = bs.readUInt()
    subindex_chunk_location = bs.tell() + bs.readUInt()
    bs.seek(0x18, NOESEEK_REL)
    # Loading root bone
    rotation = NoeQuat.fromBytes(bs.readBytes(16))
    translation = NoeVec3.fromBytes(bs.readBytes(12)) * NoeVec3((global_scale, global_scale, global_scale))
    bs.seek(4, NOESEEK_REL)
    scale = NoeVec3.fromBytes(bs.readBytes(12))
    boneMat = rotation.toMat43(transposed=1)
    boneMat[3] = translation
    boneIndex = len(bones)
    bones.append(NoeBone(boneIndex, name, boneMat))
    bs.seek(0x18, NOESEEK_REL)
    parent_name = loadStringFromPointer(bs.readUInt())
    print("Parent name: " + parent_name)
    # Loading Sub Index Chunk
    bs.seek(subindex_chunk_location, NOESEEK_ABS)
    for subDataChunkIndex in range(subdata_chunk_count):
        readSubDataChunk(bs.readUInt(), boneIndex)
    bs.seek(origonal_offset, NOESEEK_ABS)
    return


def readSubDataChunk(offset, parentBoneIndex):
    origonal_offset = bs.tell()
    bs.seek(offset - 4, NOESEEK_REL)
    print("Loading Sub Data Chunk at " + hex(bs.tell()))
    bs.seek(0x08, NOESEEK_REL)
    name = loadStringFromPointer(bs.readUInt())
    print("Sub Data Chunk name: " + name)
    bs.seek(0x0C, NOESEEK_REL)
    bs.seek(bs.readUInt() - 4, NOESEEK_REL)
    # Loading bone
    rotation = NoeQuat.fromBytes(bs.readBytes(16))
    translation = NoeVec3.fromBytes(bs.readBytes(12)) * NoeVec3((global_scale, global_scale, global_scale))
    bs.seek(4, NOESEEK_REL)
    scale = NoeVec3.fromBytes(bs.readBytes(12))
    boneMat = rotation.toMat43(transposed=1)
    boneMat[3] = translation
    #boneMat *= bones[parentBoneIndex].getMatrix() 
    boneIndex = len(bones)
    bones.append(NoeBone(boneIndex, name, boneMat, None, parentBoneIndex))

    bs.seek(origonal_offset, NOESEEK_ABS)
    return


def loadStringFromPointer(offset):
    origonal_offset = bs.tell()
    bs.seek(offset - 4, NOESEEK_REL)
    string = bs.readBytes(64).split(b'\x00')[0].decode('UTF8')
    bs.seek(origonal_offset, NOESEEK_ABS)
    return string
