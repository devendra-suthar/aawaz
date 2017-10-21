import pandas
# Importing serail library
import serial
# Importing microsoft libraries (contains kbhit(), getch())
import msvcrt
# Importing Text to Speech
import win32com.client as wincl

# Importing sklearn library for Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# Creating a instance for speech
speak = wincl.Dispatch("SAPI.SpVoice")

class GestureRecognition:

    def __init__(self):
        self.knn = KNeighborsClassifier(n_neighbors=20)
        # Create Serial port object called arduinoSerialData
        self.arduinoSerialData = serial.Serial('com4', 9600)

    # Reading data from serial input until keyboard interrupt (CTRL+C)
    def readData(self, gestureNum):
        df = pandas.DataFrame()
        count = 0
        self.arduinoSerialData.flushInput()
        while 1:
            if self.arduinoSerialData.inWaiting() > 0:
                sensorData = str(self.arduinoSerialData.readline())
                l = sensorData.split(' ')
                row = pandas.Series([gestureNum, count, l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8][:-5]],
                                    ['gest_num', 'sample_count', 'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'o', 'm'])
                df = df.append([row])
                print(gestureNum, count, l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8][:-5])
                count += 1

            x = msvcrt.kbhit()
            if x:
                break

        return df

    # Recording gestures from the device and storing them into training data file
    def recordGesture(self):
        # Creating an instance of the Serial data handling class

        # Read CSV file containg recorded gesture data samples
        # A Separator parameter 'sep' is given when the separator in csv file is not comma else it takes comma as default
        gestureSample = pandas.read_csv('TrainingData.csv')
        labels = pandas.read_csv('GestureLabels.csv')

        # When not in use even due to sma
        # ll movements the accelerometer produces some data.
        # When the serial data is not being read, It is buffered at ARDUINO.
        # Flash the buffered data in ARDUINO before starting gesture record, so as to prevent recording of false data.

        gestureLabel = input("Enter Label for this sample: ")
        name = input("Enter Text for this Gesture: ")
        newGest = pandas.Series([gestureLabel, name], ['gestLabel', 'gestName'])
        labels = labels.append([newGest])
        # Invoking readData function to read Serail Data
        sample = self.readData(gestureLabel)

        # Appending the Gesture read to the currently existing database
        gestureSample = gestureSample.append(sample)

        # Writing new updated data to the file without the index column
        gestureSample.to_csv('TrainingData.csv', index=False)
        labels.to_csv('GestureLabels.csv', index = False)

    # Training the classifier from the data recorded in the Training data file using above funciton
    def train(self):
        df = pandas.read_csv('TrainingData.csv')
        # Assigining input values to x
        X_train = df.loc[:, 'ax':'m']
        # Assigining output values (i.e. to be predicted values) to y
        Y_train = df.loc[:, 'gest_num']

        # Importing MinMaxScaler and initializing it
        min_Max = MinMaxScaler()

        # Scaling down both train and test data set
        X_train_minmax = min_Max.fit_transform(X_train)

        # Fitting k-NN on our scaled data set
        self.knn.fit(X_train_minmax, Y_train)

    # Starting detection of gestures
    def startPredicting(self):
        capturedData = pandas.DataFrame()

        self.arduinoSerialData.flushInput()

        while not msvcrt.kbhit():
            if self.arduinoSerialData.inWaiting() > 0:
                sensorData = str(self.arduinoSerialData.readline())
                # value of l read from serial
                # ["b'Detecting_Gesture:", '2087', '-466', '7265', '-14.30', '8.19', '-71.81', '0', "2000\\r\\n'"]

                l = sensorData.split(' ')

                # value of l read from serial
                # ["b'Detecting_Gesture:", '2087', '-466', '7265', '-14.30', '8.19', '-71.81', '0', "2000\\r\\n'"]
                # b' is newline characters from serail data
                if l[0] == "b'DoubleTapDetected":
                    print("Sorry My fault")
                    speak.Speak("Sorry I predicted it Incorrectly")

                    # Flushing the data buffered while the script was busy speaking the text
                    self.arduinoSerialData.flushInput()

                    # Emptying the data readed till now
                    capturedData = pandas.DataFrame()
                    predicted = []
                    continue
                elif l[0] == "b'Detecting_Gesture:":
                    # using l[8][:-5]] to remove the unnecessory characters brhind the string
                    row = pandas.Series([l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8][:-5]],
                                        ['ax', 'ay', 'az', 'gx', 'gy', 'gz', 'o', 'm'])

                    capturedData = capturedData.append([row])

                    predicted = self.knn.predict(capturedData)

                    if len(predicted) > 20:
                        output = {}
                        for x in predicted:
                            if output.get(x):
                                output[x] = output.get(x) + 1
                            else:
                                output[x] = 1

                        max_key = max(output, key=lambda k: output[k])

                        # if max_key > 12:
                        labels = pandas.read_csv('GestureLabels.csv')
                        labels.set_index('gestLabel')
                        text = labels.get_value(max_key-1, 'gestName')
                        speak.Speak(text)


                        # else:
                        #     speak.Speak("Sorry I didn't understood you, Please try again.")

                        # Emptying the data readed till now
                        capturedData = pandas.DataFrame()
                        predicted = []

                        # Flushing the data buffered while the script was busy speaking the text
                        self.arduinoSerialData.flushInput()
                        continue
                    print(predicted)

    def samplePrediction(self):
        df = pandas.read_csv('TrainingData.csv')

        # Using predefined method to automatically divide the total data into test set amd test
        X_train, X_test, Y_train, Y_test = train_test_split(df.loc[:, 'ax':'m'], df.loc[:, 'gest_num'], test_size=.5)

        # Importing MinMaxScaler and initializing it
        min_Max = MinMaxScaler()

        # Scaling down both train and test data set
        X_train_minmax = min_Max.fit_transform(X_train)
        X_test_minmax = min_Max.fit_transform((X_test))

        # Initializing and Fitting a k-NN model
        knn = KNeighborsClassifier(n_neighbors=5)

        # Fitting k-NN on our scaled data set
        knn.fit(X_train_minmax, Y_train)

        # Checking the performance of our model on the testing data set
        a = accuracy_score(Y_test, knn.predict(X_test_minmax))
        print(a)

