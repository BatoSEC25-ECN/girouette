#include "pwm_gen.h"

#include "driver/rmt_tx.h"
#include "esp_err.h"

rmt_channel_handle_t tx_chan_handle = NULL;
rmt_encoder_handle_t encoder_handle = NULL;

rmt_tx_channel_config_t tx_chan_config = {
	.gpio_num = 6,
	.clk_src = RMT_CLK_SRC_DEFAULT,
	.mem_block_symbols = 64,
	.resolution_hz = 41700 * 2,
	.trans_queue_depth = 4,
};

rmt_bytes_encoder_config_t encoder_config = {
	.bit0 = {
		.duration0 = 1,
		.level0 = 1,
		.duration1 = 1,
		.level1 = 0
	},
	.bit1 = {
		.duration0 = 1,
		.level0 = 1,
		.duration1 = 1,
		.level1 = 0
	},
	.flags.msb_first = 0,
};

rmt_transmit_config_t tx_config = {
	.loop_count = 8,
};

uint8_t data[2] = {0,1};

void run(void){
	ESP_ERROR_CHECK(rmt_new_tx_channel(&tx_chan_config, &tx_chan_handle));
	ESP_ERROR_CHECK(rmt_new_bytes_encoder(&encoder_config, &encoder_handle));
	ESP_ERROR_CHECK(rmt_enable(tx_chan_handle));
	ESP_ERROR_CHECK(rmt_transmit(tx_chan_handle, encoder_handle, (void *)&data, 2,&tx_config));
}
