import pyaudio
import _thread
import os
from scipy.signal import butter, lfilter
import numpy as np

FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 8000
CHUNK = 1024
RECORD_SECONDS = 30

p = pyaudio.PyAudio()

# Menu thread
class menu(object):
    def __init__(self):
        self.audioON = False
        self.filterON = False
        self.finished = False
    
    def selectMenu(self):
        while(True):
            os.system("clear")
            os.system("cls")
            
            print(f'AUDIO OUTPUT: {self.audioON}')
            print(f'FILTERING: {self.filterON}')
            print("\nEnter a command:\n<A> Toggle audio output\n<F> Toggle filtering\n<Q> Exit\n")
            sel = input('command: ')
            
            if sel.lower() == 'a':
                self.audioON = not self.audioON
            elif sel.lower() == 'f':
                self.filterON = not self.filterON
            elif sel.lower() == 'q':
                self.finished = True
            else:
                pass
            
            if self.finished:
                break
        

# Start an output stream on specified output_device_id
def start_out_stream(outDevice):
    stream = p.open(format=FORMAT, channels=1, rate=8000, output_device_index=outDevice, output=True)
    return stream

# Start an output stream on specified input_device_id
def start_input_stream(inDevice):
    stream = p.open(format=FORMAT, channels=1, rate=8000, input_device_index=inDevice, input=True)
    return stream

# Make a list of the connected audio devices
def list_devices():
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')

    print('The following audio devices were found:')

    print('INPUT')
    for i in range(0, num_devices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("ID: ", i, " : ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

    print('OUTPUT')
    for i in range(0, num_devices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
            print("ID: ", i, " : ", p.get_device_info_by_host_api_device_index(0, i).get('name'))


# Butterworth bandstop filter
def butter_bandstop(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='bandstop')
    return b, a

def butter_bandstop_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandstop(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y


list_devices()

input_ID = int(input("Select an input device ID:\n"))
output_ID = int(input("Select an output device ID:\n"))


# Start menu thread
menu = menu()
_thread.start_new_thread(menu.selectMenu,())


# Initialize input stream
in_stream = start_input_stream(input_ID)

# Initialize output stream
out_stream = start_out_stream(output_ID)

while(True):
    # Read a chunk of data from input
    data = in_stream.read(CHUNK)

    # If output stream is enabled, write on output
    if menu.audioON:
        # If filter is enabled, filter the signal before writing
        if menu.filterON:
            # Decode input signal
            decoded = np.frombuffer(data, 'float32')

            # Process input signal
            filtered_signal = None
            filtered_signal = butter_bandstop_filter(decoded, 500, 2000, RATE)
            
            # Encode the signal again and write on output stream
            out = np.array(filtered_signal, dtype='<f4').tobytes()
            out_stream.write(out)

        else:
            # Write signal without processing
            out_stream.write(data)
        
    if menu.finished:
        break

print("END")

# Close streams
out_stream.stop_stream()
out_stream.close()

in_stream.stop_stream()
in_stream.close()

p.terminate()
