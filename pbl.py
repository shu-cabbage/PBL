from __future__ import print_function;
import RPi.GPIO as GPIO;
import qwiic_relay;
import pi_servo_hat;
import qwiic_button;
import sys;
import time;

"""config"""
start_btn_status =False; #始動ボタンが一度でも押されたかのステータス
emergency_stop_status = False; #緊急停止ボタンが一度でも押されたかのステータス
relay_1_conveyor = 1;
relay_2_GreenRamp = 2;
relay_3_RedRamp = 3;
#gpio
sensor_pin = 20; #センサー入力ピン
button_start = 21; #緑ボタン：作動
GPIO.setmode(GPIO.BCM);
GPIO.setup(sensor_pin, GPIO.IN, pullup_down=GPIO.PUD_DOWN);
GPIO.setup(button_start, GPIO.IN, pullup_down=GPIO.PUD_DOWN);
#relay
QUAD_SOLID_STATE_RELAY = 0x08; #リレーのi2cアドレス
myRelays = qwiic_relay.QwiicRelay(QUAD_SOLID_STATE_RELAY);
#servo
servo = pi_servo_hat.PiServoHat();
servo.restart();
servo.move_servo_position(0,0);
#button
my_button = qwiic_button.QwiicButton();
brightness = 100; #led明るさ

#比較
def comparate(sensor_time):
    #config
    tolerance = 5; #許容差
    size = 10; #サイズ
    conveyor_time = 2; #センサからサーボまでかかる時間(s)  サーボとセンサの距離があまり遠くにならないようにしてほし　まあ好きに変えてくれ

    if (size - tolerance < sensor_time or sensor_time < size + tolerance):
        print("ok");

    else:
        print("bad");
        if(conveyor_time <= time.perf_counter() and conveyor_time + 0.5 >= time.perf_counter()):
            servo.move_servo_position(0,90); #仕分け機(サーボ)
            servo.move_servo_position(0,0);


def sensor_func():
    sensor_time = 0;
    myRelays.set_relay_on(relay_1_conveyor); #コンベア始動
    myRelays.set_relay_on(relay_2_GreenRamp); #緑ランプ
    sensor = GPIO.input(sensor_pin);
    if (sensor == 1): #計測開始
        sensor_time = time.perf_counter();

    if (sensor == 0): #計測終了
        time_stop = time.perf_counter();
        comparate(time_stop - sensor_time);


#割り込み処理 https://www.raspberrypirulo.net/entry/python-callback
class CallBack:
    def __init__(self):
        button_stop = 22; #黄色ボタン：停止
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(button_stop, GPIO.IN, pullup_down=GPIO.PUD_DOWN);

        # 割り込みイベント設定
        GPIO.add_event_detect(button_stop, GPIO.RISING, bouncetime=1000)
        # コールバック関数登録
        GPIO.add_event_callback(button_stop, self.my_callback_one) 
        GPIO.add_event_callback(button_stop, self.my_callback_two)

    def main_func():
        start_btn = GPIO.input(button_start);
        global start_btn_status;
        global emergency_stop_status;

        if(my_button.is_button_pressed() == False and emergency_stop_status == False): #緊急ボタン停止押されてないかつ，まだ押されてない
            my_button.LED_off();
            if(start_btn == 1 or start_btn_status == True): #始動ボタン押されている又は，押されたことがある
                start_btn_status = True; #推されたというステータス
                sensor_func();

        elif(my_button.is_button_pressed() == True): #緊急停止ボタン押された
            start_btn_status = False; #始動できなくする
            emergency_stop_status = True; #緊急停止ボタン押されたというステータス
            my_button.LED_on(brightness);
            myRelays.set_all_relays_off();
            myRelays.set_relay_on(relay_3_RedRamp); #赤ランプ

    def callback_func(self):
        global start_btn_status;
        start_btn_status = False;
        myRelays.set_all_relays_off();
        myRelays.set_relay_on(relay_3_RedRamp); #赤ランプ

cb = CallBack()
cb.callback_func() # 割り込みイベント待ち