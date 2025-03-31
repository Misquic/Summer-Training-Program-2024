#include "mongoose.h"
#include "http1.h"
//#include "specu1a.h"
//#include "funkc.h"

// HTTP server event handler function
void ev_handler(struct mg_connection *c, int ev, void *ev_data) {
	struct mg_http_serve_opts opts;
	
	if (ev == MG_EV_HTTP_MSG) {
		struct mg_http_message *hm = (struct mg_http_message *) ev_data;
		if (mg_match(hm->uri, mg_str("/api/hello"), NULL)) {              // REST API call?
			mg_http_reply(c, 200, "", "{%m:%d}\n", MG_ESC("status"), 1);    // Yes. Respond JSON
			return; 
		} 
		if(mg_match(hm->uri, mg_str("/spectr/display"), NULL)) {
			//measure_target(HANDLE DeviceHandle, HANDLE PipeHandle);
			mg_http_reply(c, 200, "", "{%m:%d}\n", MG_ESC("in progress"), 1);    // Yes. Respond JSON
			return;
		}

		memset(&opts, 0, sizeof(struct mg_http_serve_opts));
		opts.root_dir = ".";
		mg_http_serve_dir(c, hm, &opts);
	}
}

void http_main(void) {
  struct mg_mgr mgr;  // Declare event manager
  mg_mgr_init(&mgr);  // Initialise event manager
  mg_http_listen(&mgr, "http://0.0.0.0:8000", ev_handler, NULL);  // Setup listener
  for (;;) {          // Run an infinite event loop
    mg_mgr_poll(&mgr, 1000);
  }
  return;
}

