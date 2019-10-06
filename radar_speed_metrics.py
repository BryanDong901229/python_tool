#!/usr/bin/env python

import argparse
import rosbag
import rospy
import Queue
import numpy as np
from std_msgs.msg import String
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import logging
import math
import time
from dbw_mkz_msgs.msg import *
#from radar_msgs.msg import *
from conti_radar_msgs.msg import *

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class ContiRadar21XXLateralSpeed:
    def __init__(self):
        self.values = []
        self.times = []
        self.topic = '/conti_bumper_radar/conti_bumper_radar/radar_parsed'
    def add(self, topic, msg, t):
        if topic == self.topic:
            #self.values.append(msg.tracks[9].linear_velocity.y * 3.6)
            self.values.append(msg.tracks[9].lateral_vel * 3.6)
            self.times.append(t)

class ContiRadar21XXLongitudeSpeed:
    def __init__(self):
        self.values = []
        self.times = []
        self.topic = '/conti_bumper_radar/conti_bumper_radar/radar_parsed'
    def add(self, topic, msg, t):
        if topic == self.topic:
            #self.values.append(msg.tracks[9].linear_velocity.x * 3.6)
            self.values.append(msg.tracks[9].longitude_vel * 3.6)
            self.times.append(t)

class ContiRadar21SCLateralSpeed:
    def __init__(self):
        self.values = []
        self.times = []
        self.topic = '/conti_bumper_radar_21SC/conti_bumper_radar_21SC/radar_parsed'
    def add(self, topic, msg, t):
        if topic == self.topic:
            #self.values.append(msg.tracks[13].linear_velocity.y * 3.6)
            self.values.append(msg.tracks[13].lateral_vel * 3.6)
            self.times.append(t)

class ContiRadar21SCLongitudeSpeed:
    def __init__(self):
        self.values = []
        self.times = []
        self.topic = '/conti_bumper_radar_21SC/conti_bumper_radar_21SC/radar_parsed'
    def add(self, topic, msg, t):
        if topic == self.topic:
            #self.values.append(msg.tracks[13].linear_velocity.x * 3.6)
            self.values.append(msg.tracks[13].longitude_vel * 3.6)
            self.times.append(t)

class RadarReader:
    def __init__(self, args):
        self.bag_file = args.bag_file
        self.start_time_sec = None
        self.graph_data = [ ContiRadar21XXLateralSpeed(),
                            ContiRadar21XXLongitudeSpeed(),
                            ContiRadar21SCLateralSpeed(),
                            ContiRadar21SCLongitudeSpeed(),
        ]

    def read_bag(self):
        logger.info('Opening bag file: {}'.format(self.bag_file))
        bag = rosbag.Bag(self.bag_file)
        logger.info('Reading {} messages (duration: {:.1f} sec)...'.format(
            bag.get_message_count(), bag.get_end_time() - bag.get_start_time()))
        for topic, msg, t in bag.read_messages(topics=[ d.topic for d in self.graph_data ]):
            self.last_time_sec = t.to_sec()
            if self.start_time_sec is None:
                self.start_time_sec = t.to_sec()
            for data in self.graph_data:
                data.add(topic, msg, t.to_sec() - self.start_time_sec)
        self.graph()

    def graph(self):
        logger.info('Graphing data...')
        logger.info('Start time is %s and end time is %s' % (self.start_time_sec, self.last_time_sec))
        matplotlib.rcParams.update({'font.size': 8})
        self.fig = plt.figure(num = 0, figsize = (8, 6), dpi =120)
        gs = gridspec.GridSpec(2, 4)
        gs.update(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.05, hspace=0.25)

        self.graph_lateral_speed = self.fig.add_subplot(gs[0, :])
        self.graph_lateral_speed.set_title('radar lateral speed(kph) vs time')

        self.graph_lateral_speed.plot(
            self.graph_data[0].times,
            self.graph_data[0].values,
            color='red',
            marker='.',
            linestyle='solid',
            label='Conti Radar 21XX Lateral Speed KPH',
            linewidth=0.5)
        self.graph_lateral_speed.plot(
            self.graph_data[2].times,
            self.graph_data[2].values,
            color='green',
            marker='.',
            linestyle='solid',
            label='Conti Radar 21SC Lateral Speed KPH',
            linewidth=0.5)
        plt.legend()

        self.graph_longitude_speed = self.fig.add_subplot(gs[1, :], sharex = self.graph_lateral_speed)
        self.graph_longitude_speed.set_title('radar longitude speed(kph) vs time')
        self.graph_longitude_speed.plot(
            self.graph_data[1].times,
            self.graph_data[1].values,
            color='blue',
            marker='.',
            linestyle='solid',
            label='Conti Radar 21XX Longitude Speed KPH',
            linewidth=0.5)
        self.graph_longitude_speed.plot(
            self.graph_data[3].times,
            self.graph_data[3].values,
            color='purple',
            marker='.',
            linestyle='solid',
            label='Conti Radar 21SC Longitude Speed KPH',
            linewidth=0.5)

        plt.legend()
        plt.show()


def main(args):
    RadarReader(args).read_bag()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="plot radar speed metrics")
    parser.add_argument('--bag_file', help='bagfile to read')
    args = parser.parse_args()
    main(args)
