#include "mongoose.h"
#include "http.h"
#include "funkc.h"

// HTTP server event handler function
void ev_handler(struct mg_connection *c, int ev, void *ev_data) {
	struct mg_http_serve_opts opts;
	unsigned short num_of_pixels = spectr_get_num_of_pixels();
	unsigned short* data;
	int len = num_of_pixels * strlen("{\"pixel\":1230},{\"data\":3340}") + 50;
	int IntTime;
	int Gain;
	char buf[100] = "";
	long value;
	struct mg_str v, bin;
	char* message;

	//printf("%d \n", len);


	
	if (ev == MG_EV_HTTP_MSG) {
		struct mg_http_message *hm = (struct mg_http_message *) ev_data;

		if (mg_match(hm->uri, mg_str("/api/hello"), NULL)) {              // REST API call?
			mg_http_reply(c, 200, "", "{%m:%d}\n", MG_ESC("status"), 1);    // Yes. Respond JSON
			return; 
		} 
		
		if (mg_match(hm->uri, mg_str("/spectr/measure"), NULL)) {

			message = (char *)malloc(sizeof(char) * len);
			message[0] = '\0';
			data = (unsigned short *)malloc(sizeof(unsigned short) * num_of_pixels);
			if(spectr_measure(data)<0){
				mg_http_reply(c, 503, "", "{%s}\n", "USB Error\n");
			}
			else{
				spectr_data_to_string(data, num_of_pixels, message);
				//printf("message=[%s]", message);
				mg_http_reply(c, 200, "", "{%s}\n", message);    // Yes. Respond JSON
			}
			free(data);
			free(message);
			return;
		}

		
		if (mg_match(hm->uri, mg_str("/spectr/get/IntTime"), NULL)) {              // REST API call?
			IntTime = spectr_get_IntTime();
			if(IntTime <= 0){
				mg_http_reply(c, 503, "", "{%m}\n", MG_ESC("Error: unsuccesful reading of parameters"));
				printf("Error: unsuccesful reading of parameters\n\n");
				return;
			}
			mg_http_reply(c, 200, "", "{\n\"Integration_Time\":\n{\n%m:%d,\n%m:%d}}\n", MG_ESC("us"), IntTime, MG_ESC("ms"), IntTime/1000);
			printf("IntTime: %d\n\n", IntTime);
			return; 
		} 
		
		if (mg_match(hm->uri, mg_str("/spectr/get/Gain"), NULL)) {              // REST API call?
			Gain = spectr_get_Gain();
			if(Gain <= 0){
				mg_http_reply(c, 503, "", "{%m}\n", MG_ESC("Error: unsuccesful reading of parameters"));
				return;
			}
			
			mg_http_reply(c, 200, "", "{%m:%x}\n", MG_ESC("Gain"), Gain);
			return; 

			/*if(Gain == 0xFF){
				mg_http_printf_chunk(c, "aksjkm \n{%m}\n", MG_ESC("You cannot set Gain for this spectrometer :\("), Gain);
				return;
			}
			return;*/
		} 

		if (mg_match(hm->uri, mg_str("/spectr/set/IntTime"), NULL)) {

			
			
			v = mg_http_var(hm->query, mg_str("x")); 
			sprintf(buf, "%s", strtok(v.buf, " "));
			value = atoi(buf);
			printf("podano value: %d\n", value);
			switch(spectr_set_IntTime(value)){
				case -1:
					mg_http_reply(c, 503, "", "{%m:}\n", MG_ESC("Error: IntTime value too big"));
					break;
				case -2:
					mg_http_reply(c, 503, "", "{%m:}\n", MG_ESC("Error: IntTime value too short"));
					break;
				case -4:
					mg_http_reply(c, 508, "", "{%m:}\n", MG_ESC("Error: Exceeded depth of bruteforce"));
				case 1:
					//mg_http_reply(c, 200, "", "{%m: %d}, {%m: %d}\n", MG_ESC("Podanoooo"), value, MG_ESC("Ustawiono"), spectr_get_IntTime());
					mg_http_reply(c, 200, "", "{%m: %d}\n", MG_ESC("You set: "), value);
					break;
				default:
					mg_http_reply(c, 503, "", "{%m:}\n", MG_ESC("????"));
					break;
			}
			printf("\n");
			return;


			/*struct mg_http_part part;
			size_t ofs = 0;
			while ((ofs = mg_http_next_multipart(hm->body, ofs, &part)) > 0) {
				MG_INFO(("Chunk name: [%.*s] filename: [%.*s] length: %lu bytes",
						(int) part.name.len, part.name.buf, (int) part.filename.len,
						part.filename.buf, (unsigned long) part.body.len));
			}
			mg_http_reply(c, 200, "", "Thank you!");*/
		}

		

		memset(&opts, 0, sizeof(struct mg_http_serve_opts));
		opts.root_dir = ".";//"web_root";
		mg_http_serve_dir(c, ev_data, &opts);
	}
	
}

void http_main() {
  struct mg_mgr mgr;  // Declare event manager
  mg_mgr_init(&mgr);  // Initialise event manager
  mg_http_listen(&mgr, "http://0.0.0.0:8000", ev_handler, NULL);  // Setup listener
  for (;;) {          // Run an infinite event loop
    mg_mgr_poll(&mgr, 1000);
  }
  return;
}

