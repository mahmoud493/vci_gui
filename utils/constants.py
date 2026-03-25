"""utils/constants.py"""
APP_NAME    = "VCI PRO"
APP_VERSION = "1.0.0"
ORG_NAME    = "VCI"

# UDS Service IDs
SID_DIAGNOSTIC_SESSION_CONTROL = 0x10
SID_ECU_RESET                  = 0x11
SID_READ_DTC                   = 0x19
SID_READ_DATA_BY_ID            = 0x22
SID_WRITE_DATA_BY_ID           = 0x2E
SID_IO_CONTROL                 = 0x2F
SID_ROUTINE_CONTROL            = 0x31
SID_REQUEST_DOWNLOAD           = 0x34
SID_TRANSFER_DATA              = 0x36
SID_TRANSFER_EXIT              = 0x37
SID_SECURITY_ACCESS            = 0x27
SID_COMMUNICATION_CONTROL      = 0x28
SID_TESTER_PRESENT             = 0x3E

# UDS Sessions
SESSION_DEFAULT     = 0x01
SESSION_PROGRAMMING = 0x02
SESSION_EXTENDED    = 0x03

# NRC codes
NRC = {
    0x10: "generalReject",
    0x11: "serviceNotSupported",
    0x12: "subFunctionNotSupported",
    0x13: "incorrectMessageLengthOrInvalidFormat",
    0x14: "responseTooLong",
    0x21: "busyRepeatRequest",
    0x22: "conditionsNotCorrect",
    0x24: "requestSequenceError",
    0x25: "noResponseFromSubnetComponent",
    0x26: "failurePreventsExecutionOfRequestedAction",
    0x31: "requestOutOfRange",
    0x33: "securityAccessDenied",
    0x35: "invalidKey",
    0x36: "exceededNumberOfAttempts",
    0x37: "requiredTimeDelayNotExpired",
    0x70: "uploadDownloadNotAccepted",
    0x71: "transferDataSuspended",
    0x72: "generalProgrammingFailure",
    0x73: "wrongBlockSequenceCounter",
    0x78: "requestCorrectlyReceivedResponsePending",
    0x7E: "subFunctionNotSupportedInActiveSession",
    0x7F: "serviceNotSupportedInActiveSession",
}

# Standard DIDs
DID_VIN           = 0xF190
DID_ECU_SERIAL    = 0xF18C
DID_SW_VERSION    = 0xF189
DID_HW_VERSION    = 0xF191
DID_SUPPLIER_ID   = 0xF18A

# Scan address ranges
UDS_BROADCAST_ADDR = 0x7DF
UDS_ADDR_RANGE_STD = list(range(0x700, 0x780))

# Timeouts
T_REQUEST_MS      = 1000
T_SESSION_MS      = 5000
T_P2_MS           = 50
T_P2_EXT_MS       = 5000

# DoIP
DOIP_UDP_PORT     = 13400
DOIP_TCP_PORT     = 13400
DOIP_VERSION      = 0x02

# GUI
LOG_MAX_LINES     = 2000
FRAME_TABLE_MAX   = 5000
LIVE_DATA_UPDATE_MS = 100
