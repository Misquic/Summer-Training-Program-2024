/* =================================================================================

  Copyright (c) 2007 Hamamatsu Photonics K.K.

	Project  : specudef
	--------------------------------------------------------------------------------
	FileName : specudef.h
	Abstract :

================================================================================= */

#ifndef	_SPEC_UDEF_H
#define	_SPEC_UDEF_H

/*----------------------------------------------------------------------

	Error code

----------------------------------------------------------------------*/

#define		USBDEV_SUCCESS				      (0)
#define		USBDEV_INVALID_HANDLE			  (1)
#define		USBDEV_UNSUCCESS			      (2)
#define		USBDEV_INVALID_VALUE			  (3)

#define		USBDEV_CHECK_NORMAL			    (11)
#define		USBDEV_CHECK_INVALID			  (12)
#define		USBDEV_CHECK_REMOVE			    (13)

#define		USBDEV_BULK_SIZE_ERROR			(20)
#define		USBDEV_BULK_READ_ERROR			(21)
#define		USBDEV_BULK_NOT_UPDATED			(22)

#define   USBDEV_ADC_OUTPUT_ERROR     (30)

#define		USBDEV_TIME_OVER_ERROR			(101)
#define		USBDEV_TIME_UNDER_ERROR			(102)
#define		USBDEV_TIME_SET_ERROR			  (103)
#define		USBDEV_SET_GAIN_ERROR			  (106)
#define		USBDEV_SET_TRIGGER_ERROR		(108)

#define		USBDEV_RW_EEP_ADDR_ERROR		(201)
#define		USBDEV_RW_EEP_SIZE_ERROR		(202)
#define		USBDEV_RW_EEP_OVER_ERROR		(203)
#define		USBDEV_RW_EEP_ERROR			    (204)


/*----------------------------------------------------------------------

	Symbol

----------------------------------------------------------------------*/
#define		NO_FUNCTION		    0xFF

#define		GAIN_LOW		      0x00
#define		GAIN_HIGH		      0x01

#define		RISING_EDGE		    0x00
#define		FALLING_EDGE		  0x01

#define		INT_TRIGGER		    0x00
#define		EXT_ASYNCHRONOUS	0x01
#define		EXT_SYNCHRONOUS		0x02
#define		EXT_SYNCHRONOUS_B	0x03


#endif