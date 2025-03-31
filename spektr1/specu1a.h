/* =================================================================================

  Copyright (c) Hamamatsu Photonics K.K.

    Project  : specu1a
    --------------------------------------------------------------------------------
    FileName : specu1a.h
    Abstract :

================================================================================= */

#ifndef _SPEC_U1A_H
#define _SPEC_U1A_H

#ifdef  __cplusplus
extern  "C" {
#endif

#include    <windows.h>
#include    "usb100.h"
#include    "specudef.h"

// ���j�b�g�ŗL�̏����i�[����\����
typedef struct _tag_UnitInfo {
    UCHAR UnitID[8];
    UCHAR SensorName[16];
    UCHAR SerialNumber[8];
    UCHAR Reserved[8];
    USHORT WaveLengthUpper;
    USHORT WaveLengthLower;
} UNIT_INFORMATION, *PUNIT_INFORMATION;


// ���j�b�g�ɓn���p�����[�^���i�[����\����
typedef struct _tag_UnitParam {
    ULONG IntegrationTime;
    UCHAR Gain;
    UCHAR TriggerEdge;
    UCHAR TriggerMode;
    UCHAR Reserved;
} UNIT_PARAMETER, *PUNIT_PARAMETER;


/*----------------------------------------------------------------------

    �I�[�v���E�N���[�Y�n

----------------------------------------------------------------------*/

HANDLE WINAPI USB_OpenDevice(
    USHORT ProductID
    );

HANDLE WINAPI USB_OpenTargetDevice(
    CHAR *UnitID
    );

void WINAPI USB_CloseDevice(
    HANDLE DeviceHandle
    );

USHORT WINAPI USB_CheckDevice(
    HANDLE DeviceHandle
    );

HANDLE WINAPI USB_OpenPipe(
    HANDLE DeviceHandle
    );

void WINAPI USB_ClosePipe(
    HANDLE PipeHandle
    );


/*----------------------------------------------------------------------

    ���j�b�g�R���g���[���n

----------------------------------------------------------------------*/

USHORT WINAPI USB_GetParameter(
    HANDLE DeviceHandle,
    PUNIT_PARAMETER Param
    );

USHORT WINAPI USB_SetParameter(
    HANDLE DeviceHandle,
    PUNIT_PARAMETER Param
    );

USHORT WINAPI USB_SetEepromDefaultParameter(
    HANDLE DeviceHandle,
    UCHAR Set
    );

USHORT WINAPI USB_ReadUnitInformation(
    HANDLE DeviceHandle,
    PUNIT_INFORMATION Information
    );

USHORT WINAPI USB_WriteUnitInformation(
    HANDLE DeviceHandle,
    PUNIT_INFORMATION Information,
    UCHAR mark
    );

USHORT WINAPI USB_ReadCalibrationValue(
    HANDLE DeviceHandle,
    double *DataArray
    );

USHORT WINAPI USB_WriteCalibrationValue(
    HANDLE DeviceHandle,
    double *DataArray,
    UCHAR mark
    );

USHORT WINAPI USB_UserReadEEPROM(
    HANDLE DeviceHandle,
    USHORT Address,
    USHORT DataLength,
    UCHAR *Buffer
    );

USHORT WINAPI USB_UserWriteEEPROM(
    HANDLE DeviceHandle,
    USHORT Address,
    USHORT DataLength,
    UCHAR *Buffer
    );


/*----------------------------------------------------------------------

    �f�[�^�擾�n

----------------------------------------------------------------------*/

USHORT WINAPI USB_GetSensorData(
    HANDLE DeviceHandle,
    HANDLE PipeHandle,
    USHORT PixelSize,
    USHORT *Buffer
    );


/*----------------------------------------------------------------------

    �V�X�e���n�i�o�b�n�j

----------------------------------------------------------------------*/

void WINAPI USB_GetDllVersion(
    UCHAR *Version
    );

void WINAPI USB_GetSysVersion(
    UCHAR *Version
    );


/*----------------------------------------------------------------------

    X-NIR ��p�֐�

----------------------------------------------------------------------*/

USHORT WINAPI USB_GetStatusRequest(
    HANDLE DeviceHandle,
    UCHAR *Flag
    );


#ifdef  __cplusplus
}
#endif

#endif