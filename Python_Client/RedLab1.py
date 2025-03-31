from __future__ import absolute_import, division, print_function
from mcculw import ul
from mcculw.enums import ULRange
from mcculw.ul import ULError
from mcculw.enums import ScanOptions, FunctionType, Status
from mcculw.device_info import DaqDeviceInfo

from builtins import *  # @UnusedWildImport

from ctypes import c_double, cast, POINTER, addressof, sizeof, c_ushort, c_ulong
from time import sleep
from sys import stdout

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

#board number same as in InstaCal app
def measure_and_save(rate = 50_000, path = '.', measurement_i = 0, low_chan = 0, high_chan = 0, buffer_size_seconds = 4,  num_buffers_to_write = 1):
    # rate - [smp/channel/second]
    # path - path to store data, <path>/redlab_data.csv
    # low_chan, high_chan -  start and stop channels to scan
    # buffer_size_seconds - The size of the UL buffer to create, in seconds
    # num_buffers_to_write - The number of buffers to write. After this number of UL buffers are
    #       written to file, the example will be stopped.

    if(not os.path.exists(path)):
        os.mkdir(path)
    file_name = path + "/" + str(measurement_i) +  "redlab_data.csv"
    board_num = 0 # The board_num variable needs to match the desired board number configured with Instacal.
    memhandle = None
    daq_dev_info = DaqDeviceInfo(board_num)
    ai_info = daq_dev_info.get_ai_info()
    print(ai_info.supported_ranges)
    ai_range = ai_info.supported_ranges[0] # to do 

    try:
        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_analog_input:
            raise Exception('Error: The DAQ device does not support '
                            'analog input')

        print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        num_chans = high_chan - low_chan + 1

        # Create a circular buffer that can hold buffer_size_seconds worth of
        # data, or at least 10 points (this may need to be adjusted to prevent
        # a buffer overrun)
        points_per_channel = max(rate * buffer_size_seconds, 10)

        # Some hardware requires that the total_count is an integer multiple
        # of the packet size. For this case, calculate a points_per_channel
        # that is equal to or just above the points_per_channel selected
        # which matches that requirement.
        if ai_info.packet_size != 1:
            packet_size = ai_info.packet_size
            #print(packet_size)
            remainder = points_per_channel % packet_size
            if remainder != 0:
                points_per_channel += packet_size - remainder

        ul_buffer_count = points_per_channel * num_chans
        # print("ul_buffer_count: ", ul_buffer_count)

        # Write the UL buffer to the file num_buffers_to_write times.
        points_to_write = ul_buffer_count * num_buffers_to_write
        # print("points_to_write: ", points_to_write) 
        # When handling the buffer, we will read 1/10 of the buffer at a time
        write_chunk_size = int(ul_buffer_count / 10)

        ai_range = ai_info.supported_ranges[0]
        

        scan_options = (ScanOptions.BACKGROUND| ScanOptions.CONTINUOUS)
        # print("res: ", ai_info.resolution)

        if ai_info.resolution <= 16:
            # Use the win_buf_alloc method for devices with a resolution <= 16
            memhandle = ul.win_buf_alloc(ul_buffer_count)
            # Convert the memhandle to a ctypes array.
            ctypes_array = cast(memhandle, POINTER(c_ushort))
            POINTER_TYPE = c_ushort
        else:
            # Use the win_buf_alloc_32 method for devices with a resolution > 16
            memhandle = ul.win_buf_alloc_32(ul_buffer_count)
            # Convert the memhandle to a ctypes array.
            ctypes_array = cast(memhandle, POINTER(c_ulong))
            POINTER_TYPE = c_ulong

        # Allocate an array of doubles temporary storage of the data
        write_chunk_array = (POINTER_TYPE * write_chunk_size)()

        #print("write chynk size: ", write_chunk_size)

        # Check if the buffer was successfully allocated
        if not memhandle:
            raise Exception('Failed to allocate memory')

        # Start the scan
        ul.a_in_scan(
            board_num, low_chan, high_chan, ul_buffer_count,
            rate, ai_range, memhandle, scan_options)

        status = Status.IDLE
        # Wait for the scan to start fully
        while status == Status.IDLE:
            status, _, _ = ul.get_status(board_num, FunctionType.AIFUNCTION)

        # Create a file for storing the data
        with open(file_name, 'w') as f:
            #print('Writing data to ' + file_name, end='')

            # Write a header to the file
            for chan_num in range(low_chan, high_chan + 1):
                f.write('Channel ' + str(chan_num) + ',')
            f.write(u'\n')

            # Start the write loop
            prev_count = 0
            prev_index = 0
            write_ch_num = low_chan
            while status != Status.IDLE:
                # Get the latest counts
                status, curr_count, _ = ul.get_status(board_num,
                                                      FunctionType.AIFUNCTION)

                new_data_count = curr_count - prev_count

                # Check for a buffer overrun before copying the data, so
                # that no attempts are made to copy more than a full buffer
                # of data
                if new_data_count > ul_buffer_count:
                    # Print an error and stop writing
                    ul.stop_background(board_num, FunctionType.AIFUNCTION)
                    print('A buffer overrun occurred')
                    break

                # Check if a chunk is available
                if new_data_count > write_chunk_size:
                    wrote_chunk = True
                    # Copy the current data to a new array

                    # Check if the data wraps around the end of the UL
                    # buffer. Multiple copy operations will be required.
                    if prev_index + write_chunk_size > ul_buffer_count - 1:
                        first_chunk_size = ul_buffer_count - prev_index
                        second_chunk_size = (
                            write_chunk_size - first_chunk_size)

                        # Copy the first chunk of data to the
                        # write_chunk_array
                        ul.win_buf_to_array(
                            memhandle, write_chunk_array, prev_index,
                            first_chunk_size)

                        # Create a pointer to the location in
                        # write_chunk_array where we want to copy the
                        # remaining data
                        second_chunk_pointer = cast(addressof(write_chunk_array)
                                                    + first_chunk_size
                                                    * sizeof(POINTER_TYPE),
                                                    POINTER(POINTER_TYPE))

                        # Copy the second chunk of data to the
                        # write_chunk_array
                        ul.win_buf_to_array(
                            memhandle, second_chunk_pointer,
                            0, second_chunk_size)
                    else:
                        # Copy the data to the write_chunk_array
                        ul.win_buf_to_array(
                            memhandle, write_chunk_array, prev_index,
                            write_chunk_size)

                    # Check for a buffer overrun just after copying the data
                    # from the UL buffer. This will ensure that the data was
                    # not overwritten in the UL buffer before the copy was
                    # completed. This should be done before writing to the
                    # file, so that corrupt data does not end up in it.
                    status, curr_count, _ = ul.get_status(
                        board_num, FunctionType.AIFUNCTION)
                    if curr_count - prev_count > ul_buffer_count:
                        # Print an error and stop writing
                        ul.stop_background(board_num, FunctionType.AIFUNCTION)
                        print('A buffer overrun occurred')
                        break

                    for i in range(write_chunk_size):
                        #print(write_chunk_array[i])
                        # f.write(write_chunk_array[i]) 
                        f.write(str(write_chunk_array[i])  + ',')
                        write_ch_num += 1
                        if write_ch_num == high_chan + 1:
                            write_ch_num = low_chan
                            f.write(u'\n')
                else:
                    wrote_chunk = False

                if wrote_chunk:
                    # Increment prev_count by the chunk size
                    prev_count += write_chunk_size
                    # Increment prev_index by the chunk size
                    prev_index += write_chunk_size
                    # Wrap prev_index to the size of the UL buffer
                    prev_index %= ul_buffer_count

                    if prev_count >= points_to_write:
                        break
                    print('.', end='')
                else:
                    # Wait a short amount of time for more data to be
                    # acquired.
                    #print("waiting\n")
                    sleep(0.1)

        ul.stop_background(board_num, FunctionType.AIFUNCTION)
    except Exception as e:
        print('\n', e)
    finally:
        print('Done')
        if memhandle:
            # Free the buffer in a finally block to prevent  a memory leak.
            ul.win_buf_free(memhandle)

def measure_raw(rate = 50_000, chan = 0, buffer_size_seconds = 4,  num_buffers_to_write = 1):
    # rate - [smp/channel/second]
    # path - path to store data, <path>/redlab_data.csv
    # chan - channel to scan, only one
    # buffer_size_seconds - The size of the UL buffer to create, in seconds
    # num_buffers_to_write - The number of buffers to write. After this number of UL buffers are
    #       written to file, the example will be stopped.

    low_chan = chan
    high_chan = chan
    board_num = 0 # The board_num variable needs to match the desired board number configured with Instacal.
    memhandle = None
    daq_dev_info = DaqDeviceInfo(board_num)
    ai_info = daq_dev_info.get_ai_info()
    ai_range = ai_info.supported_ranges[0] # to do 

    data_array = np.empty(shape = 0, dtype = int)

    try:
        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_analog_input:
            raise Exception('Error: The DAQ device does not support '
                            'analog input')

        #print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',daq_dev_info.unique_id, ')\n', sep='')

        num_chans = high_chan - low_chan + 1

        # Create a circular buffer that can hold buffer_size_seconds worth of
        # data, or at least 10 points (this may need to be adjusted to prevent
        # a buffer overrun)
        points_per_channel = max(rate * buffer_size_seconds, 10)

        # Some hardware requires that the total_count is an integer multiple
        # of the packet size. For this case, calculate a points_per_channel
        # that is equal to or just above the points_per_channel selected
        # which matches that requirement.
        if ai_info.packet_size != 1:
            packet_size = ai_info.packet_size
            #print(packet_size)
            remainder = points_per_channel % packet_size
            if remainder != 0:
                points_per_channel += packet_size - remainder

        ul_buffer_count = points_per_channel * num_chans
        # print("ul_buffer_count: ", ul_buffer_count)

        # Write the UL buffer to the file num_buffers_to_write times.
        points_to_write = ul_buffer_count * num_buffers_to_write
        # print("points_to_write: ", points_to_write) 
        # When handling the buffer, we will read 1/10 of the buffer at a time
        write_chunk_size = int(ul_buffer_count / 10)

        ai_range = ai_info.supported_ranges[0]
        

        scan_options = (ScanOptions.BACKGROUND| ScanOptions.CONTINUOUS)
        # print("res: ", ai_info.resolution)

        if ai_info.resolution <= 16:
            # Use the win_buf_alloc method for devices with a resolution <= 16
            memhandle = ul.win_buf_alloc(ul_buffer_count)
            # Convert the memhandle to a ctypes array.
            ctypes_array = cast(memhandle, POINTER(c_ushort))
            POINTER_TYPE = c_ushort
        else:
            # Use the win_buf_alloc_32 method for devices with a resolution > 16
            memhandle = ul.win_buf_alloc_32(ul_buffer_count)
            # Convert the memhandle to a ctypes array.
            ctypes_array = cast(memhandle, POINTER(c_ulong))
            POINTER_TYPE = c_ulong

        # Allocate an array of doubles temporary storage of the data
        write_chunk_array = (POINTER_TYPE * write_chunk_size)()

        # print("write chynk size: ", write_chunk_size)

        # Check if the buffer was successfully allocated
        if not memhandle:
            raise Exception('Failed to allocate memory')

        # Start the scan
        ul.a_in_scan(
            board_num, low_chan, high_chan, ul_buffer_count,
            rate, ai_range, memhandle, scan_options)

        status = Status.IDLE
        # Wait for the scan to start fully
        while status == Status.IDLE:
            status, _, _ = ul.get_status(board_num, FunctionType.AIFUNCTION)

        # Start the write loop
        prev_count = 0
        prev_index = 0
        write_ch_num = low_chan
        while status != Status.IDLE:
            # Get the latest counts
            status, curr_count, _ = ul.get_status(board_num,
                                                    FunctionType.AIFUNCTION)

            new_data_count = curr_count - prev_count

            # Check for a buffer overrun before copying the data, so
            # that no attempts are made to copy more than a full buffer
            # of data
            if new_data_count > ul_buffer_count:
                # Print an error and stop writing
                ul.stop_background(board_num, FunctionType.AIFUNCTION)
                print('A buffer overrun occurred')
                break

            # Check if a chunk is available
            if new_data_count > write_chunk_size:
                wrote_chunk = True
                # Copy the current data to a new array

                # Check if the data wraps around the end of the UL
                # buffer. Multiple copy operations will be required.
                if prev_index + write_chunk_size > ul_buffer_count - 1:
                    first_chunk_size = ul_buffer_count - prev_index
                    second_chunk_size = (
                        write_chunk_size - first_chunk_size)

                    # Copy the first chunk of data to the
                    # write_chunk_array
                    ul.win_buf_to_array(
                        memhandle, write_chunk_array, prev_index,
                        first_chunk_size)

                    # Create a pointer to the location in
                    # write_chunk_array where we want to copy the
                    # remaining data
                    second_chunk_pointer = cast(addressof(write_chunk_array)
                                                + first_chunk_size
                                                * sizeof(POINTER_TYPE),
                                                POINTER(POINTER_TYPE))

                    # Copy the second chunk of data to the
                    # write_chunk_array
                    ul.win_buf_to_array(
                        memhandle, second_chunk_pointer,
                        0, second_chunk_size)
                else:
                    # Copy the data to the write_chunk_array
                    ul.win_buf_to_array(
                        memhandle, write_chunk_array, prev_index,
                        write_chunk_size)

                # Check for a buffer overrun just after copying the data
                # from the UL buffer. This will ensure that the data was
                # not overwritten in the UL buffer before the copy was
                # completed. This should be done before writing to the
                # file, so that corrupt data does not end up in it.
                status, curr_count, _ = ul.get_status(
                    board_num, FunctionType.AIFUNCTION)
                if curr_count - prev_count > ul_buffer_count:
                    # Print an error and stop writing
                    ul.stop_background(board_num, FunctionType.AIFUNCTION)
                    print('A buffer overrun occurred')
                    break

                data_array = np.concatenate([data_array, write_chunk_array], axis = 0, dtype = int)

            else:
                wrote_chunk = False

            if wrote_chunk:
                # Increment prev_count by the chunk size
                prev_count += write_chunk_size
                # Increment prev_index by the chunk size
                prev_index += write_chunk_size
                # Wrap prev_index to the size of the UL buffer
                prev_index %= ul_buffer_count

                if prev_count >= points_to_write:
                    break
                print('.', end='')
            else:
                # Wait a short amount of time for more data to be
                # acquired.
                #print("waiting\n")
                sleep(0.1)

        ul.stop_background(board_num, FunctionType.AIFUNCTION)
    except Exception as e:
        print('\n', e)
    finally:
        ul.stop_background(board_num, FunctionType.AIFUNCTION)
        print('Done acquiring redlab data')
        if memhandle:
            # Free the buffer in a finally block to prevent  a memory leak.
            ul.win_buf_free(memhandle)
        
        return data_array


def measure(rate = 50_000, chan = 0, buffer_size_seconds = 4,  num_buffers_to_write = 1):
    if(rate > 50_000):
        print("rate cannot excess 50_000 [Smp/sec/chan] or ?[Smp/sec]?")
    data_array = measure_raw(rate = rate, chan = chan, buffer_size_seconds = buffer_size_seconds, num_buffers_to_write = num_buffers_to_write )
    return convert_data_array(data_array)

def measure_and_concat(data_big, rate = 50_000, chan = 0, buffer_size_seconds = 4,  num_buffers_to_write = 1):
    data = measure(rate = rate, chan = chan, buffer_size_seconds = buffer_size_seconds, num_buffers_to_write = num_buffers_to_write )
    data_big = np.concat([data_big, data], axis = 0)
    return data_big

def measure_and_concat_raw(data_big, rate = 50_000, chan = 0, buffer_size_seconds = 4,  num_buffers_to_write = 1):
    data = measure_raw(rate = rate, chan = chan, buffer_size_seconds = buffer_size_seconds, num_buffers_to_write = num_buffers_to_write )
    data_big = np.concat([data_big, data], axis = 0)
    return data_big

def convert_data_file(path):

    board_num = 0 # The board_num variable needs to match the desired board number configured with Instacal.
    daq_dev_info = DaqDeviceInfo(board_num)
    ai_info = daq_dev_info.get_ai_info()
    ai_range = ai_info.supported_ranges[0]

    data = pd.read_csv(path, skiprows=0)
    data = np.array(data)[:,0]
    #print(data)
    data_converted = np.zeros(shape = data.shape)
    for i in range(len(data)):
        data_converted[i] = ul.to_eng_units(board_num, ai_range, int(data[i]))

    # print("data_converted.size: ", data_converted.size)
    #print(data_converted.dtype)

    plt.plot(data_converted, "r.", ms = 2)
    plt.show()

def convert_data_array(data, ai_range = None):

    if( ai_range is None):
        board_num = 0 # The board_num variable needs to match the desired board number configured with Instacal.
        daq_dev_info = DaqDeviceInfo(board_num)
        ai_info = daq_dev_info.get_ai_info()
        ai_range = ai_info.supported_ranges[0]
    if(type(ai_range) != type(ULRange.BIP5VOLTS)):
        print("wrong range type")
        return np.nan

    #print(data)
    data_converted = np.zeros(shape = data.shape)
    for i in range(len(data)):
        data_converted[i] = ul.to_eng_units(board_num, ai_range, int(data[i]))

    return data_converted

def counter():

    board_num = 0
    daq_dev_info = DaqDeviceInfo(board_num)
    ctr_info = daq_dev_info.get_ctr_info()
    counter_num = ctr_info.chan_info[0].channel_num
    ai_info = daq_dev_info.get_ai_info()
    ai_range = ai_info.supported_ranges[0]

    ul.c_clear(board_num, counter_num)
    while True:
        # Read and display the data.
        counter_value = ul.c_in_32(board_num, counter_num)
        print('\r    Counter ', counter_num, ':',
                str(counter_value).rjust(12), sep='', end='')
        value = ul.a_in(board_num, 0, ai_range)
        # Convert the raw value to engineering units
        eng_units_value = ul.to_eng_units(board_num, ai_range, value)
        print(" Volt: ", eng_units_value, end = "")
        stdout.flush()
        sleep(0.1)
    


## TO DO ##
# measure raw dla więdcej niż 1 kanału