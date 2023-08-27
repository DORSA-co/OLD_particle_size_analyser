import time
"""
########################################
---------------------------------------

Made with Malek & Milad

Features:

    ● Create Unlimite Object of Cameras and Live Preview By serial number
    ● Set Bandwitdh Of each Cameras
    ● Set gain,exposure,width,height,offet_x,offset_y
    ● Get tempreture of Cmeras
    ● Set Trigger Mode on
    ● There are Some diffrents between ace2(pro) and ace

---------------------------------------
########################################
"""

from pypylon import pylon
from pypylon import genicam
import cv2
import numpy as np



DEBUG = False
TRIGGER_SOURCE = ['Off', 'Software', 'Line1']
GAMMA_USER = 'User'
GAMMA_SRGB = 'sRGB'

class Collector():

    def __init__(self, serial_number, gain=0, exposure=3000, black_level=0, gamma_enable=False, gamma_mode=GAMMA_USER, gamma_value=1, max_buffer=20, trigger=False, delay_packet=100, packet_size=1500,
                frame_transmission_delay=0, width=1000, height=1000, offet_x=0, offset_y=0, manual=False, list_devices_mode=False, trigger_source='Software'):
        """Initializes the Collector

        Args:
            gain (int, optional): The gain of images. Defaults to 0.
            exposure (float, optional): The exposure of the images. Defaults to 3000.
            max_buffer (int, optional): Image buffer for cameras. Defaults to 5.
        """

        self.gain = gain
        self.exposure = exposure
        self.black_level = black_level
        self.gamma_enable = gamma_enable
        self.gamma_mode = gamma_mode
        self.gamma_value = gamma_value
        #
        self.max_buffer = max_buffer
        self.cont_eror=0
        self.serial_number = serial_number
        self.trigger = trigger
        self.trigger_source = trigger_source
        self.dp = delay_packet
        self.ps=packet_size
        self.ftd=frame_transmission_delay
        self.width=width
        self.height=height
        self.offset_x=offet_x
        self.offset_y=offset_y
        self.manual=manual
        self.list_devices_mode=list_devices_mode
        self.exitCode=0

        self.__tl_factory = pylon.TlFactory.GetInstance()
        devices = []


        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned


        for device in self.__tl_factory.EnumerateDevices():
            if (device.GetDeviceClass() == 'BaslerGigE'):                
                devices.append(device)

        # assert len(devices) > 0 , 'No Camera is Connected!
        if self.list_devices_mode:
            self.cameras = list()

            for device in devices:
                camera = pylon.InstantCamera(self.__tl_factory.CreateDevice(device))
                self.cameras.append(camera)
        
        else:
            for device in devices:
                camera = pylon.InstantCamera(self.__tl_factory.CreateDevice(device))
                # print(camera.GetDeviceInfo().GetSerialNumber())
                if camera.GetDeviceInfo().GetSerialNumber() == self.serial_number:
                    self.camera = camera
                
                    break

        #assert len(devices) > 0 , 'No Camera is Connected!'
    


    def get_tempreture(self):
        device_info = self.camera.GetDeviceInfo()
        model=str(device_info.GetModelName())
        model=model[-3:]

        if model=='PRO':
            # print(self.camera.DeviceTemperature.GetValue())
            return self.camera.DeviceTemperature.GetValue()
        else :
            # print('temp',self.camera.TemperatureAbs.GetValue())
            return self.camera.TemperatureAbs.GetValue()
    
    
    def get_fps(self):
        try:
            return self.camera.ResultingFrameRateAbs.GetValue()
        except:
            return 1


    def start_grabbing(self):

        device_info = self.camera.GetDeviceInfo()
        model=str(device_info.GetModelName())
        model=model[-3:]
        # print(model[-3:])


        try:
            # print(self.camera.IsOpen())
            # print(device_info.GetSerialNumber())

            self.camera.Open()
            
            if self.manual:

                
                if model=='PRO':
                    # print('yes pro')
                    # print(self.camera.DeviceTemperature.GetValue())
                    self.camera.ExposureTime.SetValue(self.exposure)

                    self.camera.Gain.SetValue(self.gain)
                    
                    # self.camera.GevSCPSPacketSize.SetValue(int(self.ps)+1000)
                    # self.camera.Close()
                    # self.camera.Open()
                    self.camera.GevSCPSPacketSize.SetValue(int(self.ps))
                    self.camera.Close()
                    self.camera.Open()
                                                  
                    self.camera.GevSCPD.SetValue(self.dp)
                    self.camera.Close()
                    self.camera.Open()                   
                    self.camera.GevSCFTD.SetValue(self.ftd)
                    self.camera.Close()
                    self.camera.Open()




                    self.camera.Width.SetValue(self.width)
                    self.camera.Height.SetValue(self.height)

                    self.camera.OffsetX.SetValue(self.offset_x)
                    self.camera.OffsetY.SetValue(self.offset_y)
                    



                

                else:
                    


                    self.camera.ExposureTimeAbs.SetValue(self.exposure)
                    self.camera.GainRaw.SetValue(self.gain)
                    self.camera.BlackLevelRaw.SetValue(self.black_level)
                    self.set_gamma(enable=self.gamma_enable, mode=self.gamma_mode, gamma_value=self.gamma_value)
                    
                    self.camera.GevSCPSPacketSize.SetValue(int(self.ps)+1000)
                    self.camera.Close()
                    self.camera.Open()
                                
                    self.camera.GevSCPD.SetValue(self.dp)
                    self.camera.Close()
                    self.camera.Open()                   
                    self.camera.GevSCFTD.SetValue(self.ftd)
                    self.camera.Close()
                    self.camera.Open()

                    self.camera.GevSCPSPacketSize.SetValue(int(self.ps))
                    self.camera.Close()
                    self.camera.Open()
                    self.camera.Width.SetValue(self.width)
                    self.camera.Height.SetValue(self.height)

                    self.camera.OffsetX.SetValue(self.offset_x)
                    self.camera.OffsetY.SetValue(self.offset_y)
                    


            self.camera.Close()

            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 

            self.camera.Open()

            if self.trigger:
                self.camera.TriggerSelector.SetValue('FrameStart')
                self.camera.TriggerMode.SetValue('On')
                self.camera.TriggerSource.SetValue(self.trigger_source)
                # print('triggeron on %s' % self.trigger_source)
            else:
                # self.camera.TriggerMode.SetValue('Off')
                # print('triggeroff')
                pass

            # if self.manual:
            #     self.camera.ExposureTimeAbs.SetValue(20000)


            #     # self.camera.Width.SetValue(600)
            #     print(self.camera.Width.GetValue())
            #     self.camera.Width.SetValue(600)
            #     # int64_t = self.camera.PayloadSize.GetValue()
            #     # self.camera.GevStreamChannelSelectorCamera.GevStreamChannelSelector.SetValue( 'GevStreamChannelSelector_StreamChannel0 ')
            #     # self.camera.GevSCPSPacketSize.SetValue(1500)
                             
            #     self.camera.GevSCPD.SetValue(self.dp)
                
            #     self.camera.GevSCFTD.SetValue(self.ftd)
            self.exitCode=0

            return True, 'start grabbing ok'
            
        except genicam.GenericException as e:
            # Error handling
            
            message = self.start_grabbing_error_handling(error=e)
            self.stop_grabbing()
            self.exitCode = 1
            
            return False, message

    
    def start_grabbing_error_handling(self, error):
        message = ''
        # camera in use
        if 'The device is controlled by another application' in str(error):
            message = 'camera_controlled_by_another_app'

        # expossure invalid
        elif "OutOfRangeException thrown in node 'ExposureTimeAbs' while calling 'ExposureTimeAbs.SetValue()" in str(error):
            # min
            if 'greater than or equal' in str(error):
                message = 'exposure_too_low'
            elif 'must be smaller than or equal' in str(error):
                message = 'exposure_too_high'
            else:
                message = 'exposure_invalid'

        # gain invalid
        elif "OutOfRangeException thrown in node 'GainRaw' while calling 'GainRaw.SetValue()" in str(error):
            if 'must be equal or greater than' in str(error):
                message = 'gain_too_low'
            elif 'must be equal or smaller than' in str(error):
                message = 'gain_too_high'
            else:
                message = 'gain_invalid'
        
        # black-level value
        elif "OutOfRangeException thrown in node 'BlackLevelRaw' while calling 'BlackLevelRaw.SetValue()" in str(error):
            if 'must be equal or greater than' in str(error):
                message = 'blacklevel_too_low'
            elif 'must be equal or smaller than' in str(error):
                message = 'blacklevel_too_high'
            else:
                message = 'blacklevel_invalid'

        # gamma value
        elif "OutOfRangeException thrown in node 'Gamma' while calling 'Gamma.SetValue()" in str(error):
            if 'greater than or equal' in str(error):
                message = 'gamma_too_low'
            elif 'must be smaller than or equal' in str(error):
                message = 'gamma_too_high'
            else:
                message = 'gamma_invalid'

        # packetsize invalid
        elif "OutOfRangeException thrown in node 'GevSCPSPacketSize' while calling 'GevSCPSPacketSize.SetValue()" in str(error):
            message = 'packetsize_invalid'
        
        # transmission delay
        elif "OutOfRangeException thrown in node 'GevSCFTD' while calling 'GevSCFTD.SetValue()" in str(error):
            if 'must be equal or greater than' in str(error):
                message = 'transmision_delay_too_low'
            elif 'must be equal or smaller than' in str(error):
                message = 'transmision_delay_too_high'
            else:
                message = 'transmision_delay_invalid'

        # height delay
        elif "OutOfRangeException thrown in node 'Height' while calling 'Height.SetValue()" in str(error):
            if 'must be equal or greater than' in str(error):
                message = 'height_too_low'
            elif 'must be equal or smaller than' in str(error):
                message = 'height_too_high'
            else:
                message = 'height_invalid'

        # width delay
        elif "OutOfRangeException thrown in node 'Width' while calling 'Width.SetValue()" in str(error):
            if 'must be equal or greater than' in str(error):
                message = 'width_too_low'
            elif 'must be equal or smaller than' in str(error):
                message = 'width_too_high'
            else:
                message = 'width_invalid'

        # offsetx delay
        elif "OutOfRangeException thrown in node 'OffsetX' while calling 'OffsetX.SetValue()" in str(error):
            if 'must be equal or greater than' in str(error):
                message = 'offsetx_too_low'
            elif 'must be equal or smaller than' in str(error):
                message = 'offsetx_too_high'
            else:
                message = 'offsetx_invalid'

        # offsety delay
        elif "OutOfRangeException thrown in node 'OffsetY' while calling 'OffsetY.SetValue()" in str(error):
            if 'must be equal or greater than' in str(error):
                message = 'offsety_too_low'
            elif 'must be equal or smaller than' in str(error):
                message = 'offsety_too_high'
            else:
                message = 'offsety_invalid'
        

        else:
            message = str(error)

        return message



    def stop_grabbing(self):
        self.camera.Close()

        
    def listDevices(self):
        """Lists the available devices
        """
        for i ,  camera in enumerate(self.cameras):
            device_info = camera.GetDeviceInfo()
            print(
                "Camera #%d %s @ %s (%s) @ %s" % (
                i,
                device_info.GetModelName(),
                device_info.GetIpAddress(),
                device_info.GetMacAddress(),
                device_info.GetSerialNumber(),
                )
            
            )
            print(device_info)


    def serialnumber(self):
        serial_list=[]
        for i ,  camera in enumerate(self.cameras):
            device_info = camera.GetDeviceInfo()
            serial_list.append(device_info.GetSerialNumber())
        return serial_list         




    def trigg_exec(self,):
        
        if self.trigger:
            self.camera.TriggerSoftware()
            #print(self.camera.GetQueuedBufferCount(), 'T'*100)
            while self.camera.GetQueuedBufferCount() >=10:
                pass
            #print(self.camera.GetQueuedBufferCount(), 'T'*100)
        
    
    def set_exposure(self, exposure):
        device_info = self.camera.GetDeviceInfo()
        model=str(device_info.GetModelName())
        model=model[-3:]

        try:
            if model=='PRO':
                self.camera.ExposureTime.SetValue(exposure)
            else:
                self.camera.ExposureTimeAbs.SetValue(exposure)

            self.exposure = exposure
        except:
            return


    def set_gain(self, gain):
        device_info = self.camera.GetDeviceInfo()
        model=str(device_info.GetModelName())
        model=model[-3:]

        try:
            if model=='PRO':
                self.camera.Gain.SetValue(gain)
            else:
                self.camera.GainRaw.SetValue(gain)

            self.gain = gain
        except:
            return


    def set_offsetx(self, offsetx):
        try:
            self.camera.OffsetX.SetValue(offsetx)
            self.offset_x = offsetx
        except:
            return


    def set_offsety(self, offsety):
        try:
            self.camera.OffsetY.SetValue(offsety)
            self.offset_y = offsety
        except:
            return

    
    def set_black_level(self, black_level):
        try:
            self.camera.BlackLevelRaw.SetValue(black_level)
            self.black_level = black_level
        except:
            return
    

    def set_gamma(self, enable, mode=GAMMA_USER, gamma_value=1):
        if not enable:
            self.camera.GammaEnable.SetValue(False)
            self.gamma_enable = enable
            return
        self.camera.GammaEnable.SetValue(True)
        self.gamma_enable = enable
        
        try:
            self.camera.GammaSelector.SetValue(mode)
            #
            if mode == GAMMA_USER:
                self.camera.Gamma.SetValue(gamma_value)
                self.gamma_value = gamma_value
            
            self.gamma_mode = mode
        
        except:
            return


    def getPictures(self, time_out = 50):
        Flag=True
        try:

            
            if DEBUG:
                print('TRIGE Done')

            if self.camera.IsGrabbing():
                if DEBUG:
                    print('Is grabbing')
                    
                    if self.camera.GetQueuedBufferCount() == 10:
                        # print('ERRRRRRRRRRRRRRRRRRRRRRRRRROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOORRRRRRRRRRRRRRRRRRRRRRRRR')
                        pass

                grabResult = self.camera.RetrieveResult(time_out, pylon.TimeoutHandling_ThrowException)

                # print('grab',grabResult)
                

                # print(self.camera.GetQueuedBufferCount(), 'f'*100)
                if DEBUG:
                    print('RetrieveResult')

                    if self.camera.GetQueuedBufferCount() == 10:
                        # print('ERRRRRRRRRRRRRRRRRRRRRRRRRROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOORRRRRRRRRRRRRRRRRRRRRRRRR')
                        pass

                if grabResult.GrabSucceeded():
                    
                    if DEBUG:
                        print('Grab Succed')

                    image = self.converter.Convert(grabResult)
                    img=image.Array

                else:
                    img=np.zeros([1200,1920,3],dtype=np.uint8)
                    self.cont_eror+=1
                    # print('eror',self.cont_eror)
                    # print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
                    Flag=False

            else:
                    # print('erpr')
                    img=np.zeros([1200,1920,3],dtype=np.uint8)
                    Flag=False

        except:
            #print('Time out')
            Flag=False

        
        if Flag:
            #print('yes')
            return True, img
        else:
            #print('no')
            return False, np.zeros([1200,1920,3],dtype=np.uint8)



def check_connectivity(cam_obj):
    while True:
        try:
            temp = cam_obj.get_tempreture()
        except:
            print('camera disconnected')
        cv2.waitKey(1000)



if __name__ == '__main__':

    # get available cameras serials
    collector = Collector(serial_number='0', list_devices_mode=True)
    serial_list = collector.serialnumber()
    print(serial_list)
    del collector


    collector0 = Collector(serial_number=serial_list[0], trigger=False, gain=256, exposure=100, width=6000, height=200, offset_y=0, manual=True)
    # collector1 = Collector(serial_number=serial_list[1], trigger=False)
    res, message = collector0.start_grabbing()
    # res, message = collector1.start_grabbing()
    print(res, message)


    
    while True:
        res0, img0 = collector0.getPictures()
        # temp0 = collector0.get_tempreture()
        # res1, img1 = collector1.getPictures()
        # temp1 = collector1.get_tempreture()



        if res0:
            if img0.shape[0] != 1:
                # print(img.shape)
                cv2.imshow('img1', cv2.resize(img0, None, fx=0.2, fy=0.2))
                # print(collector0.get_fps())
            
            else:
                pass
                # print('image with one row')

        else:
            # print('no frame')
            continue
    
        
        
        cv2.waitKey(50)


    
    

        

        
        