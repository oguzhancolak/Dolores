#!/usr/bin/env python

import os
import sys
import qi
from customerquery import CustomerQuery
import requests
from requests.auth import HTTPBasicAuth
from kairos_face import enroll
import json
import datetime
from chirpsdk import chirpsdk
import time


class AuthenticationLauncher(object):
    subscriber_list = []
    in_action = False

    def __init__(self, application):
        # get the session to use everywhere
        self.application = application
        self.session = application.session
        self.service_name = self.__class__.__name__

        self.logger = qi.Logger(self.service_name)
        self.logger.info("Initalizing: " + self.service_name)
        self.memory = self.session.service("ALMemory")
        self.create_signals()

        self.life = self.session.service("ALAutonomousLife")

        self.pm = self.session.service("ALPreferenceManager")
        self.pm.update()
        self.file_path = self.pm.getValue ('sound_auth', "file_path")
        self.file_name = self.pm.getValue ('sound_auth', "file_name_inaudable")
        # self.robot_id = self.pm.getValue ('global_variables', "robot_id")
        self.chirp_api_key = self.pm.getValue ('sound_auth', "chirp_api_key")
        self.chirp_secret_key = self.pm.getValue ('sound_auth', "chirp_secret_key")
        self.duration = int (self.pm.getValue ('sound_auth', "duration"))
        self.repetition = int (self.pm.getValue ('sound_auth', "repetition"))
        self.url_get = self.pm.getValue ('sound_auth', 'url_get')
        self.username = self.pm.getValue ('sound_auth', "username")
        self.password = self.pm.getValue ('sound_auth', "password")
        self.picture_path = self.pm.getValue ('my_friend', 'picture_path')
        self.gallery_name = self.pm.getValue ('my_friend', "gallery_name")

        self.amoves = self.session.service("ALAutonomousMoves")
        self.bawareness = self.session.service("ALBasicAwareness")
        self.aspeech = self.session.service("ALAnimatedSpeech")
        self.posture = self.session.service("ALRobotPosture")
        self.robot_id = "1"
        # self.create_sound ()

    # Signal related methods starts

    @qi.nobind
    def create_signals(self):
        # Create events and subscribe them here
        self.logger.info("Creating events...")

        event_name = "Authentication/GoNFC"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_go_nfc)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/GoQR"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_go_qr)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/GoListener"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_go_listener)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/GoKeyboard"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_go_keyboard)
        self.subscriber_list.append([event_subscriber, event_connection])

#        event_name = "Authentication/EnableBasics"
 #       self.memory.declareEvent(event_name)
  #      event_subscriber = self.memory.subscriber(event_name)
   #     event_connection = event_subscriber.signal.connect(self.enable_after_first_animation)
    #    self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/CheckForAction"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_check_for_action)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/ExitApp"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.on_self_exit)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/FoundWithSound"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.authentication_redirect)
        self.subscriber_list.append([event_subscriber, event_connection])

        event_name = "Authentication/PlaySound"
        self.memory.declareEvent(event_name)
        event_subscriber = self.memory.subscriber(event_name)
        event_connection = event_subscriber.signal.connect(self.play_sound)
        self.subscriber_list.append([event_subscriber, event_connection])

    @qi.nobind
    def disconnect_signals(self):
        self.logger.info("Deleting events...")
        for sub, i in self.subscriber_list:
            try:
                sub.signal.disconnect(i)
            except Exception, e:
                self.logger.info("Error unsubscribing: {}".format(e))
        self.logger.info("Unsubscribe done!")

    # Signal related methods ends

    # -------------------------------------

    # Event CallBacks Starts

    @qi.bind(methodName="on_check_for_action", paramsType=(qi.String,), returnType=qi.Void)
    def on_check_for_action(self, value):
        self.logger.info(str(value))
        if not self.in_action:
            if value == "reminder":
                self.memory.raiseEvent("Authentication/Reminder", 1)
            elif value == "endit":
                self.memory.raiseEvent("Authentication/NoAction", 1)

    @qi.bind(methodName="on_go_nfc", paramsType=(qi.String,), returnType=qi.Void)
    def on_go_nfc(self, value):
        self.in_action = True
        self.logger.info("NFC selected.")
        to_app = str(self.pm.getValue("authentication_launcher", "nfc_app"))

        self.logger.info(to_app)
        self.cleanup()
        self.life.switchFocus(to_app)

    @qi.bind(methodName="on_go_qr", paramsType=(qi.String,), returnType=qi.Void)
    def on_go_qr(self, value):
        self.in_action = True
        self.logger.info("QR selected.")
        to_app = str(self.pm.getValue("authentication_launcher", "qr_app"))
        self.logger.info(to_app)
        self.cleanup()
        self.life.switchFocus(to_app)

    @qi.bind(methodName="on_go_listener", paramsType=(qi.String,), returnType=qi.Void)
    def on_go_listener(self, value):
        self.in_action = True
        self.logger.info("Listener selected.")
        to_app = str(self.pm.getValue("authentication_launcher", "listener_app"))
        self.logger.info(to_app)
        self.cleanup()
        self.life.switchFocus(to_app)

    @qi.bind(methodName="on_go_keyboard", paramsType=(qi.String,), returnType=qi.Void)
    def on_go_keyboard(self, value):
        self.in_action = True
        self.logger.info("Keyboard selected.")
        to_app = str(self.pm.getValue("authentication_launcher", "keyboard_app"))
        self.logger.info(to_app)
        self.cleanup()
        self.life.switchFocus(to_app)

    @qi.nobind  # Enables the awareness and animation language for intro part
    def enable_after_first_animation(self, value):
        self.posture.goToPosture("Stand", 0.8)
        try:
            self.amoves.setBackgroundStrategy("backToNeutral")
        except Exception, e:
            self.logger.info("Exception while enabling autonomus moves: {}".format(e))

        try:
            self.bawareness.startAwareness()
        except Exception, e:
            self.logger.info("Exception while enabling basic awareness: {}".format(e))

        try:
            self.aspeech.setBodyLanguageModeFromStr("contextual")
        except Exception, e:
            self.logger.info("Exception while enabling animated speech: {}".format(e))
        self.logger.info("All enabled")
        
    @qi.nobind
    def on_self_exit(self, value):
        self.on_exit()


    # Event CallBacks Ends

    # -------------------------------------

    # Initiation methods for services Starts

    @qi.nobind
    def show_screen(self):
        folder = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
        self.logger.info("Loading tablet page for app: {}".format(folder))
        try:
            ts = self.session.service("ALTabletService")
            ts.loadApplication(folder)
            ts.showWebview()
            # self.play_sound()
            self.logger.info("Tablet loaded.")
        except Exception, e:
            self.logger.error("Error starting tablet page{}".format(e))


    @qi.nobind
    def hide_screen(self):
        self.logger.info("Stopping tablet")
        try:
            ts = self.session.service("ALTabletService")
            ts.hideWebview()
            self.logger.info("Tablet stopped.")
        except Exception, e:
            self.logger.error("Error hiding tablet page{}".format(e))


    @qi.nobind
    def start_dialog(self):
        self.logger.info("Loading dialog")
        self.dialog = self.session.service("ALDialog")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        topic_path = os.path.realpath(os.path.join(dir_path, "authentication", "authentication_enu.top"))
        self.logger.info("File is: {}".format(topic_path))
        try:
            self.loaded_topic = self.dialog.loadTopic(topic_path)
            self.dialog.activateTopic(self.loaded_topic)
            self.dialog.subscribe(self.service_name)
            self.logger.info("Dialog loaded!")
        except Exception, e:
            self.logger.info("Error while loading dialog: {}".format(e))
        


    @qi.nobind
    def stop_dialog(self):
        self.logger.info("Unloading dialog")
        try:
            self.dialog = self.session.service("ALDialog")
            self.dialog.unsubscribe(self.service_name)
            self.dialog.deactivateTopic(self.loaded_topic)
            self.dialog.clearConcepts()
            self.dialog.unloadTopic(self.loaded_topic)
            self.logger.info("Dialog unloaded!")
        except Exception, e:
            self.logger.info("Error while unloading dialog: {}".format(e))

    # Initiation methods for services Ends

    # ------------------------------------------

    # App Start/End Methods Starts

    @qi.nobind
    def stop_app(self):
        # To be used if internal methods need to stop the service from inside.
        # external NAOqi scripts should use ALServiceManager.stopService if they need to stop it.
        self.logger.info("Stopping service...")
        self.cleanup()
        to_app = str(self.pm.getValue("global_variables", "main_app_id"))
        self.life.switchFocus(to_app)

    @qi.nobind
    def cleanup(self):
        # called when your module is stopped
        self.logger.info("Cleaning...")
        # @TODO: insert cleaning functions here
        self.stop_dialog ()
        self.disconnect_signals()
        self.hide_screen()
        self.logger.info("Cleaned!")

    @qi.bind(methodName="on_exit", returnType=qi.Void)
    def on_exit(self):
        self.stop_app()

    @qi.nobind  # Starting the app  # @TODO: insert whatever the app should do to start
    def start_app(self):
        self.logger.info("Starting App.")
        #self.disable_for_first_animation()
        self.show_screen()
        self.start_dialog()

    @qi.nobind #Disables the awareness and animation language for intro part
    def disable_for_first_animation(self):
        try:
            self.amoves.setBackgroundStrategy("none")
        except Exception, e:
            self.logger.info("Exception while disabling autonomus moves: {}".format(e))
        try:
            self.bawareness.stopAwareness()
        except Exception, e:
            self.logger.info("Exception while disabling basic awareness: {}".format(e))
        try:
            self.aspeech.setBodyLanguageModeFromStr("disabled")
        except Exception,e:
            self.logger.info("Exception while disabling animated speech: {}".format(e))
        self.posture.goToPosture("Stand", 0.8)


    # App Start/End Methods Ends
# ________________________________________ New Functions ______________________________________

    @qi.nobind
    def create_sound(self):
        sdk = chirpsdk.ChirpSDK(self.chirp_api_key, self.chirp_secret_key)
        sdk.set_protocol('ultrasonic')
        chirp = sdk.create_chirp ('12345678')
        # sdk.streaming_interval = 500
        # sdk.start_streaming (chirp)
        self.logger.info('sound has been created with ' + chirp.identifier)
        sdk.save_wav(chirp, filename=self.file_path+self.file_name, offline=False)

    # @qi.nobind
    # def start_play(self):
    #     thread = Thread (target=self.play_sound, args=(1,))
    #     thread.start()

    @qi.nobind
    def play_sound(self, value):
        self.logger.info("Play sound arrived")
        audio = self.session.service('ALAudioPlayer')
        audio.playFile(self.file_path+"deadbeef.wav", 1.0, 0.0)
        audio.playFile (self.file_path + "deadbeef.wav", 1.0, 0.0)
        audio.playFile (self.file_path + "deadbeef.wav", 1.0, 0.0)
        audio.playFile (self.file_path + "deadbeef.wav", 1.0, 0.0)
        audio.playFile (self.file_path + "deadbeef.wav", 1.0, 0.0)
        audio.playFile (self.file_path + "deadbeef.wav", 1.0, 0.0)
        audio.playFile (self.file_path + "deadbeef.wav", 1.0, 0.0)
        audio.playFile (self.file_path + "deadbeef.wav", 1.0, 0.0)
        audio.playFile (self.file_path + "deadbeef.wav", 1.0, 0.0)
        audio.playFile (self.file_path + "deadbeef.wav", 1.0, 0.0)
        if value == "1":
            self.logger.info('first time run')
            self.auth_check()

    @qi.nobind
    def enroll_face(self, value):

        try:
            picture_path = self.picture_path
            self.logger.info('enroll known face has been worked')
            self.logger.info(picture_path)
            response = enroll.enroll_face(file=picture_path, gallery_name=self.gallery_name, subject_id=value)
            self.logger.info('Response:' + str(response))
            self.logger.info(str(datetime.now()) + 'response arrived')
            status = response['images'][0]['transaction']['status']
            self.logger.info('response status=' + status)

        except Exception, e:
            self.logger.error(e)

    @qi.nobind
    def get_customer_info(self):
            try:
                payload = {
                    'robotId': self.robot_id
                }
                headers = {
                    'Content-type': 'application/json',
                    'Accept': 'text/plain',
                }
                response = requests.post (self.url_get, data=json.dumps (payload), headers=headers,
                                          auth=HTTPBasicAuth (self.username, self.password))
                self.logger.info (response.text)
                if response.status_code == 200:
                    data = response.json ()
                    customer = CustomerQuery ()
                    customer.query_customer (data[0]['customerId'], "U")
                    self.logger.info('Customer Info=' + str(customer.jsonify()))
                    self.memory.insertData("Global/CurrentCustomer", str(customer.jsonify()))
                    self.logger.info ('Customer Info=' + self.memory.getData("Global/CurrentCustomer"))
                    self.memory.raiseEvent("Authentication/FoundWithSound", 1)
                    self.enroll_face(customer.customer_number)
                    return True
                else:
                    return False
            except Exception, e:
                self.logger.info ('Error while requesting result: {}'.format (e))
                return False

    @qi.nobind
    def auth_check(self):
            self.logger.info ("check started repetition = " + str (self.repetition))
            clickData="0"
            for x in range (1, self.repetition):
                try:
                    clickData= self.memory.getData ("Authentication/Click")
                except:
                    clickData="0"

                if self.get_customer_info ():
                    self.logger.info('found')

                    # self.enroll_face()
                    break
                elif clickData == "1":
                    self.logger.info('clicked')
                    break
                else:
                    self.play_sound("0")
                    self.logger.info('step = ' + str(x))
                    time.sleep(0.5)

    @qi.nobind
    def authentication_redirect(self, value):
        self.logger.info ('redirect is working')
        autonomous_life = self.session.service ('ALAutonomousLife')
        # try:
        #     if value == "1":
        redirect_app = str (self.memory.getData ('Global/RedirectingApp'))
        self.logger.info ("Redirection is working for=" + redirect_app)
            # else:
            #     self.logger.info ("Redirection is working for=" + self.auth_launcher_id)
            #     autonomous_life.switchFocus (self.auth_launcher_id)
        # except Exception, e:
        #     self.logger.info(e)
        #     self.logger.error(e)
        #     self.memory.raiseEvent('Authentication/ExecutionError', 1)
        #     self.logger.info('error event raised')
        self.cleanup ()
        autonomous_life.switchFocus (redirect_app)

if __name__ == "__main__":
    # with this you can run the script for tests on remote robots
    # run : python main.py --qi-url 123.123.123.123
    app = qi.Application(sys.argv)
    app.start()
    service_instance = AuthenticationLauncher(app)
    service_id = app.session.registerService(service_instance.service_name, service_instance)
    service_instance.start_app()
    app.run()
    service_instance.cleanup()
    app.session.unregisterService(service_id)
