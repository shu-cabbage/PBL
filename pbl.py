#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function;
import RPi.GPIO as GPIO;
import qwiic_i2c;
import qwiic_relay;
import pi_servo_hat;
import sys;
import time;
import json;

"""config"""
start_btn_status =False; #始動ボタンが一度でも押されたかのステータス
conveyor_status = False;
relay_conveyor = 1;
relay_GreenRamp = 2;
relay_RedRamp = 3;
#gpio
sensor_pin = 23; #センサー入力ピン
button_start = 17; #緑ボタン：作動
button_stop = 27; #黄色ボタン：停止
GPIO.setmode(GPIO.BCM);
GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN);
GPIO.setup(button_start, GPIO.IN, pull_up_down=GPIO.PUD_DOWN);
GPIO.setup(button_stop, GPIO.IN, pull_up_down=GPIO.PUD_DOWN);
#relay
QUAD_SOLID_STATE_RELAY = 0x6d; #リレーのi2cアドレス
myRelays = qwiic_relay.QwiicRelay(QUAD_SOLID_STATE_RELAY);
#servo
servo = pi_servo_hat.PiServoHat();
servo.restart();
servo.move_servo_position(0,0);
#json file
json_file = open("data.json", "r");
json_data = json.load(json_file);
json_file.close();

#比較
def comparate(sensor_time):
    #config
    tolerance = 0.5; #許容差
    size = 3; #サイズ
    conveyor_time = 2; #センサからサーボまでかかる時間(s)  サーボとセンサの距離があまり遠くにならないようにしてほし　まあ好きに変えてくれ

    if (size - tolerance < sensor_time and sensor_time < size + tolerance):
        json_data["details"].append({"value" : sensor_time, "status" : "OK"});
        output_json = open("data.json", "w");
        json.dump(json_data, output_json, indent=4);
        output_json.flush();
        print("ok");

    else:
        wait_start = time.perf_counter();
        json_data["details"].append({"value" : sensor_time, "status" : "Defective"});
        output_json = open("data.json", "w");
        json.dump(json_data, output_json, indent=4);
        output_json.flush();
        print("bad");
        while True:
            print("waiting...");
            if(time.perf_counter() - wait_start >= conveyor_time):
                break;

        print("servo start");
        servo.move_servo_position(0,90); #仕分け機(サーボ)
        time.sleep(1);
        servo.move_servo_position(0,0);
        print("servo stop");

def sensor_func():
    sensor_time = 0;
    sensor_status = False;
    global conveyor_status;
    if (conveyor_status == False):
        conveyor_status = True;
        myRelays.set_relay_on(relay_conveyor); #コンベア始動
        myRelays.set_relay_on(relay_GreenRamp); #緑ランプ
    
    sensor = GPIO.input(sensor_pin);
    if (sensor == 1 and sensor_status == False): #計測開始
        sensor_status = True;
        sensor_time = time.perf_counter();
        print(sensor_time);

    while (sensor == 1 and sensor_status == True):
        sensor = GPIO.input(sensor_pin);
        if (sensor == 0):
            break;

    if (sensor == 0 and sensor_status == True): #計測終了
        time_stop = time.perf_counter();
        print(time_stop);
        print(time_stop - sensor_time);
        comparate(time_stop - sensor_time);

while True:
    if(GPIO.input(button_stop) == 1):
        start_btn_status = False;
        conveyor_status = False;
        myRelays.set_all_relays_off();
        myRelays.set_relay_on(relay_RedRamp); #赤ランプ
        json_data["status"] = "stopped";
        output_json = open("data.json", "w");
        json.dump(json_data, output_json, indent=4);
        output_json.flush();
        print("stopped");

    #print("ready");
    if(GPIO.input(button_start) == 1 or start_btn_status == True): #始動ボタン押されている又は，押されたことがある
        start_btn_status = True; #推されたというステータス
        myRelays.set_relay_off(relay_RedRamp); #赤ランプ
        json_data["status"] = "running";
        output_json = open("data.json", "w");
        json.dump(json_data, output_json, indent=4);
        output_json.flush();
        sensor_func();