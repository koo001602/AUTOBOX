from Raspi_MotorHAT import Raspi_MotorHAT, Raspi_DCMotor
from Raspi_PWM_Servo_Driver import PWM
import RPi.GPIO as GPIO
import time
import threading

class ConveyerController:
    def __init__(self, addr=0x6f, motor_id=2, sensor_pin=17):
        # 모터 설정
        self.mh = Raspi_MotorHAT(addr=addr)
        self.motor = self.mh.getMotor(motor_id)
        self.motor_speed = 100
        
        # 서보 설정
        self.servo = PWM(addr)
        self.servo.setPWMFreq(60)
        
        # 센서 설정
        self.sensor_pin = sensor_pin
        self.stop_event = threading.Event()
        self.box_detected_flag = False # 메인에서 확인용 플래그

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.sensor_pin, GPIO.FALLING, 
            callback=self._object_detected, bouncetime=200)

        self.servo_set() # 초기값 세팅

    def _object_detected(self, channel):
        """센서 감지 시 호출되는 내부 콜백"""
        print(" 적외선 센서 감지! (모터 정지 신호)")
        self.stop_event.set()      # 모터 스레드 멈춤
        self.box_detected_flag = True # 메인 루프에 알림

    def belt_run_until_sensor(self):
        """센서 감지될 때까지 벨트 가동"""
        self.box_detected_flag = False
        self.stop_event.clear()
        
        def _worker():
            self.motor.setSpeed(self.motor_speed)
            self.motor.run(Raspi_MotorHAT.FORWARD)
            
            # stop_event가 울릴 때까지(센서감지) 계속 돔 (최대 10초 안전장치)
            start = time.time()
            while not self.stop_event.is_set():
                if time.time() - start > 15: break 
                time.sleep(0.05)
            
            self.motor.run(Raspi_MotorHAT.RELEASE)
            print("Belt Stopped.")

        t = threading.Thread(target=_worker)
        t.start()

    def emergency_stop(self):
        print("conveyer emergency stop")
        self.stop_event.set() 
        self.motor.run(Raspi_MotorHAT.RELEASE) 
        self.servo_set() 
        
        
    # --- 서보 관련 ---
    def servo_set(self):
        self.servo.setPWM(0, 0, 600)
        self.servo.setPWM(1, 0, 180)

    def move_servos_smooth(self, ch1_s, ch1_e, ch2_s, ch2_e, speed=0.005):
        steps = 150
        for i in range(steps + 1):
            pos1 = int(ch1_s + (ch1_e - ch1_s) * (i / steps))
            pos2 = int(ch2_s + (ch2_e - ch2_s) * (i / steps))
            self.servo.setPWM(0, 0, pos1)
            self.servo.setPWM(1, 0, pos2)
            time.sleep(speed)

    def push_box(self):
        print(" Pushing Box...")
        self.move_servos_smooth(600, 180, 180, 600) # Push
        time.sleep(1)
        self.move_servos_smooth(180, 600, 600, 180) # Pull

    def cleanup(self):
        
        self.motor.run(Raspi_MotorHAT.RELEASE)
        self.stop_event.set() # 스레드 안전 종료
        time.sleep(0.1)       # 스레드 정리 대기
        GPIO.cleanup()
