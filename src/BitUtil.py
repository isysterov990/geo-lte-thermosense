def testBit(int_type, offset):
    """Returns a nonzero result, 2**offset, if the bit at 'offset' is one. (offset=0 is the first bit)"""
    mask = 1 << offset
    return(int_type & mask)

def readBit(int_type, offset):
    mask = (int_type >> (offset))&1
    return mask

def setBit(int_type, offset):
    """Returns an integer with the bit at 'offset' set to 1. (offset=0 is the first bit)"""
    mask = 1 << offset
    return(int_type | mask)


def clearBit(int_type, offset):
    """Returns an integer with the bit at 'offset' cleared. (offset=0 is the first bit)"""
    mask = ~(1 << offset)
    return(int_type & mask)


def toggleBit(int_type, offset):
    """Returns an integer with the bit at 'offset' inverted, 0 -> 1 and 1 -> 0. (offset=0 is the first bit)"""
    mask = 1 << offset
    return(int_type ^ mask)
