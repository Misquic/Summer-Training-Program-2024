// spektr1.cpp : Defines the entry point for the console application.
/* whole application is for particular specrtometer,
serial num 707H5201, used in IMIF */


#include "stdafx.h"

#include "http.h"

int _tmain(int argc, _TCHAR* argv[])
{	

	spectr_open_device_productid(); // used to initialise communication and get Handles to spectrometer
	UNIT_INFORMATION Information;
	USB_ReadUnitInformation(DeviceHandle, &Information); // used to get informations like pixels
	num_of_pixels = 128 * (1 << (Information.UnitID[1] - 0x30)); // "Global variable" for func.* and spectr1.cpp, 
	http_main();


	USB_ClosePipe(PipeHandle);
	USB_CloseDevice(DeviceHandle);
	return 0;
}




