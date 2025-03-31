#include "stdafx.h"

/* needed to initialise communication with spectrometer, used only once, DeviceHandle and PipeHandle used as global variables, not used by http client */
void spectr_open_device_productid(void) {
	long id = strtol("2909", NULL, 16);

	/* Pipe Handle */
	DeviceHandle = USB_OpenDevice((unsigned short)id);
	if (DeviceHandle == INVALID_HANDLE_VALUE) {
		printf("[ERROR] USB_OpenDevice\n");
		return;
	}
	printf("DeviceHandle OK\n");

	/* Pipe Handle */
	PipeHandle = USB_OpenPipe(DeviceHandle);
	if (PipeHandle == INVALID_HANDLE_VALUE) {
		printf("[ERROR] USB_OpenPipe\n");
		USB_CloseDevice(DeviceHandle);
		return;
	}
	printf("PipeHandle OK\n\n");
	return;
}


/* get data from spectrometer to array buffer, length is number of pixels*/
int spectr_measure(unsigned short* Buffer){
	unsigned short nResult;
	unsigned short pixel;

	pixel = spectr_get_num_of_pixels();	/* pixel number */
	nResult = USB_GetSensorData(DeviceHandle, PipeHandle, pixel, Buffer);
	if (nResult != USBDEV_SUCCESS) {
		printf("[ERROR] USB_GetSensorData : code = %d\n", nResult);
		return -1;
	}

	return 0;
}

/* self explanatory */
unsigned short spectr_get_num_of_pixels(void){
	return (unsigned short)num_of_pixels;
}

/* function that writes data to string to display it later*/
void spectr_data_to_string(unsigned short* data, int num_of_pixels, char* message){
	char str_out[100] = "";
	char str[100] = "";
	int i;

	for(i = 0; i < num_of_pixels; i++){
		sprintf(str, "%d%s%s", data[i], (i== num_of_pixels - 1) ? "" : "," , ((i+1)%10) ? "": "\n" );
		strcat(message, str);
	}
	return;
}

//TO DO gettery do Integration time, Gain,
//settery do Integration time, Gain


/* Integration time in microseconds, default is 100 000 us */
int spectr_get_IntTime(){
	unsigned short nResult;
	UNIT_PARAMETER Parameters;

	nResult = USB_GetParameter(DeviceHandle, &Parameters);
	if(nResult != USBDEV_SUCCESS){
		return -1;
	}
	return Parameters.IntegrationTime;
}


/* Gain:
	00 - low gain
	01 - high gain
	FF - gain switching function is unavilable */
int spectr_get_Gain(){
	unsigned short nResult;
	UNIT_PARAMETER Parameters;

	nResult = USB_GetParameter(DeviceHandle, &Parameters);
	if(nResult != USBDEV_SUCCESS){
		return -1;
	}
	return Parameters.Gain;
}

//UNIT_PARAMETER Parameters;

int spectr_set_IntTime(long value){ 
	// the ugliest function i've written, sorry,
	//but it really works as intended, reapeted code,
	//but thats to check if passed value is good before bruteforce

	unsigned short nResult, nResult2;
	int depth = 1; // 1 because we always try at least once if value isnt already set
	UNIT_PARAMETER Parameters;

	nResult2 = USB_GetParameter(DeviceHandle, &Parameters);
	printf("jest %d, ", Parameters.IntegrationTime);
	if(value == Parameters.IntegrationTime){
		printf("\n");
		return 1;
	}

	Parameters.IntegrationTime = value;
	printf("przypisanie %d, ", Parameters.IntegrationTime);
	Parameters.Gain = 0xff;
	Parameters.TriggerEdge = 0xff;
	Parameters.TriggerMode = 0;
	nResult = USB_SetParameter(DeviceHandle, &Parameters);
	nResult2 = USB_GetParameter(DeviceHandle, &Parameters);
	printf("jest %d, ", Parameters.IntegrationTime);
	if(value == Parameters.IntegrationTime){ // if value is set in the 1st try
		printf("\n");
		return 1;
	}
	switch(nResult){ //checking if passed value isnt too small or too big, before going to bruteforce
		case USBDEV_TIME_OVER_ERROR:
			return -1;
		case USBDEV_TIME_UNDER_ERROR:
			return -2;
		default:
			break;
	}



	nResult2 = USB_GetParameter(DeviceHandle, &Parameters);
	printf("ustawienie %d \n", Parameters.IntegrationTime);	

	while(Parameters.IntegrationTime != value && depth != 40){ //maximum 40 trials bruteforce, bc spectrometer acts weird
		Parameters.IntegrationTime = value;
		printf("przypisanie %d, ", Parameters.IntegrationTime);
		Parameters.Gain = 0xff;
		Parameters.TriggerEdge = 0xff;
		Parameters.TriggerMode = 0;
		nResult = USB_SetParameter(DeviceHandle, &Parameters);
		nResult2 = USB_GetParameter(DeviceHandle, &Parameters);
		printf("ustawienie %d \n", Parameters.IntegrationTime);	
		
		depth++;
	}
	if(depth>=40){
		return -4;
	}

	switch(nResult){
		case USBDEV_SUCCESS:
			printf("OK\n");
			return 1;
		default:
			printf("status %d\n", nResult);
			return -3;
	}

	return 1;
}