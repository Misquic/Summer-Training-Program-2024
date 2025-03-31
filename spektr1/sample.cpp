/* =================================================================================

  Copyright (c) 2007 Hamamatsu Photonics K.K.

	Project  : Minispectrometer console application (sample)
	--------------------------------------------------------------------------------
	FileName : sample.c
	Abstract :
	Attention: Please add error processing if necessary.

================================================================================= */

#include <stdio.h>
#include "specu1a.h"

HANDLE DeviceHandle;	/* device handle */
HANDLE PipeHandle;		/* pipe handle */

int open_device_productid(void);
int open_device_unitid(void);

int read_UnitInformation(HANDLE DeviceHandle);
int get_Parameter(HANDLE DeviceHandle);
int read_CalibrationValue(HANDLE DeviceHandle);

int write_UnitInformation(HANDLE DeviceHandle);
int set_Parameter(HANDLE DeviceHandle);
int write_CalibrationValue(HANDLE DeviceHandle);

int measure_target(HANDLE DeviceHandle, HANDLE PipeHandle);
int measure_temperature(HANDLE DeviceHandle);

void print_Menu(void);

/*----------------------------------------------------------------------
	Main loop
----------------------------------------------------------------------*/
int main(void)
{
	char cmd;
	int iResult;
	int loop = 1;

	printf("Hamamatsu Minispectrometer sample application\n");
	printf("(0) Product ID or (1) Unit ID\n >");
	scanf("%s", &cmd);
	switch (cmd) {
		case '0':
			iResult = open_device_productid();
			break;
		case '1':
			iResult = open_device_unitid();
			break;
		default:
			iResult = 1;
			break;
	}
	if (iResult) return 1;

	print_Menu();

	while (loop == 1) {
		printf(">");
		scanf("%s", &cmd);
		switch (toupper(cmd)) {
			case '0':
				print_Menu();
				break;
			case '1':
				iResult = read_UnitInformation(DeviceHandle);
				break;
			case '2':
				iResult = write_UnitInformation(DeviceHandle);
				break;
			case '3':
				iResult = get_Parameter(DeviceHandle);
				break;
			case '4':
				iResult = set_Parameter(DeviceHandle);
				break;
			case '5':
				iResult = read_CalibrationValue(DeviceHandle);
				break;
			case '6':
				iResult = write_CalibrationValue(DeviceHandle);
				break;
			case 'M':
				iResult = measure_target(DeviceHandle, PipeHandle);
				break;
			case 'Q':
				loop = 0;
				break;
			default:
				break;
		}
	}
	USB_ClosePipe(PipeHandle);
	USB_CloseDevice(DeviceHandle);

	printf("Exit");

	return 0;
}


/*----------------------------------------------------------------------
	Menu
----------------------------------------------------------------------*/
void print_Menu(void)
{
	puts(
		"----------\n"
		"  Menu             (0) Menu\n"
		"  Unit Information (1) Read   (2) Write\n"
		"  Parameters       (3) Get    (4) Set\n"
		"  Calibration      (5) Read   (6) Write\n"
		"  Measure          (M) Measure\n"
		"  Quit             (Q) Quit\n"
	);
}


/*----------------------------------------------------------------------
	Device handle
----------------------------------------------------------------------*/
int open_device_productid(void)
{
	char key[255], proid[4];
	long id;

	printf("Product ID ?\n >");
	scanf("%s", key);
	if (strncmp(key, "290", 3)) {
		printf("Product ID : Invalid value\nExit");
		return 1;
	}

	/* Device Handle
		Ex. "2905"->0x2905 */
	strncpy(proid, key, 4);
	id = strtol(proid, NULL, 16);
	DeviceHandle = USB_OpenDevice((unsigned short)id);
	if (DeviceHandle == INVALID_HANDLE_VALUE) {
		printf("[ERROR] USB_OpenDevice\n");
		return 1;
	}
	printf("DeviceHandle OK\n");

	/* Pipe Handle */
	PipeHandle = USB_OpenPipe(DeviceHandle);
	if (PipeHandle == INVALID_HANDLE_VALUE) {
		printf("[ERROR] USB_OpenPipe\n");
		USB_CloseDevice(DeviceHandle);
		return 1;
	}
	printf("PipeHandle OK\n\n");

	return 0;
}

int open_device_unitid(void)
{
	char key[255], unitid[9];

	printf("Unit ID ?\n >");
	scanf("%s", key);
	strncpy(unitid, key, 8);
	DeviceHandle = USB_OpenTargetDevice(unitid);
	if (DeviceHandle == INVALID_HANDLE_VALUE) {
		printf("[ERROR] USB_OpenTargetDevice\n");
		return 1;
	}
	printf("DeviceHandle OK\n");

	/* Pipe Handle */
	PipeHandle = USB_OpenPipe(DeviceHandle);
	if (PipeHandle == INVALID_HANDLE_VALUE) {
		printf("[ERROR] USB_OpenPipe\n");
		USB_CloseDevice(DeviceHandle);
		return 1;
	}
	printf("PipeHandle OK\n\n");

	return 0;
}


/*----------------------------------------------------------------------
	Unit information
----------------------------------------------------------------------*/
int read_UnitInformation(HANDLE DeviceHandle)
{
	unsigned short nResult;
	UNIT_INFORMATION Information;

	nResult = USB_ReadUnitInformation(DeviceHandle, &Information);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_ReadUnitInformation : code = %d\n", nResult);
		return 1;
	}
	printf("Unit Information\n");
	printf("  Unit ID          : %.*s\n", 8, Information.UnitID);
	printf("  Sensor Name      : %.*s\n", 16, Information.SensorName);
	printf("  Serial Number    : %.*s\n", 8, Information.SerialNumber);
	printf("  Wavelength Lower : %d\n", Information.WaveLengthLower);
	printf("  Wavelength Upper : %d\n", Information.WaveLengthUpper);
	printf("\n");

	return 0;
}

int write_UnitInformation(HANDLE DeviceHandle)
{
	unsigned short nResult;
	UNIT_INFORMATION Information;
	char serial[8+1];


	/* Unit Information */
	nResult = USB_ReadUnitInformation(DeviceHandle, &Information);
	if (nResult != USBDEV_SUCCESS) {
		return 1;
	}
	printf("Seiral Number(ASCII 8byte)\n >");
	scanf("%s", serial);
	sprintf((char *)Information.SerialNumber, "%.*s", 8, serial);

	nResult = USB_WriteUnitInformation(DeviceHandle, &Information, 0xAA);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_WriteUnitInformation : code = %d\n", nResult);
		return 1;
	}

	return 0;
}


/*----------------------------------------------------------------------
	Parameters
----------------------------------------------------------------------*/
int get_Parameter(HANDLE DeviceHandle)
{
	unsigned short nResult;
	UNIT_PARAMETER Param;

	nResult = USB_GetParameter(DeviceHandle, &Param);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_GetParameter : code = %d\n", nResult);
		return 1;
	}
	printf("Parameters\n");
	printf("  IntegrationTime : %d us\n", Param.IntegrationTime);
	printf("  Gain            : %X\n", Param.Gain);
	printf("  Trigger Edge    : %X\n", Param.TriggerEdge);
	printf("  Trigger Mode    : %X\n", Param.TriggerMode);
	printf("\n");

	return 0;
}

int set_Parameter(HANDLE DeviceHandle)
{
	unsigned short nResult;
	UNIT_PARAMETER Param;
	char num[10];

	nResult = USB_GetParameter(DeviceHandle, &Param);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_GetParameter : code = %d\n", nResult);
		return 1;
	}
	printf("Integration Time :[us]\n >");
	scanf("%s", num);
	Param.IntegrationTime = atoi(num);

	printf("Gain : Low(0)/High(1)/NO_FUNCTION(255)\n >");
	scanf("%s", num);
	Param.Gain = atoi(num);

	printf("Trigger Edge : Rising(0)/Falling(1)/NO_FUNCTION(255)\n >");
	scanf("%s", num);
	Param.TriggerEdge = atoi(num);

	printf("Trigger Mode : Internal(0)/Asynchronous(1)/Synchronous(2)\n >");
	scanf("%s", num);
	Param.TriggerMode = atoi(num);

	nResult = USB_SetParameter(DeviceHandle, &Param);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_SetParameter : code = %d\n", nResult);
		return 1;
	}

	return 0;
}


/*----------------------------------------------------------------------
	Calibration coefficients
----------------------------------------------------------------------*/
int read_CalibrationValue(HANDLE DeviceHandle)
{
	unsigned short nResult;
	double DataArray[6];

	nResult = USB_ReadCalibrationValue(DeviceHandle, DataArray);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_ReadCalibrationValue : code = %d\n", nResult);
		return 1;
	}
	printf("Calibration coefficients\n");
	printf("  A  : %E\n", DataArray[0]);
	printf("  B1 : %E\n", DataArray[1]);
	printf("  B2 : %E\n", DataArray[2]);
	printf("  B3 : %E\n", DataArray[3]);
	printf("  B4 : %E\n", DataArray[4]);
	printf("  B5 : %E\n", DataArray[5]);
	printf("\n");

	return 0;
}

int write_CalibrationValue(HANDLE DeviceHandle)
{
	unsigned short nResult;
	double DataArray[6];
	char num[20];

	nResult = USB_ReadCalibrationValue(DeviceHandle, DataArray);
	if (nResult != USBDEV_SUCCESS) {
		return 1;
	}

	printf("Calibration coefficients (double)\n");

	printf("A  >");
	scanf("%s", num);
	DataArray[0] = atof(num);

	printf("B1 >");
	scanf("%s", num);
	DataArray[1] = atof(num);

	printf("B2 >");
	scanf("%s", num);
	DataArray[2] = atof(num);

	printf("B3 >");
	scanf("%s", num);
	DataArray[3] = atof(num);

	printf("B4 >");
	scanf("%s", num);
	DataArray[4] = atof(num);

	printf("B5 >");
	scanf("%s", num);
	DataArray[5] = atof(num);

	nResult = USB_WriteCalibrationValue(DeviceHandle, DataArray, 0xAA);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_WriteCalibrationValue : code = %d\n", nResult);
		return 1;
	}

	return 0;
}


/*----------------------------------------------------------------------
	Measure
----------------------------------------------------------------------*/
int measure_target(HANDLE DeviceHandle, HANDLE PipeHandle)
{
	unsigned short nResult;
	UNIT_INFORMATION Information;
	unsigned short pixel;
	unsigned short *Buffer;
	int i, j = 1;

	nResult = USB_ReadUnitInformation(DeviceHandle, &Information);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_ReadUnitInformation : code = %d\n", nResult);
		return 1;
	}
	pixel = 128 * (1 << (Information.UnitID[1] - 0x30));	/* pixel number */
	if (pixel > 2048) {
		return 1;
	}
	Buffer = (unsigned short *)malloc(sizeof(unsigned short) * pixel);

	nResult = USB_GetSensorData(DeviceHandle, PipeHandle, pixel, Buffer);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_GetSensorData : code = %d\n", nResult);
		free(Buffer);
		return 1;
	}

	for (i = 0; i < pixel; i++) {
		if (!(i%10)) {
			printf("\npixel(%3d-) ", i+1 );
		}
		printf("%5d ", *(Buffer + i));
	}
	printf("\n");
	free(Buffer);
	return 0;
}

