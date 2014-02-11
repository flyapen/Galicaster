# -*- coding:utf-8 -*-
# Galicaster, Multistream Recorder and Player
#
#       galicaster/recorder/bins/screen
#
# Copyright (c) 2011, Teltek Video Research <galicaster@teltek.es>
#
# This work is licensed under the Creative Commons Attribution-
# NonCommercial-ShareAlike 3.0 Unported License. To view a copy of
# this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California, 94105, USA.
import gobject
import gst
import re

from os import path


from galicaster.recorder import base
from galicaster.recorder import module_register


pipestr = (' ximagesrc endx=gc-endx name=gc-screen-src ! capsfilter name=gc-screen-filter ! '
           ' queue ! tee name=tee-vt  ! '
           ' queue !  ffmpegcolorspace ! queue ! xvimagesink sync=false async=false qos=false name=gc-screen-preview'
           ' tee-vt. ! queue ! valve drop=false name=gc-screen-valve ! ffmpegcolorspace ! queue ! '
           ' gc-screen-enc ! '
           ' queue ! filesink name=gc-screen-sink async=false')


class GCscreen(gst.Bin, base.Base):

    order = ["name","flavor","location","file","caps", 
             "pattern","color1","color2", "videoencoder", "muxer", "endx"
             ]
 
    gc_parameters = {
        "name": {
            "type": "text",
            "default": "ScreenCapture",
            "description": "Name assigned to the device",
            },
        "flavor": {
            "type": "flavor",
            "default": "presenter",
            "description": "Matterhorn flavor associated to the track",
            },
        "location": {
            "type": "device",
            "default": "default",
            "description": "Device's mount point of the output",
            },
        "file": {
            "type": "text",
            "default": "CAMERA.avi",
            "description": "The file name where the track will be recorded.",
             },
        "endx":{
            "type": "text",
            "default": "1920",
            "description": "bottom right",
        },
      
        "caps": {
            "type": "text",
            "default": "video/x-raw,framerate=30/1", 
            "description": "Forced capabilities", 
            },
        "videoencoder": {
            "type": "text",
            "default": "xvidenc bitrate=5000000",
            # "ffenc_mpeg2video quantizer=4 gop-size=1 bitrate=10000000",
            # "x264enc pass=5 quantizer=22 speed-preset=4 profile=1"
            "description": "Gstreamer encoder element used in the bin",
            }
        }
    
    is_pausable = True
    has_audio   = False
    has_video   = True

    __gstdetails__ = (
        "Galicaster Video Test Bin",
        "Generic/Video",
        "Bint to capture screen for screencast",
        "University of Bergen",
        )


    def __init__(self, options={}):
        base.Base.__init__(self, options)
        gst.Bin.__init__(self, self.options['name'])

        aux = (pipestr.replace('gc-screen-preview', 'sink-' + self.options['name'])
                      .replace('gc-endx', self.options['endx'])
                      .replace('gc-screen-enc', self.options['videoencoder']))

        #bin = gst.parse_bin_from_description(aux, False)
        bin = gst.parse_launch("( {} )".format(aux))
        self.add(bin)

        self.get_by_name('gc-screen-sink').set_property('location', path.join(self.options['path'], self.options['file']))
        #self.get_by_name('gc-endx').set_property('endx', self.options['endx'])
        

        #self.get_by_name('gc-screen-filter').set_property('caps', gst.Caps(self.options['caps']))
        #fr = re.findall("framerate *= *[0-9]+/[0-9]+", self.options['caps'])
        #if fr:
        #    newcaps = 'video/x-raw-yuv,' + fr[0]
            #self.get_by_name('gc-screen-vrate').set_property('caps', gst.Caps(newcaps))
     
    def changeValve(self, value):
        valve1=self.get_by_name('gc-screen-valve')
        valve1.set_property('drop', value)

    def getVideoSink(self):
        return self.get_by_name('gc-screen-preview')

    def getSource(self):
        return self.get_by_name('gc-screen-src')

    def send_event_to_src(self, event):
        src1 = self.get_by_name('gc-screen-src')
        src1.send_event(event)


gobject.type_register(GCscreen)
gst.element_register(GCscreen, 'gc-screen-bin')
module_register(GCscreen, 'screen')
