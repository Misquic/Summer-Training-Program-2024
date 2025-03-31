#ifndef _FUNKC_H
#define _FUNKC_H



#ifdef __cplusplus
extern "C" {
#endif 
///////////////////////////////////////////////////////////////

void spectr_open_device_productid(void);

int spectr_measure(unsigned short*);

unsigned short spectr_get_num_of_pixels(void);

void spectr_data_to_string(unsigned short*, int, char*);

int spectr_get_IntTime();

int spectr_get_Gain();

int spectr_set_IntTime(long value);

///////////////////////////////////////////////////////////////
#ifdef __cplusplus
}
#endif

#endif
