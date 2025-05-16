#include <stdio.h>

#include "esp_rom_sys.h"
#include "driver/ledc.h"
#include "driver/gpio.h"

#define LEDC_TIMER        LEDC_TIMER_0
#define LEDC_MODE         LEDC_LOW_SPEED_MODE
#define LEDC_CHANNEL      LEDC_CHANNEL_0
#define LEDC_DUTY_RES     LEDC_TIMER_8_BIT
#define LEDC_DUTY         128
#define LEDC_FREQUENCY    41700

#define BURST_NUM         8
#define BURST_DELAY_MICRO (int)((((BURST_NUM - 1) * 1000 * 1000) / LEDC_FREQUENCY) + (int)(((1000 * 1000) / LEDC_FREQUENCY) * 0.5))

#define PWM_PIN           GPIO_NUM_6
#define TRIGGER_PIN       GPIO_NUM_4

void sendBursts (void);

void app_main (void)
{
    // PWM setup
    ledc_timer_config_t ledc_timer = {
        .speed_mode = LEDC_MODE,
        .duty_resolution = LEDC_DUTY_RES,
        .timer_num = LEDC_TIMER,
        .freq_hz = LEDC_FREQUENCY,
        .clk_cfg = LEDC_AUTO_CLK
    };

    ledc_channel_config_t ledc_channel = {
        .speed_mode = LEDC_MODE,
        .channel = LEDC_CHANNEL,
        .timer_sel = LEDC_TIMER,
        .intr_type = LEDC_INTR_DISABLE,
        .gpio_num = PWM_PIN,
        .duty = 0,
        .hpoint = 0
    };

    gpio_config_t gpio_conf = {
        .pin_bit_mask = (0x1u << TRIGGER_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };

    ESP_ERROR_CHECK(ledc_timer_config(&ledc_timer));
    ESP_ERROR_CHECK(ledc_channel_config(&ledc_channel));

    ESP_ERROR_CHECK(gpio_config(&gpio_conf));

    while (1) {
        gpio_set_level(TRIGGER_PIN, 1);
        sendBursts();
        esp_rom_delay_us(BURST_DELAY_MICRO);
        gpio_set_level(TRIGGER_PIN, 0);

        for (int i = 0; i < 10000000; i++) {
            ;
        }
    }
}

void sendBursts (void)
{
    ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, LEDC_DUTY));
    ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, LEDC_CHANNEL));
    esp_rom_delay_us(BURST_DELAY_MICRO);
    ESP_ERROR_CHECK(ledc_stop(LEDC_MODE, LEDC_CHANNEL, 0));
    // ESP_ERROR_CHECK(ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, 0));
    // ESP_ERROR_CHECK(ledc_update_duty(LEDC_MODE, LEDC_CHANNEL));
}
